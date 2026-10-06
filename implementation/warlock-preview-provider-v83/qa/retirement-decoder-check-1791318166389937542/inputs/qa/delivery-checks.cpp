#include "preview_delivery.hpp"
#include <iostream>
using namespace preview;using namespace preview::bridge;
struct PNG final:uri::Payload{std::array<uint8_t,12> bytes{137,80,78,71,13,10,26,10,1,2,3,4};uint64_t charge()const noexcept override{return 32;}std::span<const uint8_t> png()const noexcept override{return bytes;}};
static Scope scope(uint64_t entry){return {{{1},{2},{3}},{{1},{entry+10},{5},{6},{7},{8},{1}},{10},1,true,true,false,true};}
static std::string ack(const Job& job,uint64_t sequence){Wire w;return w.text("kind","acknowledge").begin("job").job(job).end().counter("sequence",sequence).finish();}
int main(){try{
 uri::Endpoint endpoint({2,8,2,64},4,2,[](uint64_t)->std::optional<uri::NativeTime>{return uri::NativeTime{{10},1};});
 std::array<Job,2> jobs;std::array<GInputStream*,2> streams{};const auto own=scope(1).binding;
 auto initialize=[&](uint64_t entry){auto s=scope(entry);jobs[entry-1]={s.binding,s.context,{1},{1},s.clock,100};endpoint.native([&](auto& b){require(b.enroll(entry,s,32),"Actual native actor");require(b.acquire(entry,s.binding,jobs[entry-1]).status==Result::Status::Admitted,"Original job reservation");std::unique_ptr<const Buffer> bytes=std::make_unique<const PNG>();b.allocate(entry,jobs[entry-1],bytes,120);b.producerComplete(entry,jobs[entry-1]);});};
 initialize(1);require(endpoint.registerView(77,own,{1}),"Original receiver");ReceiptDelivery delivery(endpoint,own,77);const auto epoch=endpoint.registeredView(77)->epoch;initialize(2);require(endpoint.extendView(77,own,{2}),"New native pixel membership only");
 for(uint64_t entry=1;entry<=2;++entry){auto packet=endpoint.native([&](auto& b){for(const auto& r:b.inspect())if(r.entry==entry)return *r.packet;throw std::runtime_error("Actual packet");});GError* error=nullptr;gsize length=0;streams[entry-1]=endpoint.open(77,uri::encode(packet.token),&length,&error);require(streams[entry-1] && !error && length==12,"Actual GIO reader");}
 std::string event;
 while(std::getline(std::cin,event)){
  if(event=="Extend" || event=="WrongPopup"){try{delivery.extendSubjects(event=="Extend"?77:88);}catch(const std::exception&){} }
  else if(event=="Replace"){endpoint.unregisterView(77);require(endpoint.registerView(77,own,{1,2}),"Replacement receiver");}
  else{
   const uint64_t entry=event.ends_with("Old")?1:2;auto& job=jobs[entry-1];
   if(event.starts_with("Cancel"))endpoint.native([&](auto& b){b.cancel(entry,own,job);});
   else if(event.starts_with("Close")){GError* error=nullptr;require(streams[entry-1] && g_input_stream_close(streams[entry-1],nullptr,&error) && !error,"Actual reader close");g_object_unref(streams[entry-1]);streams[entry-1]=nullptr;}
   else if(event.starts_with("Fence"))require(endpoint.native([&](auto& b){return b.consumerComplete(entry,job);}),"Explicit native consumer completion");
   else if(event.starts_with("Destroy"))require(endpoint.native([&](auto& b){return b.destroy(entry,job);}).status==Result::Status::Complete,"Physical destroy");
   else if(event.starts_with("Ack")){auto proofs=endpoint.native([&](auto& b){for(const auto& r:b.inspect())if(r.entry==entry)return r.proofs;return std::vector<Receipt>{};});require(!proofs.empty(),"Original terminal proof");try{delivery.acknowledge(77,"family:"+std::to_string(job.context.incarnation.value),ack(job,proofs.back().sequence.value));}catch(const std::exception&){} }
   else require(false,"Selected model event");
  }
  unsigned oldReceipts=0,newReceipts=0;try{for(const auto& wire:delivery.pending(77)){Json j(wire);const auto id=std::string_view(Json::text(j.object(),"identity"));if(id=="family:11")++oldReceipts;else if(id=="family:12")++newReceipts;else require(false,"Exact family receipt");}}catch(const std::exception&){require(endpoint.registeredView(77)->epoch!=epoch,"Only receiver replacement hides pending projection");}
  const auto physical=endpoint.native([](auto& b){return std::pair{b.charge(),b.recordCount()};});
  std::cout<<"{\"receiver\":"<<(endpoint.registeredView(77)->epoch==epoch?"true":"false")<<",\"readers\":"<<endpoint.readers()<<",\"charge\":"<<physical.first<<",\"records\":"<<physical.second<<",\"oldReceipts\":"<<oldReceipts<<",\"newReceipts\":"<<newReceipts<<"}\n";
 }
 // Partial model traces leave live ownership. Close each actual GIO stream,
 // then perform the original physical fence/destroy/final delivery ACK.
 for(auto* stream:streams)if(stream){require(g_input_stream_close(stream,nullptr,nullptr),"Trace reader closes normally");g_object_unref(stream);}
 endpoint.unregisterView(77);require(endpoint.registerView(77,own,{1,2}),"Trace cleanup receiver");ReceiptDelivery cleanup(endpoint,own,77);
 for(uint64_t entry=1;entry<=2;++entry){const auto job=jobs[entry-1];endpoint.native([&](auto& b){for(const auto& r:b.inspect())if(r.entry==entry && !r.terminal){b.cancel(entry,own,job);require(b.consumerComplete(entry,job),"Trace explicit consumer fence");require(b.destroy(entry,job).status==Result::Status::Complete,"Trace physical destroy");break;}});auto proofs=endpoint.native([&](auto& b){for(const auto& r:b.inspect())if(r.entry==entry)return r.proofs;return std::vector<Receipt>{};});if(!proofs.empty())require(cleanup.acknowledge(77,"family:"+std::to_string(job.context.incarnation.value),ack(job,proofs.back().sequence.value)),"Trace exact final journal ACK");}
 require(endpoint.readers()==0 && endpoint.native([](auto& b){return b.recordCount()==0 && b.charge()==0 && b.requestFloor(1)==1 && b.requestFloor(2)==1;}),"Trace ownership and retained floors");endpoint.unregisterView(77);return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
