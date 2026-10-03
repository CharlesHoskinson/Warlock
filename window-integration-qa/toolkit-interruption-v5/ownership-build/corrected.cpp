
#include <hyprutils/memory/WeakPtr.hpp>
#include <hyprutils/memory/SharedPtr.hpp>
#include <hyprutils/memory/UniquePtr.hpp>
#include <format>
#include <functional>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>
extern "C" {
#include <lua.h>
#include <lauxlib.h>
}
template<class T> using SP=Hyprutils::Memory::CSharedPointer<T>;
template<class T> using WP=Hyprutils::Memory::CWeakPointer<T>;
using Hyprutils::Memory::makeShared;
using Hyprutils::Memory::makeUnique;
unsigned checks=0,scenarios=0;
void check(bool p){if(!p)throw std::runtime_error("check "+std::to_string(checks+1));++checks;}
struct Owner {uint64_t m_stableID;bool mapped=true,hidden=false;explicit Owner(uint64_t id):m_stableID(id){}bool isHidden(){return hidden;}};
using PHLWINDOW=SP<Owner>;using PHLWINDOWREF=WP<Owner>;
bool validMapped(const PHLWINDOW& owner){return owner&&owner->mapped;}
struct CBox{double x=0,y=0,width=0,height=0;};
struct Vector2D{double x=0,y=0;};
enum eMouseBindMode{MBIND_INVALID,MBIND_MOVE,MBIND_RESIZE};constexpr uint32_t BTN_LEFT=272;
namespace Layout {struct ITarget {PHLWINDOW owner;explicit ITarget(PHLWINDOW w):owner(w){}PHLWINDOW window(){return owner;}};}
struct Controller{SP<Layout::ITarget> current;SP<Layout::ITarget> target(){return current;}};
bool keepCurrentGeometry=false;uint32_t releasedButton=BTN_LEFT;
struct Manager{Controller controller;int ends=0;bool keepObserved=false;std::function<void()> onEnd;
 Controller* dragController(){return &controller;}
 void endDragTarget(){++ends;keepObserved=keepCurrentGeometry;controller.current.reset();if(onEnd)onEnd();}};
