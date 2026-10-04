#include <algorithm>
#include <functional>
#include <iostream>
#include <string>
#include <vector>
#include <hyprutils/memory/SharedPtr.hpp>
#include <hyprutils/memory/WeakPtr.hpp>
using namespace Hyprutils::Memory;
#define SP CSharedPointer
struct CCWlSeat;
enum wl_seat_capability { WL_SEAT_CAPABILITY_POINTER=1, WL_SEAT_CAPABILITY_KEYBOARD=2 };
struct Display {int error=0;};
int wl_display_get_error(Display* d) {return d->error;}
struct CCWlKeyboard {int id;explicit CCWlKeyboard(int id_):id(id_) {}};
struct CCWlPointer {int id;explicit CCWlPointer(int id_):id(id_) {}};
struct CWaylandBackend;
struct IKeyboard {virtual ~IKeyboard()=default; int id=0;};
struct IPointer {virtual ~IPointer()=default; int id=0;};
struct CWaylandKeyboard:IKeyboard { CWaylandKeyboard(SP<CCWlKeyboard> p,CWeakPointer<CWaylandBackend>) {id=p->id;} };
struct CWaylandPointer:IPointer { CWaylandPointer(SP<CCWlPointer> p,CWeakPointer<CWaylandBackend>) {id=p->id;} };
template<class T> struct Event {std::vector<int> seen; std::function<void()> callback; void emit(SP<T> p) {seen.push_back(p->id);if(callback)callback();}};
struct Core {bool ready=true; struct {Event<IKeyboard> newKeyboard;Event<IPointer> newPointer;} events;};
struct CCWlSeat {std::function<void(CCWlSeat*,wl_seat_capability)> callback;int next=0;
 void setCapabilities(std::function<void(CCWlSeat*,wl_seat_capability)> f) {callback=f;}
 int sendGetKeyboard(){return ++next;} int sendGetPointer(){return ++next;}
 void caps(int cap) {callback(this,static_cast<wl_seat_capability>(cap));}
};
namespace Aquamarine {struct CWaylandBackend;
}
// Production qualification uses Aquamarine::CWaylandBackend; fixtures forward
// the device constructor owner type through the same owning weak pointer.
struct CWaylandBackend {CWeakPointer<CWaylandBackend> self;CWeakPointer<Core> backend;
 struct {SP<CCWlSeat> seat;Display* display=nullptr;} waylandState;
 std::vector<SP<CWaylandKeyboard>> keyboards;std::vector<SP<CWaylandPointer>> pointers;
 std::vector<std::function<void()>> idleCallbacks;void initSeat();
};
void CWaylandBackend::initSeat() {
    waylandState.seat->setCapabilities([this](CCWlSeat* r, wl_seat_capability cap) {
        const bool HAS_KEYBOARD = ((uint32_t)cap) & WL_SEAT_CAPABILITY_KEYBOARD;
        const bool HAS_POINTER  = ((uint32_t)cap) & WL_SEAT_CAPABILITY_POINTER;

        if (HAS_KEYBOARD && keyboards.empty()) {
            auto k = keyboards.emplace_back(makeShared<CWaylandKeyboard>(makeShared<CCWlKeyboard>(waylandState.seat->sendGetKeyboard()), self));
            const auto weakBackend = self;
            const auto weakDevice = CWeakPointer<CWaylandKeyboard>(k);
            idleCallbacks.emplace_back([weakBackend, weakDevice]() {
                const auto parent = weakBackend.lock();
                const auto device = weakDevice.lock();
                if (!parent || !device || std::ranges::find(parent->keyboards, device) == parent->keyboards.end())
                    return;
                const auto owner = parent->backend.lock();
                if (!owner || !owner->ready || !parent->waylandState.display || false)
                    return;
                owner->events.newKeyboard.emit(SP<IKeyboard>(device));
            });
        } else if (!HAS_KEYBOARD && !keyboards.empty())
            keyboards.clear();

        if (HAS_POINTER && pointers.empty()) {
            auto p = pointers.emplace_back(makeShared<CWaylandPointer>(makeShared<CCWlPointer>(waylandState.seat->sendGetPointer()), self));
            const auto weakBackend = self;
            const auto weakDevice = CWeakPointer<CWaylandPointer>(p);
            idleCallbacks.emplace_back([weakBackend, weakDevice]() {
                const auto parent = weakBackend.lock();
                const auto device = weakDevice.lock();
                if (!parent || !device || std::ranges::find(parent->pointers, device) == parent->pointers.end())
                    return;
                const auto owner = parent->backend.lock();
                if (!owner || !owner->ready || !parent->waylandState.display || false)
                    return;
                owner->events.newPointer.emit(SP<IPointer>(device));
            });
        } else if (!HAS_POINTER && !pointers.empty())
            pointers.clear();
    });
}

