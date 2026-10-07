#pragma once
#include "client_producer.hpp"

namespace preview::bridge {
// Only the retained original-receiver path uses this decoder. The exact packet
// comes from native producer ownership, never from renderer flags. A delayed
// Offer can still say signaled:false after native completion; cleanup must use
// the actual original packet. Legacy strict decoding and its oracle stay intact.
inline ClientCommand decodeRetainedClientCommand(const std::string& identity,
        const std::string& text,const Job& expected,const std::optional<Packet>& packet) {
    Json wire(text);auto object=wire.object();
    if(std::string_view(Json::text(object,"kind"))!="release")
        return decodeClientCommand(identity,text,expected,packet);
    Json::fields(object,{"kind","frame"});auto frame=Json::child(object,"frame");
    Json::fields(frame,{"job","handle","owned","signaled","fidelity","coverage","expires"});
    const bool frontendReady=Json::boolean(frame,"signaled");
    require(packet && packet->signaled,"Original native packet readiness before retained cleanup decoding");
    if(frontendReady)return decodeClientCommand(identity,text,expected,packet);
    // Normalize only the stale boolean from the original native packet. The
    // original strict validator still checks job, identity, token, ownership,
    // fidelity, coverage and expiry. Transport retains the unmodified raw wire.
    json_object_set_boolean_member(frame,"signaled",packet->signaled);
    auto bytes=json_to_string(json_parser_get_root(wire.parser),FALSE);
    std::unique_ptr<char,decltype(&g_free)> normalized(bytes,g_free);
    return ClientCommand::Release;
}
}
