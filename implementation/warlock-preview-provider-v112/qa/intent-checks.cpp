#include "imported_admission.hpp"
#include <iostream>
using namespace preview;using namespace preview::bridge;
static void check(bool ok,const char* name){if(!ok)throw std::runtime_error(name);}
static Scope scope(uint64_t entry,uint64_t now){return {{{1},{2},{3}},{{1},{entry+10},{5},{6},{7},{8},{1}},{10},now,true,true,false,true};}
static const char* admission(ImportedIntentLedger::Admission result){using A=ImportedIntentLedger::Admission;switch(result){case A::Admitted:return "Admitted";case A::Capacity:return "Capacity";case A::Conflict:return "Conflict";case A::Expired:return "Expired";case A::Invalid:return "Invalid";}throw std::runtime_error("Typed native intent outcome");}
int main(){try{
 demand::Coordinator queue({{3,8,2,64},{1},{10},1});const auto own=scope(1,1).binding;ImportedIntentLedger ledger(own,3);NativeStartIdentity original{own,{13},{10},1,1,20};
 check(ledger.remember(3,original,3)==ImportedIntentLedger::Admission::Admitted,"Own initial intent");std::array<Job,2> jobs;
 for(uint64_t entry=1;entry<=2;++entry){check(queue.observe({entry,1,scope(entry,entry),{1},32,true}).accepted,"Own original allocator scope");auto started=queue.start(entry,100);check(started.status==demand::Attempt::Status::Started && started.job.has_value(),"Original native reservation");jobs[entry-1]=*started.job;}
 check(queue.observe({3,1,scope(3,3),{1},32,true}).accepted,"Actual own third scope");std::string status="Admitted",event;
 while(std::getline(std::cin,event)){
  if(event=="Retry"){
   auto decision=ledger.remember(3,original,queue.now());status=admission(decision);
   if(decision==ImportedIntentLedger::Admission::Admitted){auto attempt=queue.start(3,ledger.original(3).deadline);switch(attempt.status){case demand::Attempt::Status::Started:check(attempt.job && attempt.job->deadline==20 && attempt.job->request.value==1,"Original actual third job");status="Started";break;case demand::Attempt::Status::Capacity:check(!attempt.job && attempt.native.receipts.empty(),"No fake job or terminal receipt on capacity");status="Capacity";break;case demand::Attempt::Status::NotReady:status="NotReady";break;default:check(false,"Unexpected actual native attempt");}}
  }else if(event=="Renew" || event=="ChangeStamp" || event=="Foreign"){
   auto modified=original;if(event=="Renew")modified.deadline=40;else if(event=="ChangeStamp")modified.publication=2;else modified.binding.session={999};status=admission(ledger.remember(3,modified,queue.now()));
  }else if(event=="Expire"){
   check(queue.observe({3,1,scope(3,21),{1},32,true}).accepted,"Actual native clock advance");status="ClockAdvanced";
  }else if(event=="Drain"){
   auto proof=queue.nativeBroker().producerRefused(1,jobs[0]);check(proof.receipts.size()==1 && queue.nativeBroker().acknowledge(1,own,jobs[0],proof.receipts.back().sequence),"Original actual producer settlement and exact final ACK");status="CapacityReturned";
  }else check(false,"Explicitly selected model event");
  auto& broker=queue.nativeBroker();std::cout<<"{\"now\":"<<queue.now()<<",\"free\":"<<(broker.activeItems()<2?"true":"false")<<",\"issued\":"<<(broker.requestFloor(3)==1?"true":"false")<<",\"status\":\""<<status<<"\",\"deadline\":"<<ledger.original(3).deadline<<",\"charge\":"<<broker.charge()<<",\"records\":"<<broker.recordCount()<<"}\n";
 }
 // Synthetic native producer fixture has only actual reserved jobs, no pixels.
 // Every remaining reservation needs an explicit original terminal proof/ACK.
 const auto remaining=queue.nativeBroker().inspect();for(const auto& record:remaining){auto proof=queue.nativeBroker().producerRefused(record.entry,record.job);check(!proof.receipts.empty() && queue.nativeBroker().acknowledge(record.entry,own,record.job,proof.receipts.back().sequence),"Trace exact original producer proof and final ACK");}
 check(queue.nativeBroker().charge()==0 && queue.nativeBroker().recordCount()==0 && queue.nativeBroker().requestFloor(1)==1 && queue.nativeBroker().requestFloor(2)==1 && ledger.original(3)==original,"Trace cleanup preserves native floors and original intent");return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
