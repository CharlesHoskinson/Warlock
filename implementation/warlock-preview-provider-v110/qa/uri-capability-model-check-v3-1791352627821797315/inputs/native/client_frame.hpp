#pragma once
#include "preview_wire.hpp"

namespace preview::bridge {
struct ClientCapture {
    Binding binding;
    Context context;
    uint64_t request{},completed{},deadline{},width{},height{},bytes{},producerBytes{},crc{};
};
class ClientCaptureIntent {
    SourceObservation observed_;
    uint64_t request_,deadline_;
    std::string command_;
    ClientCaptureIntent(SourceObservation observed,uint64_t request,uint64_t deadline,std::string command):
        observed_(observed),request_(request),deadline_(deadline),command_(std::move(command)){}
    friend ClientCaptureIntent prepareClientCapture(Native&,const SourceObservation&,uint64_t);
public:
    const SourceObservation& observed()const noexcept{return observed_;}
    uint64_t request()const noexcept{return request_;}
    uint64_t deadline()const noexcept{return deadline_;}
    const std::string& command()const noexcept{return command_;}
};
// Preparation may consume a native request serial, but sends no capture. The
// owning caller retains this exact intent before entering the native effect.
inline ClientCaptureIntent prepareClientCapture(Native& native,const SourceObservation& observed,uint64_t deadline) {
    const auto& scope=observed.scope;
    require(observed.kind==SourceObservation::Kind::UnqualifiedClientMain && !observed.previewEligible,
            "Explicit unqualified client MAIN capture route");
    require(scope.binding==native.binding() && scope.context.lifetime==scope.binding.lifetime &&
            scope.clock.value==scope.binding.lifetime.value && scope.present && scope.sourceLive && !scope.locked && scope.gpuReady,
            "Current own native client capture scope");
    require(deadline>scope.now && deadline-scope.now<=2000000000ULL,"Original client capture deadline");
    const auto request=native.next();Wire wire;
    wire.integer("protocolVersion",3).text("kind","preview-client-scoped-request").begin("binding").binding(scope.binding).end()
        .counter("requestId",request).counter("subjectIncarnation",scope.context.incarnation.value)
        .counter("deadlineNs",deadline).begin("context").context(scope.context).end();
    auto command=wire.finish();require(command.size()<=4096,"Bounded original native capture intent");
    return ClientCaptureIntent(observed,request,deadline,std::move(command));
}
inline ClientCapture captureClient(Native& native,const ClientCaptureIntent& intent) {
    const auto& observed=intent.observed();const auto& scope=observed.scope;
    const auto request=intent.request(),deadline=intent.deadline();
    require(scope.binding==native.binding(),"Original retained native capture intent binding");
    auto reply=native.control(intent.command());auto object=reply.object();
    Json::fields(object,{"protocolVersion","kind","binding","requestId","subjectIncarnation","captureRequest",
        "outputGeneration","completedNs","width","height","encodedBytes","ownedBytes","crc32","encoding","planeSpace","previewEligible"});
    require(std::string_view(Json::text(object,"kind"))=="preview-client-owned" && decodeBinding(Json::child(object,"binding"))==scope.binding &&
            reply.counter("requestId")==request && reply.counter("captureRequest")==request &&
            reply.counter("subjectIncarnation")==scope.context.incarnation.value && reply.counter("outputGeneration")==scope.context.output.value,
            "Exact native client capture reply correlation");
    require(!Json::boolean(object,"previewEligible") && std::string_view(Json::text(object,"encoding"))=="PNG-RGBA8-straight" &&
            std::string_view(Json::text(object,"planeSpace"))=="client-logical-unqualified","Client pixels remain unqualified");
    const auto completed=reply.counter("completedNs"),bytes=reply.counter("encodedBytes"),owned=reply.counter("ownedBytes");
    const auto width=Json::integer(object,"width"),height=Json::integer(object,"height");
    // CRC32 may be zero; unlike identities it is an unsigned decimal value.
    auto raw=std::string_view(Json::text(object,"crc32"));uint64_t crc{};
    if(raw!="0")crc=decimal(raw);
    require(completed>=scope.now && completed<deadline && width>0 && width<=4096 && height>0 && height<=4096 &&
            bytes>=8 && bytes<=observed.maximumTransferBytes && owned>=bytes && crc<=UINT32_MAX,"Bounded original client capture metadata");
    return {scope.binding,scope.context,request,completed,deadline,static_cast<uint64_t>(width),static_cast<uint64_t>(height),bytes,owned,crc};
}
inline ClientCapture captureClient(Native& native,const SourceObservation& observed,uint64_t deadline) {
    return captureClient(native,prepareClientCapture(native,observed,deadline));
}
inline bool clientFrameMatches(const fd::Header& h,const ClientCapture& capture) {
    return h[fd::Magic]==fd::MAGIC && h[fd::Version]==1 && h[fd::Status]==0 &&
        fd::imageHeaderFor(h,fd::SourcePlane::ClientMain) && h[fd::Flags]==11 &&
        h[fd::Lifetime]==capture.binding.lifetime.value && h[fd::Session]==capture.binding.session.value && h[fd::Frontend]==capture.binding.frontend.value &&
        h[fd::Capture]==capture.request && h[fd::Subject]==capture.context.incarnation.value && h[fd::Output]==capture.context.output.value &&
        h[fd::Privacy]==capture.context.privacy.value && h[fd::Rendering]==capture.context.rendering.value &&
        h[fd::Scene]==capture.context.scene.value && h[fd::Content]==capture.context.content.value &&
        h[fd::Deadline]==capture.deadline && h[fd::Completed]==capture.completed && h[fd::Now]<capture.deadline &&
        h[fd::Width]==capture.width && h[fd::Height]==capture.height && h[fd::Bytes]==capture.bytes && h[fd::CRC]==capture.crc &&
        h[fd::Charge]==((capture.bytes+4095)&~uint64_t{4095}) && h[fd::Expires]>h[fd::Now];
}
// Physical mapping closure/export release and producer retirement are separate
// operations. Callers retain the exact transfer and journal until each succeeds.
inline bool releaseClient(Native& native,const ClientCapture& capture,uint64_t transfer) {
    require(capture.binding==native.binding() && transfer,"Own native client transfer release");
    auto reply=native.query(fd::Release,capture.request,capture.context.incarnation.value,transfer);
    return reply.has_value();
}
enum class ClientRetirement {Retired,PendingLock};
inline ClientRetirement decodeClientRetirement(const Json& reply,Binding owner,uint64_t request) {
    auto object=reply.object();
    if(std::string_view(Json::text(object,"kind"))=="refused") {
        Json::fields(object,{"protocolVersion","kind","reason"});require(Json::integer(object,"protocolVersion")==3,"Native retirement refusal protocol");
        require(std::string_view(Json::text(object,"reason"))=="preview-client-locked","Unresolved native producer retirement");
        return ClientRetirement::PendingLock;
    }
    Json::fields(object,{"protocolVersion","kind","binding","requestId","ownedBytes"});
    require(Json::integer(object,"protocolVersion")==3 && std::string_view(Json::text(object,"kind"))=="preview-client-retired" && decodeBinding(Json::child(object,"binding"))==owner &&
        reply.counter("requestId")==request && std::string_view(Json::text(object,"ownedBytes"))=="0","Exact own producer zero retirement");
    return ClientRetirement::Retired;
}
inline ClientRetirement retireClientState(Native& native) {
    const auto request=native.next();Wire wire;
    wire.integer("protocolVersion",3).text("kind","preview-client-retire-request").begin("binding").binding(native.binding()).end().counter("requestId",request);
    auto reply=native.control(wire.finish());return decodeClientRetirement(reply,native.binding(),request);
}
inline bool retireClient(Native& native) {return retireClientState(native)==ClientRetirement::Retired;}
}
