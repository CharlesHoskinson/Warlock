#include "retirement_journal.hpp"
#include <fstream>
#include <iostream>
using namespace preview;
using namespace preview::bridge;
static uint64_t integer(JsonObject* object,const char* name) {
    const std::string_view text=Json::text(Json::child(object,name),"#bigint");
    return text=="0"?0:decimal(text);
}
int main(int argc,char** argv){try {
    require(argc==2,"One explicitly selected Quint trace");std::ifstream stream(argv[1]);
    std::string text((std::istreambuf_iterator<char>(stream)),{});Json trace(text);
    auto states=json_object_get_array_member(trace.object(),"states");require(states,"Trace states");
    const Binding binding{{17},{18},{19}};
    const IncarnationRetirement observation{binding,{20},1,1,{17},100,30,IncarnationState::Retired};
    auto later=observation;later.request=2;later.sequence=2;later.now=101;
    const ActorRetired fact{later,1,1,0};RetirementJournal journal(binding,77,1,1);
    const auto ready=Wire().text("kind","retire-ready").begin("binding").binding(binding).end()
        .counter("subject",20).counter("observationRequest",1).counter("observationSequence",1).finish();
    auto ack=[&](uint64_t ordinal){return Wire().text("kind","retire-delivery-ack").begin("binding").binding(binding).end().counter("deliveryOrdinal",ordinal).finish();};
    uint64_t length=0,compared=0;bool last=false;
    for(guint i=0;i<json_array_get_length(states);++i) {
        auto state=Json::child(json_node_get_object(json_array_get_element(states,i)),"s");
        auto history=json_object_get_array_member(state,"history");require(history,"Trace history");
        const auto count=json_array_get_length(history);
        if(count==length+1) {
            const std::string_view event=json_array_get_string_element(history,count-1);length=count;
            if(event=="Observe")last=journal.retain(77,1,1,observation);
            else if(event=="Ready")last=journal.acceptReady(77,1,1,ready);
            else if(event=="Commit") {auto prepared=journal.prepare(77,1,1,fact);last=prepared && journal.commit(std::move(*prepared));}
            else if(event=="Abandon") {auto prepared=journal.prepare(77,1,1,fact);last=bool(prepared);}
            else if(event=="Ack")last=journal.acknowledge(77,1,ack(1));
            else if(event=="GapAck")last=journal.acknowledge(77,1,ack(2));
            else if(event=="WrongEpoch") {last=true;try{journal.pendingReadiness(77,2,binding);}catch(const std::exception&){last=false;}}
            else require(false,"Known readiness event");
            compared++;
        }else if(count!=length)require(false,"Contiguous trace history");
        const bool retained=json_object_get_boolean_member(state,"retained"),isReady=json_object_get_boolean_member(state,"ready"),completed=json_object_get_boolean_member(state,"complete");
        require(journal.size()==size_t(retained),"Compiled journal retains exact observation/completion row");
        require(journal.issued()==integer(state,"issued") && journal.acknowledged()==integer(state,"acked"),"Compiled journal issued and compact ACK prefixes");
        const auto waiting=journal.pendingReadiness(77,1,binding);
        require(waiting.size()==size_t(isReady && !completed),"Compiled retained readiness membership");
        if(!waiting.empty())require(waiting[0].entry==1 && waiting[0].subject.value==20 && waiting[0].wire==ready,"Exact original canonical readiness retry");
        require(bool(journal.nextCompletion(77,1,binding))==completed,"Compiled final delivery distinct from readiness");
        require(last==bool(json_object_get_boolean_member(state,"last")),"Compiled transport outcome, no effect-success claim");
    }
    std::cout<<"{\"passed\":true,\"statesCompared\":"<<compared<<",\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
