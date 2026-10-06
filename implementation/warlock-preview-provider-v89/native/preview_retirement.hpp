#pragma once
#include "preview_wire.hpp"

namespace preview::bridge {
enum class IncarnationState { Active, Retired, Future };
struct IncarnationRetirement {
    Binding binding;
    Id<Incarnation> subject;
    Id<Clock> clock;
    uint64_t request{},sequence{},now{},issuedThrough{};
    IncarnationState state;
};
struct RetirementCursor {
    std::optional<Binding> binding;
    uint64_t sequence{},now{},issuedThrough{};
};
struct ActorRetired {
    IncarnationRetirement native;
    uint64_t entry{},entryIssuedThrough{},requestFloor{};
};
inline const char* retirementName(IncarnationState state) {
    switch(state) {
        case IncarnationState::Active:return "Active";
        case IncarnationState::Retired:return "Retired";
        case IncarnationState::Future:return "Future";
    }
    throw std::invalid_argument("Typed native incarnation retirement state");
}
// Decode only the response from Native.control's authenticated owning socket.
// Validate everything before publishing the cursor; a refusal or bad reply
// cannot reset sequence, clock or issuance history. This is no resource proof.
inline IncarnationRetirement decodeIncarnationRetirement(const Json& reply,Binding owner,
        Id<Incarnation> subject,uint64_t request,RetirementCursor& cursor) {
    require(subject.value && request,"Positive retirement request and subject");
    auto object=reply.object();
    Json::fields(object,{"protocolVersion","kind","retirementProtocol","binding","requestId",
        "subjectIncarnation","sequence","clock","now","issuedThrough","state"});
    require(Json::integer(object,"protocolVersion")==3 && Json::integer(object,"retirementProtocol")==1 &&
        std::string_view(Json::text(object,"kind"))=="preview-incarnation-retirement-state",
        "Native retirement response protocol");
    const auto binding=decodeBinding(Json::child(object,"binding"));
    require(binding==owner && reply.counter("requestId")==request &&
        reply.counter("subjectIncarnation")==subject.value,"Exact owning retirement correlation");
    const Id<Clock> clock{reply.counter("clock")};
    require(clock.value==owner.lifetime.value,"Owning native retirement clock");
    const auto sequence=reply.counter("sequence"),now=reply.counter("now");
    const std::string_view frontier=Json::text(object,"issuedThrough");
    const uint64_t issued=frontier=="0"?0:decimal(frontier);
    const std::string_view name=Json::text(object,"state");
    require(name=="Active" || name=="Retired" || name=="Future","Closed native retirement state union");
    const auto state=name=="Active"?IncarnationState::Active:name=="Retired"?IncarnationState::Retired:IncarnationState::Future;
    require(state==IncarnationState::Future?subject.value>issued:subject.value<=issued,
        "Retirement state agrees with native issuance frontier");
    require((!cursor.binding || *cursor.binding==owner) && sequence>cursor.sequence &&
        now>=cursor.now && issued>=cursor.issuedThrough,"Monotonic owning native retirement evidence");
    const IncarnationRetirement result{binding,subject,clock,request,sequence,now,issued,state};
    cursor={owner,sequence,now,issued};
    return result;
}
inline IncarnationRetirement observeIncarnationRetirement(Native& native,Id<Incarnation> subject,
        RetirementCursor& cursor) {
    require(subject.value,"Known native retirement subject");
    const auto owner=native.binding();
    const auto request=native.next();
    auto reply=native.control("{\"protocolVersion\":3,\"kind\":\"preview-incarnation-retirement-state-request\",\"binding\":"+
        native.bindingJSON()+",\"requestId\":\""+std::to_string(request)+"\",\"subjectIncarnation\":\""+std::to_string(subject.value)+"\"}");
    return decodeIncarnationRetirement(reply,owner,subject,request,cursor);
}
inline std::string encodeIncarnationRetirement(const IncarnationRetirement& fact) {
    return Wire().text("kind","native-incarnation-retirement").begin("binding").binding(fact.binding).end()
        .counter("subject",fact.subject.value).counter("request",fact.request).counter("sequence",fact.sequence)
        .counter("clock",fact.clock.value).counter("now",fact.now).text("issuedThrough",std::to_string(fact.issuedThrough))
        .text("state",retirementName(fact.state)).finish();
}
inline std::string encodeActorRetired(const ActorRetired& fact) {
    const auto& n=fact.native;
    require(n.state==IncarnationState::Retired && fact.entry && fact.entry<=fact.entryIssuedThrough,
        "Exact permanently retired native actor fact");
    return Wire().text("kind","native-actor-retired").text("identity","family:"+std::to_string(n.subject.value))
        .begin("binding").binding(n.binding).end().counter("subject",n.subject.value)
        .counter("entry",fact.entry).counter("entryIssuedThrough",fact.entryIssuedThrough)
        .counter("requestFloor",fact.requestFloor).counter("request",n.request).counter("sequence",n.sequence)
        .counter("clock",n.clock.value).counter("now",n.now).counter("issuedThrough",n.issuedThrough).finish();
}
}
