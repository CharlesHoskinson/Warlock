#pragma once
#include "family_source.hpp"
#include "client_frame.hpp"

namespace preview::bridge {
struct FamilyCapture {
    Binding binding;Context context;
    uint64_t request{},completed{},deadline{},width{},height{},bytes{},producerBytes{},crc{};
    FamilyCrop crop;
    FamilyPlane plane{FamilyPlane::Transparent};std::optional<uint32_t> generatedColor{};bool picker=false;
};
struct PickerCaptureRefused : std::runtime_error {
    const bool stale;
    explicit PickerCaptureRefused(const std::string& reason):std::runtime_error("Native picker capture refused: "+reason),stale(reason=="preview-probe-context-stale") {}
};
inline FamilyCapture decodeFamilyCapture(const Json& reply,const FamilySourceObservation& observed,uint64_t request,uint64_t deadline) {
    if(observed.picker && std::string_view(Json::text(reply.object(),"kind"))=="refused") {
        auto object=reply.object();Json::fields(object,{"protocolVersion","kind","reason"});
        require(Json::integer(object,"protocolVersion")==3,"Exact picker refusal protocol");
        const std::string reason=Json::text(object,"reason");
        // These original native branches return before captureProbes.emplace;
        // an unrecognized/transport outcome retains custody without replay.
        const std::set<std::string> noCapture{"picker-preview-source-unavailable","picker-preview-capacity","preview-probe-deadline","preview-probe-subject","preview-probe-source-unavailable","preview-probe-output-unavailable","preview-popup-layout-unsupported","preview-family-source-unavailable","preview-probe-source-epoch-unavailable","preview-probe-context-stale","preview-probe-capture-unavailable","preview-probe-expired"};
        require(noCapture.contains(reason),("Unproven picker capture refusal: "+reason).c_str());
        throw PickerCaptureRefused(reason);
    }
    const auto& scope=observed.scope;auto object=reply.object();
    const bool backdrop=observed.plane==FamilyPlane::GeneratedBackdrop;
    if(backdrop)Json::fields(object,{"protocolVersion","kind","binding","requestId","subjectIncarnation","captureRequest","outputGeneration","completedNs","width","height","encodedBytes","ownedBytes","crc32","encoding","planeSpace","pixelX","pixelY","pixelScale","previewEligible","generatedBackdrop"});else Json::fields(object,{"protocolVersion","kind","binding","requestId","subjectIncarnation","captureRequest","outputGeneration","completedNs","width","height","encodedBytes","ownedBytes","crc32","encoding","planeSpace","pixelX","pixelY","pixelScale","previewEligible"});
    require(request && deadline>scope.now && deadline-scope.now<=2000000000ULL && Json::integer(object,"protocolVersion")==3 && std::string_view(Json::text(object,"kind"))==(observed.picker?"preview-picker-family-owned":backdrop?"preview-family-backdrop-crop-owned":"preview-family-style-crop-owned") && decodeBinding(Json::child(object,"binding"))==scope.binding && reply.counter("requestId")==request && reply.counter("captureRequest")==request && reply.counter("subjectIncarnation")==scope.context.incarnation.value && reply.counter("outputGeneration")==scope.context.output.value,"Exact native style-family capture correlation");
    require(Json::boolean(object,"previewEligible")==observed.picker && std::string_view(Json::text(object,"encoding"))=="PNG-RGBA8-straight" && std::string_view(Json::text(object,"planeSpace"))==(observed.picker?"picker-native-family-style-cropped-pixels":backdrop?"native-generated-backdrop-family-style-cropped-pixels-unqualified":"native-family-style-cropped-pixels-unqualified"),"Distinct unqualified native family pixels");
    const auto completed=reply.counter("completedNs"),bytes=reply.counter("encodedBytes"),owned=reply.counter("ownedBytes");const auto width=familyInteger(object,"width",4096),height=familyInteger(object,"height",4096);
    FamilyCrop crop{familyPixel(object,"pixelX"),familyPixel(object,"pixelY"),static_cast<uint32_t>(width),static_cast<uint32_t>(height),familyNumber(json_object_get_member(object,"pixelScale"))};
    auto raw=std::string_view(Json::text(object,"crc32"));const uint64_t crc=raw=="0"?0:decimal(raw);
    require(completed>=scope.now && completed<deadline && width && height && crop.x==observed.crop.x && crop.y==observed.crop.y && width==observed.crop.width && height==observed.crop.height && crop.scale==observed.crop.scale && bytes>=8 && bytes<=observed.maximumTransferBytes && owned>=bytes && owned<=128ULL*1024*1024 && crc<=UINT32_MAX,"Exact native family crop/bytes/original deadline");
    if(backdrop) {auto color=Json::child(object,"generatedBackdrop");Json::fields(color,{"kind","colorARGB"});const auto value=decimal(Json::text(color,"colorARGB"));require(std::string_view(Json::text(color,"kind"))=="native-opaque-generated-color" && value<=UINT32_MAX && (value>>24)==255 && observed.generatedColor==static_cast<uint32_t>(value),"Exact captured generated color");}
    return {scope.binding,scope.context,request,completed,deadline,width,height,bytes,owned,crc,crop,observed.plane,observed.generatedColor,observed.picker};
}
inline FamilyCapture captureFamily(Native& native,const FamilySourceObservation& observed,uint64_t deadline) {
    const auto& s=observed.scope;require(s.binding==native.binding() && s.context.lifetime==s.binding.lifetime && s.clock.value==s.binding.lifetime.value && s.present && s.sourceLive && !s.locked && s.gpuReady,"Own live native family capture scope");
    require(deadline>s.now && deadline-s.now<=2000000000ULL,"Original family native capture deadline");const auto request=native.next();Wire wire;
    wire.integer("protocolVersion",3).text("kind",observed.picker?"preview-picker-family-capture-request":observed.plane==FamilyPlane::GeneratedBackdrop?"preview-family-backdrop-crop-scoped-request":"preview-family-style-crop-scoped-request").begin("binding").binding(s.binding).end().counter("requestId",request).counter("subjectIncarnation",s.context.incarnation.value).counter("deadlineNs",deadline).begin("context").context(s.context).end();
    auto reply=native.control(wire.finish());return decodeFamilyCapture(reply,observed,request,deadline);
}
inline bool familyFrameMatches(const stylecropfd::Header& h,const FamilyCapture& c) {
    return c.plane==FamilyPlane::Transparent && !c.generatedColor && stylecropfd::imageHeader(h) && h[fd::Flags]==131 && h[fd::Lifetime]==c.binding.lifetime.value && h[fd::Session]==c.binding.session.value && h[fd::Frontend]==c.binding.frontend.value && h[fd::Capture]==c.request && h[fd::Subject]==c.context.incarnation.value && h[fd::Output]==c.context.output.value && h[fd::Privacy]==c.context.privacy.value && h[fd::Rendering]==c.context.rendering.value && h[fd::Scene]==c.context.scene.value && h[fd::Content]==c.context.content.value && h[fd::Completed]==c.completed && h[fd::Deadline]==c.deadline && h[fd::Now]<c.deadline && h[fd::Width]==c.width && h[fd::Height]==c.height && h[fd::Bytes]==c.bytes && h[fd::Charge]==((c.bytes+4095)&~uint64_t{4095}) && h[fd::CRC]==c.crc && h[fd::Expires]>h[fd::Now] && stylecropfd::pixelX(h)==c.crop.x && stylecropfd::pixelY(h)==c.crop.y && stylecropfd::scale(h)==c.crop.scale;
}
inline bool familyFrameMatches(const backdropfd::Header& h,const FamilyCapture& c) {
    return c.plane==FamilyPlane::GeneratedBackdrop && c.generatedColor && h[backdropfd::ColorARGB]==*c.generatedColor && backdropfd::imageHeader(h) && h[fd::Flags]==259 && h[fd::Lifetime]==c.binding.lifetime.value && h[fd::Session]==c.binding.session.value && h[fd::Frontend]==c.binding.frontend.value && h[fd::Capture]==c.request && h[fd::Subject]==c.context.incarnation.value && h[fd::Output]==c.context.output.value && h[fd::Privacy]==c.context.privacy.value && h[fd::Rendering]==c.context.rendering.value && h[fd::Scene]==c.context.scene.value && h[fd::Content]==c.context.content.value && h[fd::Completed]==c.completed && h[fd::Deadline]==c.deadline && h[fd::Now]<c.deadline && h[fd::Width]==c.width && h[fd::Height]==c.height && h[fd::Bytes]==c.bytes && h[fd::Charge]==((c.bytes+4095)&~uint64_t{4095}) && h[fd::CRC]==c.crc && h[fd::Expires]>h[fd::Now] && backdropfd::pixelX(h)==c.crop.x && backdropfd::pixelY(h)==c.crop.y && backdropfd::scale(h)==c.crop.scale;
}
inline bool releaseFamily(Native& native,const FamilyCapture& capture,uint64_t transfer) {
    require(capture.binding==native.binding() && transfer,"Own native family transfer release");if(capture.plane==FamilyPlane::GeneratedBackdrop)return native.backdropQuery(fd::Release,capture.request,capture.context.incarnation.value,transfer).has_value();
    return native.familyQuery(fd::Release,capture.request,capture.context.incarnation.value,transfer).has_value();
}
inline ClientRetirement retireFamilyState(Native& native,FamilyPlane plane=FamilyPlane::Transparent,uint64_t subject=0,bool picker=false) {
    require(!picker || (subject && plane==FamilyPlane::Transparent),"Own picker family retirement subject");
    const auto owner=native.binding();const auto request=native.next();Wire wire;wire.integer("protocolVersion",3).text("kind",picker?"preview-picker-family-retire-request":plane==FamilyPlane::GeneratedBackdrop?"preview-family-backdrop-crop-retire-request":"preview-family-style-crop-retire-request").begin("binding").binding(owner).end().counter("requestId",request);if(picker)wire.counter("subjectIncarnation",subject);auto reply=native.control(wire.finish());auto o=reply.object();
    if(std::string_view(Json::text(o,"kind"))=="refused") {Json::fields(o,{"protocolVersion","kind","reason"});require(Json::integer(o,"protocolVersion")==3 && std::string_view(Json::text(o,"reason"))=="preview-probe-locked","Unresolved family producer retirement");return ClientRetirement::PendingLock;}
    Json::fields(o,{"protocolVersion","kind","binding","requestId","ownedBytes"});require(Json::integer(o,"protocolVersion")==3 && std::string_view(Json::text(o,"kind"))==(picker?"preview-picker-family-retired":plane==FamilyPlane::GeneratedBackdrop?"preview-family-backdrop-crop-retired":"preview-family-style-crop-retired") && decodeBinding(Json::child(o,"binding"))==owner && reply.counter("requestId")==request && std::string_view(Json::text(o,"ownedBytes"))=="0","Exact own family zero producer retirement");return ClientRetirement::Retired;
}
}
