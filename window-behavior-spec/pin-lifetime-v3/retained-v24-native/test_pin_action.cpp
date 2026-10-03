#include "PinAction.hpp"
#include <cassert>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <vector>
using namespace PinAction;
struct Adapter {
 Snapshot s{101,1,1,1,"private-session","instance-1",11,true,true,false,false,false};
 std::vector<std::string> calls;
 std::function<void(Adapter&)> afterFloat,afterPin,afterRaise;
 bool floatOk=true,pinOk=true,raiseOk=true,floatMutates=true,pinMutates=true,throwFloat=false,throwPin=false,throwRaise=false;
 Snapshot snapshot(){return s;}
 Result floatWindow(){calls.push_back("float");if(floatMutates)s.floating=true;if(afterFloat)afterFloat(*this);if(throwFloat)throw std::runtime_error("actual float exception");return {floatOk,"float error","warning","invalid_state"};}
 Result pinWindow(bool value){calls.push_back(value?"pin":"unpin");if(pinMutates)s.pinned=value;if(afterPin)afterPin(*this);if(throwPin)throw std::runtime_error("actual pin exception");return {pinOk,"pin error","error","execution_failed"};}
 Result raiseWindow(){calls.push_back("raise");if(afterRaise)afterRaise(*this);if(throwRaise)throw std::runtime_error("actual raise exception");return {raiseOk,"raise error","error","unavailable"};}
};
int main(){
 int checks=0;
 auto check=[&](bool good){++checks;assert(good);};
 {Adapter a;auto r=execute(a);check(r.ok&&r.phase==Phase::Complete&&a.s.pinned&&a.s.floating&&a.calls==std::vector<std::string>{"float","pin","raise"});}
 {Adapter a;a.s.floating=true;auto r=execute(a);check(r.ok&&a.calls==std::vector<std::string>{"pin","raise"});}
 {Adapter a;a.s.floating=true;a.s.pinned=true;auto r=execute(a);check(r.ok&&!a.s.pinned&&a.calls==std::vector<std::string>{"unpin"});}
 for(int kind=0;kind<3;++kind){Adapter a;if(kind==0)a.s.live=false;if(kind==1)a.s.normal=false;if(kind==2)a.s.fullscreen=true;auto r=execute(a);check(!r.ok&&!r.actionsInvoked&&a.calls.empty());}
 {Adapter a;a.floatOk=false;auto r=execute(a);check(!r.ok&&r.phase==Phase::Float&&r.after.floating&&r.actionsInvoked&&a.calls.size()==1&&r.backend.code=="invalid_state");}
 {Adapter a;a.floatOk=false;a.floatMutates=false;auto r=execute(a);check(!r.ok&&!r.after.floating&&a.calls.size()==1);}
 {Adapter a;a.pinOk=false;a.pinMutates=false;auto r=execute(a);check(!r.ok&&r.phase==Phase::Pin&&a.s.floating&&!a.s.pinned&&a.calls.size()==2);}
 {Adapter a;a.pinOk=false;auto r=execute(a);check(!r.ok&&a.s.pinned&&a.calls.size()==2&&r.backend.code=="execution_failed");}
 {Adapter a;a.raiseOk=false;auto r=execute(a);check(!r.ok&&r.phase==Phase::Raise&&a.s.pinned&&a.calls.size()==3&&r.backend.code=="unavailable");}
 for(int phase=0;phase<3;++phase){for(int fault=0;fault<9;++fault){Adapter a;auto callback=[fault](Adapter&x){switch(fault){case 0:x.s.live=false;break;case 1:x.s.normal=false;break;case 2:x.s.fullscreen=true;break;case 3:++x.s.epoch;break;case 4:++x.s.lifetime;break;case 5:x.s.incarnation="reloaded";break;case 6:x.s.session="new-compositor";break;case 7:++x.s.pid;break;case 8:++x.s.stable;break;}};
  if(phase==0){a.afterFloat=callback;}
  if(phase==1){a.afterPin=callback;}
  if(phase==2){a.afterRaise=callback;}
  auto r=execute(a);check(!r.ok&&a.calls.size()==static_cast<unsigned>(phase+1)&&!r.reason.empty());
 }}
 {Adapter a;a.afterFloat=[](Adapter&x){x.s.pinned=true;};auto r=execute(a);check(!r.ok&&a.s.pinned&&a.calls.size()==1);}
 {Adapter a;a.afterFloat=[](Adapter&x){x.s.floating=false;};auto r=execute(a);check(!r.ok&&a.calls.size()==1);}
 {Adapter a;a.afterPin=[](Adapter&x){x.s.pinned=false;};auto r=execute(a);check(!r.ok&&a.calls.size()==2);}
 {Adapter a;a.afterRaise=[](Adapter&x){x.s.floating=false;};auto r=execute(a);check(!r.ok&&a.calls.size()==3&&a.s.pinned);}
 {Adapter a;a.afterRaise=[](Adapter&x){x.s.pinned=false;};auto r=execute(a);check(!r.ok&&!a.s.pinned);}
 {Adapter a;a.throwFloat=true;auto r=execute(a);check(!r.ok&&r.phase==Phase::Float&&r.after.floating&&r.backend.code=="exception");}
 {Adapter a;a.throwPin=true;auto r=execute(a);check(!r.ok&&r.phase==Phase::Pin&&r.after.pinned&&r.backend.reason=="actual pin exception");}
 {Adapter a;a.throwRaise=true;auto r=execute(a);check(!r.ok&&r.phase==Phase::Raise&&r.after.pinned);}
 {Adapter a;Adapter peer;peer.s.address=202;peer.s.stable=2;peer.s.pinned=true;peer.s.floating=true;a.afterFloat=[&](Adapter&){auto inner=execute(peer);check(inner.ok&&!peer.s.pinned);};auto r=execute(a);check(r.ok&&a.s.pinned&&!peer.s.pinned);}
 std::cout<<"{\"result\":\"pass\",\"cpuChecks\":"<<checks<<",\"nativeGuiExecuted\":false}\n";
}