auto g_layoutManager=makeUnique<Manager>();
struct WindowState{std::vector<PHLWINDOW> list;const auto& windows(){return list;}};
WindowState windows;
namespace Desktop{WindowState* windowState(){return &windows;}}
struct CHyprBar {
 PHLWINDOW owner;bool m_bDragPending=false,m_bDraggingThis=false,m_bTouchEv=false,m_bCancelledDown=true;int m_touchId=0;Vector2D m_captionPress;
 std::function<void()> destroying;explicit CHyprBar(PHLWINDOW w):owner(w){}~CHyprBar(){if(destroying)destroying();}
 PHLWINDOW getOwner(){return owner;}bool retireCaptionIntent();
};
struct Globals{std::vector<WP<CHyprBar>> bars;};auto g_pGlobalState=makeUnique<Globals>();
struct GestureCapture {
    PHLWINDOWREF owner;
    WP<Layout::ITarget> target;
    uint64_t stableID = 0;
    CBox origin;
    eMouseBindMode mode = MBIND_INVALID;
    uint32_t button = BTN_LEFT;
};
std::optional<GestureCapture> gesture;
bool sameGesture(const SP<Layout::ITarget>& target) {
    if (!gesture || !target || gesture->target.lock() != target)
        return false;
    const auto owner = gesture->owner.lock();
    return owner && target->window() == owner && owner->m_stableID == gesture->stableID;
}
void retireCapturedGesture(bool keepGeometry = false) {
    const auto& controller = g_layoutManager->dragController();
    if (sameGesture(controller->target())) {
        releasedButton = 0;
        const bool previous = keepCurrentGeometry;
        keepCurrentGeometry = keepGeometry;
        try {
            g_layoutManager->endDragTarget();
        } catch (...) {
            keepCurrentGeometry = previous;
            throw;
        }
        keepCurrentGeometry = previous;
    }
    gesture.reset();
}
bool CHyprBar::retireCaptionIntent() {
    // Preserve swallowed-release authority until the genuine release arrives.
    const bool hadIntent = m_bDragPending || m_bDraggingThis;
    m_bDragPending = false;
    m_bDraggingThis = false;
    m_bTouchEv = false;
    m_touchId = 0;
    m_captionPress = {};
    return hadIntent;
}
int luaRetireGestureCurrent(lua_State* state) {
    // Exact current native lifetime only. No PID/address-only recovery and no
    // synthetic input release. Success and actually-retired are separate.
    if (lua_gettop(state) != 2 || lua_type(state, 1) != LUA_TSTRING || lua_type(state, 2) != LUA_TSTRING) {
        lua_pushboolean(state, false); lua_pushboolean(state, false); return 2;
    }
    const std::string address = lua_tostring(state, 1), stableID = lua_tostring(state, 2);
    PHLWINDOW owner;
    for (const auto& window : Desktop::windowState()->windows()) {
        if (validMapped(window) && !window->isHidden() &&
            address == std::format("0x{:x}", reinterpret_cast<uintptr_t>(window.get())) &&
            stableID == std::format("{:x}", window->m_stableID)) {
            owner = window; break;
        }
    }
    if (!owner) {
        lua_pushboolean(state, false); lua_pushboolean(state, false); return 2;
    }
    const auto target = g_layoutManager->dragController()->target();
    const bool matched = sameGesture(target) && target->window() == owner;
    if (matched)
        retireCapturedGesture(true);
    bool cancelledIntent = false;
    for (const auto& barRef : g_pGlobalState->bars) {
        // Decorations are uniquely owned by the compositor. This checked
        // synchronous borrow cannot promote their weak refs to shared owners.
        // retireCaptionIntent only resets local flags and invokes no callbacks.
        if (barRef.expired())
            continue;
        auto* const bar = barRef.get();
        if (bar && bar->getOwner() == owner)
            cancelledIntent = bar->retireCaptionIntent() || cancelledIntent;
    }
    lua_pushboolean(state, !matched || !g_layoutManager->dragController()->target());
    lua_pushboolean(state, matched || cancelledIntent);
    return 2;
}
std::pair<bool,bool> invoke(lua_State* L,const PHLWINDOW& owner,const std::string& stable=""){
 lua_settop(L,0);lua_pushcfunction(L,luaRetireGestureCurrent);
 const auto address=std::format("0x{:x}",reinterpret_cast<uintptr_t>(owner.get()));
 const auto id=stable.empty()?std::format("{:x}",owner->m_stableID):stable;
 lua_pushlstring(L,address.data(),address.size());lua_pushlstring(L,id.data(),id.size());
 check(lua_pcall(L,2,2,0)==LUA_OK);check(lua_gettop(L)==2&&lua_isboolean(L,1)&&lua_isboolean(L,2));++scenarios;
 return {bool(lua_toboolean(L,1)),bool(lua_toboolean(L,2))};
}
int main(int argc,char**){
 auto* L=luaL_newstate();check(L!=nullptr);
 auto owner=makeShared<Owner>(0xa1),peer=makeShared<Owner>(0xb2);windows.list={owner,peer};
 auto bar=makeUnique<CHyprBar>(owner);auto other=makeUnique<CHyprBar>(peer);
 g_pGlobalState->bars={WP<CHyprBar>{bar},WP<CHyprBar>{other}};
 const auto ref=WP<CHyprBar>{bar};check(!ref.expired()&&ref.get()==bar.get());
 check((invoke(L,owner)==std::pair{true,false}));check(ref==bar&&bar->m_bCancelledDown);
 if(argc>1){lua_close(L);return 0;}
 bar->m_bDragPending=true;other->m_bDragPending=true;
 check((invoke(L,owner)==std::pair{true,true}));check(!bar->m_bDragPending&&other->m_bDragPending&&bar->m_bCancelledDown);
 bar->m_bDraggingThis=true;bar->m_bTouchEv=true;bar->m_touchId=7;
 check((invoke(L,owner)==std::pair{true,true}));check(!bar->m_bDraggingThis&&!bar->m_bTouchEv&&bar->m_touchId==0);
 bar->m_bDragPending=true;check((invoke(L,owner,"a2")==std::pair{false,false}));check(bar->m_bDragPending);
 owner->hidden=true;check((invoke(L,owner)==std::pair{false,false}));check(bar->m_bDragPending);owner->hidden=false;
 owner->mapped=false;check((invoke(L,owner)==std::pair{false,false}));check(bar->m_bDragPending);owner->mapped=true;
 bar->m_bDragPending=false;auto target=makeShared<Layout::ITarget>(owner);gesture=GestureCapture{owner,target,owner->m_stableID,{},MBIND_MOVE,BTN_LEFT};
 g_layoutManager->controller.current=target;
 check((invoke(L,owner)==std::pair{true,true}));check(g_layoutManager->ends==1&&g_layoutManager->keepObserved&&!keepCurrentGeometry&&!gesture&&!g_layoutManager->controller.current&&releasedButton==0);
 gesture=GestureCapture{owner,target,owner->m_stableID,{},MBIND_RESIZE,BTN_LEFT};g_layoutManager->controller.current=target;
 check((invoke(L,owner)==std::pair{true,true}));check(g_layoutManager->ends==2&&g_layoutManager->keepObserved);
 const auto foreign=makeShared<Layout::ITarget>(peer);g_layoutManager->controller.current=foreign;
 check((invoke(L,owner)==std::pair{true,false}));check(g_layoutManager->controller.current==foreign&&g_layoutManager->ends==2);
 g_layoutManager->controller.current.reset();
 bool destructorQueried=false;bar->m_bDragPending=true;
 bar->destroying=[&]{destructorQueried=true;check(ref.expired()&&ref.get()!=nullptr);check((invoke(L,owner)==std::pair{true,false}));};
 bar.reset();check(destructorQueried&&ref.expired()&&ref.get()==nullptr);
 check((invoke(L,owner)==std::pair{true,false}));
 // A new uniquely owned bar never becomes reachable through an old weak handle.
 bar=makeUnique<CHyprBar>(owner);bar->m_bDragPending=true;
 check((invoke(L,owner)==std::pair{true,false}));check(bar->m_bDragPending&&ref.get()==nullptr);
 g_pGlobalState->bars.push_back(WP<CHyprBar>{bar});
 check((invoke(L,owner)==std::pair{true,true}));check(!bar->m_bDragPending);
 // Delegated core callbacks may destroy decorations before the borrowing loop.
 gesture=GestureCapture{owner,target,owner->m_stableID,{},MBIND_MOVE,BTN_LEFT};g_layoutManager->controller.current=target;
 g_layoutManager->onEnd=[&]{bar.reset();};
 check((invoke(L,owner)==std::pair{true,true}));check(g_layoutManager->ends==3&&!bar);g_layoutManager->onEnd={};
 check((invoke(L,peer)==std::pair{true,true}));check(!other->m_bDragPending);
 // Invalid Lua shape/type preserves the ordinary two-boolean refusal contract.
 lua_settop(L,0);lua_pushcfunction(L,luaRetireGestureCurrent);check(lua_pcall(L,0,2,0)==LUA_OK);
 check(!lua_toboolean(L,1)&&!lua_toboolean(L,2));++scenarios;
 lua_settop(L,0);lua_pushcfunction(L,luaRetireGestureCurrent);lua_pushinteger(L,1);lua_pushstring(L,"a1");check(lua_pcall(L,2,2,0)==LUA_OK);
 check(!lua_toboolean(L,1)&&!lua_toboolean(L,2));++scenarios;
 lua_close(L);std::cout<<checks<<" assertions / "<<scenarios<<" actual unique-weak ABI Lua scenarios PASS\n";
}
