#pragma once
#include "effect_cancellation.hpp"
#include <json-glib/json-glib.h>
#include <charconv>
#include <cstring>
#include <initializer_list>
#include <optional>
#include <string_view>

namespace warlock::cancellation {
enum class Kind { Negotiate, Prepare, Commit, Cancel, Query, Ack };
struct Parsed { Kind kind; Key key; U requestId{}, deadline{}, preparedId{}; };
inline bool exact(JsonObject* o,std::initializer_list<const char*> keys) noexcept {
    if(!o || json_object_get_size(o)!=keys.size())return false;
    for(auto* k:keys)if(!json_object_has_member(o,k))return false;
    return true;
}
inline JsonObject* child(JsonObject* o,const char* k) noexcept {
    if(!o)return nullptr;
    auto* n=json_object_get_member(o,k);
    return n && JSON_NODE_HOLDS_OBJECT(n)?json_node_get_object(n):nullptr;
}
inline bool integer(JsonObject* o,const char* k,int n) noexcept {
    auto* v=json_object_get_member(o,k);
    return v && JSON_NODE_HOLDS_VALUE(v) && json_node_get_value_type(v)==G_TYPE_INT64 && json_node_get_int(v)==n;
}
inline const char* string(JsonObject* o,const char* k) noexcept {
    auto* v=json_object_get_member(o,k);
    return v && JSON_NODE_HOLDS_VALUE(v) && json_node_get_value_type(v)==G_TYPE_STRING?json_node_get_string(v):nullptr;
}
inline std::optional<U> decimal(JsonObject* o,const char* k) noexcept {
    const char* p=string(o,k);if(!p)return {};
    std::string_view s(p);if(s.empty() || s.size()>20 || (s.size()>1 && s[0]=='0'))return {};
    for(char c:s)if(c<'0'||c>'9')return {};
    U n{};auto r=std::from_chars(s.data(),s.data()+s.size(),n);
    if(r.ec!=std::errc{} || r.ptr!=s.data()+s.size() || !n)return {};
    return n;
}
// The authority's duplicate-member tracking must run before this parser.
// Caller supplies authenticated peer/start and independently verifies the grant.
inline std::optional<Parsed> parse(JsonObject* o,U peer,U start) noexcept {
    if(!o || !peer || !start || !integer(o,"protocolVersion",3))return {};
    const char* name=string(o,"kind");if(!name)return {};
    Parsed p{};
    if(!std::strcmp(name,"effect-cancellation-negotiate"))p.kind=Kind::Negotiate;
    else if(!std::strcmp(name,"effect-prepare"))p.kind=Kind::Prepare;
    else if(!std::strcmp(name,"effect-commit"))p.kind=Kind::Commit;
    else if(!std::strcmp(name,"effect-cancel"))p.kind=Kind::Cancel;
    else if(!std::strcmp(name,"effect-decision-request"))p.kind=Kind::Query;
    else if(!std::strcmp(name,"effect-decision-ack"))p.kind=Kind::Ack;
    else return {};
    if(p.kind==Kind::Negotiate) {
        if(!exact(o,{"protocolVersion","kind","binding","requestId","cancellationProtocol"}) || !integer(o,"cancellationProtocol",1))return {};
        auto id=decimal(o,"requestId");if(!id)return {};p.requestId=*id;
    } else {
        bool shape=p.kind==Kind::Prepare ? exact(o,{"protocolVersion","kind","binding","effectProtocol","cancellationProtocol","intent","deadlineMonotonicNs"}) : exact(o,{"protocolVersion","kind","binding","effectProtocol","cancellationProtocol","intent","deadlineMonotonicNs","preparedId"});
        if(!shape || !integer(o,"effectProtocol",1) || !integer(o,"cancellationProtocol",1))return {};
        auto d=decimal(o,"deadlineMonotonicNs");if(!d)return {};p.deadline=*d;
        if(p.kind!=Kind::Prepare) {auto id=decimal(o,"preparedId");if(!id)return {};p.preparedId=*id;}
    }
    auto* b=child(o,"binding");if(!exact(b,{"lifetime","session","frontend"}))return {};
    auto life=decimal(b,"lifetime"), session=decimal(b,"session"), frontend=decimal(b,"frontend");
    if(!life || !session || !frontend)return {};
    p.key.owner={peer,start,*life,*session,*frontend};
    if(p.kind==Kind::Negotiate)return p;
    auto* i=child(o,"intent");if(!exact(i,{"request","generation","incarnation","operation","context"}))return {};
    auto operation=string(i,"operation");if(!operation || std::strcmp(operation,"restore"))return {};
    auto request=decimal(i,"request"),generation=decimal(i,"generation"),incarnation=decimal(i,"incarnation");
    auto* c=child(i,"context");if(!exact(c,{"lifetime","epoch","output","revision"}))return {};
    auto native=decimal(c,"lifetime"),epoch=decimal(c,"epoch"),output=decimal(c,"output"),revision=decimal(c,"revision");
    if(!request || !generation || !incarnation || !native || !epoch || !output || !revision || *native!=*life || *epoch!=*frontend)return {};
    p.key.intent={*request,*generation,*incarnation,*native,*epoch,*output,*revision,Intent::Operation::Restore};
    return p;
}
}

// Raw-wire entry point for the production dispatch. Structured JsonObject
// parsing alone cannot detect duplicate keys or decoded embedded NULs.
#include <string>
#include <unordered_map>
#include <unordered_set>
namespace warlock::cancellation {
inline bool boundedWire(std::string_view bytes) noexcept {
    if(bytes.empty() || bytes.size()>8192)return false;
    bool quoted=false;unsigned depth=0;
    for(std::size_t i=0;i<bytes.size();++i) {
        const char c=bytes[i];if(!c)return false;
        if(quoted) {
            if(c=='\\') {
                if(++i==bytes.size())return false;
                if(bytes[i]=='u' && i+4<bytes.size() && bytes.substr(i+1,4)=="0000")return false;
            } else if(c=='"')quoted=false;
        } else if(c=='"')quoted=true;
        else if(c=='{' || c=='[') {if(++depth>4)return false;}
        else if(c=='}' || c==']') {if(!depth)return false;--depth;}
    }
    return !quoted && !depth;
}
struct DuplicateGuard {
    std::unordered_map<JsonObject*,std::unordered_set<std::string>> members;
    bool invalid{};
    static void member(JsonParser*,JsonObject* object,const gchar* name,gpointer data) noexcept {
        auto& guard=*static_cast<DuplicateGuard*>(data);
        if(guard.invalid)return;
        try {if(!guard.members[object].insert(name).second)guard.invalid=true;}
        catch(...) {guard.invalid=true;}
    }
};
inline std::optional<Parsed> parseWire(std::string_view bytes,U peer,U start) noexcept {
    if(!boundedWire(bytes))return {};
    DuplicateGuard guard;JsonParser* parser=json_parser_new();if(!parser)return {};
    g_signal_connect(parser,"object-member",G_CALLBACK(DuplicateGuard::member),&guard);
    GError* error=nullptr;std::optional<Parsed> result;
    if(json_parser_load_from_data(parser,bytes.data(),static_cast<gssize>(bytes.size()),&error) && !guard.invalid) {
        auto* root=json_parser_get_root(parser);
        if(root && JSON_NODE_HOLDS_OBJECT(root))result=parse(json_node_get_object(root),peer,start);
    }
    if(error)g_error_free(error);
    g_object_unref(parser);
    return result;
}
}
