#include <algorithm>
#include <array>
#include <chrono>
#include <functional>
#include <iostream>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <wayland-client-protocol.h>
#include <hyprutils/memory/SharedPtr.hpp>
#include <hyprutils/memory/WeakPtr.hpp>
#include <hyprutils/signal/Signal.hpp>
using namespace Hyprutils::Memory;
#define SP CSharedPointer
#define AQ_LOG_DEBUG 0
struct CCWlKeyboard {
 std::function<void(CCWlKeyboard*,uint32_t,wl_proxy*,wl_array*)> enter;
 std::function<void(CCWlKeyboard*,uint32_t,wl_proxy*)> leave;
 std::function<void(CCWlKeyboard*,uint32_t,uint32_t,uint32_t,wl_keyboard_key_state)> key;
 std::function<void(CCWlKeyboard*,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t)> modifiers;
 void* resource(){return this;}
 void setEnter(decltype(enter)&& f){enter=std::move(f);}
 void setLeave(decltype(leave)&& f){leave=std::move(f);}
 void setKey(decltype(key)&& f){key=std::move(f);}
 void setModifiers(decltype(modifiers)&& f){modifiers=std::move(f);}
};
struct Surface {void* resource(){return this;}};
struct Owner {void log(int,const char*){}};
namespace Aquamarine {
struct IKeyboard {
 struct SKeyEvent {uint32_t timeMs=0,key=0;bool pressed=false;};
 struct SModifiersEvent {uint32_t depressed=0,latched=0,locked=0,group=0;};
 struct {Hyprutils::Signal::CSignalT<SKeyEvent> key;Hyprutils::Signal::CSignalT<SModifiersEvent> modifiers;} events;
};
struct CWaylandBackend;
struct CWaylandKeyboard : IKeyboard {
 SP<CCWlKeyboard> keyboard;CWeakPointer<CWaylandBackend> backend;
 CWaylandKeyboard(SP<CCWlKeyboard>,CWeakPointer<CWaylandBackend>);
 ~CWaylandKeyboard();
};
struct CWaylandOutput {struct {SP<Surface> surface;} waylandState;};
struct CWaylandBackend {
 SP<Owner> backend=makeShared<Owner>();
 std::vector<SP<CWaylandKeyboard>> keyboards;
 std::vector<SP<CWaylandOutput>> outputs;
};
}
using namespace Aquamarine;
static std::unordered_set<CWaylandBackend*> failedParentTransports;
@@HELPER@@
@@CONSTRUCTOR@@
@@DESTRUCTOR@@
int checks=0;
void check(bool yes,const char* label){++checks;if(!yes){std::cerr<<"FAIL "<<label<<'\n';throw 1;}}
struct World {
 SP<CWaylandBackend> parent=makeShared<CWaylandBackend>();
 SP<CWaylandOutput> output=makeShared<CWaylandOutput>();
 World(){output->waylandState.surface=makeShared<Surface>();parent->outputs.push_back(output);}
 wl_proxy* surface(){return static_cast<wl_proxy*>(output->waylandState.surface->resource());}
 SP<CWaylandKeyboard> keyboard(){auto k=makeShared<CWaylandKeyboard>(makeShared<CCWlKeyboard>(),CWeakPointer<CWaylandBackend>(parent));parent->keyboards.push_back(k);return k;}
 void enter(SP<CWaylandKeyboard> k){uint32_t held[]={30,42};wl_array keys{sizeof held,sizeof held,held};k->keyboard->enter(k->keyboard.get(),1,surface(),&keys);}
 void press(SP<CWaylandKeyboard> k,uint32_t code){k->keyboard->key(k->keyboard.get(),1,100,code,WL_KEYBOARD_KEY_STATE_PRESSED);}
 void release(SP<CWaylandKeyboard> k,uint32_t code){k->keyboard->key(k->keyboard.get(),1,101,code,WL_KEYBOARD_KEY_STATE_RELEASED);}
 void mods(SP<CWaylandKeyboard> k,uint32_t depressed){k->keyboard->modifiers(k->keyboard.get(),1,depressed,0,0,0);}
 void leave(SP<CWaylandKeyboard> k){k->keyboard->leave(k->keyboard.get(),1,surface());}
};
int main(){try {
 {
  World w;auto k=w.keyboard();std::vector<IKeyboard::SKeyEvent> keys;std::vector<IKeyboard::SModifiersEvent> mods;
  auto kl=k->events.key.listen([&](const auto& e){keys.push_back(e);});auto ml=k->events.modifiers.listen([&](const auto& e){mods.push_back(e);});
  w.press(k,30);w.mods(k,1);check(keys.empty()&&mods.empty()&&!keyboardState.contains(k.get()),"unentered key and modifiers refused");
  Surface foreign;wl_array empty{};k->keyboard->enter(k->keyboard.get(),1,static_cast<wl_proxy*>(foreign.resource()),&empty);
  w.press(k,30);check(keys.empty()&&!keyboardState.contains(k.get()),"foreign surface cannot establish keyboard focus");
  w.enter(k);check(keys.empty()&&keyboardState.at(k.get()).held==std::array<bool,768>{}&&keyboardState.at(k.get()).focused,"owned enter invents no keys");
  w.press(k,30);w.press(k,30);w.release(k,42);w.press(k,768);
  k->keyboard->key(k->keyboard.get(),1,102,42,static_cast<wl_keyboard_key_state>(2));
  check(keys.size()==1&&keys[0].key==30&&keys[0].pressed,"valid current key transition only");
  w.mods(k,1);check(mods.size()==1&&mods[0].depressed==1,"focused modifiers admitted");
  w.release(k,30);check(keys.size()==2&&!keys.back().pressed,"physical key release balanced");
  w.press(k,30);w.leave(k);check(keys.size()==4&&!keys.back().pressed&&keys.back().key==30,"leave cancels held key");
  check(mods.size()==2&&!mods.back().depressed&&!mods.back().latched&&!mods.back().locked&&!mods.back().group,"leave resets modifiers");
  check(!keyboardState.at(k.get()).focused&&keyboardState.at(k.get()).held==std::array<bool,768>{},"leave clears private focus and keys");
  w.leave(k);check(keys.size()==4&&mods.size()==2,"duplicate leave silent");
  w.press(k,42);w.release(k,30);w.mods(k,1);check(keys.size()==4&&mods.size()==2,"late key and modifiers refused after leave");
  w.enter(k);check(keys.size()==4&&keyboardState.at(k.get()).held==std::array<bool,768>{},"reentry snapshot invents no presses");
  w.release(k,30);check(keys.size()==4,"unpaired release after reentry refused");
  w.press(k,42);w.release(k,42);check(keys.size()==6&&keys[4].pressed&&!keys[5].pressed,"fresh pair admitted after reentry");
  failedParentTransports.insert(w.parent.get());w.enter(k);w.press(k,30);w.mods(k,1);w.leave(k);
  check(keys.size()==6&&mods.size()==2,"failed parent callbacks refuse");failedParentTransports.erase(w.parent.get());
  w.parent->keyboards.clear();w.enter(k);w.press(k,30);w.mods(k,1);w.leave(k);
  check(keys.size()==6&&mods.size()==2,"retired device callbacks refuse");
 }
 {
  World w;auto first=w.keyboard(),second=w.keyboard();w.enter(first);w.enter(second);
  int one=0,two=0;auto a=first->events.key.listen([&](const auto&){++one;});auto b=second->events.key.listen([&](const auto&){++two;});
  w.press(first,30);w.press(second,42);w.mods(second,1);w.leave(first);
  check(one==2&&two==1&&keyboardState.at(second.get()).held[42]&&keyboardState.at(second.get()).focused&&keyboardState.at(second.get()).modifiers,"leave preserves another keyboard");
  retireParentKeyboards(w.parent->keyboards);
  check(one==2&&two==2&&w.parent->keyboards.empty()&&!keyboardState.at(second.get()).held[42]&&!keyboardState.at(second.get()).modifiers,"capability cancels before retirement");
 }
 {
  World w;auto k=w.keyboard();w.enter(k);w.press(k,30);int releases=0,resets=0;
  auto key=k->events.key.listen([&](const IKeyboard::SKeyEvent& e){if(!e.pressed){++releases;check(!keyboardState.at(k.get()).focused,"focus cleared before release callback");w.press(k,42);w.mods(k,1);w.leave(k);}});
  auto mod=k->events.modifiers.listen([&](const auto&){++resets;});w.leave(k);
  check(releases==1&&resets==1&&keyboardState.at(k.get()).held==std::array<bool,768>{},"reentrant leave cannot revive keys or modifiers");
 }
 {
  World w;auto k=w.keyboard();w.enter(k);CWeakPointer<CWaylandKeyboard> weak=k;auto protocol=k->keyboard;int calls=0;
  auto a=k->events.key.listen([&](const auto&){++calls;w.parent->keyboards.clear();check(!weak.expired(),"key callback retains matched keyboard");});
  auto b=k->events.key.listen([&](const auto&){++calls;check(!weak.expired(),"second key callback retains keyboard");});
  k.reset();protocol->key(protocol.get(),1,100,30,WL_KEYBOARD_KEY_STATE_PRESSED);
  check(calls==2&&weak.expired(),"key callback snapshot retires normally");
 }
 {
  World w;auto k=w.keyboard();w.enter(k);CWeakPointer<CWaylandKeyboard> weak=k;auto protocol=k->keyboard;int calls=0;
  auto a=k->events.modifiers.listen([&](const auto&){++calls;w.parent->keyboards.clear();check(!weak.expired(),"modifier callback retains matched keyboard");});
  auto b=k->events.modifiers.listen([&](const auto&){++calls;check(!weak.expired(),"second modifier callback retains keyboard");});
  k.reset();protocol->modifiers(protocol.get(),1,1,0,0,0);
  check(calls==2&&weak.expired(),"modifier callback snapshot retires normally");
 }
 {
  World w;auto k=w.keyboard();w.enter(k);w.parent->keyboards.clear();w.parent.reset();int calls=0;
  auto a=k->events.key.listen([&](const auto&){++calls;});w.press(k,30);w.leave(k);w.mods(k,1);
  check(calls==0,"expired backend callbacks refuse");
 }
 check(keyboardState.empty()&&failedParentTransports.empty(),"normal hook teardown erases private state");
 std::cout<<"checks: "<<checks<<'\n';return 0;
}catch(...){return 1;}}
