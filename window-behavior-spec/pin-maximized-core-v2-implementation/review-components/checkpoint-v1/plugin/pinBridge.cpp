#include "pinBridge.hpp"
#include "PinAction.hpp"
#include "PinLifetime.hpp"
#include "PinStacking.hpp"
#include "PinBoundary.hpp"
#include "barDeco.hpp"
#include <hyprland/src/Compositor.hpp>
#include <hyprland/src/config/shared/actions/ConfigActions.hpp>
#include <hyprland/src/config/lua/objects/LuaWindow.hpp>
#include <hyprland/src/desktop/state/WindowState.hpp>
#include <hyprland/src/desktop/state/FocusState.hpp>
#include <hyprland/src/managers/SeatManager.hpp>
#include <hyprland/src/protocols/XDGShell.hpp>
#include <hyprland/src/protocols/XDGDialog.hpp>
#include <hyprland/src/managers/fullscreen/FullscreenController.hpp>
#include <hyprland/src/managers/eventLoop/EventLoopManager.hpp>
#include <hyprland/src/render/Renderer.hpp>
#include <hyprland/src/event/EventBus.hpp>
#include "PinJson.hpp"
#include <hyprland/src/desktop/state/pin/NativePinState.hpp>
#include <hyprland/src/desktop/state/pin/CorePolicyBuild.hpp>
#include <fstream>
#include <sstream>
#include <map>
#include <set>
#include <limits>
#include <sys/random.h>
#include <unistd.h>
extern "C" {
#include <lua.h>
}
using namespace Desktop::View;
namespace {
using Json=PinJson;
struct Lease {PHLWINDOWREF owner;uint64_t generation=0,epoch=0,operation=0;Time::steady_tp started;};
PinLifetime<PHLWINDOW,PHLWINDOWREF> identities;
std::map<CWindow*,Lease> feedback;
std::set<CWindow*> busy;
std::vector<Json> results;
uint64_t epoch=1,nextOperation=0;
std::string signature,compositorStart,incarnation;
bool initialized=false,feedbackEnabled=false;
bool stackingActive=false;
PinStacking::Report lastStack;
SP<CEventLoopTimer> timer;
CHyprSignalListener opened,closed,pinChanged,floatingChanged,fullscreenChanged,workspaceChanged;
bool eligibleOwner(const PHLWINDOW&w){return validMapped(w)&&!w->isHidden()&&w->m_workspace&&!w->m_workspace->m_isSpecialWorkspace;}
uint64_t lifetime(const PHLWINDOW&w,bool create){return identities.query(w,validMapped(w),create);}
void retireFeedback(const PHLWINDOW&owner){
 if(!owner)return;
 const auto found=feedback.find(owner.get());if(found==feedback.end())return;
 feedback.erase(found);
 if(eligibleOwner(owner))g_pHyprRenderer->damageWindow(owner,true);
 if(timer&&feedback.empty())timer->updateTimeout(std::nullopt);
}

Json token(const PHLWINDOW&w){
 const auto generation=lifetime(w,true);
 if(!initialized||!w||!generation||!epoch)return nullptr;
 return {{"address",std::format("0x{:x}",reinterpret_cast<uintptr_t>(w.get()))},{"stableId",std::format("{:x}",w->m_stableID)},{"pid",w->getPID()},
  {"session",signature},{"compositorPid",getpid()},{"compositorStart",compositorStart},{"incarnation",incarnation},{"epoch",std::to_string(epoch)},{"generation",std::to_string(generation)}};
}
PinAction::Snapshot sample(const PHLWINDOW&w){
 PinAction::Snapshot s;s.epoch=epoch;s.session=signature;s.incarnation=incarnation;
 if(!w)return s;
 s.address=reinterpret_cast<uintptr_t>(w.get());s.stable=w->m_stableID;s.pid=w->getPID();s.lifetime=lifetime(w,false);
 s.live=initialized&&epoch&&s.lifetime&&validMapped(w);s.normal=eligibleOwner(w);s.floating=w->m_isFloating;s.pinned=w->m_pinned;s.fullscreen=Fullscreen::controller()->isFullscreen(w);
 const auto modes=Fullscreen::controller()->getFullscreenModes(w);const auto restore=Desktop::Pin::state()->snapshot(w);
 s.internalMode=modes.internal;s.clientMode=modes.client;s.capability=Desktop::Pin::capabilityVersion();s.nativeAdmission=Desktop::Pin::state()->admits(w);
 s.restoreKnown=restore.valid;s.restoreOrigin=restore.pinOrigin;s.restoreManaged=restore.pinManaged;s.restoreFloating=restore.floating;s.layoutHandled=restore.layoutHandled;
 s.restoreGeneration=restore.generation;s.target=restore.target;s.layoutTarget=restore.layoutTarget;s.space=restore.space;
 s.workspace=reinterpret_cast<uintptr_t>(w->m_workspace.get());s.monitor=reinterpret_cast<uintptr_t>(w->m_monitor.lock().get());
 const auto position=w->position(IGeometric::GEOMETRIC_CURRENT);const auto size=w->size(IGeometric::GEOMETRIC_CURRENT);s.geometry={position.x,position.y,size.x,size.y};
 const auto&b=restore.box;s.restoreGeometry={b.logicalBox.x,b.logicalBox.y,b.logicalBox.w,b.logicalBox.h,b.visualBox.x,b.visualBox.y,b.visualBox.w,b.visualBox.h};return s;
}
Json snapshotJson(const PinAction::Snapshot&s){
 std::vector<Json> geometry,restoreGeometry;
 for(auto value:s.geometry)geometry.emplace_back(std::format("{:.17g}",value));
 for(auto value:s.restoreGeometry)restoreGeometry.emplace_back(std::format("{:.17g}",value));
 return {{"address",std::format("0x{:x}",s.address)},{"stableId",std::format("{:x}",s.stable)},{"pid",s.pid},{"epoch",std::to_string(s.epoch)},{"generation",std::to_string(s.lifetime)},{"session",s.session},{"incarnation",s.incarnation},{"live",s.live},{"normal",s.normal},{"floating",s.floating},{"pinned",s.pinned},{"fullscreen",s.fullscreen},
 {"internalMode",s.internalMode},{"clientMode",s.clientMode},{"capability",static_cast<int>(s.capability)},{"nativeAdmission",s.nativeAdmission},{"restoreKnown",s.restoreKnown},{"restoreOrigin",s.restoreOrigin},{"restoreManaged",s.restoreManaged},{"restoreFloating",s.restoreFloating},{"layoutHandled",s.layoutHandled},{"restoreGeneration",std::to_string(s.restoreGeneration)},
 {"target",std::format("0x{:x}",s.target)},{"layoutTarget",std::format("0x{:x}",s.layoutTarget)},{"space",std::format("0x{:x}",s.space)},{"workspace",std::format("0x{:x}",s.workspace)},{"monitor",std::format("0x{:x}",s.monitor)},{"geometry",geometry},{"restoreGeometry",restoreGeometry}};
}
std::string phaseName(PinAction::Phase p){switch(p){case PinAction::Phase::Validate:return "validate";case PinAction::Phase::Float:return "float";case PinAction::Phase::Pin:return "pin";case PinAction::Phase::Raise:return "raise";case PinAction::Phase::Complete:return "complete";}return "unknown";}
Json reportJson(const PinAction::Report&r,const Json&captured){return {{"schema",2},{"corePolicyBuild",std::string(Desktop::Pin::policyBuildIdentity())},{"ok",r.ok},{"phase",phaseName(r.phase)},{"reason",r.reason},{"actionsInvoked",r.actionsInvoked},{"possiblePartialOutcome",!r.ok&&r.actionsInvoked},{"captured",captured},{"before",snapshotJson(r.before)},{"after",snapshotJson(r.after)},{"desiredPinned",r.desired},{"backend",{{"ok",r.backend.ok},{"message",r.backend.reason},{"level",r.backend.level},{"code",r.backend.code}}}};}
PinAction::Result result(const Config::Actions::ActionResult&r){if(r)return {true,{},{},{}};return {false,r.error().message,Config::toString(r.error().level),Config::toString(r.error().code)};}
struct FocusWitness{
 PHLWINDOW window;
 SP<CWLSurfaceResource> coreSurface,keyboardSurface;
 SP<CWLSeatResource> keyboardResource;
 static FocusWitness current(){return {Desktop::focusState()->window(),Desktop::focusState()->surface(),g_pSeatManager->m_state.keyboardFocus.lock(),g_pSeatManager->m_state.keyboardFocusResource.lock()};}
 bool operator==(const FocusWitness&)const=default;
};
struct Adapter{
 PHLWINDOW owner;
 const FocusWitness&focus;
 bool invoked=false;
 PinAction::Phase phase=PinAction::Phase::Validate;
 PinAction::Snapshot snapshot(){return sample(owner);}
 PinAction::Result floatWindow(){if(focus!=FocusWitness::current())return {false,"Captured core/Seat focus changed before float","error","focus"};invoked=true;phase=PinAction::Phase::Float;return result(Config::Actions::floatWindow(Config::Actions::TOGGLE_ACTION_ENABLE,owner));}
 PinAction::Result pinWindow(bool value){if(focus!=FocusWitness::current())return {false,"Captured core/Seat focus changed before pin","error","focus"};invoked=true;phase=PinAction::Phase::Pin;return result(Config::Actions::pinWindow(value?Config::Actions::TOGGLE_ACTION_ENABLE:Config::Actions::TOGGLE_ACTION_DISABLE,owner));}
 PinAction::Result raiseWindow(){if(focus!=FocusWitness::current())return {false,"Captured core/Seat focus changed before raise","error","focus"};invoked=true;phase=PinAction::Phase::Raise;Desktop::windowState()->raise(owner);if(lastStack.ok&&focus==FocusWitness::current())return {true,{},{},{}};return {false,"Owning raise did not confirm protected order/core/Seat focus","error","stack"};}
};
PinStacking::Snapshot stackSnapshot(){
 PinStacking::Snapshot s;s.epoch=initialized?epoch:0;
 const auto focus=Desktop::focusState()->window();s.focus=reinterpret_cast<uintptr_t>(focus.get());
 s.coreSurface=reinterpret_cast<uintptr_t>(Desktop::focusState()->surface().get());s.keyboardSurface=reinterpret_cast<uintptr_t>(g_pSeatManager->m_state.keyboardFocus.lock().get());s.keyboardResource=reinterpret_cast<uintptr_t>(g_pSeatManager->m_state.keyboardFocusResource.lock().get());s.pointerSurface=reinterpret_cast<uintptr_t>(g_pSeatManager->m_state.pointerFocus.lock().get());
 for(const auto&owner:Desktop::windowState()->windows()){
  if(!validMapped(owner))continue;
  PinStacking::Node n;n.key=reinterpret_cast<uintptr_t>(owner.get());n.stable=owner->m_stableID;n.generation=lifetime(owner,false);n.pid=owner->getPID();
  const auto parent=owner->parent();n.parent=reinterpret_cast<uintptr_t>(parent.get());n.workspace=reinterpret_cast<uintptr_t>(owner->m_workspace.get());n.monitor=reinterpret_cast<uintptr_t>(owner->m_monitor.lock().get());
  n.eligible=eligibleOwner(owner);n.pinned=owner->m_pinned;n.floating=owner->m_isFloating;n.x11=owner->m_isX11;n.fullscreen=Fullscreen::controller()->isFullscreen(owner);
  const auto modes=Fullscreen::controller()->getFullscreenModes(owner);n.internalMode=modes.internal;n.clientMode=modes.client;
  n.nativeAdmission=Desktop::Pin::state()->admits(owner);n.restoreOrigin=Desktop::Pin::state()->maxOrigin(owner);n.coreProtected=Desktop::Pin::effective(owner);
  const auto dialog=owner->m_xdgSurface&&owner->m_xdgSurface->m_toplevel?owner->m_xdgSurface->m_toplevel->m_dialog.lock():nullptr;
  n.modal=owner->isModal()||(dialog&&dialog->modal);
  const auto position=owner->position(IGeometric::GEOMETRIC_CURRENT);const auto size=owner->size(IGeometric::GEOMETRIC_CURRENT);n.geometry={position.x,position.y,size.x,size.y};s.nodes.push_back(n);
 }
 return s;
}
struct StackAdapter{
 std::map<PinStacking::Key,PHLWINDOW> owners;
 const FocusWitness focus=FocusWitness::current();
 const SP<CWLSurfaceResource> pointer=g_pSeatManager->m_state.pointerFocus.lock();
 StackAdapter(){for(const auto&owner:Desktop::windowState()->windows())if(validMapped(owner))owners.emplace(reinterpret_cast<uintptr_t>(owner.get()),owner);}
 PinStacking::Snapshot snapshot(){return stackSnapshot();}
 bool raise(PinStacking::Key key){const auto found=owners.find(key);if(found==owners.end()||!eligibleOwner(found->second)||!lifetime(found->second,false))return false;Desktop::windowState()->raise(found->second);return true;}
};
void clearFeedback(){
 const auto old=feedback;feedback.clear();
 if(timer)timer->updateTimeout(std::nullopt);
 for(const auto&[_,lease]:old){const auto owner=lease.owner.lock();if(eligibleOwner(owner))g_pHyprRenderer->damageWindow(owner,true);}
}
void tick(SP<CEventLoopTimer> self){
 const auto captured=feedback;const auto now=Time::steadyNow();
 for(const auto&[key,lease]:captured){
  auto current=feedback.find(key);if(current==feedback.end()||current->second.operation!=lease.operation)continue;
  const auto owner=lease.owner.lock();
  const bool valid=initialized&&feedbackEnabled&&lease.epoch==epoch&&eligibleOwner(owner)&&!Fullscreen::controller()->isFullscreen(owner,Fullscreen::FSMODE_FULLSCREEN)&&lifetime(owner,false)==lease.generation;
  if(!valid||now<lease.started||now-lease.started>=std::chrono::milliseconds(220))feedback.erase(key);
  if(eligibleOwner(owner))g_pHyprRenderer->damageWindow(owner,true);
 }
 self->updateTimeout(feedback.empty()?std::nullopt:std::optional<Time::steady_dur>{std::chrono::milliseconds(16)});
}
Json perform(const PHLWINDOW&owner){
 const auto focus=FocusWitness::current();
 const auto captured=token(owner);PinAction::Report report;report.before=sample(owner);report.after=report.before;
 if(captured.is_null()){report.reason="Exact native lifetime unavailable";}
 else if(busy.contains(owner.get())){report.reason="Same captured owner pin operation already active";}
 else if(stackingActive){report.reason="Pin operation inside captured stacking callback refused";}
 else if(nextOperation==std::numeric_limits<uint64_t>::max()){report.reason="Pin operation generation exhausted";}
 else{
  const auto operation=++nextOperation;busy.insert(owner.get());
  struct Release{CWindow*owner;~Release(){busy.erase(owner);}}release{owner.get()};
  // Repeated attempts retire any old feedback even when the new action refuses.
  const auto old=feedback.find(owner.get());if(old!=feedback.end()){feedback.erase(old);if(eligibleOwner(owner))g_pHyprRenderer->damageWindow(owner,true);}
  Adapter adapter{owner,focus};
  try{
   report=PinAction::executeConservative(adapter,report.before);
   if(report.ok){
    repairPinStacking();const auto after=sample(owner);
    if(!lastStack.ok||focus!=FocusWitness::current()||!PinAction::completedState(report.before,after,report.desired)){report.ok=false;report.phase=PinAction::Phase::Raise;report.reason="Pin action reached; protected order/exact owner/core or Seat focus confirmation refused";}
    report.after=after;
   }
  }catch(const std::exception&error){report.ok=false;report.phase=adapter.phase;report.actionsInvoked=adapter.invoked;report.reason=std::string("Native observation failed: ")+error.what();}
  catch(...){report.ok=false;report.phase=adapter.phase;report.actionsInvoked=adapter.invoked;report.reason="Unknown native observation failure";}
  if(report.ok&&feedbackEnabled&&timer){feedback[owner.get()]={owner,report.after.lifetime,epoch,operation,Time::steadyNow()};g_pHyprRenderer->damageWindow(owner,true);timer->updateTimeout(std::chrono::milliseconds(16));}
 }
 const auto value=reportJson(report,captured);if(results.size()==64)results.erase(results.begin());results.push_back(value);return value;
}
PHLWINDOW luaOwner(lua_State*state){
 PHLWINDOW selected;
 if(lua_gettop(state)==1&&lua_type(state,1)==LUA_TUSERDATA&&lua_getmetatable(state,1)){
  const int supplied=lua_gettop(state);
  for(const auto&owner:Desktop::windowState()->windows()){
   if(!owner)continue;
   Config::Lua::Objects::CLuaWindow::push(state,owner);const int candidate=lua_gettop(state);
   if(!lua_getmetatable(state,candidate)){lua_pop(state,1);continue;}
   const bool native=lua_rawequal(state,supplied,-1);lua_pop(state,1);
   const bool exact=native&&lua_compare(state,1,candidate,LUA_OPEQ);lua_pop(state,1);
   if(exact){selected=owner;break;}
  }
 }
 return selected;
}
int pushJson(lua_State*state,const Json&value){const auto text=value.dump();lua_pushlstring(state,text.data(),text.size());return 1;}
Json requestToken(lua_State*state){
 if(lua_gettop(state)!=1||lua_type(state,1)!=LUA_TTABLE)throw std::runtime_error("pin_request requires one full identity table");
 const std::set<std::string> names{"address","stableId","pid","session","compositorPid","compositorStart","incarnation","epoch","generation"};
 Json value=Json::object();lua_pushnil(state);
 while(lua_next(state,1)){
  if(lua_type(state,-2)!=LUA_TSTRING){lua_pop(state,2);throw std::runtime_error("Pin identity key must be exact string");}
  size_t length=0;const char*data=lua_tolstring(state,-2,&length);const std::string key(data,length);
  if(!names.contains(key)){lua_pop(state,2);throw std::runtime_error("Unknown pin identity field");}
  if(key=="pid"||key=="compositorPid"){
   if(!lua_isinteger(state,-1)||lua_tointeger(state,-1)<=0||lua_tointeger(state,-1)>std::numeric_limits<int>::max()){lua_pop(state,2);throw std::runtime_error("Exact positive integer PID required");}
   value[key]=static_cast<int>(lua_tointeger(state,-1));
  }else{
   if(lua_type(state,-1)!=LUA_TSTRING){lua_pop(state,2);throw std::runtime_error("Exact pin identity string required");}
   data=lua_tolstring(state,-1,&length);value[key]=std::string(data,length);
  }
  lua_pop(state,1);
 }
 if(value.size()!=names.size()){throw std::runtime_error("Incomplete pin identity; no active fallback");}
 return value;
}
}
void initPinBridge(){
 if(Desktop::Pin::capabilityVersion()!=1||Desktop::Pin::policyBuildIdentity()!=Desktop::Pin::NATIVE_PIN_CORE_SOURCE_ID)throw std::runtime_error("Exact native MAX core policy build unavailable");
 if(initialized)throw std::runtime_error("Pin bridge already initialized");
 signature=g_pCompositor->m_instanceSignature;if(signature.empty())throw std::runtime_error("Actual compositor signature unavailable");
 std::ifstream file("/proc/self/stat");std::string line;std::getline(file,line);const auto close=line.rfind(')');if(close==std::string::npos)throw std::runtime_error("Compositor start unavailable");
 std::istringstream fields(line.substr(close+2));std::string value;for(int i=0;i<=19;++i){if(!(fields>>value))throw std::runtime_error("Compositor start incomplete");}compositorStart=value;
 unsigned char random[16];if(getrandom(random,sizeof(random),0)!=static_cast<ssize_t>(sizeof(random)))throw std::runtime_error("Fresh plugin incarnation unavailable");incarnation.clear();for(auto byte:random)incarnation+=std::format("{:02x}",byte);
 epoch=1;nextOperation=0;identities.clear();feedbackEnabled=false;initialized=true;
 try{
  for(const auto&owner:Desktop::windowState()->windows())lifetime(owner,true);
  opened=Event::bus()->m_events.window.open.listen([](PHLWINDOW owner){identities.opened(owner,validMapped(owner));repairPinStacking();});
  closed=Event::bus()->m_events.window.close.listen([](PHLWINDOW owner){identities.closed(owner);retireFeedback(owner);repairPinStacking();});
  pinChanged=Event::bus()->m_events.window.pin.listen([](PHLWINDOW owner){retireFeedback(owner);repairPinStacking();});
  floatingChanged=Event::bus()->m_events.window.floating.listen([](PHLWINDOW owner){retireFeedback(owner);repairPinStacking();});
  fullscreenChanged=Event::bus()->m_events.window.fullscreen.listen([](PHLWINDOW owner){retireFeedback(owner);repairPinStacking();});
  workspaceChanged=Event::bus()->m_events.window.moveToWorkspace.listen([](PHLWINDOW owner,PHLWORKSPACE workspace){if(!workspace||workspace->m_isSpecialWorkspace||!eligibleOwner(owner))retireFeedback(owner);repairPinStacking();});
  timer=makeShared<CEventLoopTimer>(std::nullopt,[](SP<CEventLoopTimer> self,void*){tick(self);},nullptr);g_pEventLoopManager->addTimer(timer);
  repairPinStacking();
 }catch(...){exitPinBridge();throw;}
}
void exitPinBridge(){
 opened.reset();closed.reset();pinChanged.reset();floatingChanged.reset();fullscreenChanged.reset();workspaceChanged.reset();clearFeedback();if(timer){timer->cancel();g_pEventLoopManager->removeTimer(timer);timer.reset();}identities.clear();busy.clear();results.clear();initialized=false;lastStack={};stackingActive=false;
}
void reloadPinBridge(){clearFeedback();if(epoch==std::numeric_limits<uint64_t>::max())epoch=0;else if(epoch)++epoch;}
bool toggleCapturedPin(const PHLWINDOW&owner,std::string&reason){try{const auto report=perform(owner);reason=report.at("reason").get<std::string>();return report.at("ok").get<bool>();}catch(...){reason="Pin outcome uncertain after native observation failure; no retry";return false;}}
float pinFeedbackAlpha(const PHLWINDOW&owner){
 if(!initialized||!feedbackEnabled||!owner)return 1.F;
 const auto found=feedback.find(owner.get());if(found==feedback.end())return 1.F;
 const auto&lease=found->second;const auto now=Time::steadyNow();
 if(!eligibleOwner(owner)||Fullscreen::controller()->isFullscreen(owner,Fullscreen::FSMODE_FULLSCREEN)||lease.owner.lock()!=owner||lease.epoch!=epoch||lifetime(owner,false)!=lease.generation||now<lease.started)return 1.F;
 const auto elapsed=std::chrono::duration<double,std::milli>(now-lease.started).count();if(elapsed>=220.)return 1.F;return static_cast<float>(0.65+0.35*elapsed/220.);
}
int luaPinCapturedWindow(lua_State*state){
 try{const auto value=perform(luaOwner(state));lua_pushboolean(state,value.at("ok").get<bool>());const auto reason=value.at("reason").get<std::string>();lua_pushlstring(state,reason.data(),reason.size());pushJson(state,value);return 3;}
 catch(...){lua_pushboolean(state,false);lua_pushliteral(state,"Pin outcome uncertain; no retry");lua_pushliteral(state,"{\"ok\":false,\"phase\":\"unknown\",\"reason\":\"Pin outcome uncertain; no retry\",\"actionsInvoked\":true,\"possiblePartialOutcome\":true}");return 3;}
}
int luaPinIdentity(lua_State*state){return pushJson(state,token(luaOwner(state)));}
int luaPinRequest(lua_State*state){
 bool enteredPerform=false;
 try{
  const auto captured=requestToken(state);PHLWINDOW selected;
  for(const auto&owner:Desktop::windowState()->windows())if(token(owner)==captured){selected=owner;break;}
  if(!selected)return pushJson(state,{{"ok",false},{"phase","validate"},{"reason","Stale or foreign complete pin identity"},{"actionsInvoked",false},{"possiblePartialOutcome",false}});
  enteredPerform=true;return pushJson(state,perform(selected));
 }catch(const std::exception&error){return pushJson(state,{{"ok",false},{"phase",enteredPerform?"unknown":"validate"},{"reason",error.what()},{"actionsInvoked",enteredPerform},{"possiblePartialOutcome",enteredPerform}});}
 catch(...){return pushJson(state,{{"ok",false},{"phase",enteredPerform?"unknown":"validate"},{"reason","Unknown native pin failure"},{"actionsInvoked",enteredPerform},{"possiblePartialOutcome",enteredPerform}});}
}
int luaPinCapture(lua_State*state){
 try{
  if(lua_gettop(state)!=1||lua_type(state,1)!=LUA_TTABLE)throw std::runtime_error("One exact public identity table required");
  const std::set<std::string> names{"address","stableId","pid"};std::set<std::string> seen;
  std::string address,stable;int pid=0;lua_pushnil(state);
  while(lua_next(state,1)){
   if(lua_type(state,-2)!=LUA_TSTRING){lua_pop(state,2);throw std::runtime_error("Exact public key string required");}
   size_t length=0;const char*bytes=lua_tolstring(state,-2,&length);const std::string key(bytes,length);
   if(!names.contains(key)||!seen.insert(key).second){lua_pop(state,2);throw std::runtime_error("Unknown public identity field");}
   if(key=="address"||key=="stableId"){
    if(lua_type(state,-1)!=LUA_TSTRING){lua_pop(state,2);throw std::runtime_error("Public address string required");}
    bytes=lua_tolstring(state,-1,&length);if(key=="address")address=std::string(bytes,length);else stable=std::string(bytes,length);
   }else{
    if(!lua_isinteger(state,-1)||lua_tointeger(state,-1)<=0||(key=="pid"&&lua_tointeger(state,-1)>std::numeric_limits<int>::max())){lua_pop(state,2);throw std::runtime_error("Exact safe public integer required");}
    pid=static_cast<int>(lua_tointeger(state,-1));
   }
   lua_pop(state,1);
  }
  if(seen!=names)throw std::runtime_error("Incomplete public owner; no active fallback");
  PHLWINDOW selected;
  for(const auto&owner:Desktop::windowState()->windows())if(eligibleOwner(owner)&&std::format("{:x}",owner->m_stableID)==stable&&owner->getPID()==pid&&address==std::format("0x{:x}",reinterpret_cast<uintptr_t>(owner.get()))){if(selected)throw std::runtime_error("Ambiguous public owner");selected=owner;}
  return pushJson(state,selected?token(selected):Json(nullptr));
 }catch(...){return pushJson(state,nullptr);}
}
int luaPinEvents(lua_State*state){return pushJson(state,results);}
int luaPinFeedbackEnabled(lua_State*state){
 if(lua_gettop(state)!=1||lua_type(state,1)!=LUA_TBOOLEAN){lua_pushboolean(state,false);return 1;}
 feedbackEnabled=lua_toboolean(state,1);if(!feedbackEnabled)clearFeedback();lua_pushboolean(state,true);return 1;
}
void repairPinStacking() noexcept{
 if(!initialized||stackingActive)return;
 stackingActive=true;struct Release{~Release(){stackingActive=false;}}release;
 try{StackAdapter adapter;lastStack=PinStacking::enforce(adapter);
  const auto plan=PinStacking::makePlan(adapter.snapshot());std::vector<PinStacking::Key> actual;
  for(const auto&owner:Desktop::Pin::band())actual.push_back(reinterpret_cast<uintptr_t>(owner.get()));
  if(!plan.ok||actual!=plan.order){lastStack.ok=false;lastStack.reason="Shared core render/hit band disagrees with protected native order";}
 }
 catch(const std::exception&error){lastStack.ok=false;lastStack.actionsInvoked=true;try{lastStack.reason=error.what();}catch(...) {}}
 catch(...){lastStack.ok=false;lastStack.actionsInvoked=true;}
}
int luaPinStackState(lua_State*state){
 const auto keyboard=g_pSeatManager->m_keyboard.lock();
 const auto current=stackSnapshot();const auto plan=PinStacking::makePlan(current);std::vector<Json> rows;
 for(const auto&n:current.nodes)rows.push_back({{"address",std::format("0x{:x}",n.key)},{"stableId",std::format("{:x}",n.stable)},{"pid",n.pid},{"generation",std::to_string(n.generation)},{"parent",std::format("0x{:x}",n.parent)},{"workspace",std::format("0x{:x}",n.workspace)},{"monitor",std::format("0x{:x}",n.monitor)},{"eligible",n.eligible},{"pinned",n.pinned},{"floating",n.floating},{"modal",n.modal},{"x11",n.x11},{"fullscreen",n.fullscreen},{"internalMode",n.internalMode},{"clientMode",n.clientMode},{"nativeAdmission",n.nativeAdmission},{"restoreOrigin",n.restoreOrigin},{"coreProtected",n.coreProtected},{"geometry",std::format("{},{},{},{}",n.geometry[0],n.geometry[1],n.geometry[2],n.geometry[3])}});
 std::vector<Json> leases;
 for(const auto&[_,lease]:feedback){const auto owner=lease.owner.lock();if(!owner)continue;leases.push_back({{"captured",token(owner)},{"generation",std::to_string(lease.generation)},{"epoch",std::to_string(lease.epoch)},{"operation",std::to_string(lease.operation)},{"alpha",std::format("{}",pinFeedbackAlpha(owner))}});}
 return pushJson(state,{{"session",signature},{"compositorPid",getpid()},{"compositorStart",compositorStart},{"incarnation",incarnation},{"epoch",std::to_string(current.epoch)},{"focus",std::format("0x{:x}",current.focus)},{"keyboardPresent",bool(keyboard)},{"keyboardModifiers",keyboard?static_cast<int>(keyboard->getModifiers()):0},{"order",rows},{"feedback",leases},{"feedbackEnabled",feedbackEnabled},{"planValid",plan.ok},{"satisfied",PinStacking::satisfied(current,plan)},{"lastPassComplete",lastStack.ok},{"lastPassActionsInvoked",lastStack.actionsInvoked},{"lastPassCalls",static_cast<int>(lastStack.calls)},{"reason",lastStack.reason}});
}
int luaPinBarState(lua_State*state){
 std::vector<Json> rows;
 if(g_pGlobalState)for(const auto&reference:g_pGlobalState->bars){
  // Unique-backed bar is only borrowed synchronously; never weak.lock().
  const auto bar=reference.get();if(!bar)continue;const auto owner=bar->getOwner();const auto captured=token(owner);if(captured.is_null())continue;
  std::vector<Json> boxes;for(const auto&box:bar->pinButtonBoxes())boxes.push_back(std::vector<Json>{std::format("{:.17g}",box.x),std::format("{:.17g}",box.y),std::format("{:.17g}",box.w),std::format("{:.17g}",box.h)});
  rows.push_back({{"captured",captured},{"pinHitBoxes",boxes}});
 }
 return pushJson(state,rows);
}
