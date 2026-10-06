#include "preview_wire.hpp"
#include "preview-control-delivery.h"
#include <iostream>
using namespace preview;
using namespace preview::bridge;
int main(){try {
    const PreviewControlGrant owner{17,18,19,77,1};PreviewControlDelivery state{};
    require(preview_control_delivery_init(&state,owner),"Original fixture receiver grant");
    uint64_t invoked=0;std::string line;
    while(std::getline(std::cin,line)) {
        require(line.size()<=65536,"Bounded native fixture input");Json envelope(line);
        const std::string_view op=Json::text(envelope.object(),"op");
        if(op=="finish") {require(!state.prefix.inFlight,"Normal fixture close outside dispatch");std::cout<<"{\"finished\":true,\"invoked\":"<<invoked<<"}"<<std::endl;return 0;}
        require(op=="packet","Closed fixture operation");const std::string wire=Json::text(envelope.object(),"wire");
        Json message(wire);auto packet=message.object();
        Json::fields(packet,{"previewProtocol","kind","binding","receiverEpoch","controlOrdinal","entries"});
        require(Json::integer(packet,"previewProtocol")==3 && std::string_view(Json::text(packet,"kind"))=="preview-commands","Typed control protocol");
        const auto binding=decodeBinding(Json::child(packet,"binding"));
        const PreviewControlGrant incoming{binding.lifetime.value,binding.session.value,binding.frontend.value,77,message.counter("receiverEpoch")};
        auto entries=json_object_get_array_member(packet,"entries");require(entries && json_array_get_length(entries)==1,"Singleton control entry");
        auto entry=json_node_get_object(json_array_get_element(entries,0));Json::fields(entry,{"identity","commands"});
        require(std::string_view(Json::text(entry,"identity")).starts_with("family:"),"Typed fixture identity");
        auto commands=json_object_get_array_member(entry,"commands");require(commands && json_array_get_length(commands)==1,"One immutable command");
        const auto ordinal=message.counter("controlOrdinal");
        auto decision=preview_control_delivery_receive(&state,incoming,ordinal,wire.c_str(),wire.size());
        if(decision==PREVIEW_CONTROL_INVOKE) {
            ++invoked;
            // A dispatcher can return with an Unknown/refused effect. Its
            // delivery receipt still cannot authorize a second invocation.
            require(preview_control_delivery_complete(&state,ordinal),"Complete original dispatch");
        }
        const auto receipt=preview_control_delivery_receipt(&state);
        std::string acknowledgment="null";
        if(decision!=PREVIEW_CONTROL_REFUSED && receipt)acknowledgment=Wire().integer("previewProtocol",3).text("kind","preview-control-delivered")
            .begin("binding").binding({{17},{18},{19}}).end().counter("receiverEpoch",1).counter("controlOrdinal",receipt).finish();
        std::cout<<"{\"decision\":"<<decision<<",\"invoked\":"<<invoked<<",\"effectOutcome\":\"Unknown\",\"receipt\":"<<acknowledgment<<"}"<<std::endl;
    }
    require(false,"Explicit normal fixture close");
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
