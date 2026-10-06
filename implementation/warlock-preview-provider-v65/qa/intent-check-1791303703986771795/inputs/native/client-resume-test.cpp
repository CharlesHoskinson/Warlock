#include "client_producer.hpp"
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
    SourceObservation prior{{{{1},{2},{3}},{{1},{4},{5},{6},{7},{8},{9}},{1},1,true,true,false,true},1,32,1,SourceObservation::Kind::UnqualifiedClientMain,false};
    uint64_t now=1;uri::Endpoint endpoint({1,4,1,32},1,1,[&](uint64_t)->std::optional<uri::NativeTime>{return uri::NativeTime{{1},now};});
    check(endpoint.enableDemand({{1,4,1,32},{1},{1},1}),"One shared native demand coordinator");
    Job original;
    endpoint.nativeDemand([&](auto& queue){check(queue.observe({1,1,prior.scope,{1},32,true}).accepted,"Original source demand");auto started=queue.start(1,2000000001);check(started.job.has_value(),"Original job reserved");original=*started.job;});
    check(endpoint.registerView(77,original.binding,{1}),"Exact retained URI view");ReceiptDelivery delivery(endpoint,original.binding,77);
    auto allocate=[&](const Job& job){auto result=endpoint.native([&](auto& b){std::unique_ptr<const Buffer> payload=std::make_unique<const PNG>();return b.allocate(1,job,payload,job.deadline+3000000000ULL);});check(result.receipts.size()==1 && result.receipts[0].packet.has_value(),"Real shared Broker allocation");return endpoint.native([&](auto& b){return *b.producerComplete(1,job).receipts.at(0).packet;});};
    const auto packet=allocate(original);GError* error=nullptr;gsize length{};auto held=endpoint.open(77,uri::encode(packet.token),&length,&error);check(held && !error,"Actual original held GIO reader");
    auto fresh=prior;fresh.observation++;fresh.request++;fresh.scope.now++;fresh.scope.context.privacy.value++;
    auto attempt=[&](uint64_t publication,uint64_t lease,const SourceObservation& observation){return endpoint.nativeDemand([&](auto& queue){return reserveClientResume(queue,original,prior,1,observation,publication,lease);});};
    check(!attempt(2,2,fresh),"No new native reservation while old capture is owned");
    endpoint.native([&](auto& b){b.release(1,original.binding,original,packet.token);check(!b.consumerComplete(1,original),"Held reader prevents physical drain");});
    check(!attempt(2,2,fresh),"No resume while held reader/charge/journal remain");
    check(g_input_stream_close(held,nullptr,&error) && !error,"Actual old held reader closes");g_object_unref(held);
    endpoint.native([&](auto& b){check(b.consumerComplete(1,original),"Actual synthetic consumer drain");check(b.destroy(1,original).status==Result::Status::Complete,"Actual physical synthetic storage destruction");check(b.charge()==0 && b.recordCount()==1,"Zero physical charge keeps terminal journal");});
    check(!attempt(2,2,fresh),"Terminal proof still blocks next capture until ACK");
    endpoint.native([&](auto& b){check(!b.acknowledge(1,original.binding,original,{2}),"Nonterminal sequence cannot clear journal");});
    auto terminal=delivery.pending(77);check(terminal.size()==1,"Exact retained terminal projection");
    Wire ack;check(delivery.acknowledge(77,"family:4",ack.text("kind","acknowledge").begin("job").job(original).end().counter("sequence",3).finish()),"Exact original terminal ACK");
    check(!attempt(0,2,fresh) && !attempt(2,1,fresh),"Missing publication or repeated old lease cannot restart");
    for(const auto mutation:{0,1,2,3,4,5,6,7,8,9,10,11,12}) {
        auto invalid=fresh;
        if(mutation==0)invalid.kind=SourceObservation::Kind::UnqualifiedRootMonitorPlane;
        if(mutation==1)invalid.previewEligible=true;
        if(mutation==2)invalid.scope.binding.session.value++;
        if(mutation==3)invalid.scope.context.incarnation.value++;
        if(mutation==4)invalid.scope.clock.value++;
        if(mutation==5)invalid.observation=prior.observation;
        if(mutation==6)invalid.request=prior.request;
        if(mutation==7)invalid.scope.now=0;
        if(mutation==8)invalid.scope.context.output.value--;
        if(mutation==9)invalid.scope.context.privacy.value=prior.scope.context.privacy.value-1;
        if(mutation==10)invalid.scope.context.scene.value--;
        if(mutation==11)invalid.scope.context.content.value--;
        if(mutation==12)invalid.scope.now=UINT64_MAX;
        bool rejected=false;try{attempt(2,2,invalid);}catch(const std::exception&){rejected=true;}check(rejected,"Foreign/stale/incoherent/overflow observation rejected");
        endpoint.native([&](auto& b){check(b.recordCount()==0 && b.charge()==0 && b.requestFloor(1)==1 && b.nativeScope(1).context==prior.scope.context,"Rejected observation changes no ownership or original replay floor");});
    }
    for(const auto mutation:{0,1,2,3,4}){
        auto unavailable=fresh;if(mutation==0)unavailable.scope.present=false;if(mutation==1)unavailable.scope.locked=true;if(mutation==2)unavailable.scope.gpuReady=false;
        if(mutation==3){unavailable.scope.sourceLive=false;unavailable.scope.context.scene.value++;}if(mutation==4)unavailable.maximumTransferBytes=33;
        check(!attempt(2,2,unavailable),"Unavailable native source or unchanged resource limit prevents capture");
        endpoint.native([&](auto& b){check(b.recordCount()==0 && b.charge()==0 && b.requestFloor(1)==1,"No invented job or native budget increase");});
    }
    const auto next=attempt(2,2,fresh);check(next.has_value(),"New lease and fresh native scope reserve next job");
    check(next->request.value==2 && next->origin.value==2 && next->binding==original.binding && next->clock==original.clock && next->context==fresh.scope.context && next->deadline==fresh.scope.now+2000000000ULL,"New request/origin/context/issued deadline on unchanged owning binding");
    check(original.request.value==1 && original.deadline==2000000001 && packet.expires==5000000001,"Original job/deadline/frame expiration unchanged");
    now=fresh.scope.now;const auto newer=allocate(*next);check(newer.token!=packet.token && newer.expires>packet.expires,"Same physical allocator gives new opaque token and original new expiration");
    auto oldRead=endpoint.open(77,uri::encode(packet.token),&length,&error);check(!oldRead && error,"Old URI cannot alias the new native packet");g_clear_error(&error);
    auto newRead=endpoint.open(77,uri::encode(newer.token),&length,&error);check(newRead && !error,"Exact new GIO reader admitted");
    std::array<uint8_t,4> bytes{};check(g_input_stream_read(newRead,bytes.data(),bytes.size(),nullptr,&error)==4 && !error,"Actual new immutable storage readable");
    check(g_input_stream_close(newRead,nullptr,&error) && !error,"New GIO reader closes");g_object_unref(newRead);
    Wire oldAck;check(!delivery.acknowledge(77,"family:4",oldAck.text("kind","acknowledge").begin("job").job(original).end().counter("sequence",3).finish()),"Old ACK cannot erase newer resource");
    endpoint.native([&](auto& b){check(b.charge()==32 && b.recordCount()==1 && b.inspect().at(0).job==*next,"New owner survives old ACK");b.release(1,next->binding,*next,newer.token);check(b.consumerComplete(1,*next),"New physical consumer drain");check(b.destroy(1,*next).receipts.at(0).sequence.value==6,"Same Broker proof sequence remains continuous");});
    Wire newAck;check(delivery.acknowledge(77,"family:4",newAck.text("kind","acknowledge").begin("job").job(*next).end().counter("sequence",6).finish()),"Exact new terminal ACK on same delivery epoch");
    endpoint.native([&](auto& b){check(b.charge()==0 && b.recordCount()==0 && b.requestFloor(1)==2,"Both jobs drained with monotonic retained request floor");});
    std::cout<<"{\"passed\":true,\"checks\":"<<checks<<",\"nativeAcceptance\":false,\"scope\":\"Actual native resume scheduler/Broker/GIO/ReceiptDelivery conformance with synthetic PNG and source; no live Native capture or GUI unlock claim\"}\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
