#include <array>
#include <chrono>
#include <iostream>
#include <unordered_map>
#include <vector>
#include <hyprutils/memory/SharedPtr.hpp>
#include <hyprutils/memory/WeakPtr.hpp>
#include <hyprutils/signal/Signal.hpp>
using namespace Hyprutils::Memory;
#define SP CSharedPointer
namespace Aquamarine {
struct IKeyboard {
 struct SKeyEvent {uint32_t timeMs=0,key=0;bool pressed=false;};
 struct SModifiersEvent {uint32_t depressed=0,latched=0,locked=0,group=0;};
};
struct CWaylandKeyboard {
 struct {Hyprutils::Signal::CSignalT<IKeyboard::SKeyEvent> key;
         Hyprutils::Signal::CSignalT<IKeyboard::SModifiersEvent> modifiers;} events;
 ~CWaylandKeyboard();
};
}
using namespace Aquamarine;
struct PrivateParentKeyboard {
    std::array<bool, 768> held{};
    bool modifiers = false;
    bool focused = false;
};
static std::unordered_map<CWaylandKeyboard*, PrivateParentKeyboard> keyboardState;
static bool admitParentKey(CWaylandKeyboard* keyboard, uint32_t key, bool pressed) {
    if (key >= 768) return false;
    auto& state = keyboardState[keyboard];
    if (state.held[key] == pressed) return false;
    state.held[key] = pressed;
    return true;
}
static void cancelHeldParentKeys(const std::vector<SP<CWaylandKeyboard>>& keyboards) {
    const auto retiring = keyboards;
    const auto now = static_cast<uint32_t>(std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::steady_clock::now().time_since_epoch()).count());
    for (const auto& keyboard : retiring) {
        const auto state = keyboardState.find(keyboard.get());
        if (state == keyboardState.end()) continue;
        const auto held = state->second.held;
        const bool hadModifiers = state->second.modifiers;
        state->second.focused = false;
        state->second.held.fill(false);
        state->second.modifiers = false;
        bool emitted = false;
        for (uint32_t key = 0; key < held.size(); ++key) {
            if (!held[key]) continue;
            (void)now;
            emitted = true;
        }
        if (emitted || hadModifiers) keyboard->events.modifiers.emit(IKeyboard::SModifiersEvent{});
    }
}

static void retireParentKeyboards(std::vector<SP<CWaylandKeyboard>>& keyboards) {
    cancelHeldParentKeys(keyboards);
    keyboards.clear();
}


Aquamarine::CWaylandKeyboard::~CWaylandKeyboard() {
    keyboardState.erase(this);
}

