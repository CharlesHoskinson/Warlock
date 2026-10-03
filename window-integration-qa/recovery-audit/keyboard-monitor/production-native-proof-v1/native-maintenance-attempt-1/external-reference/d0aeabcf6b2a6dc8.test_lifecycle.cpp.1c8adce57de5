#include "candidate/src/backend/NestedLifecycle.hpp"
#include <cassert>
#include <iostream>
#include <climits>
int main() {
 using namespace Aquamarine::NestedPolicy;
 assert(selection(nullptr)==Selection::Unspecified);
 assert(selection("wayland")==Selection::Wayland);
 for (const char* value : {"", "drm", "headless", "WAYLAND", "wayland,drm", "wayland "}) assert(selection(value)==Selection::Invalid);
 ConfigureLifecycle state;
 assert(!state.bufferAllowed()); assert(!state.announce());
 state.stageSize(320,240); assert(state.width==320&&state.height==240); assert(!state.bufferAllowed());
 assert(state.acknowledge()); assert(!state.bufferAllowed());
 assert(state.announce()); assert(state.bufferAllowed()); assert(!state.announce());
 state.stageSize(480,360); assert(state.acknowledge()); assert(!state.announce()); assert(state.bufferAllowed());
 assert(state.width==480&&state.height==360);
 state.destroy(); assert(!state.acknowledge()); assert(!state.announce()); assert(!state.bufferAllowed());
 state.stageSize(1,1); assert(state.width==480&&state.height==360);
 ConfigureLifecycle dead; dead.destroy(); assert(!dead.acknowledge()); assert(!dead.announce());
 ConfigureLifecycle fallback; fallback.stageSize(0,0); assert(fallback.width==1280&&fallback.height==720);
 // Boundary sizes are staged without authorizing state/frame/buffer delivery.
 for (const auto& [w,h] : {std::pair{1,1},std::pair{INT_MAX,INT_MAX},std::pair{-1,240},std::pair{320,-1},std::pair{0,0}}) {
   ConfigureLifecycle staged; staged.stageSize(w,h);
   assert(staged.width==(w>0?w:1280)&&staged.height==(h>0?h:720));
   assert(!staged.acknowledged&&!staged.announced&&!staged.bufferAllowed());
 }
 // Destruction between ACK and its deferred callback cannot announce/revive.
 ConfigureLifecycle queued; assert(queued.acknowledge());queued.destroy();
 assert(!queued.announce()&&!queued.bufferAllowed());
 // A synchronous state listener can destroy an announced output. The same
 // helper predicate must then deny both the relay's frame and buffer request.
 ConfigureLifecycle reentrant;assert(reentrant.acknowledge());assert(reentrant.announce());
 assert(reentrant.bufferAllowed());reentrant.destroy();assert(!reentrant.bufferAllowed());
 // Actual parent-loss source wiring destroys each output lifecycle; independent
 // outputs retain their own state until that invalidation reaches them.
 ConfigureLifecycle one,two;assert(one.acknowledge()&&one.announce());assert(two.acknowledge()&&two.announce());
 one.destroy();assert(!one.bufferAllowed()&&two.bufferAllowed());two.destroy();assert(!two.bufferAllowed());
 // Exhaustive six-event sequences (46,656) check the real helper, including destruction/reconfigure.
 for (unsigned trace=0;trace<46656;trace++) {
   unsigned actions=trace; ConfigureLifecycle actual; bool ack=false,published=false,destroyed=false;
   for(int step=0;step<6;step++) {
     unsigned event=actions%6; actions/=6;
     if(event==0) actual.stageSize(step+1,step+2);
     if(event==1) {assert(actual.acknowledge()==!destroyed);if(!destroyed)ack=true;}
     if(event==2) {bool allowed=ack&&!published&&!destroyed;assert(actual.announce()==allowed);if(allowed)published=true;}
     if(event==3||event==4) assert(actual.bufferAllowed()==(ack&&published&&!destroyed));
     if(event==5) {actual.destroy();destroyed=true;}
     assert(actual.bufferAllowed()==(ack&&published&&!destroyed));
   }
 }
 std::cout << "selection/lifecycle boundaries, staged sizes, reentrant-destruction/parent-loss helper states and 46656 exhaustive event traces passed\n";
}
