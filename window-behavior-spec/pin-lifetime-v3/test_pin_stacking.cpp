#include "native-candidate/PinStacking.hpp"
#include <cassert>
#include <iostream>
#include <stdexcept>
using namespace PinStacking;
struct CPU {
 Snapshot s;int fault=0;std::vector<Key> calls;
 explicit CPU(Snapshot value):s(std::move(value)){}
 Snapshot snapshot(){return s;}
 bool raise(Key k){calls.push_back(k);auto i=std::find_if(s.nodes.begin(),s.nodes.end(),[&](auto&n){return n.key==k;});if(i==s.nodes.end())return false;
  auto n=*i;s.nodes.erase(i);s.nodes.push_back(n);
  if(fault==1)s.epoch++;
  if(fault==2)s.focus=2;
  if(fault==3)s.nodes[0].generation++;
  if(fault==4)s.nodes[0].pinned=!s.nodes[0].pinned;
  if(fault==6)s.keyboardSurface++;
  if(fault==7)s.coreSurface++;
  if(fault==8)s.pointerSurface++;
  if(fault==9)s.keyboardResource++;
  return fault!=5;
 }
};
Snapshot base(){Snapshot s;s.epoch=1;s.focus=4;
 for(Key k:{1,3,2,4}){Node n;n.key=k;n.stable=k;n.generation=1;n.pid=100;n.workspace=11;n.monitor=22;n.eligible=true;n.floating=true;n.pinned=k==1||k==2;n.parent=k==3?1:0;n.modal=k==3;s.nodes.push_back(n);}return s;}
int main(){int checks=0;auto check=[&](bool b){++checks;assert(b);};
 CPU c{base()};auto r=enforce(c);check(r.ok);check(c.calls==std::vector<Key>({1,3,2}));check(c.s.focus==4);check(c.s.nodes.back().key==2);check(c.s.nodes[1].pinned);check(!c.s.nodes[2].pinned);
 c=CPU(base());c.raise(1);c.raise(3);c.calls.clear();r=enforce(c);check(r.ok);check(c.calls==std::vector<Key>({2,1,3}));
 for(int f=1;f<=9;++f){c=CPU(base());c.fault=f;r=enforce(c);check(!r.ok&&r.actionsInvoked);check(c.calls.size()==1);}
 c=CPU(base());c.s.nodes[0].parent=3;check(!makePlan(c.s).ok);
 c=CPU(base());c.s.nodes.push_back(c.s.nodes[0]);check(!makePlan(c.s).ok);
 c=CPU(base());c.s.nodes[0].generation=0;check(!makePlan(c.s).ok);
 c=CPU(base());c.s.epoch=0;check(!makePlan(c.s).ok);
 c=CPU(base());c.s.nodes[0].eligible=false;r=enforce(c);check(r.ok);check(r.plan.protectedKeys==std::set<Key>({2}));check(c.calls==std::vector<Key>({2}));
 c=CPU(base());c.s.nodes[1].modal=false;r=enforce(c);check(r.ok);check(r.plan.protectedKeys==std::set<Key>({1,2}));
 c=CPU(base());c.s.nodes[0].x11=true;c.s.nodes[1].x11=true;c.s.nodes[1].modal=false;r=enforce(c);check(r.ok);check(r.plan.protectedKeys.contains(3));
 c=CPU(base());c.s.nodes[1].workspace=12;r=enforce(c);check(r.ok);check(!r.plan.protectedKeys.contains(3));
 c=CPU(base());c.s.nodes[0].fullscreen=true;r=enforce(c);check(r.ok);check(!r.plan.protectedKeys.contains(1));
 c=CPU(base());r=enforce(c);c.calls.clear();r=enforce(c);check(r.ok&&c.calls.empty());
 c=CPU(base());c.s.nodes[0].pinned=false;c.s.nodes[2].pinned=false;r=enforce(c);check(r.ok&&c.calls.empty());
 c=CPU(base());auto captured=c.s;std::reverse(c.s.nodes.begin(),c.s.nodes.end());check(contextSame(captured,c.s));c.s.nodes[0].geometry[0]=1;check(!contextSame(captured,c.s));
 std::cout<<checks<<" pin stacking CPU assertions PASS\n";
}
