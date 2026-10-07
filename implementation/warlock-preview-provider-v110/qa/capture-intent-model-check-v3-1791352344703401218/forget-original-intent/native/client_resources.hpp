#pragma once
#include "client_frame.hpp"

namespace preview::bridge {
enum class ClientResourceOperation {Observe,ReleaseExport,RetireProducer};
enum class ClientResourceStatus {Observed,Settled,PendingExport,PendingLock};
inline const char* clientResourceName(ClientResourceOperation value) {
    switch(value) {
        case ClientResourceOperation::Observe:return "observe";
        case ClientResourceOperation::ReleaseExport:return "release-export";
        case ClientResourceOperation::RetireProducer:return "retire-producer";
    }
    throw std::invalid_argument("Closed original native resource operation");
}
struct ClientResourceCursor {std::optional<Binding> binding;uint64_t sequence{},now{};};
struct ClientResourceSnapshot {
    Binding binding;Id<Incarnation> subject;
    uint64_t capture{},request{},sequence{},clock{},now{},producerBytes{},exportTransfer{},exportBytes{};
    ClientResourceOperation operation;ClientResourceStatus status;bool locked{};
    bool backendEmpty()const noexcept{return !producerBytes && !exportTransfer && !exportBytes;}
};
inline uint64_t resourceAmount(JsonObject* object,const char* field) {
    const std::string_view text=Json::text(object,field);return text=="0"?0:decimal(text);
}
// This decoder is called on the authenticated Native control channel. It has
// no authority over local mappings/readers, terminal receipts or incarnation
// retirement. A malformed reply cannot publish part of the replay cursor.
inline ClientResourceSnapshot decodeClientResources(const Json& reply,const ClientCaptureIntent& intent,
        ClientResourceOperation operation,uint64_t request,ClientResourceCursor& cursor) {
    auto object=reply.object();
    Json::fields(object,{"protocolVersion","kind","resourceProtocol","operation","binding","requestId",
        "captureRequest","subjectIncarnation","sequence","clock","now","status","producerState",
        "producerBytes","exportState","exportTransfer","exportBytes","locked"});
    const auto& scope=intent.observed().scope;
    require(request>intent.request() && Json::integer(object,"protocolVersion")==3 &&
        Json::integer(object,"resourceProtocol")==1 &&
        std::string_view(Json::text(object,"kind"))=="preview-client-resources" &&
        std::string_view(Json::text(object,"operation"))==clientResourceName(operation) &&
        decodeBinding(Json::child(object,"binding"))==scope.binding && reply.counter("requestId")==request &&
        reply.counter("captureRequest")==intent.request() &&
        reply.counter("subjectIncarnation")==scope.context.incarnation.value,
        "Exact original native capture resource reply correlation");
    ClientResourceSnapshot result{scope.binding,scope.context.incarnation,intent.request(),request,
        reply.counter("sequence"),reply.counter("clock"),reply.counter("now"),
        resourceAmount(object,"producerBytes"),resourceAmount(object,"exportTransfer"),resourceAmount(object,"exportBytes"),
        operation,ClientResourceStatus::Observed,Json::boolean(object,"locked")};
    require((!cursor.binding || *cursor.binding==scope.binding) && result.clock==scope.clock.value && result.clock==scope.binding.lifetime.value &&
        result.sequence>cursor.sequence && result.now>=cursor.now && result.now>=scope.now,
        "Fresh original native capture resource sequence and clock");
    require(std::string_view(Json::text(object,"producerState"))==(result.producerBytes?"Owned":"Retired") &&
        std::string_view(Json::text(object,"exportState"))==(result.exportTransfer?"Live":"Released") &&
        bool(result.exportTransfer)==bool(result.exportBytes) && (!result.exportTransfer || result.producerBytes) &&
        result.exportBytes<=intent.observed().maximumTransferBytes,
        "Consistent original native producer and export ownership");
    const std::string_view status=Json::text(object,"status");
    if(operation==ClientResourceOperation::Observe) {
        require(status=="Observed","Typed native resource observation status");
    }else if(operation==ClientResourceOperation::ReleaseExport) {
        require(status=="Settled" && !result.exportTransfer && !result.exportBytes,"Scoped native export release result");
        result.status=ClientResourceStatus::Settled;
    }else if(status=="Settled") {
        require(result.backendEmpty(),"Scoped native producer retirement zero");result.status=ClientResourceStatus::Settled;
    }else if(status=="PendingExport") {
        require(result.producerBytes && result.exportTransfer && result.exportBytes,"Original pending native export barrier");
        result.status=ClientResourceStatus::PendingExport;
    }else {
        require(status=="PendingLock" && result.locked && result.producerBytes && !result.exportTransfer && !result.exportBytes,
            "Original pending native lock barrier");result.status=ClientResourceStatus::PendingLock;
    }
    cursor={scope.binding,result.sequence,result.now};return result;
}
inline ClientResourceSnapshot clientResources(Native& native,const ClientCaptureIntent& intent,
        ClientResourceOperation operation,uint64_t transfer,ClientResourceCursor& cursor) {
    require(native.binding()==intent.observed().scope.binding &&
        (operation==ClientResourceOperation::ReleaseExport?transfer>0:transfer==0),
        "Original native resource authority and transfer");
    const auto request=native.next();Wire wire;
    const auto kind=operation==ClientResourceOperation::Observe?"preview-client-resource-state-request":
        operation==ClientResourceOperation::ReleaseExport?"preview-client-resource-release-request":"preview-client-resource-retire-request";
    wire.integer("protocolVersion",3).text("kind",kind).begin("binding").binding(native.binding()).end()
        .counter("requestId",request).counter("captureRequest",intent.request())
        .counter("subjectIncarnation",intent.observed().scope.context.incarnation.value).text("transfer",std::to_string(transfer));
    auto reply=native.control(wire.finish());return decodeClientResources(reply,intent,operation,request,cursor);
}
}