int checks=0;
void check(bool yes,const char* label){++checks;if(!yes){std::cerr<<"FAIL "<<label<<'\n';throw 1;}}
int main(){try {
 for(unsigned mask=0;mask<4;++mask){
  auto k=makeShared<CWaylandKeyboard>();std::vector<SP<CWaylandKeyboard>> keyboards{k};
  std::vector<uint32_t> expected,seen;int resets=0;
  for(unsigned i=0;i<2;++i)if(mask&(1u<<i)){check(admitParentKey(k.get(),30+i,true),"initial key admitted");expected.push_back(30+i);}
  const auto size=keyboardState.size();
  auto key=k->events.key.listen([&](const IKeyboard::SKeyEvent& e){
   check(!e.pressed,"no invented key press");check(e.timeMs>0,"cancellation timestamp");
   check(keyboardState.at(k.get()).held==std::array<bool,768>{}&&!keyboardState.at(k.get()).modifiers,"clear before callback");seen.push_back(e.key);
  });
  auto mod=k->events.modifiers.listen([&](const IKeyboard::SModifiersEvent& e){
   check(!e.depressed&&!e.latched&&!e.locked&&!e.group,"zero modifiers");++resets;
   check(seen==expected,"modifier reset follows releases");
  });
  cancelHeldParentKeys(keyboards);check(seen==expected,"only admitted held keys cancelled");
  check(resets==(mask?1:0),"one modifier reset per batch");
  cancelHeldParentKeys(keyboards);check(seen==expected&&resets==(mask?1:0),"repeat cancellation silent");
  check(keyboardState.size()==size,"untracked keyboard inserts no state");
 }
 {
  auto k=makeShared<CWaylandKeyboard>();std::vector<SP<CWaylandKeyboard>> keyboards{k};
  check(!admitParentKey(k.get(),768,true)&&!admitParentKey(k.get(),UINT32_MAX,true),"out of range keys refused");
  for(unsigned i=0;i<768;++i){
   check(admitParentKey(k.get(),i,true),"bounded key admitted");
   check(!admitParentKey(k.get(),i,true),"duplicate key down refused");
   if(i%2==0){check(admitParentKey(k.get(),i,false),"physical release admitted");check(!admitParentKey(k.get(),i,false),"unpaired key up refused");}
  }
  int calls=0;auto key=k->events.key.listen([&](const IKeyboard::SKeyEvent& e){check(e.key<768&&e.key%2==1&&!e.pressed,"already released key excluded");++calls;});
  cancelHeldParentKeys(keyboards);check(calls==384,"all bounded held keys cancelled");
 }
 {
  auto k=makeShared<CWaylandKeyboard>();std::vector<SP<CWaylandKeyboard>> keyboards{k};keyboardState[k.get()].modifiers=true;
  int calls=0;auto mod=k->events.modifiers.listen([&](const IKeyboard::SModifiersEvent&){++calls;check(!keyboardState.at(k.get()).modifiers,"modifier record cleared before callback");});
  cancelHeldParentKeys(keyboards);cancelHeldParentKeys(keyboards);check(calls==1,"modifier only cancellation");
 }
 {
  auto k=makeShared<CWaylandKeyboard>();std::vector<SP<CWaylandKeyboard>> keyboards{k};admitParentKey(k.get(),30,true);
  int calls=0,depth=0;auto key=k->events.key.listen([&](const IKeyboard::SKeyEvent&){++calls;if(!depth){++depth;cancelHeldParentKeys(keyboards);--depth;}});
  cancelHeldParentKeys(keyboards);check(calls==1,"reentry cannot replay key");
 }
 {
  auto first=makeShared<CWaylandKeyboard>(),second=makeShared<CWaylandKeyboard>();
  std::vector<SP<CWaylandKeyboard>> keyboards{first,second};CWeakPointer<CWaylandKeyboard> w1=first,w2=second;
  admitParentKey(first.get(),30,true);admitParentKey(second.get(),42,true);int calls=0,resets=0;
  auto one=first->events.key.listen([&](const IKeyboard::SKeyEvent&){++calls;keyboards.clear();check(!w1.expired()&&!w2.expired(),"snapshot retains keyboards during removal");});
  auto two=second->events.key.listen([&](const IKeyboard::SKeyEvent&){++calls;});
  auto m1=first->events.modifiers.listen([&](const IKeyboard::SModifiersEvent&){++resets;});
  auto m2=second->events.modifiers.listen([&](const IKeyboard::SModifiersEvent&){++resets;});
  first.reset();second.reset();cancelHeldParentKeys(keyboards);
  check(calls==2&&resets==2,"snapshot completes both keyboard batches");check(w1.expired()&&w2.expired(),"snapshot releases retired keyboards");
 }
 {
  auto k=makeShared<CWaylandKeyboard>();std::vector<SP<CWaylandKeyboard>> keyboards{k};CWeakPointer<CWaylandKeyboard> weak=k;admitParentKey(k.get(),42,true);
  int calls=0;auto key=k->events.key.listen([&](const IKeyboard::SKeyEvent&){++calls;check(keyboards.size()==1&&!weak.expired(),"cancellation before capability retirement");});
  k.reset();retireParentKeyboards(keyboards);
  check(calls==1&&keyboards.empty()&&weak.expired(),"capability retirement completes cancellation");
 }
 check(keyboardState.empty(),"normal keyboard teardown erases private state");
 std::cout<<"checks: "<<checks<<'\n';return 0;
}catch(...){return 1;}}
