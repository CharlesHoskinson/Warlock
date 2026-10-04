#include <algorithm>
#include <functional>
#include <iostream>
#include <memory>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <hyprutils/memory/SharedPtr.hpp>
#include <hyprutils/memory/WeakPtr.hpp>
#include "NestedLifecycle.hpp"
using namespace Hyprutils::Memory;
#define SP CSharedPointer
#define AQ_LOG_CRITICAL 1
#define TRACE(...)
using scheduleFrameReason=int;
constexpr int AQ_SCHEDULE_NEEDS_FRAME=1;
struct wl_display { int error=0, pending=0, failAt=0; };
int wl_display_get_error(wl_display* d) { return d->error; }
int wl_display_get_fd(wl_display*) { return 12; }
int wl_display_flush(wl_display*) { return 0; }
int wl_display_prepare_read(wl_display*) { return 0; }
int wl_display_read_events(wl_display* d) { if(d->failAt==1)d->error=32; return d->error?-1:0; }
int wl_display_dispatch_pending(wl_display* d) { ++d->pending; if(d->failAt==2)d->error=32; return 0; }
int wl_display_dispatch(wl_display* d) { if(d->failAt==3)d->error=32; return 0; }
void wl_display_disconnect(wl_display*) {}
struct Counter { int count=0; void emit(){++count;} };
struct Proxy { int destroy=0, attach=0, commit=0; void sendDestroy(){++destroy;} void sendAttach(void*,int,int){++attach;} void sendCommit(){++commit;} };
struct Scheduler {
 bool scheduled=false, inflight=false, running=false; Counter frameReady;
 bool canSchedule(){return !scheduled&&!inflight&&!running;}
 void requestReschedule(){}
 void invalidate(){scheduled=inflight=running=false;}
 void setFrameScheduled(bool b){scheduled=b;}
 bool frameInFlight(){return inflight;}
 bool frameRunning(){return running;}
};
struct SPollFD {int fd;std::function<void()> onSignal; SPollFD(int f,std::function<void()> c):fd(f),onSignal(c){} };
struct Device { static inline int retired=0; ~Device(){++retired;} };
namespace Aquamarine {
struct CBackend {
 bool ready=true; int logs=0; struct {Counter pollFDsChanged;} events;
 std::vector<SP<std::function<void()>>> pending;
 void log(int,const char*){++logs;}
 void removeIdleEvent(SP<std::function<void()>> f){std::erase(pending,f);}
 void addIdleEvent(SP<std::function<void()>> f){pending.push_back(f);}
 void idle(){auto copy=pending;pending.clear();for(auto& f:copy)(*f)();}
};
struct CWaylandBackend;
struct CWaylandOutput {
 CWeakPointer<CWaylandOutput> self;
 CWeakPointer<CWaylandBackend> backend;
 bool needsFrame=true;
 Scheduler sched;
 struct { SP<Proxy> frameCallback,surface,xdgSurface,xdgToplevel; } waylandState;
 struct {Counter destroy;} events;
 SP<std::function<void()>> frameIdle;
 bool destroy(); ~CWaylandOutput(); void initFrame(); void scheduleFrame(scheduleFrameReason);
};
struct CWaylandBackend {
 CWeakPointer<CWaylandBackend> self;
 CWeakPointer<CBackend> backend;
 std::vector<SP<CWaylandOutput>> outputs;
 std::vector<SP<Device>> pointers,keyboards;
 std::vector<std::function<void()>> idleCallbacks;
 CWeakPointer<CWaylandOutput> focusedOutput;
 unsigned lastEnterSerial=12;
 struct {wl_display* display;} waylandState;
 bool dispatchEvents(); std::vector<SP<SPollFD>> pollFDs();
};
}
using namespace Aquamarine;
struct wl_proxy;
@@KEYBOARD_SURFACE_MAP@@
static std::unordered_set<CWaylandBackend*> failedParentTransports;
static std::unordered_set<CWaylandOutput*> retiredOutputs;
static std::unordered_map<CWaylandOutput*,std::shared_ptr<NestedPolicy::ConfigureLifecycle>> outputLifecycle;
static std::unordered_map<CWaylandOutput*,SP<Proxy>> outputViewport;
static std::unordered_map<CWaylandOutput*,uint64_t> frameGeneration;
[[maybe_unused]] static void cancelHeldParentButtons(const std::vector<SP<Device>>&) {}
[[maybe_unused]] static void cancelHeldParentKeys(const std::vector<SP<Device>>&) {}
@@DISPATCH@@
@@POLL@@
@@DESTROY@@
@@DESTRUCTOR@@
@@SCHEDULE@@
void CWaylandOutput::initFrame() {
 auto lifecycle=outputLifecycle.at(this);
@@FRAME@@
}
int checks=0;
void check(bool yes,const char* label){++checks;if(!yes){std::cerr<<"FAIL "<<label<<'\n';throw 1;}}
int main(){
 try {
  setenv("AQ_BACKENDS","wayland",1);
  for(int fault: {0,1,2}){
   auto owner=makeShared<CBackend>();auto parent=makeShared<CWaylandBackend>();parent->self=parent;parent->backend=owner;
   wl_display display;parent->waylandState.display=&display;
   auto output=makeShared<CWaylandOutput>();output->self=output;output->backend=parent;
   output->waylandState.surface=makeShared<Proxy>();output->waylandState.xdgSurface=makeShared<Proxy>();output->waylandState.xdgToplevel=makeShared<Proxy>();output->waylandState.frameCallback=makeShared<Proxy>();
   auto policy=std::make_shared<NestedPolicy::ConfigureLifecycle>();policy->acknowledged=policy->announced=true;
   policy->stageSize(800,600);policy->acknowledge();policy->presentation.queueCommit(policy->presentation.acked.generation,800,600);
   outputLifecycle[output.get()]=policy;outputViewport[output.get()]=makeShared<Proxy>();parent->outputs.push_back(output);parent->focusedOutput=output;
   output->initFrame();output->sched.scheduled=output->sched.inflight=true;owner->addIdleEvent(output->frameIdle);auto copiedFrame=output->frameIdle;
   parent->pointers.push_back(makeShared<Device>());parent->keyboards.push_back(makeShared<Device>());int published=0;parent->idleCallbacks.push_back([&]{++published;});
   check(parent->pollFDs().size()==1,"healthy descriptor offered");
   int retiredBefore=Device::retired;
   if(fault==0)display.error=32;else display.failAt=fault;
   check(!parent->dispatchEvents(),"transport dispatch refuses loss");
   check(parent->pointers.empty()&&parent->keyboards.empty(),"actual vectors retired");
   check(Device::retired==retiredBefore+2,"unretained input objects destroyed");
   check(parent->outputs.empty(),"output vector retired");
   check(parent->focusedOutput.expired()&&parent->lastEnterSerial==0,"focus and serial retired");
   check(!owner->ready&&policy->destroyed,"strict selection and policy fenced");
   check(!output->needsFrame&&!output->waylandState.frameCallback&&!output->sched.scheduled&&!output->sched.inflight,"frame state retired");
   check(published==0&&parent->idleCallbacks.empty(),"queued publication discarded");
   check(output->events.destroy.count==1,"one output retirement signal");
   check(output->waylandState.surface->attach==0&&output->waylandState.surface->commit==0,"no dead parent publication");
   check(parent->pollFDs().empty(),"failed descriptor withdrawn");
   check(owner->events.pollFDsChanged.count==0,"descriptor notification deferred");
   check(owner->pending.size()==1,"frame task removed and one notification queued");
   output->scheduleFrame(0);check(owner->pending.size()==1&&!output->needsFrame,"late frame scheduling refused");
   (*copiedFrame)();check(output->sched.frameReady.count==0,"copied frame task fenced");
   check(!parent->dispatchEvents()&&owner->logs==1&&owner->pending.size()==1,"repeated dispatch is one shot");
   owner->idle();check(owner->events.pollFDsChanged.count==1,"consumer notified on core idle");
   check(!output->destroy()&&output->events.destroy.count==1,"reentrant output retirement refused");
   auto raw=output.get();output.reset();(*copiedFrame)();check(!outputLifecycle.contains(raw),"copied task safe after output destruction");
   failedParentTransports.erase(parent.get());
  }
  auto owner=makeShared<CBackend>();auto parent=makeShared<CWaylandBackend>();parent->self=parent;parent->backend=owner;wl_display display;parent->waylandState.display=&display;
  int published=0;parent->idleCallbacks.push_back([&]{++published;});check(parent->dispatchEvents()&&published==1,"healthy dispatch preserved");
  owner.reset();check(!parent->dispatchEvents(),"missing owner refused");
  parent->waylandState.display=nullptr;check(!parent->dispatchEvents()&&parent->pollFDs().empty(),"missing display refused");
  std::cout<<"checks: "<<checks<<'\n';return 0;
 }catch(...){return 1;}
}
