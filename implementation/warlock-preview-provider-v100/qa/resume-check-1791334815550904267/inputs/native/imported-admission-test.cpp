#include "imported_admission.hpp"
#include <iostream>
using namespace preview;using namespace preview::bridge;
static unsigned checks=0;
static void check(bool ok,const char* name){if(!ok)throw std::runtime_error(name);++checks;}
template<class F>static bool denied(F f){try{f();return false;}catch(const std::exception&){return true;}}
static Scope scope(uint64_t entry,uint64_t now){return {{{1},{2},{3}},{{1},{entry+10},{5},{6},{7},{8},{1}},{10},now,true,true,false,true};}
int main(){try{
 using Admission=ImportedIntentLedger::Admission;const auto own=scope(1,1).binding;
 check(denied([&]{ImportedIntentLedger invalid(own,0);}) && denied([&]{ImportedIntentLedger invalid(own,257);}),"Intent inventory rejects invalid limits");
 auto foreign=own;foreign.session={999};ImportedIntentLedger ledger(own,3);NativeStartIdentity original{own,{13},{10},1,1,20};
 check(ledger.remember(3,original,1)==Admission::Admitted && ledger.original(3)==original && ledger.size()==1,"Actual immutable own unissued native intent retained");
 check(ledger.remember(3,original,2)==Admission::Admitted && ledger.original(3).deadline==20,"Retry retains original deadline despite newer native clock");
 auto changed=original;changed.deadline=40;check(ledger.remember(3,changed,2)==Admission::Conflict,"Capacity retry cannot renew original deadline");
 changed=original;changed.publication=2;check(ledger.remember(3,changed,2)==Admission::Conflict,"Changed original publication refuses");
 changed=original;changed.lease=2;check(ledger.remember(3,changed,2)==Admission::Conflict,"Changed original input lease refuses");
 changed=original;changed.subject={14};check(ledger.remember(3,changed,2)==Admission::Conflict,"Changed native incarnation refuses");
 changed=original;changed.clock={11};check(ledger.remember(3,changed,2)==Admission::Conflict,"Original native clock domain retained");
 changed=original;changed.binding=foreign;check(ledger.remember(3,changed,2)==Admission::Invalid,"Foreign native binding has no intent authority");
 check(ledger.remember(4,original,2)==Admission::Conflict && ledger.size()==1,"Same native subject cannot alias another actor");
 check(ledger.remember(3,original,20)==Admission::Expired && ledger.original(3)==original,"Expired unissued work retains original identity without fresh deadline");
 check(ledger.remember(0,original,1)==Admission::Invalid && ledger.remember(3,original,0)==Admission::Invalid,"Zero native actor or clock observation refused");
 NativeStartIdentity second{own,{12},{10},1,1,100},first{own,{11},{10},1,1,100};check(ledger.remember(1,first,1)==Admission::Admitted && ledger.remember(2,second,1)==Admission::Admitted,"Distinct bounded native intent identities");
 NativeStartIdentity fourth{own,{14},{10},1,1,100};check(ledger.remember(4,fourth,1)==Admission::Capacity && ledger.size()==3,"Retained inventory capacity does not erase original history");
 demand::Coordinator queue({{3,8,2,64},{1},{10},1});
 check(queue.observe({1,1,scope(1,1),{1},32,true}).accepted,"First real allocator scope");auto a=queue.start(1,100);check(a.status==demand::Attempt::Status::Started && a.job.has_value(),"First exact native job reservation");
 check(queue.observe({2,1,scope(2,2),{1},32,true}).accepted,"Second real allocator scope");auto b=queue.start(2,100);check(b.status==demand::Attempt::Status::Started && b.job.has_value(),"Second exact native job reservation");
 check(queue.observe({3,1,scope(3,3),{1},32,true}).accepted,"Third genuine scope observation");auto waiting=queue.start(3,ledger.original(3).deadline);
 check(waiting.status==demand::Attempt::Status::Capacity && !waiting.job && waiting.native.receipts.empty() && queue.nativeBroker().requestFloor(3)==0,"Physical capacity feedback has no fabricated job/proof or request-floor advance");
 check(queue.nativeBroker().activeItems()==2 && queue.nativeBroker().charge()==64 && queue.nativeBroker().recordCount()==2,"Waiting intent does not evict original reservations or erase charges");
 auto terminal=queue.nativeBroker().producerRefused(1,*a.job);check(terminal.receipts.size()==1 && queue.nativeBroker().acknowledge(1,own,*a.job,terminal.receipts.back().sequence),"Actual first producer proof and exact ACK return capacity");
 check(queue.observe({3,1,scope(3,21),{1},32,true}).accepted,"Actual later clock after capacity returns");auto late=queue.start(3,ledger.original(3).deadline);
 check(late.status==demand::Attempt::Status::NotReady && !late.job && late.native.receipts.empty() && queue.nativeBroker().requestFloor(3)==0,"Returned capacity cannot revive expired original intent");
 changed=original;changed.deadline=40;check(ledger.remember(3,changed,21)==Admission::Conflict && ledger.original(3).deadline==20,"Late retry cannot replace original unissued deadline");
 auto secondTerminal=queue.nativeBroker().producerRefused(2,*b.job);check(queue.nativeBroker().acknowledge(2,own,*b.job,secondTerminal.receipts.back().sequence),"Second exact original proof settles reservation");
 check(queue.nativeBroker().charge()==0 && queue.nativeBroker().recordCount()==0 && queue.nativeBroker().requestFloor(1)==1 && queue.nativeBroker().requestFloor(2)==1 && queue.nativeBroker().requestFloor(3)==0 && ledger.size()==3,"Allocator drains while original actor floors and intent history remain");
 std::cout<<"{\"passed\":true,\"checks\":"<<checks<<",\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
