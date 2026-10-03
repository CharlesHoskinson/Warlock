#include "native-candidate/PinBoundary.hpp"
#include <cassert>
#include <iostream>
struct Mock {
 PinAction::Snapshot s;bool invoked=false,refuseFloat=false;PinAction::Phase phase=PinAction::Phase::Validate;int count=0,throwAt=0;
 PinAction::Snapshot snapshot(){if(++count==throwAt)throw std::runtime_error("Actual injected snapshot callback failure");return s;}
 PinAction::Result floatWindow(){if(refuseFloat)return {false,"Captured focus changed before native call","error","focus"};invoked=true;phase=PinAction::Phase::Float;s.floating=true;return {true,{},{},{}};}
 PinAction::Result pinWindow(bool desired){invoked=true;phase=PinAction::Phase::Pin;s.pinned=desired;return {true,{},{},{}};}
 PinAction::Result raiseWindow(){invoked=true;phase=PinAction::Phase::Raise;return {true,{},{},{}};}
};
int main(){int checks=0;auto check=[&](bool v){++checks;assert(v);};
 PinAction::Snapshot s;s.address=1;s.stable=1;s.pid=11;s.epoch=1;s.lifetime=1;s.session="private";s.incarnation="actual";s.live=true;s.normal=true;
 for(int i=1;i<=7;++i){Mock m;m.s=s;m.throwAt=i;auto r=PinAction::executeConservative(m,s);check(!r.ok);check(r.actionsInvoked==(i>1));check(r.before.address==1);check(r.after.address==1);check(r.phase==(i==1?PinAction::Phase::Validate:i<=3?PinAction::Phase::Float:i<=5?PinAction::Phase::Pin:PinAction::Phase::Raise));}
 Mock m;m.s=s;auto r=PinAction::executeConservative(m,s);check(r.ok&&r.actionsInvoked&&r.after.pinned);
 Mock pre;pre.s=s;pre.refuseFloat=true;auto refused=PinAction::executeConservative(pre,s);check(!refused.ok);check(!refused.actionsInvoked);check(refused.phase==PinAction::Phase::Validate);check(!pre.s.floating&&!pre.s.pinned);
 std::cout<<checks<<" native exception boundary CPU assertions PASS\n";
}
