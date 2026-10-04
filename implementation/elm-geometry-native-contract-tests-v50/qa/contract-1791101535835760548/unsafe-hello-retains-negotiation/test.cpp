
#include "PlacementPolicy.hpp"
#include <json-glib/json-glib.h>
#include <algorithm>
#include <charconv>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <limits>
#include <map>
#include <memory>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
namespace Render::SceneTrace {struct Frame {};}
uint64_t lifetime=7,geometryRevision=8,factsRevision=9,outputGeneration=10;
std::string error(const std::string& reason){return "ERROR:"+reason;}
namespace Fullscreen {enum Mode{FSMODE_NONE,FSMODE_MAXIMIZED,FSMODE_FULLSCREEN};}
struct Modes {Fullscreen::Mode internal;};
struct Vec {double x,y;};
struct Limits {Vec minSize,maxSize;};
struct Top {Limits m_current;};struct Xdg {std::shared_ptr<Top> m_toplevel;};struct RawWindow {std::shared_ptr<Xdg> m_xdgSurface;};
struct Session { std::string start; uint64_t id; uint64_t frontend; uint64_t effectRequest=0, generation=0; std::string lastPayload, lastReply; std::vector<Render::SceneTrace::Frame> retained; bool geometryEnabled=false; uint64_t geometryFrontend=0; std::set<std::string> geometryOperations{}; };
std::string quote(const std::string& value) {
    JsonNode* node = json_node_new(JSON_NODE_VALUE);
    json_node_set_string(node, value.c_str());
    gchar* output = json_to_string(node, FALSE);
    std::string result(output); g_free(output); json_node_free(node);
    return result;
}
bool fields(JsonObject* object, std::initializer_list<const char*> expected) {
    if (json_object_get_size(object) != expected.size()) return false;
    for (const char* key : expected) if (!json_object_has_member(object, key)) return false;
    return true;
}
std::optional<uint64_t> counter(JsonObject* object, const char* key, bool allowZero = false) {
    JsonNode* node = json_object_get_member(object, key);
    if (!node || !JSON_NODE_HOLDS_VALUE(node) || json_node_get_value_type(node) != G_TYPE_STRING) return {};
    std::string text = json_node_get_string(node);
    if (text.empty() || text.size() > 20 || (text.size() > 1 && text[0] == '0') ||
        !std::all_of(text.begin(), text.end(), [](char c) { return c >= '0' && c <= '9'; })) return {};
    uint64_t number;
    auto parsed = std::from_chars(text.data(), text.data() + text.size(), number);
    if (parsed.ec != std::errc{} || parsed.ptr != text.data() + text.size() || (!allowZero && !number)) return {};
    return number;
}
JsonObject* objectMember(JsonObject* object, const char* key) {
    JsonNode* node = json_object_get_member(object,key);
    return node && JSON_NODE_HOLDS_OBJECT(node) ? json_node_get_object(node) : nullptr;
}
std::string binding(const Session& session) {
    return "{\"lifetime\":\"" + std::to_string(lifetime) + "\",\"session\":\"" + std::to_string(session.id) +
        "\",\"frontend\":\"" + std::to_string(session.frontend) + "\"}";
}

std::string effectOutcome(const Session& session, const std::string& intent, const char* status, const char* reason, int protocol=1) {
    return "{\"protocolVersion\":3,\"kind\":\"effect-outcome\",\"effectProtocol\":"+std::to_string(protocol)+",\"binding\":"+binding(session)+
        ",\"intent\":"+intent+",\"status\":"+quote(status)+",\"reason\":"+quote(reason)+
        ",\"revision\":"+quote(std::to_string(protocol==2 ? geometryRevision : factsRevision))+",\"outputGeneration\":"+quote(std::to_string(outputGeneration))+"}";
}

