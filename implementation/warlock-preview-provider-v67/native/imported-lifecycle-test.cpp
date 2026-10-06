#include "imported_lifecycle.hpp"
#include <iostream>
using namespace preview;using namespace preview::bridge;
static unsigned checks=0;
static void check(bool ok,const char* reason){require(ok,reason);++checks;}
struct PNG final:uri::Payload {
    std::array<uint8_t,12> bytes{137,80,78,71,13,10,26,10,1,2,3,4};
    uint64_t charge()const noexcept override{return 32;}
    std::span<const uint8_t> png()const noexcept override{return bytes;}
};
int main(){try {
    SourceObservation first{{{{1},{2},{3}},{{1},{4},{5},{6},{7},{8},{9}},{1},1,true,true,false,true},1,32,1,SourceObservation::Kind::UnqualifiedClientMain,false};
    auto second=first;second.scope.context.incarnation.value=10;second.scope.now=2;second.observation=2;second.request=2;
    uint64_t now=2;uri::Endpoint endpoint({2,8,2,64},4,2,[&](uint64_t)->std::optional<uri::NativeTime>{return uri::NativeTime{{1},now};});
    check(endpoint.enableDemand({{2,8,2,64},{1},{1},1}),"One two-entry physical demand coordinator");
    auto start=[&](uint64_t entry,const SourceObservation& source){return endpoint.nativeDemand([&](auto& q){check(q.observe({entry,1,source.scope,{1},32,true}).accepted,"Own distinct source demand");const auto a=q.start(entry,source.scope.now+2000000000ULL);check(a.job.has_value(),"Original own job reserved");return *a.job;});};
    const auto a=start(1,first),b=start(2,second);check(endpoint.registerView(77,a.binding,{1,2}),"One shared own URI receiver");ReceiptDelivery delivery(endpoint,a.binding,77);
    auto allocate=[&](uint64_t entry,const Job& job){return endpoint.native([&](auto& broker){std::unique_ptr<const Buffer> payload=std::make_unique<const PNG>();check(broker.allocate(entry,job,payload,job.deadline+3000000000ULL).receipts.size()==1,"Actual Broker adopts immutable payload");return *broker.producerComplete(entry,job).receipts.at(0).packet;});};
    const auto pa=allocate(1,a),pb=allocate(2,b);check(pa.token!=pb.token,"Distinct native opaque tokens under shared owner");
    GError* error=nullptr;gsize length{};auto held=endpoint.open(77,uri::encode(pb.token),&length,&error);check(held && !error,"Actual held sibling GIO reader");
    auto stopped=second;stopped.scope.sourceLive=false;stopped.scope.context.scene.value++;stopped.scope.now=3;stopped.observation++;stopped.request++;
    check(endpoint.native([&](auto& broker){return broker.observe(2,stopped.scope,32);}),"Coherent stopped sibling scope admitted");now=3;
    auto present=[&](const SourceObservation& scope,const Packet& packet,uint64_t publication,uint64_t lease){return endpoint.native([&](auto& broker){return admitRetainedImportedPresentation(broker,2,b,scope,packet,1,publication,lease);});};
    check(present(stopped,pb,2,2),"Stopped sibling retains original Historical packet on new lease");
    check(!present(stopped,pb,0,2) && !present(stopped,pb,2,1) && !present(stopped,pa,2,2),"Missing/reused presentation and foreign packet do not gain ownership");
    endpoint.native([&](auto& broker){check(broker.charge()==64 && broker.recordCount()==2 && broker.requestFloor(2)==1 && broker.nextProofSequence()==5,"Re-presentation does not allocate, renew or release either job");});
    for(const auto mutation:{0,1,2,3,4,5}) {
        auto invalid=pb;if(mutation==0)invalid.job.request.value++;if(mutation==1)invalid.token.sequence++;if(mutation==2)invalid.signaled=false;if(mutation==3)invalid.expires++;if(mutation==4)invalid.fidelity=Packet::Fidelity::Family;if(mutation==5)invalid.job.deadline++;
        check(!present(stopped,invalid,2,2),"Altered metadata cannot re-present original sibling authority");
    }
    auto fresh=first;fresh.scope.now=4;fresh.observation=4;fresh.request=4;fresh.scope.context.privacy.value++;
    std::optional<NativeStartIdentity> intent;
    auto resume=[&](const SourceObservation& scope,uint64_t publication=2,uint64_t lease=2){return endpoint.nativeDemand([&](auto& q){return reserveImportedResume(q,1,a,first,1,scope,publication,lease,intent);});};
    check(!resume(fresh),"Own allocated record prevents new demand despite new lease");
    endpoint.native([&](auto& broker){broker.release(1,a.binding,a,pa.token);check(broker.consumerComplete(1,a),"Own storage drains independently from sibling reader");check(broker.destroy(1,a).receipts.at(0).sequence.value==5,"Exact original terminal proof5");});
    check(!resume(fresh),"Own terminal journal still blocks resume");
    Wire ack;check(delivery.acknowledge(77,"family:4",ack.text("kind","acknowledge").begin("job").job(a).end().counter("sequence",5).finish()),"Exact own terminal ACK permits proof-safe retirement");
    endpoint.native([&](auto& broker){check(importedEntryRetired(broker,1) && !importedEntryRetired(broker,2) && broker.charge()==32 && broker.recordCount()==1,"Sibling remains physically charged while first entry retires");});
    check(!resume(fresh,0,2) && !resume(fresh,2,1),"No reservation for absent gate or repeated old lease");
    for(const auto mutation:{0,1,2,3,4,5,6,7,8,9,10}) {
        auto invalid=fresh;if(mutation==0)invalid.scope.binding.session.value++;if(mutation==1)invalid.scope.context.incarnation.value++;if(mutation==2)invalid.scope.clock.value++;if(mutation==3)invalid.observation=first.observation;if(mutation==4)invalid.request=first.request;if(mutation==5)invalid.scope.now=0;if(mutation==6)invalid.scope.context.output.value--;if(mutation==7)invalid.scope.context.content.value--;if(mutation==8)invalid.previewEligible=true;if(mutation==9)invalid.kind=SourceObservation::Kind::UnqualifiedRootMonitorPlane;if(mutation==10)invalid.scope.now=UINT64_MAX;
        bool rejected=false;try{resume(invalid);}catch(const std::exception&){rejected=true;}check(rejected,"Foreign/stale/incoherent/overflow native scope rejected");
        endpoint.native([&](auto& broker){check(broker.charge()==32 && broker.recordCount()==1 && broker.requestFloor(1)==1,"Rejection preserves sibling ownership and own replay floor");});
    }
    for(const auto mutation:{0,1,2,3,4}) {
        auto invalid=fresh;if(mutation==0)invalid.scope.present=false;if(mutation==1)invalid.scope.locked=true;if(mutation==2)invalid.scope.gpuReady=false;if(mutation==3){invalid.scope.sourceLive=false;invalid.scope.context.scene.value++;}if(mutation==4)invalid.maximumTransferBytes=65;
        check(!resume(invalid),"Unavailable source does not invent live capture or enlarge budget");
    }
    const auto next=resume(fresh);check(next.has_value(),"Own new job can start while sibling remains physically owned");
    check(next->request.value==2 && next->origin.value==2 && next->binding==a.binding && next->clock==a.clock && next->context==fresh.scope.context && next->deadline==fresh.scope.now+2000000000ULL,"New original issued job identity/clock/deadline exact");
    now=4;const auto pn=allocate(1,*next);check(pn.token!=pa.token && pn.token!=pb.token && a.deadline==2000000001ULL && pb.expires==5000000002ULL,"Old job and sibling expiration unchanged; token never aliases");
    std::array<uint8_t,4> bytes{};check(g_input_stream_read(held,bytes.data(),bytes.size(),nullptr,&error)==4 && !error,"Held sibling remains readable across independent resume");
    auto oldRead=endpoint.open(77,uri::encode(pa.token),&length,&error);check(!oldRead && error,"Old URI cannot alias newly reserved resource");g_clear_error(&error);
    check(g_input_stream_close(held,nullptr,&error) && !error,"Actual sibling held reader closes");g_object_unref(held);
    auto finish=[&](uint64_t entry,const Job& job,const Packet& packet){return endpoint.native([&](auto& broker){broker.release(entry,job.binding,job,packet.token);check(broker.consumerComplete(entry,job),"Independent actual physical consumer drain");return broker.destroy(entry,job).receipts.at(0).sequence.value;});};
    const auto bn=finish(2,b,pb),an=finish(1,*next,pn);check(bn==8 && an==9,"Original shared terminal proof sequence remains continuous");
    Wire ba,aa;check(delivery.acknowledge(77,"family:10",ba.text("kind","acknowledge").begin("job").job(b).end().counter("sequence",bn).finish()),"Exact sibling final ACK");check(delivery.acknowledge(77,"family:4",aa.text("kind","acknowledge").begin("job").job(*next).end().counter("sequence",an).finish()),"Exact resumed final ACK");
    endpoint.native([&](auto& broker){check(broker.charge()==0 && broker.recordCount()==0 && broker.requestFloor(1)==2 && broker.requestFloor(2)==1,"All physical and journal ownership retired; independent monotonic floors retained");});
    endpoint.unregisterView(77);std::cout<<"{\"passed\":true,\"checks\":"<<checks<<",\"nativeAcceptance\":false,\"scope\":\"Actual two-entry retained/resume helper, Broker, GIO and ReceiptDelivery; synthetic native scope/PNG, actual GUI/native resumption remains unqualified\"}\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
