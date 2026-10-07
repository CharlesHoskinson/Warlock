#include "preview_uri.hpp"
#include <iostream>
#include <type_traits>
using namespace preview;
static unsigned checks=0,frees=0;
static void check(bool ok,const char* name){if(!ok)throw std::runtime_error(name);++checks;}
struct PNG final:uri::Payload {
    std::array<uint8_t,12> bytes{137,80,78,71,13,10,26,10,1,2,3,4};
    ~PNG(){++frees;}
    uint64_t charge()const noexcept override{return 32;}
    std::span<const uint8_t> png()const noexcept override{return bytes;}
};
static demand::NativeDemand observation(){return {1,1,{{{1},{2},{3}},{{1},{4},{5},{6},{7},{8},{1}},{10},1,true,true,false,true},{11},32,true};}
int main(){try{
    static_assert(!std::is_copy_constructible_v<demand::Coordinator>);
    static_assert(!std::is_move_constructible_v<demand::Coordinator>);
    uint64_t now=1;uri::Endpoint endpoint({2,8,2,64},2,1,[&](uint64_t)->std::optional<uri::NativeTime>{return uri::NativeTime{{10},now};});
    bool threw=false;try{endpoint.nativeDemand([](auto& q){return q.now();});}catch(const std::logic_error&){threw=true;}check(threw,"unconfigured scheduling fails closed");
    threw=false;try{endpoint.enableDemand({{2,8,2,128},{1},{10},2});}catch(const std::invalid_argument&){threw=true;}check(threw,"capacity policy cannot disagree with physical broker");
    check(endpoint.enableDemand({{2,8,2,64},{1},{10},2}),"native demand enabled once");
    check(!endpoint.enableDemand({{2,8,2,64},{1},{10},9}),"policy cannot be replaced");
    Broker* uriBroker=endpoint.native([](auto& b){return &b;});Broker* schedulerBroker=endpoint.nativeDemand([](auto& q){return &q.nativeBroker();});check(uriBroker==schedulerBroker,"one actual physical broker");
    auto d=observation();check(endpoint.nativeDemand([&](auto& q){return q.observe(d).accepted;}),"native observed scope enrolled");
    auto attempt=endpoint.nativeDemand([](auto& q){return q.start(1,20);});check(attempt.status==demand::Attempt::Status::Started,"demand creates exact admitted job");const auto job=*attempt.job;
    auto offer=endpoint.native([&](auto& b){std::unique_ptr<const Buffer> bytes=std::make_unique<const PNG>();return b.allocate(1,job,bytes,50);});check(offer.receipts.size()==1 && uriBroker->charge()==32,"URI ownership sees scheduler reservation");
    endpoint.native([&](auto& b){return b.producerComplete(1,job);});endpoint.nativeDemand([](auto& q){q.poll();});
    check(endpoint.registerView(77,job.binding,{1}),"trusted view bound to actual owner");
    auto token=offer.receipts.front().packet->token;GError* error=nullptr;gsize length=0;
    auto stream=endpoint.open(77,uri::encode(token),&length,&error);check(stream && !error && length==12 && endpoint.readers()==1,"URI stream reads exact broker image");
    std::array<uint8_t,4> bytes{};check(g_input_stream_read(stream,bytes.data(),4,nullptr,&error)==4 && bytes[0]==137,"actual GIO read succeeds");
    d.scope.now=now=3;d.scope.context.content={2};check(endpoint.nativeDemand([&](auto& q){return q.observe(d).accepted;}),"new content enrolled without deleting old image");
    auto next=endpoint.nativeDemand([](auto& q){return q.start(1,30);});check(next.status==demand::Attempt::Status::Started && uriBroker->charge()==64,"new capture shares capacity with old URI reader");
    endpoint.native([&](auto& b){return b.producerRefused(1,*next.job);});
    d.visible=false;endpoint.nativeDemand([&](auto& q){return q.observe(d);});
    check(g_input_stream_read(stream,bytes.data(),4,nullptr,&error)==-1 && error,"revoked demand blocks retained stream");g_clear_error(&error);
    check(!endpoint.native([&](auto& b){return b.consumerComplete(1,job);}) && uriBroker->charge()==32 && frees==0,"retained reader prevents physical retirement");
    check(g_input_stream_close(stream,nullptr,&error) && !error,"stream close drops reader only");g_object_unref(stream);
    check(endpoint.readers()==0 && uriBroker->charge()==32 && frees==0,"closed stream does not fabricate terminal proof");
    check(endpoint.native([&](auto& b){return b.consumerComplete(1,job);}),"actual consumer completion accepted after read references drain");
    auto retired=endpoint.native([&](auto& b){return b.destroy(1,job);});check(retired.receipts.size()==2 && uriBroker->charge()==0 && frees==1,"physical destruction precedes final receipts");
    check(!endpoint.native([&](auto& b){return b.acknowledge(1,job.binding,job,retired.receipts.front().sequence);}),"partial terminal acknowledgement retains record");
    check(endpoint.native([&](auto& b){return b.acknowledge(1,job.binding,job,retired.receipts.back().sequence);}),"exact final acknowledgement releases record");
    endpoint.unregisterView(77);
    // Completion and exact ack may happen in one native callback before poll.
    auto refused=endpoint.native([&](auto& b){return b.producerRefused(1,*next.job);});endpoint.native([&](auto& b){return b.acknowledge(1,next.job->binding,*next.job,refused.receipts.back().sequence);});
    d.visible=true;d.lease=2;d.scope.now=now=5;d.scope.context.content={3};endpoint.nativeDemand([&](auto& q){return q.observe(d);});
    auto third=endpoint.nativeDemand([](auto& q){return q.start(1,40);});check(third.status==demand::Attempt::Status::Started && third.job->request.value==3,"same broker preserves floor across drain");
    endpoint.native([&](auto& b){auto done=b.producerRefused(1,*third.job);return b.acknowledge(1,third.job->binding,*third.job,done.receipts.back().sequence);});
    endpoint.nativeDemand([](auto& q){q.poll();});check(endpoint.nativeDemand([](auto& q){return !q.inspect(1).capture;}),"native exact retirement before poll cannot strand demand");
    std::cout<<"{\"passed\":true,\"checks\":"<<checks<<"}\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