std::string performGeometryEffect(Session& session,JsonObject* object) {
    const auto intent=objectMember(object,"intent");
    if(!intent || !fields(intent,{"request","generation","incarnation","operation","context"})) return error("effect-schema");
    const auto request=counter(intent,"request"),generation=counter(intent,"generation"),targetId=counter(intent,"incarnation");
    const auto context=objectMember(intent,"context");
    if(!request || !generation || !targetId || !context || !fields(context,{"lifetime","epoch","output","revision"})) return error("effect-schema");
    const auto native=counter(context,"lifetime"),epoch=counter(context,"epoch"),output=counter(context,"output"),expected=counter(context,"revision");
    const auto op=json_object_get_member(intent,"operation");
    if(!native || !epoch || !output || !expected || !op || !JSON_NODE_HOLDS_VALUE(op) || json_node_get_value_type(op)!=G_TYPE_STRING) return error("effect-schema");
    const std::string operation=json_node_get_string(op);
    gchar* raw=json_to_string(json_object_get_member(object,"intent"),FALSE);const std::string encoded(raw);g_free(raw);
    const auto reply=[&](const char* status,const char* reason){return effectOutcome(session,encoded,status,reason,2);};
    if(!session.geometryEnabled || session.geometryFrontend!=session.frontend || !session.geometryOperations.contains(operation)) return reply("Refused","geometry-operation-not-negotiated");
    const std::string fingerprint="2:"+quote(operation)+":"+std::to_string(*request)+":"+std::to_string(*generation)+":"+std::to_string(*targetId)+":"+std::to_string(*native)+":"+std::to_string(*epoch)+":"+std::to_string(*output)+":"+std::to_string(*expected);
    if(*native!=lifetime || *epoch!=session.frontend) return reply("Refused","authority-mismatch");
    if(*request==session.effectRequest) return fingerprint==session.lastPayload ? session.lastReply : reply("Refused","request-reuse");
    if(*request<session.effectRequest || *generation<=session.generation) return reply("Refused","operation-order");
    session.effectRequest=*request;session.generation=*generation;session.lastPayload=fingerprint;
    session.lastReply=reply("Unknown","effect-unproven");
    const auto reject=[&](const char* reason){session.lastReply=reply("Refused",reason);return session.lastReply;};
    if(operation!="maximize" && operation!="restore-geometry") return reject("unsupported-operation");
    return "ADMITTED";
}

