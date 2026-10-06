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
    SourceObservation source{{{{1},{2},{3}},{{1},{4},{5},{6},{7},{8},{9}},{1},1,true,true,false,true},1,32,1,SourceObservation::Kind::UnqualifiedClientMain,false};
    uint64_t now=1;uri::Endpoint endpoint({1,4,1,32},1,1,[&](uint64_t)->std::optional<uri::NativeTime>{return uri::NativeTime{{1},now};});
    check(endpoint.enableDemand({{1,4,1,32},{1},{1},1}),"One shared native authority");
    Job job;endpoint.nativeDemand([&](auto& q){check(q.observe({1,1,source.scope,{1},32,true}).accepted,"Actual original demand");auto started=q.start(1,2000000001);check(started.job.has_value(),"Actual original reservation");job=*started.job;});
    check(endpoint.registerView(77,job.binding,{1}),"Same native URI receiver");ReceiptDelivery delivery(endpoint,job.binding,77);
    endpoint.native([&](auto& b){std::unique_ptr<const Buffer> payload=std::make_unique<const PNG>();check(b.allocate(1,job,payload,5000000001).receipts.size()==1,"Actual owned original synthetic storage");});
    const auto packet=endpoint.native([&](auto& b){return *b.producerComplete(1,job).receipts.at(0).packet;});
    auto admit=[&](const SourceObservation& current,const Packet& frame,uint64_t publication,uint64_t lease){return endpoint.native([&](auto& b){return admitRetainedClientPresentation(b,job,current,frame,1,publication,lease);});};
    check(!admit(source,packet,0,2) && !admit(source,packet,2,1),"Missing or old presentation gate cannot rebind");
    auto stopped=source;stopped.scope.sourceLive=false;stopped.scope.context.scene.value++;stopped.scope.context.content.value++;stopped.scope.now++;stopped.observation++;stopped.request++;
    check(endpoint.native([&](auto& b){return admitClientObservation(b,job,stopped);}),"Actual coherent native stopped scope admitted");now=stopped.scope.now;
    check(admit(stopped,packet,2,2),"New trusted presentation can retain stopped source Historical pixels");
    endpoint.native([&](auto& b){check(b.recordCount()==1 && b.charge()==32 && b.requestFloor(1)==1 && b.nextProofSequence()==3 && b.inspect()[0].job==job && b.inspect()[0].packet->expires==packet.expires,"Re-presentation creates no job, receipt, renewal or ownership mutation");});
    for(const auto mutation:{0,1,2,3,4}) {
        auto invalid=stopped;
        if(mutation==0)invalid.scope.binding.session.value++;
        if(mutation==1)invalid.scope.context.incarnation.value++;
        if(mutation==2)invalid.scope.now++;
        if(mutation==3)invalid.kind=SourceObservation::Kind::UnqualifiedRootMonitorPlane;
        if(mutation==4)invalid.previewEligible=true;
        bool rejected=false;try{admit(invalid,packet,2,2);}catch(const std::exception&){rejected=true;}check(rejected,"Foreign/stale/unadmitted scope cannot re-present an owned URI");
    }
    for(const auto mutation:{0,1,2,3,4,5,6}) {
        auto invalid=packet;
        if(mutation==0)invalid.job.request.value++;
        if(mutation==1)invalid.token.sequence++;
        if(mutation==2)invalid.signaled=false;
        if(mutation==3)invalid.expires++;
        if(mutation==4)invalid.coverage=15;
        if(mutation==5)invalid.fidelity=Packet::Fidelity::Family;
        if(mutation==6)invalid.job.deadline++;
        check(!admit(stopped,invalid,2,2),"Changed packet metadata cannot alias original retained authority");
    }
    GError* error=nullptr;gsize length{};auto held=endpoint.open(77,uri::encode(packet.token),&length,&error);check(held && !error,"Actual same Historical URI remains readable after source stop");
    std::array<uint8_t,4> bytes{};check(g_input_stream_read(held,bytes.data(),bytes.size(),nullptr,&error)==4 && !error,"Actual stopped source independent immutable pixel storage readable");
    endpoint.native([&](auto& b){b.release(1,job.binding,job,packet.token);check(!b.consumerComplete(1,job),"Original held reader still prevents physical drain");});
    check(!admit(stopped,packet,2,2),"Revoked cleanup packet cannot gain a new presentation lease");
    check(g_input_stream_close(held,nullptr,&error) && !error,"Actual retained reader closes");g_object_unref(held);
    endpoint.native([&](auto& b){check(b.consumerComplete(1,job),"Original physical consumer drain");check(b.destroy(1,job).receipts.at(0).sequence.value==3,"Original terminal sequence unrenewed");});
    check(!admit(stopped,packet,2,2),"Terminal journal cannot be re-presented");
    Wire ack;check(delivery.acknowledge(77,"family:4",ack.text("kind","acknowledge").begin("job").job(job).end().counter("sequence",3).finish()),"Exact original terminal ACK");
    check(!admit(stopped,packet,2,2),"Retired storage cannot be re-presented");
    endpoint.native([&](auto& b){check(b.recordCount()==0 && b.charge()==0 && b.requestFloor(1)==1,"No fresh native job invented for stopped source");});
    std::cout<<"{\"passed\":true,\"checks\":"<<checks<<",\"nativeAcceptance\":false,\"scope\":\"Actual retained-presentation helper/Broker/GIO/ReceiptDelivery with synthetic source and PNG; actual Elm/native reopened Historical qualification remains separate\"}\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
