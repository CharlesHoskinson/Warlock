#include "preview_retirement.hpp"
#include <iostream>
using namespace preview;
using namespace preview::bridge;
int main() {
    const Binding owner{{10},{20},{1}};
    RetirementCursor cursor;
    uint64_t accepted=0;
    std::string event,status;
    while(std::getline(std::cin,event)) {
        const auto before=cursor;
        auto sequence=cursor.sequence+1,now=cursor.now+10,issued=3+cursor.sequence;
        uint64_t subject=2,clock=10,request=100;
        Binding binding=owner;
        std::string state=event=="Retired"?"Retired":"Active";
        if(event=="FutureZero") {state="Future";issued=0;}
        else if(event=="WrongBinding")binding.frontend={2};
        else if(event=="WrongClock")clock=11;
        else if(event=="WrongRequest")request=101;
        else if(event=="WrongSubject")subject=1;
        else if(event=="Replay")sequence=cursor.sequence;
        else if(event=="EarlierNow")now=cursor.now-1;
        else if(event=="EarlierFrontier")issued=cursor.issuedThrough-1;
        else if(event=="RetiredAbove") {state="Retired";issued=1;}
        else if(event=="FutureBelow") {state="Future";issued=3;}
        else if(event=="Unknown")state="Gone";
        auto text=Wire().integer("protocolVersion",3).text("kind","preview-incarnation-retirement-state")
            .integer("retirementProtocol",1).begin("binding").binding(binding).end().counter("requestId",request)
            .counter("subjectIncarnation",subject).counter("sequence",sequence).counter("clock",clock)
            .counter("now",now).text("issuedThrough",std::to_string(issued)).text("state",state).finish();
        try {
            const auto fact=decodeIncarnationRetirement(Json(text),owner,{2},100,cursor);
            require(fact.sequence==sequence && fact.now==now && fact.issuedThrough==issued,"Exact decoded native facts");
            ++accepted;status=retirementName(fact.state);
        }catch(const std::exception&) {
            require(cursor.binding==before.binding && cursor.sequence==before.sequence && cursor.now==before.now && cursor.issuedThrough==before.issuedThrough,"Refusal preserves entire native cursor");
            status="Invalid";
        }
        std::cout<<"{\"sequence\":"<<cursor.sequence<<",\"now\":"<<cursor.now<<",\"issued\":"<<cursor.issuedThrough<<",\"accepted\":"<<accepted<<",\"status\":\""<<status<<"\"}\n";
    }
}
