#include "retirement_journal.hpp"
#include <fstream>
#include <iostream>
using namespace preview;
using namespace preview::bridge;
static uint64_t integer(JsonObject* object,const char* name) {
    const std::string_view text=Json::text(Json::child(object,name),"#bigint");
    return text=="0"?0:decimal(text);
}
static std::set<uint64_t> values(JsonObject* state,const char* name) {
    auto list=json_object_get_array_member(Json::child(state,name),"#set");
    require(list,"Exact model set");std::set<uint64_t> result;
    for(guint i=0;i<json_array_get_length(list);++i)
        result.insert(decimal(Json::text(json_node_get_object(json_array_get_element(list,i)),"#bigint")));
    return result;
}
int main(int argc,char** argv){try {
    require(argc==2,"One explicitly selected poll trace");std::ifstream stream(argv[1]);
    std::string text((std::istreambuf_iterator<char>(stream)),{});Json trace(text);
    auto states=json_object_get_array_member(trace.object(),"states");require(states,"Trace states");
    const Binding binding{{17},{18},{19}};RetirementJournal journal(binding,77,1,3);
    auto observation=[&](uint64_t entry){return IncarnationRetirement{binding,{20+entry},{17},entry,entry,100,30,IncarnationState::Retired};};
    auto ready=[&](uint64_t entry){return Wire().text("kind","retire-ready").begin("binding").binding(binding).end().counter("subject",20+entry).counter("observationRequest",entry).counter("observationSequence",entry).finish();};
    auto ack=[&](uint64_t ordinal){return Wire().text("kind","retire-delivery-ack").begin("binding").binding(binding).end().counter("deliveryOrdinal",ordinal).finish();};
    uint64_t length=0,compared=0,selected=0;bool last=false;
    for(guint i=0;i<json_array_get_length(states);++i) {
        auto state=Json::child(json_node_get_object(json_array_get_element(states,i)),"s");
        auto history=json_object_get_array_member(state,"history");require(history,"Trace history");
        const auto count=json_array_get_length(history);
        if(count==length+1) {
            const std::string event=json_array_get_string_element(history,count-1);length=count;
            if(event.starts_with("Observe")){const auto entry=decimal(event.substr(7));last=journal.retain(77,1,entry,observation(entry));}
            else if(event.starts_with("Ready")){const auto entry=decimal(event.substr(5));last=journal.acceptReady(77,1,entry,ready(entry));}
            else if(event.starts_with("Complete")) {
                const auto entry=decimal(event.substr(8));auto fact=observation(entry);fact.request+=10;fact.sequence+=10;fact.now++;
                auto prepared=journal.prepare(77,1,entry,{fact,entry,3,0});last=prepared && journal.commit(std::move(*prepared));
            }else if(event=="Poll") {
                auto candidate=journal.nextReadiness(77,1,binding);selected=candidate?candidate->entry:0;last=true;
                if(candidate)require(candidate->subject.value==20+selected && candidate->wire==ready(selected),"Exact original retry wire and subject");
            }else if(event=="WrongEpoch") {last=true;try{journal.nextReadiness(77,2,binding);}catch(const std::exception&){last=false;}}
            else if(event=="Ack")last=journal.acknowledge(77,1,ack(journal.acknowledged()+1));
            else require(false,"Known poll event");
            compared++;
        }else if(count!=length)require(false,"Contiguous trace history");
        const auto retained=values(state,"retained"),isReady=values(state,"ready"),complete=values(state,"complete");
        require(journal.size()==retained.size(),"Compiled exact bounded journal membership");
        require(journal.issued()==integer(state,"issued") && journal.acknowledged()==integer(state,"acked"),"Compiled unchanged delivery prefixes");
        auto waiting=journal.pendingReadiness(77,1,binding);std::set<uint64_t> actual;
        for(const auto& row:waiting)actual.insert(row.entry);
        auto expected=isReady;for(auto entry:complete)expected.erase(entry);
        require(actual==expected,"Compiled accepted pending membership");
        require(selected==integer(state,"selected"),"Compiled fair one-candidate selection");
        require(last==bool(json_object_get_boolean_member(state,"last")),"Compiled original receiver outcome");
    }
    std::cout<<"{\"passed\":true,\"statesCompared\":"<<compared<<",\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
