#include "control_reservations.hpp"
#include <fstream>
#include <iostream>
#include <memory>
using namespace preview::bridge;
static uint64_t number(JsonObject* object,const char* name) {
    const std::string_view text=Json::text(Json::child(object,name),"#bigint");
    return text=="0"?0:decimal(text);
}
int main(int argc,char** argv){try {
    require(argc==2,"One exact reservation trace");std::ifstream stream(argv[1]);
    const std::string text((std::istreambuf_iterator<char>(stream)),{});Json trace(text);
    auto states=json_object_get_array_member(trace.object(),"states");require(states,"Model states");
    PreviewControlDelivery channel{};PreviewControlGrant owner{17,18,19,77,1};
    require(preview_control_delivery_init(&channel,owner),"Fresh native fixture grant");
    auto bank=std::make_unique<ControlReservations>(channel,4);
    uint64_t a=0,b=0,oldA=0,length=0,compared=0,lastOrdinal=0;int last=0;
    std::map<uint64_t,std::string> wires;
    auto body=[](char group,uint64_t slot,bool changed=false){
        return std::string("{\"identity\":\"fixture:")+group+"\",\"commands\":[{\"kind\":\"cancel\",\"fixture\":\""+group+std::to_string(slot)+(changed?"changed":"")+"\"}]}";
    };
    auto issue=[&](uint64_t group,char alias,uint64_t slot,bool changed=false){
        auto ticket=bank->issue(owner,group,slot,body(alias,slot,changed));
        last=ticket?1:0;if(ticket){lastOrdinal=ticket->ordinal;
            auto previous=wires.find(ticket->ordinal);
            require(previous==wires.end() || previous->second==ticket->wire,"Exact original retained retry wire");
            wires[ticket->ordinal]=ticket->wire;
        }
    };
    for(guint i=0;i<json_array_get_length(states);++i) {
        auto state=Json::child(json_node_get_object(json_array_get_element(states,i)),"s");
        auto history=json_object_get_array_member(state,"history");require(history,"Exact history");
        auto count=json_array_get_length(history);
        if(count==length+1){
            const std::string event=json_array_get_string_element(history,count-1);length=count;
            try {
                if(event=="Boundary") {
                    require(count==1 && bank->transportEmpty(),"Only explicit empty prior-prefix boundary fixture");
                    // A separate synthetic grant represents a prior confirmed history.
                    // No production channel, issuer, identity or prefix is reset.
                    bank.reset();channel={};owner.receiver=78;
                    require(preview_control_delivery_init(&channel,owner),"Separate boundary fixture grant");
                    channel.prefix.delivered=UINT64_MAX-3;channel.prefix.ordered=TRUE;channel.confirmed=UINT64_MAX-3;
                    bank=std::make_unique<ControlReservations>(channel,4);last=1;
                }else if(event=="ReserveA" || event=="ReserveB") {
                    auto row=bank->reserve(owner,2);last=row?1:0;
                    if(row){if(event=="ReserveA")a=*row;else b=*row;}
                }else if(event=="CapacityProbe") {last=bank->reserve(owner,1)?1:0;}
                else if(event=="SecondIssuer") {ControlReservations forbidden(channel,4);last=1;}
                else if(event=="ForeignReserve") {auto foreign=owner;foreign.receiver++;last=bank->reserve(foreign,2)?1:0;}
                else if(event=="IssueA1")issue(a,'A',1);
                else if(event=="IssueA2")issue(a,'A',2);
                else if(event=="IssueB1")issue(b,'B',1);
                else if(event=="IssueB2")issue(b,'B',2);
                else if(event=="ChangedA1")issue(a,'A',1,true);
                else if(event=="OldA1")issue(oldA,'A',1);
                else if(event=="ReleaseA" || event=="ReleaseB") {
                    auto& group=event=="ReleaseA"?a:b;last=bank->release(owner,group)?1:0;
                    if(last){if(event=="ReleaseA")oldA=a;group=0;}
                }else if(event=="Deliver") {
                    for(const auto& [ordinal,wire]:wires) {
                        if(ordinal<=channel.prefix.delivered)continue;
                        require(bank->ownsTicket(owner,ordinal,wire),"Actual native ticket dispatch admission");
                        require(preview_control_delivery_receive(&channel,owner,ordinal,wire.c_str(),wire.size())==PREVIEW_CONTROL_INVOKE,"Actual contiguous dispatcher entry");
                        require(preview_control_delivery_complete(&channel,ordinal),"Actual dispatcher returned, effect outcome unspecified");
                    }
                    if(channel.prefix.delivered)require(preview_control_delivery_confirm(&channel,owner,channel.prefix.delivered),"Actual original frontend receipt confirmation");
                    last=1;
                }else require(false,"Known exact event");
            }catch(const std::runtime_error&){last=-1;}
            ++compared;
        }else require(count==length,"Contiguous trace");
        require(a==number(state,"a") && b==number(state,"b"),"Compiled reservation membership");
        require(bank->issued()==number(state,"issued"),"Compiled original issued prefix");
        require(bank->reserved()==number(state,"ar")+number(state,"br"),"Compiled retained unused quota");
        require(bank->reservationThrough()==number(state,"groups"),"Compiled original reservation namespace");
        require(bank->reservationCount()==size_t(bool(a)+bool(b)),"Compiled bounded reservation count");
        std::set<uint64_t> retained;
        for(auto key:{"a1","a2","b1","b2"}){auto ordinal=number(state,key);if(ordinal)retained.insert(ordinal);}
        require(bank->ticketCount()==retained.size(),"Compiled bounded retained ticket count");
        for(const auto& [ordinal,wire]:wires)require(bank->ownsTicket(owner,ordinal,wire)==retained.contains(ordinal),"Compiled exact retained ticket ownership");
        require(channel.prefix.delivered==number(state,"delivered") && channel.confirmed==number(state,"confirmed"),"Compiled dispatched and frontend-confirmed prefixes");
        const auto expected=Json::text(Json::child(state,"last"),"#bigint");
        require(last==std::stoi(expected),"Compiled original admission outcome");
        require(lastOrdinal==number(state,"lastOrdinal"),"Compiled original slot retry ordinal");
        require(bank->transportEmpty()==(!a && !b && channel.confirmed==channel.prefix.delivered),"Compiled independent transport close barrier");
    }
    std::cout<<"{\"passed\":true,\"statesCompared\":"<<compared<<",\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
