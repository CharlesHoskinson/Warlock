#include "client_producer.hpp"
#include <iostream>
using namespace preview;using namespace preview::bridge;
int main(){try {
    unsigned checks=0;auto check=[&](bool ok,const char* reason){require(ok,reason);++checks;};
    const Binding binding{{12618083744238620417ULL},{2},{1}};
    const Context context{{12618083744238620417ULL},{2},{1},{1},{2},{1},{42}};
    const Job job{binding,context,{1},{1},binding.lifetime.value?Id<Clock>{binding.lifetime.value}:Id<Clock>{0},203485677514126};
    const Packet packet{job,{{},1},true,Packet::Fidelity::Client,1,203488683636209};
    Wire acquire;const auto acquired=acquire.text("kind","acquire").begin("job").job(job).end().finish();
    Wire cancel;const auto cancelled=cancel.text("kind","cancel").begin("job").job(job).end().finish();
    Wire release;release.text("kind","release").begin("frame");packetJSON(release,packet);const auto released=release.end().finish();
    check(decodeClientCommand("family:2",acquired,job,{})==ClientCommand::Acquire,"Exact original Acquire");
    check(decodeClientCommand("family:2",cancelled,job,{})==ClientCommand::Cancel,"Exact original Cancel");
    check(decodeClientCommand("family:2",released,job,packet)==ClientCommand::Release,"Exact owned client Release");
    auto rejectHeld=[&](const std::string& identity,const std::string& text,std::optional<Packet> held){bool refused=false;try{decodeClientCommand(identity,text,job,held);}catch(const std::exception&){refused=true;}check(refused,"Malformed/foreign client command refuses");};
    auto reject=[&](const std::string& identity,const std::string& text){rejectHeld(identity,text,packet);};
    reject("family:3",acquired);reject("family:02",acquired);rejectHeld("family:2",released,{});
    for(const char* field:{"lifetime","session","frontend"}) {
        Json message(acquired);auto own=Json::child(Json::child(message.object(),"job"),"binding");json_object_set_string_member(own,field,"999");auto bytes=json_to_string(json_parser_get_root(message.parser),FALSE);reject("family:2",bytes);g_free(bytes);
    }
    for(const char* field:{"lifetime","incarnation","output","privacy","rendering","scene","content"}) {
        Json message(acquired);auto own=Json::child(Json::child(message.object(),"job"),"context");json_object_set_string_member(own,field,"999");auto bytes=json_to_string(json_parser_get_root(message.parser),FALSE);reject("family:2",bytes);g_free(bytes);
    }
    for(const char* field:{"request","origin","clock","deadline"}) {
        for(const char* value:{"999","01","0","18446744073709551616"}) {
            Json message(acquired);auto own=Json::child(message.object(),"job");json_object_set_string_member(own,field,value);auto bytes=json_to_string(json_parser_get_root(message.parser),FALSE);reject("family:2",bytes);g_free(bytes);
        }
    }
    for(const char* field:{"kind","job"}) {
        Json message(acquired);json_object_remove_member(message.object(),field);auto bytes=json_to_string(json_parser_get_root(message.parser),FALSE);reject("family:2",bytes);g_free(bytes);
    }
    for(const char* field:{"owned","signaled"}) {
        Json message(released);json_object_set_boolean_member(Json::child(message.object(),"frame"),field,FALSE);auto bytes=json_to_string(json_parser_get_root(message.parser),FALSE);reject("family:2",bytes);g_free(bytes);
    }
    for(const char* field:{"handle","fidelity","expires"}) {
        Json message(released);json_object_set_string_member(Json::child(message.object(),"frame"),field,"foreign");auto bytes=json_to_string(json_parser_get_root(message.parser),FALSE);reject("family:2",bytes);g_free(bytes);
    }
    Json extra(acquired);json_object_set_boolean_member(extra.object(),"extra",TRUE);auto bytes=json_to_string(json_parser_get_root(extra.parser),FALSE);reject("family:2",bytes);g_free(bytes);
    reject("family:2","{\"kind\":\"acknowledge\"}");reject("family:2","{\"kind\":\"acquire\",\"kind\":\"cancel\",\"job\":{}}");
    SourceObservation observed{{binding,context,{binding.lifetime.value},203483677058877,true,true,false,true},75,311296,1,SourceObservation::Kind::UnqualifiedClientMain,false};
    Json source(sourceJSON(observed));check(!Json::boolean(source.object(),"previewEligible") && source.counter("maximumTransferBytes")==311296,"Source stays explicitly unqualified/lossless");
    observed.kind=SourceObservation::Kind::UnqualifiedRootMonitorPlane;bool refused=false;try{sourceJSON(observed);}catch(const std::exception&){refused=true;}check(refused,"Monitor cannot alias client encoder");
    std::cout<<"{\"passed\":true,\"checks\":"<<checks<<",\"nativeAcceptance\":false}\n";
    return 0;
}catch(const std::exception& exception){std::cerr<<exception.what()<<'\n';return 1;}}
