#include "client_producer.hpp"
#include "retirement_journal.hpp"
#include "detachment_journal.hpp"
#include <iostream>
using namespace preview;using namespace preview::bridge;
int main(){try {
    unsigned checks=0;size_t maximum=0;
    auto check=[&](bool ok,const char* why){require(ok,why);++checks;};
    const Binding binding{{UINT64_MAX},{UINT64_MAX},{UINT64_MAX}};
    const Context context{{UINT64_MAX},{UINT64_MAX},{UINT64_MAX},{UINT64_MAX},{UINT64_MAX},{UINT64_MAX},{UINT64_MAX}};
    const Job job{binding,context,{UINT64_MAX},{UINT64_MAX},{UINT64_MAX},UINT64_MAX};
    Token token;token.brokerNonce.fill(255);token.sequence=UINT64_MAX;
    const auto handle=uri::encode(token);check(handle.size()==std::string_view("elm-shell://preview/").size()+64,"Original encoded token fixed64 hexadecimal characters");check(uri::decode(handle)==token,"Original maximum token roundtrip");
    Packet packet{job,token,false,Packet::Fidelity::Client,1,UINT64_MAX};
    auto offer=frameEvent("offer",packet);packet.signaled=true;auto fence=frameEvent("fence",packet);
    auto batch="["+offer+","+fence+"]";maximum=std::max(maximum,batch.size());
    Json decoded("{\"events\":"+batch+"}");check(json_array_get_length(json_object_get_array_member(decoded.object(),"events"))==2,"Original two-event acquisition result");
    check(offer.size()<=4096 && fence.size()<=4096 && batch.size()<=8192,"Maximum numeric/token original frame serializers fit reserved dispatch bytes");
    check(offer.find("18446744073709551615")!=offer.npos && offer.find('\\')==offer.npos,"Counters are maximum decimal strings; fixed frame fields need no variable escaping");
    const uint64_t popup=UINT64_MAX,epoch=UINT64_MAX;
    DetachmentJournal scoped(binding,popup,epoch);
    ActorDetached fact{binding,{UINT64_MAX},epoch,UINT64_MAX,UINT64_MAX,UINT64_MAX};
    auto ready=Wire().text("kind","detach-ready").begin("binding").binding(binding).end().counter("receiverEpoch",epoch).counter("subject",UINT64_MAX).counter("entry",UINT64_MAX).counter("entryIssuedThrough",UINT64_MAX).counter("requestFloor",UINT64_MAX).finish();
    check(scoped.acceptReady(popup,epoch,fact,ready),"Original maximum scoped readiness retained");
    auto prepared=scoped.prepare(popup,epoch,fact);check(prepared.has_value(),"Original maximum scoped completion prepared");
    // This real original journal issues1. Any valid UInt64 delivery ordinal can
    // add at most19 decimal characters; no field contains unbounded user text.
    auto scopedBound=prepared->wire().size()+19+2;maximum=std::max(maximum,scopedBound);
    check(scopedBound<=4096,"Original scoped completion plus maximum delivery ordinal fits one event budget");
    const auto exactScoped=prepared->wire();check(scoped.commit(std::move(*prepared)),"Original scoped completion committed");
    auto* nextScoped=scoped.nextCompletion(popup,epoch);check(nextScoped && *nextScoped==exactScoped,"Original scoped nextCompletion returns one exact retained wire");
    auto other=fact;other.entry=UINT64_MAX-1;other.subject={UINT64_MAX-1};
    auto otherReady=Wire().text("kind","detach-ready").begin("binding").binding(binding).end().counter("receiverEpoch",epoch).counter("subject",other.subject.value).counter("entry",other.entry).counter("entryIssuedThrough",other.entryIssuedThrough).counter("requestFloor",other.requestFloor).finish();
    check(scoped.acceptReady(popup,epoch,other,otherReady),"Second original scoped actor retained");auto another=scoped.prepare(popup,epoch,other);check(another && scoped.commit(std::move(*another)),"Second original scoped completion committed");
    check(scoped.size()==2 && *scoped.nextCompletion(popup,epoch)==exactScoped,"Two scoped completions still return only next one, not whole inventory");
    RetirementJournal permanent(binding,popup,epoch);
    IncarnationRetirement observed{binding,{UINT64_MAX},{UINT64_MAX},UINT64_MAX-1,UINT64_MAX-1,UINT64_MAX-1,UINT64_MAX,IncarnationState::Retired};
    check(permanent.retain(popup,epoch,UINT64_MAX,observed),"Original maximum permanent retirement observation retained");
    auto retireReady=Wire().text("kind","retire-ready").begin("binding").binding(binding).end().counter("subject",UINT64_MAX).counter("observationRequest",UINT64_MAX-1).counter("observationSequence",UINT64_MAX-1).finish();
    check(permanent.acceptReady(popup,epoch,UINT64_MAX,retireReady),"Original exact permanent readiness retained");
    auto completed=observed;completed.request=UINT64_MAX;completed.sequence=UINT64_MAX;completed.now=UINT64_MAX;
    ActorRetired retired{completed,UINT64_MAX,UINT64_MAX,UINT64_MAX};
    auto permanentPrepared=permanent.prepare(popup,epoch,UINT64_MAX,retired);check(permanentPrepared.has_value(),"Original maximum permanent completion prepared");
    const auto permanentBound=permanentPrepared->wire().size()+19+2;maximum=std::max(maximum,permanentBound);
    check(permanentBound<=4096,"Original permanent completion plus maximum delivery ordinal fits one event budget");
    const auto exactPermanent=permanentPrepared->wire();check(permanent.commit(std::move(*permanentPrepared)),"Original permanent completion committed");
    auto* nextPermanent=permanent.nextCompletion(popup,epoch,binding);check(nextPermanent && *nextPermanent==exactPermanent,"Original permanent nextCompletion returns one exact retained wire");
    check(maximum<=8192,"All original native dispatch output shapes fit the conservative pre-effect reservation");
    std::cout<<"{\"passed\":true,\"checks\":"<<checks<<",\"maximumBoundedBatchBytes\":"<<maximum<<",\"reservedDispatchBytes\":8192,\"syntheticMaximumFields\":true,\"maximumOrdinalDigitsAnalyticallyIncluded\":true,\"actualCore\":false,\"nativeAcceptance\":false}\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
