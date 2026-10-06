#include "imported_lifecycle.hpp"
#include "imported_enrollment.hpp"
#include <iostream>
using namespace preview;using namespace preview::bridge;
static Scope scope(uint64_t entry,uint64_t now){return {{{1},{2},{3}},{{1},{entry+10},{5},{6},{7},{8},{1}},{10},now,true,true,false,true};}
static const char* admission(ImportedIntentLedger::Admission a){using A=ImportedIntentLedger::Admission;switch(a){case A::Conflict:return "Conflict";case A::Expired:return "Expired";case A::Invalid:return "Invalid";case A::Capacity:return "Capacity";case A::Admitted:return "Admitted";}throw std::runtime_error("Typed intent");}
int main(){try{
 const auto own=scope(1,1).binding;uri::Endpoint endpoint({3,8,2,64},2,1,[](uint64_t)->std::optional<uri::NativeTime>{return uri::NativeTime{{10},4};});require(endpoint.enableDemand({{3,8,2,64},{1},{10},1}),"Own shared resume queue");auto& queue=*endpoint.nativeDemand([](auto& q){return &q;});std::array<Job,3> jobs;
 for(uint64_t entry=1;entry<=3;++entry){require(queue.observe({entry,1,scope(entry,entry),{1},32,true}).accepted,"Own observation");auto attempt=queue.start(entry,100);require(attempt.job.has_value(),"Owned job");jobs[entry-1]=*attempt.job;if(entry==1){auto proof=queue.nativeBroker().producerRefused(entry,jobs[0]);require(queue.nativeBroker().acknowledge(entry,own,jobs[0],proof.receipts.back().sequence),"Old exact ACK before resume");}}
 require(endpoint.registerView(77,own,{1,2,3}),"Original receiver");const auto epoch=endpoint.registeredView(77)->epoch;
 SourceObservation previous{scope(1,1),1,32,1,SourceObservation::Kind::UnqualifiedClientMain,false};std::optional<NativeStartIdentity> intent;uint64_t now=4,queries=0;bool known=false,fault=false;std::string status="Ready",event;
 while(std::getline(std::cin,event)){
  if(event=="Retry" || event=="ChangeStamp")endpoint.nativeDemandView(77,[&](auto& q,uri::View* view){if(!importedReceiver(view,own,epoch)){status="ReceiverRejected";return;}++queries;SourceObservation fresh{scope(1,now),queries+1,32,queries+1,SourceObservation::Kind::UnqualifiedClientMain,false};auto result=reserveImportedResumeAttempt(q,1,jobs[0],previous,1,fresh,event=="ChangeStamp"?3:2,2,intent);status=admission(result.intent);if(result.intent==ImportedIntentLedger::Admission::Admitted){switch(result.native.status){case demand::Attempt::Status::Started:status="Started";break;case demand::Attempt::Status::Capacity:status="Capacity";break;case demand::Attempt::Status::NativeRejected:status="NativeRejected";break;default:throw std::runtime_error("Unexpected typed resume");}known=result.native.status==demand::Attempt::Status::Started;}});
  else if(event=="Expire"){now=2000000005ULL;status="ClockAdvanced";}
  else if(event=="Drain"){auto proof=queue.nativeBroker().producerRefused(3,jobs[2]);require(queue.nativeBroker().acknowledge(3,own,jobs[2],proof.receipts.back().sequence),"Exact unrelated physical proof ACK");status="CapacityReturned";}
  else if(event=="ReplaceReceiver"){auto view=*endpoint.registeredView(77);endpoint.unregisterView(77);require(endpoint.registerView(77,own,view.entries),"Actual replaced epoch");status="ReceiverReplaced";}
  else if(event=="RejectNative"){auto wrong=queue.nativeBroker().nativeScope(1);wrong.context.privacy={1};require(!queue.nativeBroker().observe(1,wrong,32),"Actual incoherence retained");fault=true;status="Incoherent";}
  else throw std::runtime_error("Explicit model event");
  auto& broker=queue.nativeBroker();std::cout<<"{\"now\":"<<now<<",\"deadline\":"<<(intent?intent->deadline:0)<<",\"free\":"<<(broker.activeItems()<2?"true":"false")<<",\"records\":"<<broker.recordCount()<<",\"charge\":"<<broker.charge()<<",\"floor\":"<<broker.requestFloor(1)<<",\"receiver\":"<<(endpoint.registeredView(77)->epoch==epoch?"true":"false")<<",\"status\":\""<<status<<"\",\"known\":"<<(known?"true":"false")<<",\"fault\":"<<(fault?"true":"false")<<",\"queries\":"<<queries<<"}\n";
 }
 for(const auto& row:queue.nativeBroker().inspect()){auto proof=row.terminal?Result{}:queue.nativeBroker().producerRefused(row.entry,row.job);const auto sequence=row.terminal?row.proofs.back().sequence:proof.receipts.back().sequence;require(queue.nativeBroker().acknowledge(row.entry,own,row.job,sequence),"Exact remaining proof/ACK");}
 require(queue.nativeBroker().recordCount()==0 && queue.nativeBroker().charge()==0 && queue.nativeBroker().requestFloor(1)==(known?2:1),"Cleanup retains original floor");return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
