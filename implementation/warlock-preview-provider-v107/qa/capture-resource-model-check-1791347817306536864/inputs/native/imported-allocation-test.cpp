#include "client_import.hpp"
#include <cstdlib>
#include <iostream>
#include <new>
static thread_local int allocationFault=-1;
[[gnu::noinline]] void* operator new(std::size_t size){if(allocationFault>0 && --allocationFault==0){allocationFault=-1;throw std::bad_alloc();}if(auto p=std::malloc(size?size:1))return p;throw std::bad_alloc();}
[[gnu::noinline]] void operator delete(void* p)noexcept{std::free(p);}
[[gnu::noinline]] void operator delete(void* p,std::size_t)noexcept{std::free(p);}
using namespace preview;using namespace preview::bridge;
static unsigned checks=0;
static void check(bool value,const char* name){require(value,name);++checks;}
static fd::Header header(const ClientCapture& c){
 fd::Header h{};h[fd::Magic]=fd::MAGIC;h[fd::Version]=1;h[fd::Lifetime]=c.binding.lifetime.value;h[fd::Session]=c.binding.session.value;h[fd::Frontend]=c.binding.frontend.value;
 h[fd::Request]=c.request+1;h[fd::Capture]=c.request;h[fd::Subject]=c.context.incarnation.value;h[fd::Output]=c.context.output.value;
 h[fd::Completed]=c.completed;h[fd::Now]=c.completed+1;h[fd::Width]=c.width;h[fd::Height]=c.height;h[fd::Bytes]=c.bytes;h[fd::Charge]=4096;h[fd::Transfer]=12;
 h[fd::Privacy]=c.context.privacy.value;h[fd::Rendering]=c.context.rendering.value;h[fd::Scene]=c.context.scene.value;h[fd::Content]=c.context.content.value;h[fd::Flags]=11;h[fd::Deadline]=c.deadline;h[fd::Expires]=500;return h;
}
int main(){try{
 for(int scenario:{0,1,2,3}){
  Scope scope{{{1},{2},{3}},{{1},{4},{5},{6},{7},{8},{9}},{1},102,true,true,false,true};Job job{scope.binding,scope.context,{1},{1},scope.clock,200};Broker broker({2,8,2,4096});
  check(broker.enroll(1,scope,4096) && broker.acquire(1,job.binding,job).status==Result::Status::Admitted,"Original actual Broker reservation");
  ClientCapture capture{job.binding,job.context,10,100,200,1,1,16,4096,0};auto h=header(capture);
  const std::array<uint8_t,16> png{137,80,78,71,13,10,26,10,1,2,3,4,5,6,7,8};auto mapping=std::make_unique<fd::Mapped>(fd::seal(png),h,4096,fd::SourcePlane::ClientMain);
  auto candidate=mapping.get();std::unique_ptr<const Buffer> payload=std::move(mapping);fd::Mapped* retained=nullptr;bool threw=false;
  allocationFault=scenario==1?1:scenario==2?2:-1;
  try{allocateImportedMapping(broker,1,job,payload,candidate,retained,scenario==3?scope.now:500);}catch(const std::bad_alloc&){threw=true;}
  allocationFault=-1;
  if(scenario==0)check(!threw && !payload && retained==candidate,"Successful actual adoption publishes exact native mapping");
  if(scenario==1)check(threw && payload && !retained,"Pre-transfer allocation exception cannot retain caller mapping");
  if(scenario==2)check(threw && !payload && retained==candidate && broker.inspect().front().packet.has_value(),"Post-transfer receipt allocation exception retains actual Broker mapping");
  if(scenario==3)check(!threw && payload && !retained && !broker.inspect().front().packet,"Refused actual adoption cannot publish dangling caller mapping");
  check(broker.charge()==4096 && broker.recordCount()==1,"Exception or refusal never erases original native reservation");broker.cancel(1,job.binding,job);
  if(retained){broker.producerComplete(1,job);check(broker.consumerComplete(1,job) && retained->close() && retained->png().empty(),"Actual adopted mmap/FD drains before original native terminal proof");check(broker.destroy(1,job).status==Result::Status::Complete,"Actual adopted buffer reaches original terminal proof");}
  else{payload.reset();check(broker.producerRefused(1,job).status==Result::Status::Complete,"Unadopted local FD closes before original refused/cancelled proof");}
  auto rows=broker.inspect();check(rows.front().terminal && broker.charge()==0 && broker.acknowledge(1,job.binding,job,rows.front().proofs.back().sequence) && !broker.recordCount(),"Only actual final acknowledgment clears original Broker record");
 }
 std::cout<<"{\"passed\":true,\"checks\":"<<checks<<",\"allocationCases\":4,\"nativeAcceptance\":false}\n";return 0;
}catch(const std::exception& exception){allocationFault=-1;std::cerr<<exception.what()<<'\n';return 1;}}
