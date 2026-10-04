#include <array>
#include <chrono>
#include <functional>
#include <iostream>
#include <unordered_map>
#include <vector>
#include <hyprutils/memory/SharedPtr.hpp>
#include <hyprutils/memory/WeakPtr.hpp>
#include <hyprutils/signal/Signal.hpp>
#include "NestedPresentation.hpp"
using namespace Hyprutils::Memory;
#define SP CSharedPointer
namespace Aquamarine {
struct IPointer {struct SButtonEvent {uint32_t timeMs=0,button=0;bool pressed=false;};};
struct CWaylandPointer {
 struct {Hyprutils::Signal::CSignalT<IPointer::SButtonEvent> button;Hyprutils::Signal::CSignalT<> frame;} events;
 ~CWaylandPointer();
};
}
using namespace Aquamarine;
static std::unordered_map<CWaylandPointer*,NestedPolicy::BalancedButtons> pointerButtons;
static std::unordered_map<CWaylandPointer*,int> parentPointerPosition;
Aquamarine::CWaylandPointer::~CWaylandPointer() {
    pointerButtons.erase(this);
    parentPointerPosition.erase(this);
}

static void cancelHeldParentButtons(const std::vector<SP<CWaylandPointer>>& pointers) {
    const auto retiring = pointers;
    const auto now = static_cast<uint32_t>(std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::steady_clock::now().time_since_epoch()).count());
    for (const auto& pointer : retiring) {
        const auto state = pointerButtons.find(pointer.get());
        if (state == pointerButtons.end()) continue;
        const auto held = state->second.held;
        state->second.held.fill(0);
        bool emitted = false;
        for (const auto button : held) {
            if (!button) continue;
            (void)now;
            emitted = true;
        }
        if (emitted) pointer->events.frame.emit();
    }
}

int checks=0;
void check(bool yes,const char* label){++checks;if(!yes){std::cerr<<"FAIL "<<label<<'\n';throw 1;}}
int main(){
 try {
  for(unsigned mask=0;mask<8;++mask){
   auto p=makeShared<CWaylandPointer>();std::vector<SP<CWaylandPointer>> pointers{p};
   std::vector<uint32_t> expected,seen;int frames=0;
   for(unsigned i=0;i<3;++i)if(mask&(1u<<i)){check(pointerButtons[p.get()].admit(272+i,true,true),"setup admitted real press");expected.push_back(272+i);}
   const auto stateBefore=pointerButtons.size();
   auto button=p->events.button.listen([&](const IPointer::SButtonEvent& e){
    check(!e.pressed,"no synthesized press");check(e.timeMs>0,"cancellation timestamp");
    check(pointerButtons.at(p.get()).held==std::array<uint32_t,32>{},"clear before callback");seen.push_back(e.button);
   });
   auto frame=p->events.frame.listen([&]{++frames;});
   cancelHeldParentButtons(pointers);check(seen==expected,"only admitted held buttons cancelled");
   check(frames==(mask?1:0),"one frame for cancellation batch");
   cancelHeldParentButtons(pointers);check(seen==expected&&frames==(mask?1:0),"repeat cancellation silent");
   check(pointerButtons.size()==stateBefore,"untracked pointer inserts no state");
  }
  {
   auto p=makeShared<CWaylandPointer>();std::vector<SP<CWaylandPointer>> pointers{p};
   pointerButtons[p.get()].admit(272,true,true);pointerButtons[p.get()].admit(273,true,true);pointerButtons[p.get()].admit(272,false,false);
   std::vector<uint32_t> seen;auto listener=p->events.button.listen([&](const IPointer::SButtonEvent& e){seen.push_back(e.button);});
   cancelHeldParentButtons(pointers);check(seen==std::vector<uint32_t>{273},"already released button excluded");
  }
  {
   auto p=makeShared<CWaylandPointer>();std::vector<SP<CWaylandPointer>> pointers{p};pointerButtons[p.get()].admit(272,true,true);
   int calls=0,depth=0;auto listener=p->events.button.listen([&](const IPointer::SButtonEvent&){++calls;if(!depth){++depth;cancelHeldParentButtons(pointers);--depth;}});
   cancelHeldParentButtons(pointers);check(calls==1,"reentrant cancellation cannot replay");
  }
  {
   auto first=makeShared<CWaylandPointer>(),second=makeShared<CWaylandPointer>();
   std::vector<SP<CWaylandPointer>> pointers{first,second};CWeakPointer<CWaylandPointer> w1=first,w2=second;
   pointerButtons[first.get()].admit(272,true,true);pointerButtons[second.get()].admit(273,true,true);
   int calls=0,frames=0;
   auto one=first->events.button.listen([&](const IPointer::SButtonEvent&){++calls;pointers.clear();check(!w1.expired()&&!w2.expired(),"snapshot retains devices during removal");});
   auto two=second->events.button.listen([&](const IPointer::SButtonEvent&){++calls;});
   auto frame1=first->events.frame.listen([&]{++frames;});auto frame2=second->events.frame.listen([&]{++frames;});
   first.reset();second.reset();cancelHeldParentButtons(pointers);
   check(calls==2&&frames==2,"snapshot completes both cancellation batches");
   check(w1.expired()&&w2.expired(),"snapshot releases retired devices");
  }
  {
   auto p=makeShared<CWaylandPointer>();std::vector<SP<CWaylandPointer>> pointers{p};
   for(unsigned b=1;b<=32;++b)check(pointerButtons[p.get()].admit(b,true,true),"bounded held slot accepted");
   check(!pointerButtons[p.get()].admit(33,true,true),"overflow cannot invent tracked press");
   int count=0;auto listener=p->events.button.listen([&](const IPointer::SButtonEvent& e){check(e.button>=1&&e.button<=32&&!e.pressed,"bounded cancel event identity");++count;});
   cancelHeldParentButtons(pointers);check(count==32,"all bounded held slots cancelled");
  }
  check(pointerButtons.empty()&&parentPointerPosition.empty(),"normal pointer teardown clears private state");
  std::cout<<"checks: "<<checks<<'\n';return 0;
 }catch(...){return 1;}
}
