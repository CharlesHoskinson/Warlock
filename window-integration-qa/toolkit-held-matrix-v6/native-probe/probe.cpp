// Private QA observation only: no focus, input cancellation, dispatch or hooks.
#include <hyprland/src/plugins/PluginAPI.hpp>
#include <hyprland/src/desktop/state/WindowState.hpp>
#include <hyprland/src/desktop/state/ViewState.hpp>
#include <hyprland/src/desktop/state/FocusState.hpp>
#include <hyprland/src/desktop/state/LayerState.hpp>
#include <hyprland/src/desktop/view/LayerSurface.hpp>
#include <hyprland/src/render/decorations/DecorationPositioner.hpp>
#include <hyprland/src/desktop/history/WindowHistoryTracker.hpp>
#include <hyprland/src/desktop/view/Window.hpp>
#include <hyprland/src/desktop/view/Group.hpp>
#include <hyprland/src/desktop/view/WLSurface.hpp>
#include <hyprland/src/desktop/Workspace.hpp>
#include <hyprland/src/protocols/XDGShell.hpp>
#include <hyprland/src/protocols/XDGDialog.hpp>
#include <hyprland/src/protocols/core/DataDevice.hpp>
#include <hyprland/src/protocols/InputCapture.hpp>
#include <hyprland/src/managers/input/InputManager.hpp>
#include <hyprland/src/managers/SeatManager.hpp>
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
std::vector<std::string> events;
std::unordered_set<uint32_t> signalDownButtons;
std::string quote(const std::string& value){std::string out="\"";for(const unsigned char c:value){if(c=='\"'||c=='\\'){out+='\\';out+=c;}else if(c<32){out+=std::format("\\u{:04x}",unsigned(c));}else out+=c;}return out+'\"';}
bool modal(const PHLWINDOW& w){if(!w)return false;const auto d=w->m_xdgSurface&&w->m_xdgSurface->m_toplevel?w->m_xdgSurface->m_toplevel->m_dialog.lock():nullptr;return w->isModal()||(d&&d->modal);}
std::string surfaceBox(const PHLWINDOW& w){if(w){const auto surface=w->wlSurface();if(surface){const auto box=surface->getSurfaceBoxGlobal();if(box)return std::format("[{},{},{},{}]",box->x,box->y,box->w,box->h);}}return "null";}
std::string id(const PHLWINDOW& w){return w?std::format(R"({{"address":"0x{:x}","stableId":"{:x}","pid":{},"modal":{},"mapped":{},"hidden":{},"acceptsInput":{},"surfaceBox":{}}})",reinterpret_cast<uintptr_t>(w.get()),w->m_stableID,w->getPID(),modal(w),w->m_isMapped,w->isHidden(),w->acceptsInput(),surfaceBox(w)):"null";}
PHLWINDOW target(PHLWINDOW w){std::unordered_set<Desktop::View::CWindow*> seen;while(Desktop::View::validMapped(w)&&seen.insert(w.get()).second){PHLWINDOW child;for(auto it=Desktop::History::windowTracker()->fullHistory().rbegin();it!=Desktop::History::windowTracker()->fullHistory().rend();++it){const auto c=it->lock();if(Desktop::View::validMapped(c)&&c!=w&&c->m_workspace==w->m_workspace&&c->parent()==w&&modal(c)){child=c;break;}}if(!child)break;w=child;}return w;}
std::string baseState(){const auto pos=g_pInputManager->getMouseCoordsInternal();const auto hit=Desktop::viewState()->hitTest().windowAt(pos,Desktop::View::ALLOW_FLOATING|Desktop::View::RESERVED_EXTENTS|Desktop::View::INPUT_EXTENTS);const auto surface=g_pSeatManager->m_state.pointerFocus.lock();const auto pointer=Desktop::viewState()->query().type(Desktop::View::VIEW_TYPE_WINDOW).surface(surface).runWindow();std::string history="[";bool first=true;for(const auto& ref:Desktop::History::windowTracker()->fullHistory()){if(!first)history+=",";first=false;history+=id(ref.lock());}history+="]";std::string windows="[";first=true;for(const auto& window:Desktop::windowState()->windows()){if(!first)windows+=",";first=false;windows+=id(window);}windows+="]";return std::format(R"({{"cursor":[{},{}],"hitOwner":{},"pointerOwner":{},"pointerSurfacePresent":{},"nativeFocus":{},"modalTarget":{},"historyOldToNew":{},"windows":{},"sessionLocked":{},"exclusiveLayers":{},"clickMode":{},"constrained":{},"heldButtons":{},"seatGrab":{},"captured":{},"dnd":{},"dragTarget":{}}})",pos.x,pos.y,id(hit),id(pointer),bool(surface),id(Desktop::focusState()->window()),id(target(hit)),history,windows,g_pSessionLockManager->isSessionLocked(),g_pInputManager->m_exclusiveLSes.size(),int(g_pInputManager->getClickMode()),g_pInputManager->isConstrained(),g_pInputManager->hasHeldButtons(),bool(g_pSeatManager->m_seatGrab),PROTO::inputCapture->isCaptured(),PROTO::data->dndActive(),bool(g_layoutManager->dragController()->target()));}
// Additional public read-only authority: exact target, mode, held IDs, real groups.
std::string state(){
 const auto& controller=g_layoutManager->dragController();
 const auto drag=controller->target();
 std::string held="[";bool first=true;
 for(const auto button:signalDownButtons){if(!first)held+=",";first=false;held+=std::to_string(button);}held+="]";
 std::string groups="[";first=true;
 for(const auto& weak:Desktop::View::groups()){
  const auto group=weak.lock();if(!group)continue;
  if(!first){groups+=",";}
  first=false;std::string members="[";bool memberFirst=true;
  for(const auto& ref:group->windows()){if(!memberFirst)members+=",";memberFirst=false;members+=id(ref.lock());}members+="]";
  groups+=std::format(R"({{"head":{},"current":{},"members":{},"locked":{},"denied":{}}})",id(group->head()),id(group->current()),members,group->locked(),group->denied());
 }groups+="]";
 std::string decorations="[";bool firstDecoration=true;
 for(const auto& window:Desktop::windowState()->windows()){
  if(!Desktop::View::validMapped(window))continue;
  for(const auto& owned:window->m_windowDecorations){
   const auto decoration=owned.get();if(!decoration)continue;
   const auto kind=decoration->getDecorationType();
   if(decoration->getDisplayName()!="Hyprbar" && kind!=DECORATION_GROUPBAR)continue;
   const auto box=g_pDecorationPositioner->getWindowDecorationBox(decoration);
   if(!firstDecoration){decorations+=",";}firstDecoration=false;
   decorations+=std::format(R"({{"window":{},"name":{},"type":{},"flags":{},"box":[{},{},{},{}]}})",id(window),quote(decoration->getDisplayName()),int(kind),decoration->getDecorationFlags(),box.x,box.y,box.w,box.h);
  }
 }
 decorations+="]";std::string layers="[";bool firstLayer=true;
 const auto pointerSurface=g_pSeatManager->m_state.pointerFocus.lock();
 const auto pointerLayer=Desktop::viewState()->query().type(Desktop::View::VIEW_TYPE_LAYER_SURFACE).surface(pointerSurface).runLayer();
 std::string pointerOwner="null";
 for(const auto& layer:Desktop::layerState()->layers()){
  const auto box=layer->logicalBox();
  const auto row=std::format(R"({{"address":"0x{:x}","pid":{},"namespace":{},"mapped":{},"visible":{},"box":{}}})",reinterpret_cast<uintptr_t>(layer.get()),layer->getPID(),quote(layer->m_namespace),layer->m_mapped,layer->visible(),box?std::format("[{},{},{},{}]",box->x,box->y,box->w,box->h):"null");
  if(!firstLayer){layers+=",";}firstLayer=false;layers+=row;if(layer==pointerLayer)pointerOwner=row;
 }layers+="]";
 auto result=baseState();result.pop_back();
 result+=std::format(R"(,"coreDragTarget":{},"coreDragTargetType":{},"coreDragMode":{},"coreExclusiveDeviceGrab":{},"signalDownButtonIds":{},"groups":{}}})",id(drag?drag->window():nullptr),drag?int(drag->type()):-1,int(controller->mode()),controller->exclusiveDeviceGrab(),held,groups);
 result.pop_back();result+=",\"decorationAllocations\":"+decorations+",\"layers\":"+layers+",\"pointerLayerOwner\":"+pointerOwner+"}";
 return result;
}
int luaState(lua_State* L){const auto value=state();lua_pushlstring(L,value.data(),value.size());return 1;}
int luaEvents(lua_State* L){std::string value="[";bool first=true;for(const auto& event:events){if(!first)value+=",";first=false;value+=event;}value+="]";lua_pushlstring(L,value.data(),value.size());return 1;}
void authorize(){const char* value=getenv("XDG_RUNTIME_DIR");if(!value)throw std::runtime_error("QA runtime missing");const auto path=std::string(value);if(!std::regex_match(path,std::regex("/run/user/"+std::to_string(getuid())+"/wqa/[0-9a-f]{4}")))throw std::runtime_error("Private QA runtime required");struct stat info{};if(lstat(path.c_str(),&info)||!S_ISDIR(info.st_mode)||info.st_uid!=getuid()||(info.st_mode&0777)!=0700)throw std::runtime_error("Owned QA runtime required");std::ifstream file("/proc/self/cgroup");std::string group((std::istreambuf_iterator<char>(file)),{});if(group.find("/qa-harness.slice/qa-harness-")==std::string::npos)throw std::runtime_error("QA scope required");struct rlimit limit{};if(getrlimit(RLIMIT_CORE,&limit)||limit.rlim_cur!=1||limit.rlim_max!=1)throw std::runtime_error("QA core limit required");if(std::string(__hyprland_api_get_hash())!=__hyprland_api_get_client_hash())throw std::runtime_error("Native ABI mismatch");}
}
APICALL EXPORT std::string PLUGIN_API_VERSION(){return HYPRLAND_API_VERSION;}
APICALL EXPORT PLUGIN_DESCRIPTION_INFO PLUGIN_INIT(HANDLE h){authorize();handle=h;HyprlandAPI::addLuaFunction(handle,"toolkit_held_probe","state",luaState);HyprlandAPI::addLuaFunction(handle,"toolkit_held_probe","events",luaEvents);buttonListener=Event::bus()->m_events.input.mouse.button.listen([](IPointer::SButtonEvent e,Event::SCallbackInfo& info){if(e.state==WL_POINTER_BUTTON_STATE_PRESSED){signalDownButtons.insert(e.button);}else{signalDownButtons.erase(e.button);}
if(events.size()==256){events.erase(events.begin());}
events.push_back(std::format(R"({{"button":{},"buttonState":{},"cancelledAtObservation":{},"timeMs":{},"native":{}}})",e.button,int(e.state),info.cancelled,e.timeMs,state()));});return {"toolkit_held_probe","Private read-only exact held-gesture/group QA observation","QA","1"};}
APICALL EXPORT void PLUGIN_EXIT(){buttonListener.reset();events.clear();signalDownButtons.clear();}
