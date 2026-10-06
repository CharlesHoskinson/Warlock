#include "imported_admission.hpp"
#include <iostream>
using namespace preview;using namespace preview::bridge;
static void check(bool value,const char* name){if(!value)throw std::runtime_error(name);}
static Scope scope(uint64_t entry,uint64_t now){return {{{1},{2},{3}},{{1},{entry+10},{5},{6},{7},{8},{1}},{10},now,true,true,false,true};}
static const char* name(ImportedIntentLedger::Admission a){using A=ImportedIntentLedger::Admission;switch(a){case A::Admitted:return "Admitted";case A::Conflict:return "Conflict";case A::Expired:return "Expired";case A::Invalid:return "Invalid";case A::Capacity:return "Capacity";}throw std::runtime_error("Typed admission");}
int main(){try{
 demand::Coordinator queue({{3,8,2,64},{1},{10},1});const auto own=scope(1,1).binding;ImportedIntentLedger ledger(own,3);
 NativeStartIdentity current{own,{13},{10},1,1,20};
 check(ledger.remember(3,current,3)==ImportedIntentLedger::Admission::Admitted,"Initial own intent");
 std::array<Job,2> jobs;
 for(uint64_t entry=1;entry<=2;++entry){check(queue.observe({entry,1,scope(entry,entry),{1},32,true}).accepted,"Original scope");auto result=queue.start(entry,10000);check(result.job.has_value(),"Original actual job");jobs[entry-1]=*result.job;}
 check(queue.observe({3,1,scope(3,3),{1},32,true}).accepted,"Original unissued actor");std::string status="Admitted",event;
 while(std::getline(std::cin,event)){
  current=ledger.original(3);
  if(event=="Retry"){
   auto decision=ledger.remember(3,current,queue.now());status=name(decision);
   if(decision==ImportedIntentLedger::Admission::Admitted){auto result=queue.start(3,current.deadline);
    if(result.status==demand::Attempt::Status::Started){check(result.job && result.job->deadline==current.deadline && result.job->request.value==1,"Actual first successor job");status="Started";}
    else{check(result.status==demand::Attempt::Status::Capacity && !result.job && result.native.receipts.empty(),"Local capacity has no fabricated job or proof");status="Capacity";}
   }
  }else if(event=="Expire"){
   check(queue.observe({3,current.lease,scope(3,current.deadline+1),{current.lease},32,true}).accepted,"Actual native clock observation");status="ClockAdvanced";
  }else if(event=="Drain"){
   auto result=queue.nativeBroker().producerRefused(1,jobs[0]);check(result.receipts.size()==1 && queue.nativeBroker().acknowledge(1,own,jobs[0],result.receipts.back().sequence),"Original exact settlement");status="CapacityReturned";
  }else if(event=="Renew"){
   auto proposed=current;proposed.deadline++;status=name(ledger.remember(3,proposed,queue.now()));
  }else{
   auto proposed=current;proposed.publication++;proposed.lease++;proposed.deadline=queue.now()+20;
   if(event=="OldStamp"){proposed.publication=current.publication;proposed.lease=current.lease;}
   else if(event=="Partial")proposed.lease=current.lease;
   else if(event=="Foreign")proposed.binding.session={999};
   else if(event=="WrongClock")proposed.clock={999};
   else check(event=="Advance","Explicit model event");
   auto decision=ledger.advance(3,proposed,queue.now());status=name(decision);
   if(decision==ImportedIntentLedger::Admission::Admitted)check(queue.observe({3,proposed.lease,scope(3,queue.now()),{proposed.lease},32,true}).accepted,"New exact intent scope");
  }
  const auto active=ledger.original(3);const auto previous=ledger.predecessor(3);auto& broker=queue.nativeBroker();
  check(ledger.size()==1 && ledger.predecessorCount()<=1,"Bounded retained intent history");
  std::cout<<"{\"now\":"<<queue.now()<<",\"deadline\":"<<active.deadline<<",\"publication\":"<<active.publication<<",\"lease\":"<<active.lease<<",\"previous\":"<<(previous?previous->deadline:0)<<",\"free\":"<<(broker.activeItems()<2?"true":"false")<<",\"issued\":"<<(broker.requestFloor(3)==1?"true":"false")<<",\"status\":\""<<status<<"\",\"charge\":"<<broker.charge()<<",\"records\":"<<broker.recordCount()<<"}\n";
 }
 for(const auto& row:queue.nativeBroker().inspect()){auto result=queue.nativeBroker().producerRefused(row.entry,row.job);check(!result.receipts.empty() && queue.nativeBroker().acknowledge(row.entry,own,row.job,result.receipts.back().sequence),"Exact terminal cleanup");}
 check(queue.nativeBroker().recordCount()==0 && queue.nativeBroker().charge()==0 && queue.nativeBroker().requestFloor(1)==1 && queue.nativeBroker().requestFloor(2)==1,"Cleanup preserves original request floors");return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
