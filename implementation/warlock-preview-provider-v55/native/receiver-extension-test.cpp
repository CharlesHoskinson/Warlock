#include "imported_clients.hpp"
#include <iostream>
using namespace preview;
static unsigned checks=0,frees=0;
static void check(bool ok,const char* name){if(!ok)throw std::runtime_error(name);++checks;}
struct PNG final:uri::Payload {
    std::array<uint8_t,12> bytes{137,80,78,71,13,10,26,10,1,2,3,4};
    ~PNG(){++frees;}
    uint64_t charge()const noexcept override{return 32;}
    std::span<const uint8_t> png()const noexcept override{return bytes;}
};
static demand::NativeDemand observation(uint64_t entry,uint64_t now) {
    return {entry,1,{{{1},{2},{3}},{{1},{entry+10},{5},{6},{7},{8},{1}},{10},now,true,true,false,true},{11},32,true};
}
int main(){try {
    const auto normal=bridge::ImportedClients::allocationLimits(2),dynamic=bridge::ImportedClients::allocationLimits(256);
    check(normal.entries==2 && dynamic.entries==256 && normal.items==2 && dynamic.items==2 && normal.records==8 && dynamic.records==8 && normal.bytes==128ULL*1024*1024 && dynamic.bytes==normal.bytes,"actor inventory does not multiply global physical limits");
    for(size_t invalid:{size_t{0},size_t{257}}){bool denied=false;try{bridge::ImportedClients::allocationLimits(invalid);}catch(const std::exception&){denied=true;}check(denied,"overbound or empty actor inventory rejected");}
    uint64_t now=1;uri::Endpoint endpoint({4,8,2,64},4,2,[&](uint64_t)->std::optional<uri::NativeTime>{return uri::NativeTime{{10},now};});
    check(endpoint.enableDemand({{4,8,2,64},{1},{10},1}),"one bounded physical broker and scheduler");
    auto first=observation(1,now);check(endpoint.nativeDemand([&](auto& q){return q.observe(first).accepted;}),"first native actor enrolled");
    auto started=endpoint.nativeDemand([](auto& q){return q.start(1,20);});check(started.status==demand::Attempt::Status::Started && started.job.has_value(),"original first job admitted");const auto job=*started.job;
    auto offered=endpoint.native([&](auto& broker){std::unique_ptr<const Buffer> bytes=std::make_unique<const PNG>();return broker.allocate(1,job,bytes,50);});
    check(offered.receipts.size()==1,"actual first payload transferred to physical broker");endpoint.native([&](auto& broker){broker.producerComplete(1,job);});
    check(endpoint.registerView(77,job.binding,{1}),"one actual receiver registered");const auto original=*endpoint.registeredView(77);
    GError* error=nullptr;gsize length=0;auto reader=endpoint.open(77,uri::encode(offered.receipts.front().packet->token),&length,&error);
    check(reader && !error && length==12 && endpoint.readers()==1,"first actual GIO reader held");
    std::array<uint8_t,4> bytes{};check(g_input_stream_read(reader,bytes.data(),4,nullptr,&error)==4 && bytes[0]==137,"original stream starts at original PNG header");
    auto second=observation(2,++now);check(endpoint.nativeDemand([&](auto& q){return q.observe(second).accepted;}),"distinct second own native actor enrolled");
    check(endpoint.extendView(77,job.binding,{2}),"same receiver admits new own native membership");const auto extended=*endpoint.registeredView(77);
    check(extended.epoch==original.epoch && extended.binding==original.binding && extended.entries==std::set<uint64_t>{1,2},"receiver identity epoch and original membership preserved");
    check(g_input_stream_read(reader,bytes.data(),4,nullptr,&error)==4 && !error && bytes==std::array<uint8_t,4>{13,10,26,10},"held original reader continues after membership grows");
    auto secondStart=endpoint.nativeDemand([](auto& q){return q.start(2,30);});check(secondStart.status==demand::Attempt::Status::Started && secondStart.job->request.value==1 && secondStart.job->context.incarnation!=job.context.incarnation,"distinct actors retain independent original request floors");
    auto secondOffer=endpoint.native([&](auto& broker){std::unique_ptr<const Buffer> payload=std::make_unique<const PNG>();return broker.allocate(2,*secondStart.job,payload,50);});
    endpoint.native([&](auto& broker){broker.producerComplete(2,*secondStart.job);});
    auto secondReader=endpoint.open(77,uri::encode(secondOffer.receipts.front().packet->token),&length,&error);check(secondReader && !error && endpoint.readers()==2,"new own receiver membership exposes only its actual owned packet");
    auto third=observation(3,++now);check(endpoint.nativeDemand([&](auto& q){return q.observe(third).accepted;}),"third native actor may observe while physical capacity stays full");
    auto waiting=endpoint.nativeDemand([](auto& q){return q.start(3,40);});check(waiting.status==demand::Attempt::Status::Capacity && !waiting.job && waiting.native.receipts.empty(),"third capture gets capacity feedback without fabricated native job or refusal");
    check(endpoint.native([](auto& broker){return broker.charge()==64 && broker.activeItems()==2 && broker.recordCount()==2 && broker.requestFloor(3)==0;}),"observing new actors does not evict allocations or advance their request floors");
    auto foreign=observation(4,++now);foreign.scope.binding.session={999};check(endpoint.nativeDemand([&](auto& q){return q.observe(foreign).accepted;}),"controlled foreign native actor exists for ownership rejection");
    const auto prior=*endpoint.registeredView(77);
    check(!endpoint.extendView(77,job.binding,{3,4}),"mixed own and foreign native membership is atomic refusal");
    check(endpoint.registeredView(77)->entries==prior.entries && endpoint.registeredView(77)->epoch==prior.epoch,"atomic refusal cannot partly authorize the valid prefix");
    check(!endpoint.extendView(77,foreign.scope.binding,{3}) && !endpoint.extendView(99,job.binding,{3}) && !endpoint.extendView(77,job.binding,{}) && !endpoint.extendView(77,job.binding,{0}) && !endpoint.extendView(77,job.binding,{999}),"foreign receiver owner absent receiver empty zero and unenrolled actor refused");
    check(endpoint.extendView(77,job.binding,{3}) && endpoint.extendView(77,job.binding,{1,2}),"valid membership and duplicates retain receiver epoch");
    check(endpoint.registeredView(77)->epoch==original.epoch && endpoint.readers()==2 && frees==0,"membership does not masquerade as reader closure or physical retirement");
    endpoint.native([&](auto& broker){broker.release(1,job.binding,job,offered.receipts.front().packet->token);});
    check(g_input_stream_read(reader,bytes.data(),4,nullptr,&error)==-1 && error,"membership extension cannot bypass exact original native revoke");g_clear_error(&error);
    check(!endpoint.native([&](auto& broker){return broker.consumerComplete(1,job);}) && endpoint.native([](auto& broker){return broker.charge()==64;}),"revoked held reader remains physically charged");
    check(g_input_stream_close(reader,nullptr,&error) && !error,"original held reader closes normally");g_object_unref(reader);
    check(endpoint.native([&](auto& broker){return broker.consumerComplete(1,job);}),"original consumer completes only after actual reader drains");
    auto retired=endpoint.native([&](auto& broker){return broker.destroy(1,job);});check(retired.status==Result::Status::Complete && frees==1 && endpoint.native([](auto& broker){return broker.charge()==32 && broker.recordCount()==2;}),"physical destroy releases charge while exact receipt is retained");
    check(endpoint.native([&](auto& broker){return broker.acknowledge(1,job.binding,job,retired.receipts.back().sequence);}),"exact original terminal ACK clears original record");
    third.scope.now=++now;check(endpoint.nativeDemand([&](auto& q){return q.observe(third).accepted;}),"third actor refreshes genuine own clock after physical capacity returns");
    auto next=endpoint.nativeDemand([](auto& q){return q.start(3,40);});check(next.status==demand::Attempt::Status::Started && next.job->request.value==1 && next.job->deadline==40 && endpoint.native([](auto& broker){return broker.charge()==64 && broker.activeItems()==2;}),"third actor admitted only with original request domain and original deadline after real drain");
    check(endpoint.native([](auto& broker){return broker.requestFloor(1)==1 && broker.requestFloor(2)==1 && broker.requestFloor(3)==1;}),"old actor floors are retained after new physical admission");
    auto refused=endpoint.native([&](auto& broker){return broker.producerRefused(3,*next.job);});check(refused.receipts.size()==1 && endpoint.native([&](auto& broker){return broker.acknowledge(3,next.job->binding,*next.job,refused.receipts.back().sequence);}),"explicit actual producer refusal retains terminal identity");
    endpoint.native([&](auto& broker){broker.release(2,secondStart.job->binding,*secondStart.job,secondOffer.receipts.front().packet->token);});
    check(g_input_stream_close(secondReader,nullptr,&error) && !error,"second actual receiver stream closes normally");g_object_unref(secondReader);
    auto secondRetired=endpoint.native([&](auto& broker){return broker.destroy(2,*secondStart.job);});check(secondRetired.status==Result::Status::Complete && endpoint.native([&](auto& broker){return broker.acknowledge(2,secondStart.job->binding,*secondStart.job,secondRetired.receipts.back().sequence);}),"second physical destroy precedes exact final ACK");
    endpoint.unregisterView(77);check(!endpoint.registeredView(77) && endpoint.readers()==0 && frees==2 && endpoint.native([](auto& broker){return broker.recordCount()==0 && broker.charge()==0;}),"all original and new physical resources close without leaked ownership");
    std::cout<<"{\"passed\":true,\"checks\":"<<checks<<",\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
