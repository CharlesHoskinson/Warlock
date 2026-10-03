// Private QA observation only: no focus, input cancellation, dispatch or hooks.
#include <hyprland/src/plugins/PluginAPI.hpp>
#include <hyprland/src/desktop/state/WindowState.hpp>
#include <hyprland/src/desktop/state/ViewState.hpp>
#include <hyprland/src/desktop/state/FocusState.hpp>
#include <hyprland/src/desktop/history/WindowHistoryTracker.hpp>
#include <hyprland/src/desktop/view/Window.hpp>
#include <hyprland/src/desktop/view/WLSurface.hpp>
#include <hyprland/src/desktop/Workspace.hpp>
#include <hyprland/src/protocols/XDGShell.hpp>
#include <hyprland/src/protocols/XDGDialog.hpp>
#include <hyprland/src/protocols/core/DataDevice.hpp>
#include <hyprland/src/protocols/InputCapture.hpp>
#include <hyprland/src/managers/input/InputManager.hpp>
#include <hyprland/src/managers/SeatManager.hpp>
#include <hyprland/src/devices/IKeyboard.hpp>
#include <hyprland/src/managers/SessionLockManager.hpp>
#include <hyprland/src/layout/LayoutManager.hpp>
#include <hyprland/src/layout/supplementary/DragController.hpp>
#include <hyprland/src/event/EventBus.hpp>
#include <format>
#include <fstream>
#include <regex>
#include <sys/resource.h>
#include <sys/stat.h>
#include <unistd.h>
#include <unordered_set>
extern "C" {
#include <lua.h>
}
namespace {
HANDLE handle=nullptr;
CHyprSignalListener buttonListener;
CHyprSignalListener keyboardListener;
std::vector<std::string> keyboardEvents;
uint64_t keyboardSequence=0;
std::vector<std::string> events;
bool modal(const PHLWINDOW& w){if(!w)return false;const auto d=w->m_xdgSurface&&w->m_xdgSurface->m_toplevel?w->m_xdgSurface->m_toplevel->m_dialog.lock():nullptr;return w->isModal()||(d&&d->modal);}
std::string surfaceBox(const PHLWINDOW& w){if(w){const auto surface=w->wlSurface();if(surface){const auto box=surface->getSurfaceBoxGlobal();if(box)return std::format("[{},{},{},{}]",box->x,box->y,box->w,box->h);}}return "null";}
std::string id(const PHLWINDOW& w){return w?std::format(R"({{"address":"0x{:x}","stableId":"{:x}","pid":{},"modal":{},"mapped":{},"hidden":{},"acceptsInput":{},"surfaceBox":{}}})",reinterpret_cast<uintptr_t>(w.get()),w->m_stableID,w->getPID(),modal(w),w->m_isMapped,w->isHidden(),w->acceptsInput(),surfaceBox(w)):"null";}
PHLWINDOW target(PHLWINDOW w){std::unordered_set<Desktop::View::CWindow*> seen;while(Desktop::View::validMapped(w)&&seen.insert(w.get()).second){PHLWINDOW child;for(auto it=Desktop::History::windowTracker()->fullHistory().rbegin();it!=Desktop::History::windowTracker()->fullHistory().rend();++it){const auto c=it->lock();if(Desktop::View::validMapped(c)&&c!=w&&c->m_workspace==w->m_workspace&&c->parent()==w&&modal(c)){child=c;break;}}if(!child)break;w=child;}return w;}
std::string state(){const auto pos=g_pInputManager->getMouseCoordsInternal();const auto hit=Desktop::viewState()->hitTest().windowAt(pos,Desktop::View::ALLOW_FLOATING|Desktop::View::RESERVED_EXTENTS|Desktop::View::INPUT_EXTENTS);const auto surface=g_pSeatManager->m_state.pointerFocus.lock();const auto pointer=Desktop::viewState()->query().type(Desktop::View::VIEW_TYPE_WINDOW).surface(surface).runWindow();std::string history="[";bool first=true;for(const auto& ref:Desktop::History::windowTracker()->fullHistory()){if(!first)history+=",";first=false;history+=id(ref.lock());}history+="]";std::string windows="[";first=true;for(const auto& window:Desktop::windowState()->windows()){if(!first)windows+=",";first=false;windows+=id(window);}windows+="]";return std::format(R"({{"cursor":[{},{}],"hitOwner":{},"pointerOwner":{},"pointerSurfacePresent":{},"nativeFocus":{},"modalTarget":{},"historyOldToNew":{},"windows":{},"sessionLocked":{},"exclusiveLayers":{},"clickMode":{},"constrained":{},"heldButtons":{},"seatGrab":{},"captured":{},"dnd":{},"dragTarget":{}}})",pos.x,pos.y,id(hit),id(pointer),bool(surface),id(Desktop::focusState()->window()),id(target(hit)),history,windows,g_pSessionLockManager->isSessionLocked(),g_pInputManager->m_exclusiveLSes.size(),int(g_pInputManager->getClickMode()),g_pInputManager->isConstrained(),g_pInputManager->hasHeldButtons(),bool(g_pSeatManager->m_seatGrab),PROTO::inputCapture->isCaptured(),PROTO::data->dndActive(),bool(g_layoutManager->dragController()->target()));}
std::string keyboardState(){
    const auto surface=g_pSeatManager->m_state.keyboardFocus.lock();
    const auto seatResource=g_pSeatManager->m_state.keyboardFocusResource.lock();
    const auto owner=Desktop::viewState()->query().type(Desktop::View::VIEW_TYPE_WINDOW).surface(surface).runWindow();
    const auto keyboard=g_pSeatManager->m_keyboard.lock();
    const auto map=keyboard?keyboard->m_xkbKeymap:nullptr;
    return std::format(R"({{"keyboardSurfacePresent":{},"keyboardResourcePresent":{},"keyboardOwner":{},"coreNativeFocus":{},"keyboardPresent":{},"keyboardVirtual":{},"keymapPresent":{},"keymapOverridden":{},"activeLayout":{},"minKeycode":{},"maxKeycode":{}}})",
      bool(surface),bool(seatResource),id(owner),id(Desktop::focusState()->window()),bool(keyboard),
      keyboard?keyboard->isVirtual():false,bool(map),keyboard?keyboard->m_keymapOverridden:false,
      keyboard?keyboard->m_activeLayout:0,map?xkb_keymap_min_keycode(map):0,map?xkb_keymap_max_keycode(map):0);
}
int luaKeyboardState(lua_State* L){const auto value=keyboardState();lua_pushlstring(L,value.data(),value.size());return 1;}
int luaKeyboardEvents(lua_State* L){std::string value="[";bool first=true;for(const auto& event:keyboardEvents){if(!first)value+=",";first=false;value+=event;}value+="]";lua_pushlstring(L,value.data(),value.size());return 1;}
void observeKeyboard(){
    keyboardListener=Event::bus()->m_events.input.keyboard.key.listen([](IKeyboard::SKeyEvent e,Event::SCallbackInfo& info){
      if(keyboardEvents.size()==512)keyboardEvents.erase(keyboardEvents.begin());
      const auto keyboard=g_pSeatManager->m_keyboard.lock();
      const bool symAvailable=keyboard&&keyboard->m_xkbState&&e.keycode<=UINT32_MAX-8;
      const auto sym=symAvailable?xkb_state_key_get_one_sym(keyboard->m_xkbState,e.keycode+8):0;
      keyboardEvents.push_back(std::format(R"({{"sequence":{},"keycode":{},"keyState":{},"timeMs":{},"cancelledAtObservation":{},"seatKeySymAvailableAtObservation":{},"seatKeySymAtObservation":{},"seat":{}}})",
        ++keyboardSequence,e.keycode,int(e.state),e.timeMs,info.cancelled,symAvailable,sym,keyboardState()));
    });
}
int luaState(lua_State* L){const auto value=state();lua_pushlstring(L,value.data(),value.size());return 1;}
int luaEvents(lua_State* L){std::string value="[";bool first=true;for(const auto& event:events){if(!first)value+=",";first=false;value+=event;}value+="]";lua_pushlstring(L,value.data(),value.size());return 1;}
void authorize(){const char* value=getenv("XDG_RUNTIME_DIR");if(!value)throw std::runtime_error("QA runtime missing");const auto path=std::string(value);if(!std::regex_match(path,std::regex("/run/user/"+std::to_string(getuid())+"/wqa/[0-9a-f]{4}")))throw std::runtime_error("Private QA runtime required");struct stat info{};if(lstat(path.c_str(),&info)||!S_ISDIR(info.st_mode)||info.st_uid!=getuid()||(info.st_mode&0777)!=0700)throw std::runtime_error("Owned QA runtime required");std::ifstream file("/proc/self/cgroup");std::string group((std::istreambuf_iterator<char>(file)),{});if(group.find("/qa-harness.slice/qa-harness-")==std::string::npos)throw std::runtime_error("QA scope required");struct rlimit limit{};if(getrlimit(RLIMIT_CORE,&limit)||limit.rlim_cur!=1||limit.rlim_max!=1)throw std::runtime_error("QA core limit required");if(std::string(__hyprland_api_get_hash())!=__hyprland_api_get_client_hash())throw std::runtime_error("Native ABI mismatch");}
}
APICALL EXPORT std::string PLUGIN_API_VERSION(){return HYPRLAND_API_VERSION;}
APICALL EXPORT PLUGIN_DESCRIPTION_INFO PLUGIN_INIT(HANDLE h){authorize();handle=h;HyprlandAPI::addLuaFunction(handle,"qt_modal_probe","keyboard_state",luaKeyboardState);HyprlandAPI::addLuaFunction(handle,"qt_modal_probe","keyboard_events",luaKeyboardEvents);observeKeyboard();HyprlandAPI::addLuaFunction(handle,"qt_modal_probe","state",luaState);HyprlandAPI::addLuaFunction(handle,"qt_modal_probe","events",luaEvents);buttonListener=Event::bus()->m_events.input.mouse.button.listen([](IPointer::SButtonEvent e,Event::SCallbackInfo& info){if(events.size()==256)events.erase(events.begin());events.push_back(std::format(R"({{"button":{},"buttonState":{},"cancelledAtObservation":{},"timeMs":{},"native":{}}})",e.button,int(e.state),info.cancelled,e.timeMs,state()));});return {"qt_modal_probe","Private read-only Qt modal QA observation","QA","1"};}
APICALL EXPORT void PLUGIN_EXIT(){keyboardListener.reset();keyboardEvents.clear();keyboardSequence=0;buttonListener.reset();events.clear();}
