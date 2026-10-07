#ifdef ANCESTOR_FLOOR
#include "preview_retirement.hpp"
#else
#include "retirement_journal.hpp"
#endif
#include <iostream>
using namespace preview;using namespace preview::bridge;
const Binding binding{{11},{22},{33}};
static IncarnationRetirement observation(uint64_t subject,uint64_t request,uint64_t sequence,uint64_t now) {
    return {binding,{subject},{11},request,sequence,now,1000,IncarnationState::Retired};
}
static ActorRetired fact(uint64_t entry,const IncarnationRetirement& original,uint64_t floor=0) {
    auto next=original;next.request+=1;next.sequence+=1;next.now+=1;
    return {next,entry,1000,floor};
}
int main() {
 try {
#ifdef ANCESTOR_FLOOR
    std::cout<<encodeActorRetired(fact(1,observation(2,10,1,100)))<<'\n';
#else
    unsigned checks=0;const auto check=[&](bool ok,const char* message){if(!ok)throw std::runtime_error(message);++checks;};
    const auto rejects=[&](auto call,const char* message){bool refused=false;try{call();}catch(const std::exception&){refused=true;}check(refused,message);};
    RetirementJournal journal(binding,77,1,2);
    const auto one=observation(2,10,1,100),two=observation(3,13,4,103);
    check(journal.retain(77,1,1,one),"Own first observation retained");
    check(journal.retain(77,1,2,two),"Own sibling observation retained");
    check(!journal.retain(77,1,3,observation(4,20,7,110)),"Capacity preserves original observations");
    check(journal.size()==2 && journal.issued()==0,"Observation slots consume no completion ordinal");
    check(journal.retain(77,1,1,one) && journal.size()==2,"Duplicate observation retains one original record");
    auto changed=one;changed.request++;
    rejects([&]{journal.retain(77,1,1,changed);},"Observation correlation cannot be silently replaced");
    rejects([&]{journal.observation(77,2,binding,1);},"Replaced epoch cannot read original correlation");
    auto foreign=binding;foreign.frontend.value++;
    rejects([&]{journal.observation(77,1,foreign,1);},"Foreign binding cannot read journal");
    const auto ready=[&](const IncarnationRetirement& original){return Wire().text("kind","retire-ready").begin("binding").binding(binding).end().counter("subject",original.subject.value).counter("observationRequest",original.request).counter("observationSequence",original.sequence).finish();};
    check(journal.ready(77,1,1,ready(one)),"Exact readiness matches retained native observation");
    check(!journal.ready(77,1,1,ready(two)),"Sibling readiness cannot settle first actor");
    rejects([&]{journal.ready(78,1,1,ready(one));},"Foreign popup refused before readiness lookup");
    rejects([&]{journal.ready(77,1,1,"{\"kind\":\"retire-ready\",\"extra\":true}");},"Malformed readiness refused");
    auto abandoned=journal.prepare(77,1,1,fact(1,one));
    check(abandoned.has_value() && journal.issued()==0 && journal.size()==2,"Prepared final consumes no ordinal or slot");
    {Json wire(abandoned->wire());auto nested=Json::child(wire.object(),"fact");check(std::string_view(Json::text(nested,"requestFloor"))=="0","Unissued actor zero request floor is canonical and retained");}
    abandoned.reset();
    auto early=journal.prepare(77,1,1,fact(1,one));
    auto later=journal.prepare(77,1,2,fact(2,two));
    check(later && journal.commit(std::move(*later)),"Newer sibling completion retained before sending");
    check(!journal.commit(std::move(*early)) && journal.issued()==1 && journal.size()==2,"Stale preparation cannot skip or reuse ordinal");
    auto first=journal.prepare(77,1,1,fact(1,one));
    auto moved=std::move(*first);
    check(!journal.commit(std::move(*first)),"Moved-from completion cannot publish an empty wire");
    check(journal.commit(std::move(moved)),"Older exact actor completion gets independent next delivery ordinal");
    check(!journal.commit(std::move(moved)),"Prepared completion commits at most once");
    const auto ack=[&](uint64_t ordinal,Binding owner=binding){return Wire().text("kind","retire-delivery-ack").begin("binding").binding(owner).end().counter("deliveryOrdinal",ordinal).finish();};
    const auto* offered=journal.nextCompletion(77,1,binding);check(offered,"First completion retained for delivery");
    const std::string original=*offered;
    for(unsigned i=0;i<100;i++)check(*journal.nextCompletion(77,1,binding)==original,"Lost transmissions retain byte-identical original completion");
    check(!journal.acknowledge(77,1,ack(2)),"Gap acknowledgment cannot discard completion");
    check(journal.size()==2 && journal.acknowledged()==0,"Gap preserves whole pending journal");
    rejects([&]{journal.acknowledge(77,2,ack(1));},"Receiver replacement cannot confirm delivery");
    rejects([&]{journal.acknowledge(77,1,ack(1,foreign));},"Foreign binding cannot confirm delivery");
    check(journal.acknowledge(77,1,ack(1)) && journal.size()==1 && journal.acknowledged()==1,"Exact next processing acknowledgment frees only its record");
    check(journal.acknowledge(77,1,ack(1)) && journal.size()==1,"Lost acknowledgment replay is idempotent");
    {Json pending(*journal.nextCompletion(77,1,binding));check(pending.counter("deliveryOrdinal")==2 && Json::text(Json::child(pending.object(),"fact"),"subject")==std::string("2"),"Older actor fact preserved behind newer sibling confirmation");}
    check(journal.acknowledge(77,1,ack(2)) && journal.size()==0 && !journal.nextCompletion(77,1,binding),"Original completions both confirmed");
    check(!journal.acknowledge(77,1,ack(3)) && journal.issued()==2 && journal.acknowledged()==2,"Future acknowledgment cannot reset compact prefix");
    RetirementJournal turnover(binding,88,2,2);const auto neighbor=observation(21,1,1,1);
    check(turnover.retain(88,2,1,neighbor),"Neighbor observation held throughout turnover");
    for(uint64_t entry=2;entry<=281;entry++) {
        auto observed=observation(entry+20,entry*3,entry*3,entry*10);
        check(turnover.retain(88,2,entry,observed),"Bounded continuing journal admits next observation");
        auto prepared=turnover.prepare(88,2,entry,fact(entry,observed));
        check(prepared && turnover.commit(std::move(*prepared)),"Continuing completion retained");
        check(turnover.size()==2 && turnover.issued()==entry-1,"Active journal remains bounded with nonreused ordinals");
        check(turnover.acknowledge(88,2,ack(entry-1)) && turnover.size()==1,"Exact confirmation frees only current completion");
        const auto* retained=turnover.observation(88,2,binding,1);
        check(retained && retained->subject==neighbor.subject && retained->request==1 && retained->sequence==1,"Neighbor original correlation remains unchanged");
    }
    std::cout<<"{\"passed\":true,\"checks\":"<<checks<<",\"sequentialCompletions\":280,\"nativeAcceptance\":false,\"actorTurnoverAccepted\":false,\"fullReleaseAccepted\":false}\n";
#endif
 }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
 return 0;
}
