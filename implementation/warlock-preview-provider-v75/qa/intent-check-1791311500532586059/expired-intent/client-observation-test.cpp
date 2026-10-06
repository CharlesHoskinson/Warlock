#include "client_producer.hpp"
#include <iostream>
using namespace preview;using namespace preview::bridge;
static unsigned checks=0,freed=0;
static void check(bool ok,const char* reason){require(ok,reason);++checks;}
struct PNG final:uri::Payload {
    std::array<uint8_t,12> bytes{137,80,78,71,13,10,26,10,1,2,3,4};
    ~PNG(){++freed;}
    uint64_t charge()const noexcept override{return 32;}
    std::span<const uint8_t> png()const noexcept override{return bytes;}
};
static SourceObservation initial(){return {{{{1},{2},{3}},{{1},{4},{5},{6},{7},{8},{9}},{10},1,true,true,false,true},1,32,1,SourceObservation::Kind::UnqualifiedClientMain,false};}
static Job original(){const auto s=initial().scope;return {s.binding,s.context,{1},{11},s.clock,20};}
int main(){try {
    for(const std::string kind:{"content","scene","stopped","output","privacy","rendering","locked","absent","gpu"}) {
        uint64_t now=1;uri::Endpoint endpoint({1,4,1,32},1,1,[&](uint64_t)->std::optional<uri::NativeTime>{return uri::NativeTime{{10},now};});
        auto observed=initial();const auto job=original();
        endpoint.native([&](auto& b){check(b.enroll(1,observed.scope,32),"Native source enrolled");check(b.acquire(1,job.binding,job).status==Result::Status::Admitted,"Original job reserved");});
        auto offered=endpoint.native([&](auto& b){std::unique_ptr<const Buffer> payload=std::make_unique<const PNG>();return b.allocate(1,job,payload,50);});
        const auto token=offered.receipts.at(0).packet->token;endpoint.native([&](auto& b){b.producerComplete(1,job);});
        check(endpoint.registerView(77,job.binding,{1}),"Exact view enrollment");GError* error=nullptr;gsize size{};
        auto stream=endpoint.open(77,uri::encode(token),&size,&error);check(stream && !error,"Actual initial GIO reader");
        observed.scope.now=now=2;observed.observation++;
        if(kind=="content")observed.scope.context.content.value++;
        if(kind=="scene")observed.scope.context.scene.value++;
        if(kind=="stopped"){observed.scope.sourceLive=false;observed.scope.context.scene.value++;}
        if(kind=="output")observed.scope.context.output.value++;
        if(kind=="privacy")observed.scope.context.privacy.value++;
        if(kind=="rendering")observed.scope.context.rendering.value++;
        if(kind=="locked")observed.scope.locked=true;
        if(kind=="absent")observed.scope.present=false;
        if(kind=="gpu")observed.scope.gpuReady=false;
        check(clientFactsChanged(initial(),observed),"Meaningful facts detected");
        check(endpoint.native([&](auto& b){return admitClientObservation(b,job,observed);}),"Actual shared authority update");
        std::array<uint8_t,4> bytes{};auto read=g_input_stream_read(stream,bytes.data(),bytes.size(),nullptr,&error);
        const bool retained=kind=="content" || kind=="scene" || kind=="stopped";
        check(retained?(read==4 && !error):(read==-1 && error),"Held reader respects historical versus revoked authority");g_clear_error(&error);
        endpoint.native([&](auto& b){check(b.charge()==32 && b.inspect().at(0).job==job,"Changed facts retain original job and physical charge");b.release(1,job.binding,job,token);check(!b.consumerComplete(1,job),"Held stream blocks physical retirement");});
        check(g_input_stream_close(stream,nullptr,&error) && !error,"Actual held reader closes");g_object_unref(stream);
        const auto prior=freed;
        auto terminal=endpoint.native([&](auto& b){check(b.charge()==32 && b.recordCount()==1,"Reader close is not terminal proof");check(b.consumerComplete(1,job),"Native consumer drain confirmed");return b.destroy(1,job);});
        check(terminal.receipts.size()==1 && terminal.receipts.back().kind==Receipt::Kind::Released && freed==prior+1,"Physical destruction precedes Released proof");
        endpoint.native([&](auto& b){check(b.charge()==0 && b.recordCount()==1,"Proof retained after physical zero");check(b.acknowledge(1,job.binding,job,terminal.receipts.back().sequence),"Exact terminal acknowledgment");check(b.recordCount()==0,"Journal drained only after acknowledgment");});
    }
    for(const std::string kind:{"monitor","eligible","binding","lifetime","subject","clock"}) {
        Broker broker({1,4,1,32});auto observed=initial();const auto job=original();broker.enroll(1,observed.scope,32);
        if(kind=="monitor")observed.kind=SourceObservation::Kind::UnqualifiedRootMonitorPlane;
        if(kind=="eligible")observed.previewEligible=true;
        if(kind=="binding")observed.scope.binding.session.value++;
        if(kind=="lifetime")observed.scope.context.lifetime.value++;
        if(kind=="subject")observed.scope.context.incarnation.value++;
        if(kind=="clock")observed.scope.clock.value++;
        bool refused=false;try{admitClientObservation(broker,job,observed);}catch(const std::exception&){refused=true;}check(refused,"Foreign/elevated observation refuses");
    }
    auto old=initial(),current=old;current.scope.now++;current.observation++;current.request++;
    check(!clientFactsChanged(old,current),"Metadata/clock advance alone produces no repeated source decoration work");
    Json seed(clientSeed(current,2,1));check(seed.counter("publication")==2 && seed.counter("lease")==1 && std::string_view(Json::text(seed.object(),"kind"))=="source-seed","Exact current typed source stamp");
    Json retained(clientObservation(current));check(std::string_view(Json::text(Json::child(retained.object(),"event"),"kind"))=="observe","Hidden retained owner receives facts without enrollment");
    std::cout<<"{\"passed\":true,\"checks\":"<<checks<<",\"nativeAcceptance\":false}\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