bool rawEligible(const std::shared_ptr<RawWindow>& window) {
    const auto raw=window->m_xdgSurface->m_toplevel->m_current;
    if(!std::isfinite(raw.minSize.x) || !std::isfinite(raw.minSize.y) || !std::isfinite(raw.maxSize.x) || !std::isfinite(raw.maxSize.y) || raw.minSize.x<0 || raw.minSize.y<0 || raw.maxSize.x<0 || raw.maxSize.y<0 || raw.maxSize.x>0 || raw.maxSize.y>0 || raw.minSize.x>1 || raw.minSize.y>1) return false;
    return true;
}
void newHello(Session& session) {++session.frontend;session.retained.clear(); session.effectRequest=0; session.generation=0; session.lastPayload.clear(); session.lastReply.clear();}
struct Caps {bool maximize,restore;};
Caps caps(bool eligible,bool unresolved,bool originalCompatible,Fullscreen::Mode mode,bool placementKnown) {
 Modes modes{mode};return {eligible && !unresolved && originalCompatible && modes.internal==Fullscreen::FSMODE_NONE,eligible && !unresolved && modes.internal==Fullscreen::FSMODE_MAXIMIZED && placementKnown};
}
std::string fingerprint(int version,const std::string& operation,uint64_t r,uint64_t gen,uint64_t t,uint64_t life,uint64_t e,uint64_t o,uint64_t rev) {
 std::optional<uint64_t> request=r,requestId=r,generation=gen,targetId=t,target=t,native=life,epoch=e,output=o,expected=rev;
 if(version==1){const std::string fingerprint="1:"+quote(operation)+":"+std::to_string(*requestId)+":"+std::to_string(*generation)+":"+std::to_string(*target)+":"+std::to_string(*native)+":"+std::to_string(*epoch)+":"+std::to_string(*output)+":"+std::to_string(*expected);return fingerprint;}
 {const std::string fingerprint="2:"+quote(operation)+":"+std::to_string(*request)+":"+std::to_string(*generation)+":"+std::to_string(*targetId)+":"+std::to_string(*native)+":"+std::to_string(*epoch)+":"+std::to_string(*output)+":"+std::to_string(*expected);return fingerprint;}
}
std::string invoke(Session& s,const std::string& text) {
 auto* parser=json_parser_new();GError* failure=nullptr;
 if(!json_parser_load_from_data(parser,text.c_str(),text.size(),&failure)) {
  if(failure){g_error_free(failure);}
  g_object_unref(parser);return "JSON-ERROR";
 }
 auto* node=json_parser_get_root(parser);if(!JSON_NODE_HOLDS_OBJECT(node)){g_object_unref(parser);return "ROOT-ERROR";}
 auto result=performGeometryEffect(s,json_node_get_object(node));g_object_unref(parser);return result;
}
std::string packet(unsigned request,const char* op="maximize",const char* epoch="1") {
 return "{\"intent\":{\"request\":\""+std::to_string(request)+"\",\"generation\":\""+std::to_string(request)+"\",\"incarnation\":\"11\",\"operation\":\""+op+"\",\"context\":{\"lifetime\":\"7\",\"epoch\":\""+epoch+"\",\"output\":\"10\",\"revision\":\"8\"}}}";
}
unsigned checks=0;
bool check(bool value,const char* name){++checks;if(!value)std::fprintf(stderr,"FAIL %s\n",name);return value;}
#define CHECK(v,n) if(!check((v),(n)))return 1
int main(){
 using namespace Elm::Placement;
 auto key=*Identity::fromNative(7,11),other=*Identity::fromNative(8,11);
 auto scope=*Scope::fromNative(-4,2,0,3,4),changed=*Scope::fromNative(-4,2,0,3,5);
 CHECK(!Identity::fromNative(0,11)&&!Identity::fromNative(7,0),"zero native identities rejected");
 CHECK(!Scope::fromNative(0,2,0,3,4)&&!Scope::fromNative(-4,0,0,3,4)&&!Scope::fromNative(-4,2,0,0,4)&&!Scope::fromNative(-4,2,0,3,0),"explicit scope generations and workarea required");
 Records records;Original origin{{31,49,320,180},{35,55,312,170}};
 CHECK(!records.hasRecord(key,key)&&!records.read(key,key,scope),"externally maximized absence explicit");
 CHECK(records.capture(key,other,scope,origin)==Capture::StaleIdentity,"stale lifetime cannot capture");
 CHECK(records.capture(key,key,scope,{{0,0,-1,1},{0,0,1,1}})==Capture::InvalidRect,"invalid original cannot occupy record");
 CHECK(records.capture(key,key,scope,origin)==Capture::Captured,"first original captured");
 CHECK(records.hasRecord(key,key)&&!records.hasRecord(key,other)&&!records.hasRecord(other,other),"hasRecord requires exact live native identity");
 CHECK(records.hasRecord(key,key)&&!records.read(key,key,changed),"workarea change retains evidence but denies compatibility");
 CHECK(records.capture(key,key,changed,{{90,90,500,400},{91,91,490,390}})==Capture::Duplicate&&records.read(key,key,scope)==origin&&!records.read(key,key,changed),"incompatible duplicate never overwrites first original");
 for(unsigned i=12;i<267;++i) {auto id=*Identity::fromNative(7,i);CHECK(records.capture(id,id,scope,origin)==Capture::Captured,"all256 immutable records usable");}
 auto full=*Identity::fromNative(7,267);CHECK(records.size()==256&&records.capture(full,full,scope,origin)==Capture::Capacity&&!records.hasRecord(full,full)&&records.read(key,key,scope)==origin,"full store refuses without eviction");
 CHECK(records.retire(key)&&!records.hasRecord(key,key)&&!records.retire(key)&&records.capture(full,full,scope,origin)==Capture::Captured,"exact retirement permits one fresh original");
 Session s;s.id=12;s.frontend=1;
 auto before=invoke(s,packet(1));CHECK(before.find("geometry-operation-not-negotiated")!=std::string::npos&&s.effectRequest==0,"effect2 before attach denied before journal");
 s.geometryEnabled=true;s.geometryFrontend=1;s.geometryOperations={"maximize","restore-geometry"};
 CHECK(invoke(s,"{\"intent\":{}}")=="ERROR:effect-schema"&&s.effectRequest==0,"malformed intent cannot dispatch");
 CHECK(invoke(s,packet(1,"activate")).find("geometry-operation-not-negotiated")!=std::string::npos&&s.effectRequest==0,"legacy operation cannot use geometry negotiation");
 CHECK(invoke(s,packet(1))=="ADMITTED"&&s.effectRequest==1&&s.generation==1,"exact negotiated operation reaches pre-native admission");
 CHECK(invoke(s,packet(1)).find("Unknown")!=std::string::npos,"exact retry returns cached original Unknown without admission");
 CHECK(invoke(s,packet(1,"restore-geometry")).find("request-reuse")!=std::string::npos,"same request changed operation rejected");
 CHECK(invoke(s,packet(2,"maximize","2")).find("authority-mismatch")!=std::string::npos&&s.effectRequest==1,"wrong frontend rejected before shared journal");
 s.geometryFrontend=2;CHECK(invoke(s,packet(2)).find("geometry-operation-not-negotiated")!=std::string::npos,"stale negotiation frontend denied");
 s.geometryFrontend=1;newHello(s);CHECK(!s.geometryEnabled&&s.geometryFrontend==0&&s.geometryOperations.empty()&&s.frontend==2,"actual hello clears operation negotiation");
 CHECK(invoke(s,packet(2,"maximize","2")).find("geometry-operation-not-negotiated")!=std::string::npos&&s.effectRequest==0,"fresh binding after hello cannot bypass attach");
 auto f=fingerprint(2,"maximize",1,1,11,7,1,10,8);
 CHECK(f!=fingerprint(1,"maximize",1,1,11,7,1,10,8),"effect version participates in shared fingerprint");
 CHECK(f!=fingerprint(2,"restore-geometry",1,1,11,7,1,10,8)&&f!=fingerprint(2,"maximize",2,1,11,7,1,10,8)&&f!=fingerprint(2,"maximize",1,2,11,7,1,10,8)&&f!=fingerprint(2,"maximize",1,1,12,7,1,10,8)&&f!=fingerprint(2,"maximize",1,1,11,8,1,10,8)&&f!=fingerprint(2,"maximize",1,1,11,7,2,10,8)&&f!=fingerprint(2,"maximize",1,1,11,7,1,11,8)&&f!=fingerprint(2,"maximize",1,1,11,7,1,10,9),"every operation and context counter changes fingerprint");
 auto w=std::make_shared<RawWindow>();w->m_xdgSurface=std::make_shared<Xdg>();w->m_xdgSurface->m_toplevel=std::make_shared<Top>();
 w->m_xdgSurface->m_toplevel->m_current={{1,1},{0,0}};CHECK(rawEligible(w),"zero max with ordinary min admits raw constraint stage");
 for(int i=1;i<=4;++i){w->m_xdgSurface->m_toplevel->m_current.maxSize={double(i),0};CHECK(!rawEligible(w),"tiny positive raw limit cannot exploit Window max normalization");}
 w->m_xdgSurface->m_toplevel->m_current={{2,1},{0,0}};CHECK(!rawEligible(w),"constrained minimum refuses");
 w->m_xdgSurface->m_toplevel->m_current={{1,1},{-1,0}};CHECK(!rawEligible(w),"negative raw limit refuses");
 w->m_xdgSurface->m_toplevel->m_current={{1,1},{NAN,0}};CHECK(!rawEligible(w),"nonfinite raw limit refuses");
 CHECK(caps(true,false,true,Fullscreen::FSMODE_NONE,false).maximize&&!caps(true,false,true,Fullscreen::FSMODE_NONE,false).restore,"ordinary snapshot advertises distinct maximize");
 CHECK(!caps(true,false,true,Fullscreen::FSMODE_MAXIMIZED,false).maximize&&!caps(true,false,true,Fullscreen::FSMODE_MAXIMIZED,false).restore,"external MAX with no original advertises neither action");
 CHECK(caps(true,false,true,Fullscreen::FSMODE_MAXIMIZED,true).restore,"owned compatible MAX enables geometry restore");
 CHECK(!caps(true,true,true,Fullscreen::FSMODE_NONE,false).maximize&&!caps(true,true,true,Fullscreen::FSMODE_MAXIMIZED,true).restore,"Unknown barrier disables both geometry actions");
 CHECK(!caps(true,false,false,Fullscreen::FSMODE_NONE,false).maximize,"incompatible retained origin disables recapture");
 CHECK(!caps(false,false,true,Fullscreen::FSMODE_NONE,false).maximize&&!caps(false,false,true,Fullscreen::FSMODE_MAXIMIZED,true).restore,"actual preflight ineligibility suppresses advertised actions");
 std::printf("checks %u\n",checks);return 0;
}