struct Fixture {SP<Core> core=makeShared<Core>();SP<CWaylandBackend> parent=makeShared<CWaylandBackend>();Display display;
 Fixture(){parent->self=parent;parent->backend=core;parent->waylandState.seat=makeShared<CCWlSeat>();parent->waylandState.display=&display;parent->initSeat();}
 void caps(int n){parent->waylandState.seat->caps(n);} void drain(){auto q=std::move(parent->idleCallbacks);parent->idleCallbacks.clear();for(auto& f:q)f();}
};
static int count=0;
void check(bool v,const char* name) {++count;if(!v){std::cerr<<"FAIL "<<name<<'\n';std::exit(1);}}
int main() {
 {Fixture f;f.caps(3);f.drain();check(f.core->events.newPointer.seen.size()==1,"live pointer published");check(f.core->events.newKeyboard.seen.size()==1,"live keyboard published");f.drain();check(f.core->events.newPointer.seen.size()==1,"no repeat on empty drain");}
 {Fixture f;f.caps(3);auto weakP=CWeakPointer<CWaylandPointer>(f.parent->pointers[0]);auto weakK=CWeakPointer<CWaylandKeyboard>(f.parent->keyboards[0]);f.caps(0);check(!weakP.lock(),"unpublished pointer retires before queue drain");check(!weakK.lock(),"unpublished keyboard retires before queue drain");f.drain();check(f.core->events.newPointer.seen.empty(),"retired pointer not published");check(f.core->events.newKeyboard.seen.empty(),"retired keyboard not published");}
 {Fixture f;f.caps(3);int p=f.parent->pointers[0]->id,k=f.parent->keyboards[0]->id;f.caps(0);f.caps(3);f.drain();check(f.core->events.newPointer.seen==std::vector<int>{f.parent->pointers[0]->id},"only replacement pointer");check(f.core->events.newKeyboard.seen==std::vector<int>{f.parent->keyboards[0]->id},"only replacement keyboard");check(f.parent->pointers[0]->id!=p&&f.parent->keyboards[0]->id!=k,"replacement incarnations distinct");}
 {Fixture f;f.caps(3);auto p=f.parent->pointers[0];auto k=f.parent->keyboards[0];f.caps(0);f.drain();check(f.core->events.newPointer.seen.empty(),"retained retired pointer refused");check(f.core->events.newKeyboard.seen.empty(),"retained retired keyboard refused");}
 {Fixture f;f.caps(3);f.caps(3);f.drain();check(f.core->events.newPointer.seen.size()==1,"duplicate pointer cap does not requeue");check(f.core->events.newKeyboard.seen.size()==1,"duplicate keyboard cap does not requeue");}
 {Fixture f;f.caps(3);f.caps(1);f.drain();check(f.core->events.newPointer.seen.size()==1,"pointer unaffected by keyboard loss");check(f.core->events.newKeyboard.seen.empty(),"keyboard independently retired");}
 {Fixture f;f.caps(3);f.caps(2);f.drain();check(f.core->events.newKeyboard.seen.size()==1,"keyboard unaffected by pointer loss");check(f.core->events.newPointer.seen.empty(),"pointer independently retired");}
 {Fixture f;for(int i=0;i<16;++i){f.caps(3);f.caps(0);}f.caps(3);f.drain();check(f.core->events.newPointer.seen.size()==1,"pointer burst only current");check(f.core->events.newKeyboard.seen.size()==1,"keyboard burst only current");}
 {Fixture f;f.caps(3);f.core->ready=false;f.drain();check(f.core->events.newPointer.seen.empty(),"not ready pointer refused");check(f.core->events.newKeyboard.seen.empty(),"not ready keyboard refused");}
 {Fixture f;f.caps(3);f.display.error=1;f.drain();check(f.core->events.newPointer.seen.empty(),"failed transport pointer refused");check(f.core->events.newKeyboard.seen.empty(),"failed transport keyboard refused");}
 {Fixture f;f.caps(3);auto q=std::move(f.parent->idleCallbacks);auto core=f.core;f.parent.reset();for(auto& task:q)task();check(core->events.newPointer.seen.empty(),"dead backend pointer refused");check(core->events.newKeyboard.seen.empty(),"dead backend keyboard refused");}
 {Fixture f;f.caps(3);f.core.reset();f.drain();check(true,"dead core safely refused");}
 {Fixture f;f.caps(3);f.core->events.newKeyboard.callback=[&]{f.caps(0);};f.drain();check(f.core->events.newPointer.seen.empty(),"reentrant keyboard listener retires queued pointer");}
 std::cout<<"checks: "<<count<<'\n';
}
