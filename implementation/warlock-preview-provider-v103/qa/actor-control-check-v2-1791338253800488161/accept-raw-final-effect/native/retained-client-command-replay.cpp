#include "retained_client_command.hpp"
#include <iostream>
using namespace preview;using namespace preview::bridge;
int main(){try {
    const Binding binding{{17},{18},{19}};const Context context{{17},{21},{1},{1},{1},{1},{1}};
    const Job job{binding,context,{1},{1},{17},2000000010};
    const Packet original{job,{{},1},true,Packet::Fidelity::Client,1,2000001010};
    std::string event;
    while(std::getline(std::cin,event)) {
        auto packet=original;packet.signaled=event=="Ready" || event=="NativeUnreadyTrue";
        Wire message;message.text("kind","release").begin("frame");packetJSON(message,packet);const auto raw=message.end().finish();
        Json parsed(raw);auto frame=Json::child(parsed.object(),"frame");std::string identity="family:21";
        std::optional<Packet> known=original;
        if(event=="NativeUnreadyTrue" || event=="NativeUnreadyFalse")known->signaled=false;
        else if(event=="Unowned")json_object_set_boolean_member(frame,"owned",FALSE);
        else if(event=="BadJob")json_object_set_string_member(Json::child(frame,"job"),"request","2");
        else if(event=="BadHandle")json_object_set_string_member(frame,"handle",uri::encode(Token{{},2}).substr(std::string_view("elm-shell://preview/").size()).c_str());
        else if(event=="BadExpiry")json_object_set_string_member(frame,"expires","2000001011");
        else if(event=="BadCoverage")json_array_add_string_element(json_object_get_array_member(frame,"coverage"),"modal");
        else if(event=="FlagType")json_object_set_int_member(frame,"signaled",1);
        else if(event=="MissingPacket")known={};
        else if(event=="BadIdentity")identity="family:22";
        else if(event=="ExtraField")json_object_set_boolean_member(frame,"extra",TRUE);
        else require(event=="Ready" || event=="LateOffer" || event=="DuplicateFlag","Known exact decoder event");
        auto encoded=json_to_string(json_parser_get_root(parsed.parser),FALSE);std::string text(encoded);g_free(encoded);
        if(event=="DuplicateFlag") {
            const auto offset=text.find("\"signaled\":false");require(offset!=std::string::npos,"Explicit duplicate boolean fixture");
            text.replace(offset,std::string("\"signaled\":false").size(),"\"signaled\":false,\"signaled\":true");
        }
        auto accepts=[&](bool retained){try {
            const auto decoded=retained?decodeRetainedClientCommand(identity,text,job,known):decodeClientCommand(identity,text,job,known);
            return decoded==ClientCommand::Release;
        }catch(const std::exception&){return false;}};
        std::cout<<"{\"accepted\":"<<(accepts(true)?"true":"false")<<",\"legacy\":"<<(accepts(false)?"true":"false")<<"}\n";
    }
    return std::cin.bad()?2:0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
