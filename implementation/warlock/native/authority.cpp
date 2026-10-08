#include <hyprland/src/desktop/state/LayerState.hpp>
#include <hyprland/src/desktop/view/LayerSurface.hpp>
#include "incarnation-retirement.hpp"
#include "capture-resources.hpp"
#include <hyprland/src/render/warlock/screen_shader.hpp>
#include <hyprland/src/config/ConfigValue.hpp>
#include <hyprland/src/desktop/rule/windowRule/WindowRuleApplicator.hpp>
#include "WindowPolicy.hpp"
#include "../candidate/PlacementPolicy.hpp"
#include "../candidate/EffectBarrier.hpp"
#include "../candidate/ProspectiveGeometry.hpp"
#include "SceneTrace.hpp"
#include "SceneModal.hpp"
#include "navigation-modal.hpp"
#include <hyprland/src/managers/SeatManager.hpp>
#include <hyprland/src/managers/EventManager.hpp>
#include <hyprland/src/managers/input/InputManager.hpp>
#include <hyprland/src/managers/SessionLockManager.hpp>
#include <hyprland/src/state/MonitorState.hpp>
#include <hyprland/src/state/WorkspaceState.hpp>
#include <hyprland/src/desktop/state/GlobalWindowController.hpp>
#include <hyprland/src/managers/fullscreen/FullscreenController.hpp>
#include <hyprland/src/plugins/PluginAPI.hpp>
#include <hyprland/src/Compositor.hpp>
#include <hyprland/src/debug/HyprCtl.hpp>
#include <hyprland/src/desktop/state/WindowState.hpp>
#include <hyprland/src/desktop/state/FocusState.hpp>
#include <hyprland/src/desktop/Workspace.hpp>
#include <hyprland/src/render/Renderer.hpp>
#include <hyprland/src/desktop/view/Window.hpp>
#include <hyprland/src/event/EventBus.hpp>
#include <hyprland/src/layout/target/Target.hpp>
#include <hyprland/src/layout/space/Space.hpp>
#include <hyprland/src/layout/supplementary/DragController.hpp>
#include <hyprland/src/protocols/XDGShell.hpp>
#include <cmath>
#include <bit>
#include <json-glib/json-glib.h>
#include <sys/random.h>
#include <sys/stat.h>
#include <unistd.h>
#include <charconv>
#include <fstream>
#include <limits>
#include <map>
#include <sstream>
#include <set>
#include <thread>

#include "binding-registration.hpp"
#include "grant-registry.hpp"
#include "preview_capture.hpp"
#include "client_capture.hpp"
#include "popup_tree.hpp"
#include "family_revision.hpp"
#include "style_revision.hpp"
#include "preview_fd.hpp"
#include "family_crop_fd.hpp"
#include "family_style_crop_fd.hpp"
#include "generated_backdrop_fd.hpp"
#include "picker-probe-table.hpp"
#include "family_crop_capture.hpp"
#include "source_epoch.hpp"
#include <hyprland/src/protocols/core/Compositor.hpp>
#include <charconv>
#include <memory>

namespace {
HANDLE pluginHandle;
SP<SHyprCtlCommand> command;
CHyprSignalListener opened, closed, activated, previewLocked, previewReloaded, previewOutputRemoved;
uint64_t previewPrivacy=1,previewRendering=1,previewObservation=0;
std::string previewFdAddress;
std::vector<PHLWINDOWREF> recentFocus;
struct Activation { PHLWINDOWREF root; uint64_t incarnation; };
std::vector<Activation> activationHistory;
// A native input journal, never a window-selection policy. Capture membership
// on chord entry; coalesced notifications are hints to read this exact record.
struct SwitcherChord {
    uint64_t generation=0,ownerSession=0,ownerFrontend=0;
    std::vector<int> steps;
    std::vector<uint64_t> roots,history;
    std::optional<uint64_t> origin;
    bool released=false,cancelled=false,consumed=false;
};
SwitcherChord switcherChord;
uint64_t switcherSerial=0;
CHyprSignalListener switcherKeys, pointerFrames;
uint64_t pointerSerial=1;
std::string pointerState="idle", pointerOwner="null";
std::set<uint32_t> switcherAlts;
bool switcherTab=false,switcherStepAvailable=false;
struct SwitcherSelection {uint64_t request=0,generation=0,root=0;};
std::map<uint64_t,SwitcherSelection> switcherSelections;
uint64_t switcherOwnerSession=0,switcherOwnerFrontend=0;

uint64_t outputGeneration=0;
std::string previousOutputs;
std::thread::id ownerThread;
uint64_t lifetime = 0, incarnation = 0, sequence = 0, revision = 0;
std::string previousProjection;
uint64_t factsSequence = 0, factsRevision = 0;
std::string previousFacts;
struct Member { PHLWINDOWREF window; uint64_t id; };
std::vector<Member> members;
struct MotionWindow { Member member; CBox goal; PHLWORKSPACEREF workspace; float alpha; };
struct MotionWorkspace { PHLWORKSPACEREF workspace; Vector2D goal; float alpha; };
struct AcceptedMotion {
    std::vector<MotionWindow> windows{};
    std::vector<MotionWorkspace> workspaces{};
    uint64_t output=0;
    std::string intent{};
    bool settle=false;
};
Elm::Placement::Records geometryPlacements;
Elm::Geometry::Barriers effectBarriers;
struct Session { std::string start; uint64_t id; uint64_t frontend; uint64_t effectRequest=0, generation=0; std::string lastPayload, lastReply; std::vector<Render::SceneTrace::Frame> retained; int geometryProtocol=0; bool geometryEnabled=false; uint64_t geometryFrontend=0; std::set<std::string> geometryOperations{}; bool reducedMotion=true; uint64_t motionRequest=0; pid_t presentationPid=0; std::string presentationStart{}; AcceptedMotion motion{}; };
std::map<pid_t, Session> sessions;
enum class ShellRoute {Applications,System,Notifications};
struct ShellShortcut {uint64_t serial;ShellRoute route;};
uint64_t shellShortcutSerial=0,shellShortcutSession=0,shellShortcutFrontend=0;
std::vector<ShellShortcut> shellShortcuts;

struct ExportedImage {preview::fd::Owned file;preview::capture::Reservation reservation;uint64_t transfer;bool sent=false;};
struct CaptureProbe {
    uint64_t session{},frontend{},incarnation{},request{},output{},completed{},checksum{};
    std::unique_ptr<const preview::capture::OwnedPng> image;
    uint64_t privacy=1,rendering=1,scene=1,content=1,deadline=1;bool revoked=false;bool client=false;bool popup=false;bool family=false;bool crop=false;bool styled=false;bool backdrop=false;uint32_t generatedColor=0;CBox cropBounds{};double cropScale=0;std::vector<preview::FamilyNode> capturedMembers{};std::unique_ptr<ExportedImage> exported{};
};
std::map<CaptureKey,CaptureProbe> captureProbes;
void erasePeerCaptures(pid_t peer) {std::erase_if(captureProbes,[&](const auto& item){return item.first.peer==peer;});}
uint64_t productCaptureSubject(pid_t peer,uint64_t subject,uint64_t request) {
    const auto found=captureProbes.find(CaptureKey(peer,subject));
    return found!=captureProbes.end() && subject && found->second.request==request ? subject : 0;
}
struct PreviewSource {preview::SourceEpoch epoch;WP<CWLSurfaceResource> surface;CHyprSignalListener commit,destroy;bool dead=false;};
std::map<uint64_t,std::unique_ptr<PreviewSource>> previewSources;
std::map<uint64_t,preview::capture::SurfaceRevisionTracker> clientTrees;
std::map<uint64_t,preview::capture::SurfaceRevisionTracker> popupTrees;
struct FamilySource {std::map<uint64_t,preview::capture::SurfaceRevisionTracker> trees;preview::FamilyRevision revision;};
std::map<uint64_t,FamilySource> familySources;
std::map<uint64_t,preview::StyleRevision> familyStyles;
void sourceChanged(uint64_t id,bool destroyed) noexcept {
    auto found=previewSources.find(id);if(found==previewSources.end())return;
    auto& source=*found->second;if(destroyed)source.dead=true;
    if(!source.epoch.commit() || destroyed)for(auto& [pid,probe]:captureProbes)if(probe.incarnation==id)probe.revoked=true;
}
void trackSource(PHLWINDOW window,uint64_t id) {
    auto surface=window->resource();if(!surface)return;
    auto source=std::make_unique<PreviewSource>();source->surface=surface;
    source->commit=surface->m_events.commit.listen([id]{sourceChanged(id,false);});
    source->destroy=surface->m_events.destroy.listen([id]{sourceChanged(id,true);});
    previewSources.emplace(id,std::move(source));
}
std::unique_ptr<preview::capture::Budget> captureBudget;
std::unique_ptr<Elm::GrantRetirement::Registry> grantRegistry;
uint64_t retirementSequence=0;
uint64_t incarnationRetirementSequence=0;
uint64_t captureResourceSequence=0;
Elm::GrantRetirement::Peer verifiedPeer(pid_t pid,const std::string& start) {
    uint64_t ticks=0;
    const auto parsed=std::from_chars(start.data(),start.data()+start.size(),ticks);
    if(pid<=0 || parsed.ec!=std::errc{} || parsed.ptr!=start.data()+start.size() || ticks==0) throw std::runtime_error("unverified-peer");
    return {static_cast<uint64_t>(pid),ticks};
}

uint64_t randomIdentity() {
    for (int tries = 0; tries < 4; ++tries) {
        uint64_t value = 0;
        if (getrandom(&value, sizeof(value), 0) != sizeof(value))
            throw std::runtime_error("Authority entropy unavailable");
        if (value != 0) return value;
    }
    throw std::runtime_error("Authority identity unavailable");
}
std::string startTime(pid_t pid) {
    const std::string path = "/proc/" + std::to_string(pid);
    struct stat info{};
    if (stat(path.c_str(), &info) || info.st_uid != getuid()) return "";
    std::ifstream source(path + "/stat");
    std::string line; std::getline(source, line);
    const auto end = line.rfind(')');
    if (end == std::string::npos) return "";
    std::istringstream fields(line.substr(end + 1));
    std::string field;
    for (int i = 0; i <= 19; ++i) if (!(fields >> field)) return "";
    return field;
}
pid_t parentPid(pid_t pid) {
    if(startTime(pid).empty()) return 0;
    std::ifstream source("/proc/"+std::to_string(pid)+"/stat");std::string line;std::getline(source,line);const auto end=line.rfind(')');
    if(end==std::string::npos) return 0;
    std::istringstream fields_(line.substr(end+1));char state;pid_t parent=0;fields_>>state>>parent;return parent>0 && !startTime(parent).empty() ? parent : 0;
}
std::string error(const std::string& reason) {
    return "{\"protocolVersion\":3,\"kind\":\"refused\",\"reason\":\"" + reason + "\"}";
}
std::string quote(const std::string& value) {
    JsonNode* node = json_node_new(JSON_NODE_VALUE);
    json_node_set_string(node, value.c_str());
    gchar* output = json_to_string(node, FALSE);
    std::string result(output); g_free(output); json_node_free(node);
    return result;
}
std::string label(const std::string& title) {
    gchar* valid = g_utf8_make_valid(title.c_str(), title.size());
    std::string result;
    const char* cursor = valid;
    for (int count = 0; *cursor;) {
        const auto character = g_utf8_get_char(cursor);
        const int cost = character > 0xFFFF ? 2 : 1;
        if (count + cost > 256) break;
        count += cost;
        const char* next = g_utf8_next_char(cursor);
        if (g_utf8_get_char(cursor) < 32) result += ' ';
        else result.append(cursor, next - cursor);
        cursor = next;
    }
    g_free(valid); return result;
}
bool fields(JsonObject* object, std::initializer_list<const char*> expected) {
    if (json_object_get_size(object) != expected.size()) return false;
    for (const char* key : expected) if (!json_object_has_member(object, key)) return false;
    return true;
}
std::optional<uint64_t> counter(JsonObject* object, const char* key, bool allowZero = false) {
    JsonNode* node = json_object_get_member(object, key);
    if (!node || !JSON_NODE_HOLDS_VALUE(node) || json_node_get_value_type(node) != G_TYPE_STRING) return {};
    std::string text = json_node_get_string(node);
    if (text.empty() || text.size() > 20 || (text.size() > 1 && text[0] == '0') ||
        !std::all_of(text.begin(), text.end(), [](char c) { return c >= '0' && c <= '9'; })) return {};
    uint64_t number;
    auto parsed = std::from_chars(text.data(), text.data() + text.size(), number);
    if (parsed.ec != std::errc{} || parsed.ptr != text.data() + text.size() || (!allowZero && !number)) return {};
    return number;
}
JsonObject* objectMember(JsonObject* object, const char* key) {
    JsonNode* node = json_object_get_member(object,key);
    return node && JSON_NODE_HOLDS_OBJECT(node) ? json_node_get_object(node) : nullptr;
}
std::string binding(const Session& session) {
    return "{\"lifetime\":\"" + std::to_string(lifetime) + "\",\"session\":\"" + std::to_string(session.id) +
        "\",\"frontend\":\"" + std::to_string(session.frontend) + "\"}";
}
void forget(const PHLWINDOW& window) {
    Render::SceneTrace::forget(window);
    std::erase_if(members,[&](const Member& member) {
        if(member.window.lock() && member.window.lock()!=window) return false;
        if(const auto key=Elm::Placement::Identity::fromNative(lifetime,member.id)) geometryPlacements.retire(*key);
        effectBarriers.retire({lifetime,member.id});previewSources.erase(member.id);clientTrees.erase(member.id);popupTrees.erase(member.id);familySources.erase(member.id);familyStyles.erase(member.id);return true;
    });
}
void birth(const PHLWINDOW& window) {
    forget(window);
    if (incarnation == std::numeric_limits<uint64_t>::max()) throw std::runtime_error("Incarnation exhausted");
    if(window->parent() && Desktop::WindowPolicy::isMinimized(window->parent())) {
        if(!Desktop::WindowPolicy::applyMinimized({window},true)) throw std::runtime_error("Inherited minimized state unavailable");
        window->setSuspended(true);
    }
    const auto id=++incarnation;
    if(!Render::SceneTrace::bind(window,lifetime,id)) throw std::runtime_error("Draw identity unavailable");
    members.push_back({window,id});trackSource(window,id);
}
void notifyEffectChange() noexcept {
    // A trusted compositor socket emits an invalidation hint, never scene facts.
    // Readers reacquire their own authenticated revision-bound projection.
    try { if (g_pEventManager) g_pEventManager->postEvent(SHyprIPCEvent{"elmwindowstate",std::to_string(lifetime)}); } catch (...) {}
}
std::string projection() {
    std::erase_if(members,[](const Member& member) { return !member.window.lock(); });
    std::string result = "["; size_t count = 0;
    for (const auto& window : Desktop::windowState()->windows()) {
        if (!window->m_isMapped) continue;
        if (++count > 256) throw std::runtime_error("Projection bound");
        auto found = std::find_if(members.begin(),members.end(),[&](const Member& member) { return member.window.lock() == window; });
        if (found == members.end()) throw std::runtime_error("Missing window incarnation");
        if (count > 1) result += ',';
        result += "{\"incarnation\":\"" + std::to_string(found->id) + "\",\"application\":" + quote(label(window->m_class)) + ",\"label\":" + quote(label(window->m_title)) + ",\"minimized\":" + std::string(Desktop::WindowPolicy::isMinimized(window) ? "true" : "false") + "}";
    }
    return result + "]";
}
std::string identityOf(const PHLWINDOW& window) {
    if (!window) return "null";
    const auto found = std::find_if(members.begin(), members.end(), [&](const Member& member) { return member.window.lock() == window; });
    if (found == members.end()) throw std::runtime_error("Unregistered scene member");
    return quote(std::to_string(found->id));
}
void recordActivation(const PHLWINDOW& window) noexcept {
    // Both observations derive from the same committed native activation. The
    // exported family history grants no focus/effect authority to the frontend.
    try {
        std::erase_if(recentFocus,[&](const auto& reference){return !reference.lock() || reference.lock()==window;});
        if(!window) return;
        if(recentFocus.size()>=256) recentFocus.erase(recentFocus.begin());
        recentFocus.emplace_back(window);
        auto root=window;
        std::vector<PHLWINDOW> path;
        while(root->parent()) {
            if(path.size()>=256 || std::ranges::find(path,root)!=path.end()) return;
            path.push_back(root);root=root->parent();
        }
        const auto member=std::ranges::find_if(members,[&](const Member& item){return item.window.lock()==root;});
        if(member==members.end() || !root->m_isMapped) return;
        std::erase_if(activationHistory,[&](const Activation& item){return !item.root.lock() || item.root.lock()==root;});
        if(activationHistory.size()>=256) activationHistory.erase(activationHistory.begin());
        activationHistory.push_back({root,member->id});
    } catch(...) { activationHistory.clear(); }
}
std::string activationRoots() {
    std::string result="[";size_t count=0;
    for(const auto& entry:activationHistory | std::views::reverse) {
        const auto root=entry.root.lock();
        if(!root || !root->m_isMapped || root->parent()) continue;
        const auto member=std::ranges::find_if(members,[&](const Member& item){return item.window.lock()==root && item.id==entry.incarnation;});
        if(member==members.end()) continue;
        if(count++) result+=',';
        result+=quote(std::to_string(entry.incarnation));
    }
    return result+"]";
}
void notifySwitcher() noexcept {
    try {if(g_pEventManager)g_pEventManager->postEvent(SHyprIPCEvent{"warlockswitcher",std::to_string(lifetime)});}catch(...){}
}
void cancelSwitcher() noexcept {
    if(switcherChord.generation && !switcherChord.consumed && !switcherChord.cancelled){switcherChord.cancelled=true;notifySwitcher();}
}
std::optional<std::vector<PHLWINDOW>> nativeFamily(PHLWINDOW window);
void switcherStep(int direction) noexcept {
    try {
        if(g_layoutManager->dragController()->target() || switcherAlts.empty() || !switcherTab || !switcherStepAvailable || g_pSessionLockManager->isSessionLocked() || !g_pInputManager->m_exclusiveLSes.empty())return;
        switcherStepAvailable=false;
        if(!switcherChord.generation || switcherChord.released || switcherChord.cancelled || switcherChord.consumed) {
            if(switcherSerial==std::numeric_limits<uint64_t>::max())return;
            SwitcherChord next;next.generation=++switcherSerial;
            next.ownerSession=switcherOwnerSession;next.ownerFrontend=switcherOwnerFrontend;
            for(const auto& member:members) {
                const auto root=member.window.lock();
                if(!root || !root->m_isMapped || root->parent() || !root->m_workspace || root->m_workspace->m_id<=0 || root->isHidden())continue;
                const auto family=nativeFamily(root);
                if(!family || family->empty() || std::ranges::any_of(*family,[&](const auto& window){return !window->m_workspace || window->m_workspace!=root->m_workspace || window->isHidden() || window->onSpecialWorkspace();}))continue;
                next.roots.push_back(member.id);
            }
            if(next.roots.size()>256)return;
            for(const auto& entry:activationHistory | std::views::reverse)
                if(std::ranges::find(next.roots,entry.incarnation)!=next.roots.end())next.history.push_back(entry.incarnation);
            auto focused=Desktop::focusState()->window();std::set<PHLWINDOW> path;
            while(focused && focused->parent()){if(path.size()>=256 || !path.insert(focused).second){focused=nullptr;break;}focused=focused->parent();}
            for(const auto& member:members)if(focused && member.window.lock()==focused)next.origin=member.id;
            switcherChord=std::move(next);
        }
        if(switcherChord.steps.size()>=4096){cancelSwitcher();return;}
        switcherChord.steps.push_back(direction);notifySwitcher();
    }catch(...){cancelSwitcher();}
}
// Read the core drag controller; the shell never chooses a gesture target.
// Render pre observes transitions after native input dispatch. Every competing
// native operation also checks the controller directly, before any mutation.
void refreshPointerOwnership() {
    const auto& controller=g_layoutManager->dragController();
    const auto target=controller->target();
    const std::string state=!target ? "idle" : controller->mode()==MBIND_MOVE ? "move" : "resize";
    const std::string owner=target ? identityOf(target->window()) : "null";
    if(state==pointerState && owner==pointerOwner)return;
    if(pointerSerial==std::numeric_limits<uint64_t>::max())throw std::runtime_error("Pointer observation exhausted");
    pointerState=state;pointerOwner=owner;++pointerSerial;
    if(target){cancelSwitcher();shellShortcuts.clear();}
    if(g_pEventManager)g_pEventManager->postEvent(SHyprIPCEvent{"warlockpointer",std::to_string(lifetime)});
}
std::string pointerOwnership(const Session& session,uint64_t request) {
    refreshPointerOwnership();
    return "{\"protocolVersion\":3,\"kind\":\"pointer-ownership\",\"ownershipProtocol\":1,\"binding\":"+binding(session)+",\"requestId\":"+quote(std::to_string(request))+",\"serial\":"+quote(std::to_string(pointerSerial))+",\"state\":"+quote(pointerState)+",\"owner\":"+pointerOwner+"}";
}
void notifyShellShortcuts() noexcept {try {if(g_pEventManager)g_pEventManager->postEvent(SHyprIPCEvent{"warlockshortcuts",std::to_string(lifetime)});}catch(...) {}}
void shellShortcut(ShellRoute route) noexcept {
    try {
        if(g_layoutManager->dragController()->target() || !shellShortcutSession || !shellShortcutFrontend || g_pSessionLockManager->isSessionLocked() || !g_pInputManager->m_exclusiveLSes.empty() || (switcherChord.generation && !switcherChord.cancelled && !switcherChord.consumed && !switcherChord.released) || shellShortcutSerial==std::numeric_limits<uint64_t>::max())return;
        if(shellShortcuts.size()==64)shellShortcuts.erase(shellShortcuts.begin());
        shellShortcuts.push_back({++shellShortcutSerial,route});notifyShellShortcuts();
    } catch(...) {shellShortcuts.clear();}
}
int appsMenu(lua_State*){shellShortcut(ShellRoute::Applications);return 0;}
int systemMenu(lua_State*){shellShortcut(ShellRoute::System);return 0;}
int notificationHistory(lua_State*){shellShortcut(ShellRoute::Notifications);return 0;}
std::string shellShortcutJournal(const Session& session,uint64_t request) {
    const bool blocked=g_layoutManager->dragController()->target() || g_pSessionLockManager->isSessionLocked() || !g_pInputManager->m_exclusiveLSes.empty();
    std::string events="[";
    if(!blocked)for(const auto& event:shellShortcuts) {
        if(events.size()>1)events+=',';
        const std::string route=event.route==ShellRoute::Applications?"applications":event.route==ShellRoute::System?"system":"notifications";
        events+="{\"serial\":"+quote(std::to_string(event.serial))+",\"route\":"+quote(route)+"}";
    }
    return "{\"protocolVersion\":3,\"kind\":\"shell-shortcuts\",\"shortcutProtocol\":1,\"binding\":"+binding(session)+",\"requestId\":"+quote(std::to_string(request))+",\"serial\":"+quote(std::to_string(shellShortcutSerial))+",\"blocked\":"+(blocked?"true":"false")+",\"events\":"+events+"]}";
}
int switcherForward(lua_State*){switcherStep(1);return 0;}
int switcherReverse(lua_State*){switcherStep(-1);return 0;}
void switcherKey(IKeyboard::SKeyEvent event,Event::SCallbackInfo& info) {
    const bool pressed=event.state==WL_KEYBOARD_KEY_STATE_PRESSED;
    // The initial step is admitted by the configured compositor keybinding,
    // not by IPC or a frontend packet. Release/cancel survive popup startup.
    const auto keyboard=g_pSeatManager->m_keyboard.lock();
    const auto symbol=keyboard && keyboard->m_xkbState ? xkb_state_key_get_one_sym(keyboard->m_xkbState,event.keycode+8) : 0;
    if(pressed && (symbol==0xffe9 || symbol==0xffea))switcherAlts.insert(event.keycode);
    if(!pressed && switcherAlts.erase(event.keycode) && switcherAlts.empty() && switcherChord.generation && !switcherChord.cancelled && !switcherChord.consumed && !switcherChord.released){switcherChord.released=true;notifySwitcher();}
    if(symbol==0xff09 || symbol==0xfe20 || (!pressed && switcherTab && event.keycode==15)){
        if(pressed && !switcherTab){switcherTab=true;switcherStepAvailable=true;}
        if(!pressed){switcherTab=false;switcherStepAvailable=false;}
        if(pressed && switcherChord.generation && !switcherChord.released && !switcherChord.cancelled && !switcherChord.consumed && !switcherAlts.empty()){
            switcherStep(symbol==0xfe20 ? -1 : 1);info.cancelled=true;
        }
    }
    if(symbol==0xff1b && switcherChord.generation && !switcherChord.consumed){if(pressed)cancelSwitcher();}
}
std::string switcherJournal(const Session& session,bool observing=false) {
    auto& chord=switcherChord;
    if(!observing && chord.generation && !chord.ownerSession){chord.ownerSession=session.id;chord.ownerFrontend=session.frontend;}
    const auto array=[](const std::vector<uint64_t>& values){std::string result="[";for(auto value:values){if(result.size()>1)result+=',';result+=quote(std::to_string(value));}return result+"]";};
    std::string steps="[";for(auto value:chord.steps){if(steps.size()>1)steps+=',';steps+=std::to_string(value);}steps+=']';
    const bool mine=chord.ownerSession==session.id && chord.ownerFrontend==session.frontend;
    return "{\"generation\":"+quote(std::to_string(chord.generation))+",\"roots\":"+array(chord.roots)+",\"history\":"+array(chord.history)+",\"origin\":"+(chord.origin?quote(std::to_string(*chord.origin)):"null")+",\"steps\":"+steps+",\"released\":"+(chord.released?"true":"false")+",\"cancelled\":"+((chord.cancelled || (!observing && chord.generation && !mine))?"true":"false")+",\"consumed\":"+(chord.consumed?"true":"false")+"}";
}
std::string sceneFacts(bool includeAttention=true) {
    // Native facts only. Vector position is not claimed to be final paint order:
    // specialized fullscreen/effect passes may currently disagree with it.
    const auto boolean = [](bool value) { return value ? "true" : "false"; };
    std::string result = "{\"focused\":" + identityOf(Desktop::focusState()->window()) + ",\"windows\":[";
    size_t count = 0, position = 0;
    for (const auto& window : Desktop::windowState()->windows()) {
        const auto stackPosition = position++;
        if (!window->m_isMapped) continue;
        if (++count > 256) throw std::runtime_error("Scene facts bound");
        if (count > 1) result += ',';
        const auto workspace = window->m_workspace;
        const auto monitor = window->m_monitor.lock();
        const auto owner = window->parent();
        const auto at=window->position(Desktop::View::IGeometric::GEOMETRIC_GOAL);
        const auto size=window->size(Desktop::View::IGeometric::GEOMETRIC_GOAL);
        result += "{\"incarnation\":" + identityOf(window) + ",\"owner\":" + identityOf(owner) + ",\"application\":" + quote(label(window->m_class)) +
            ",\"stackPosition\":" + std::to_string(stackPosition) +
            ",\"workspace\":" + (workspace ? quote(std::to_string(window->workspaceID())) : "null") +
            ",\"monitor\":" + (monitor ? quote(std::to_string(window->monitorID())) : "null") +
            ",\"geometry\":["+std::to_string(at.x)+","+std::to_string(at.y)+","+std::to_string(size.x)+","+std::to_string(size.y)+"]"+
            ",\"fullscreenMode\":"+std::to_string(static_cast<int>(Fullscreen::controller()->getFullscreenModes(window).internal))+
            ",\"workspaceVisible\":" + boolean(workspace && workspace->isVisible()) +
            ",\"hidden\":" + boolean(window->isHidden()) +
            ",\"pinned\":" + boolean(window->m_pinned) +
            (includeAttention ? ",\"attention\":" + std::string(boolean(window->m_isUrgent)) : "") +
            ",\"allowedOverFullscreen\":" + boolean(window->isAllowedOverFullscreen()) +
            ",\"renderOverFullscreen\":" + boolean(window->shouldRenderOverFullscreen()) +
            ",\"acceptsInput\":" + boolean(window->acceptsInput()) +
            ",\"shouldRenderAny\":" + boolean(g_pHyprRenderer->shouldRenderWindow(window)) +
            ",\"shouldRenderOwnMonitor\":" + boolean(monitor && g_pHyprRenderer->shouldRenderWindow(window, monitor)) +
            ",\"minimized\":" + std::string(Desktop::WindowPolicy::isMinimized(window) ? "true" : "false") + "}";
    }
    return result + "]}";
}
std::string traceNumbers(const std::array<double,5>& values) {
    std::string result="[";for(size_t i=0;i<values.size();++i){if(i)result+=',';result+=std::to_string(values[i]);}return result+"]";
}
std::string renderTrace(const std::vector<Render::SceneTrace::Frame>& frames) {
    std::string result="[";size_t count=0;
    for(const auto& frame:frames) {
        if(count++) result+=',';
        result+="{\"monitor\":"+quote(std::to_string(frame.monitor))+",\"frame\":"+quote(std::to_string(frame.serial))+",\"complete\":"+(frame.complete?"true":"false")+",\"overflow\":"+(frame.overflow?"true":"false")+",\"committed\":"+(frame.committed?"true":"false")+",\"outputConfiguration\":"+traceNumbers(frame.output)+",\"outputTransform\":"+std::to_string(frame.transform)+",\"configurationGeneration\":"+quote(std::to_string(frame.outputGeneration))+",\"draws\":[";
        size_t draws=0;
        for(const auto& draw:frame.draws) {
            if(draws++) result+=',';
            const auto window=draw.window.lock();
            const auto found=std::find_if(members.begin(),members.end(),[&](const Member& member){return window && member.window.lock()==window;});
            const bool retired=draw.incarnation && (draw.authority!=lifetime || found==members.end() || found->id!=draw.incarnation);
            result+="{\"incarnation\":"+(draw.incarnation?quote(std::to_string(draw.incarnation)):std::string("null"))+",\"authority\":"+(draw.authority?quote(std::to_string(draw.authority)):std::string("null"))+",\"retired\":"+(retired?"true":"false")+",\"unbound\":"+((draw.hadWindow && !draw.incarnation)?"true":"false")+",\"main\":"+(draw.main?"true":"false")+",\"popup\":"+(draw.popup?"true":"false")+",\"surface\":"+quote(std::to_string(draw.surface))+",\"box\":["+std::to_string(draw.box[0])+","+std::to_string(draw.box[1])+","+std::to_string(draw.box[2])+","+std::to_string(draw.box[3])+"],\"alpha\":"+std::to_string(draw.alpha)+",\"input\":[";
            for(size_t i=0;i<draw.input.size();++i){if(i)result+=',';const auto& r=draw.input[i];result+="["+std::to_string(r[0])+","+std::to_string(r[1])+","+std::to_string(r[2])+","+std::to_string(r[3])+"]";}
            result+="]}";
        }
        result+="]}";
    }
    return result+"]";
}
void refreshOutputs() {
    std::string value;
    for (const auto& monitor : State::monitorState()->monitors()) {
        value += std::to_string(monitor->m_id) + ":" + monitor->m_name + ":" +
            std::to_string(monitor->m_position.x) + ":" + std::to_string(monitor->m_position.y) + ":" +
            std::to_string(monitor->m_size.x) + ":" + std::to_string(monitor->m_size.y) + ":" +
            std::to_string(monitor->m_scale) + ":" + std::to_string(static_cast<int>(monitor->m_transform)) + ";";
    }
    if (value != previousOutputs) {
        if (outputGeneration == std::numeric_limits<uint64_t>::max()) throw std::runtime_error("Output generation exhausted");
        ++outputGeneration; previousOutputs = value;
    }
}
std::string refreshFacts() {
    refreshOutputs();
    const auto value = sceneFacts();
    if (value != previousFacts) {
        if (factsRevision == std::numeric_limits<uint64_t>::max()) throw std::runtime_error("Scene dependency revision exhausted");
        ++factsRevision; previousFacts = value;
    }
    return value;
}
std::optional<std::vector<PHLWINDOW>> nativeFamily(PHLWINDOW window) {
    std::vector<PHLWINDOW> path;
    while (window && window->parent()) {
        if (path.size()>=256 || std::ranges::find(path,window)!=path.end()) return {};
        path.push_back(window); window=window->parent();
    }
    if (!window || !window->m_isMapped) return {};
    const auto root=window;
    std::vector<PHLWINDOW> family;
    for (const auto& candidate : Desktop::windowState()->windows()) {
        if (!candidate->m_isMapped) continue;
        PHLWINDOW ancestor=candidate;path.clear();
        while(ancestor && ancestor!=root) {
            if(path.size()>=256 || std::ranges::find(path,ancestor)!=path.end()) return {};
            path.push_back(ancestor);ancestor=ancestor->parent();
        }
        if(ancestor==root) family.push_back(candidate);
        if(family.size()>256) return {};
    }
    return family;
}
bool geometryTargetEligible(const PHLWINDOW& window,int protocol=1);
#include "geometry.inc"

PHLWINDOW successor(const std::vector<PHLWINDOW>& family) {
    for (const auto& reference : recentFocus | std::views::reverse) {
        const auto window=reference.lock();
        if (!window || std::ranges::find(family,window)!=family.end() || !window->m_isMapped || !window->acceptsInput() ||
            !window->m_workspace || !window->m_workspace->isVisible() || !g_pHyprRenderer->shouldRenderWindow(window)) continue;
        const auto recipient=SceneModal::focusRecipient(window);
        if(recipient.has_value() && *recipient==window) return window;
    }
    return nullptr;
}
std::string effectOutcome(const Session& session, const std::string& intent, const char* status, const char* reason, int protocol=1) {
    return "{\"protocolVersion\":3,\"kind\":\"effect-outcome\",\"effectProtocol\":"+std::to_string(protocol)+",\"binding\":"+binding(session)+
        ",\"intent\":"+intent+",\"status\":"+quote(status)+",\"reason\":"+quote(reason)+
        ",\"revision\":"+quote(std::to_string(protocol==2 ? geometryRevision : factsRevision))+",\"outputGeneration\":"+quote(std::to_string(outputGeneration))+"}";
}
#include "motion-profile.inc"

std::string performEffect(Session& session, JsonObject* object, const std::string&) {
    JsonObject* intent=objectMember(object,"intent");
    if(!intent || !fields(intent,{"request","generation","incarnation","operation","context"})) return error("effect-schema");
    const auto requestId=counter(intent,"request"), generation=counter(intent,"generation"), target=counter(intent,"incarnation");
    JsonObject* context=objectMember(intent,"context");
    if(!requestId || !generation || !target || !context || !fields(context,{"lifetime","epoch","output","revision"})) return error("effect-schema");
    const auto native=counter(context,"lifetime"), epoch=counter(context,"epoch"), output=counter(context,"output"), expected=counter(context,"revision");
    JsonNode* operationNode=json_object_get_member(intent,"operation");
    if(!native || !epoch || !output || !expected || !operationNode || !JSON_NODE_HOLDS_VALUE(operationNode) || json_node_get_value_type(operationNode)!=G_TYPE_STRING) return error("effect-schema");
    const std::string operation=json_node_get_string(operationNode);
    gchar* raw=json_to_string(json_object_get_member(object,"intent"),FALSE);std::string encoded(raw);g_free(raw);
    const auto selection=switcherSelections.find(session.id);
    const bool fenced=selection!=switcherSelections.end() && selection->second.request==*requestId;
    // Retry identity belongs to the immutable effect intent. A newer selection
    // preparation must never change the already recorded terminal reply.
    const std::string fingerprint="1:"+quote(operation)+":"+std::to_string(*requestId)+":"+std::to_string(*generation)+":"+std::to_string(*target)+":"+std::to_string(*native)+":"+std::to_string(*epoch)+":"+std::to_string(*output)+":"+std::to_string(*expected);
    if(*native!=lifetime || *epoch!=session.frontend) return effectOutcome(session,encoded,"Refused","authority-mismatch");
    if(*requestId==session.effectRequest) return fingerprint==session.lastPayload ? session.lastReply : effectOutcome(session,encoded,"Refused","request-reuse");
    if(*requestId<session.effectRequest || *generation<=session.generation) return effectOutcome(session,encoded,"Refused","operation-order");
    refreshFacts();
    const auto reject=[&](const char* reason) {session.lastReply=effectOutcome(session,encoded,"Refused",reason);return session.lastReply;};
    // The journal is bounded to one request per authenticated peer/epoch. Older
    // identities refuse; exact retry returns its original terminal outcome.
    session.effectRequest=*requestId;session.generation=*generation;session.lastPayload=fingerprint;
    session.lastReply=effectOutcome(session,encoded,"Unknown","effect-unproven");
    if(selection!=switcherSelections.end() && *requestId<selection->second.request)return reject("superseded-switcher-selection");
    if(fenced) {
        const auto& chosen=selection->second;
        if(chosen.generation!=switcherChord.generation || chosen.root!=*target || switcherChord.ownerSession!=session.id || switcherChord.ownerFrontend!=session.frontend || switcherChord.cancelled || switcherChord.consumed || std::ranges::find(switcherChord.roots,*target)==switcherChord.roots.end() || operation=="minimize")return reject("switcher-cancelled-or-retired");
        // This callback never pumps the event loop. Consume before the first
        // possible mutation; Unknown cannot make the chord executable again.
        switcherChord.consumed=true;notifySwitcher();
    }
    if(operation!="minimize" && operation!="restore" && operation!="activate") return reject("unsupported-operation");
    if(*output!=outputGeneration || *expected!=factsRevision) return reject("dependency-mismatch");
    if(g_layoutManager->dragController()->target()) return reject("native-pointer-owned");
    if(g_pSessionLockManager->isSessionLocked() || !g_pInputManager->m_exclusiveLSes.empty()) return reject("exclusive-input");
    const auto member=std::find_if(members.begin(),members.end(),[&](const Member& entry){return entry.id==*target;});
    if(member==members.end() || !member->window.lock() || !member->window.lock()->m_isMapped) return reject("stale-incarnation");
    const auto targetWindow=member->window.lock();const auto family=nativeFamily(targetWindow);
    if(!family.has_value() || family->empty()) return reject("invalid-family");
    for(const auto& window:*family) {
        for(const auto& entry:members) if(entry.window.lock()==window && effectBarriers.blocked({lifetime,entry.id})) return reject("native-operation-unresolved");
    }
    const bool minimize=operation=="minimize";
    const bool activate=operation=="activate";
    const auto destination=targetWindow->m_workspace;
    const auto destinationMonitor=targetWindow->m_monitor.lock();
    if(!destination || destination->m_id<=0 || !destinationMonitor || !destinationMonitor->m_enabled || destination->m_monitor.lock()!=destinationMonitor) return reject("ineligible-workspace-owner");
    const bool navigating=!destination->isVisible();
    const auto previousWorkspace=destinationMonitor->m_activeWorkspace;
    for(const auto& window : *family) {
        if(!window->m_workspace || window->onSpecialWorkspace() || window->isHidden() || (minimize && !window->m_workspace->isVisible())) return reject("ineligible-family");
        if(window->m_workspace!=destination || window->m_monitor.lock()!=destinationMonitor) return reject("mixed-family-workspace-owner");
        // The core's pinned focus path can reassign workspace membership.
        const auto focusMonitor=Desktop::focusState()->monitor();
        if(!minimize && window->m_pinned && (!focusMonitor || focusMonitor->m_activeWorkspace!=destination)) return reject("implicit-transfer-required");
        if(Desktop::WindowPolicy::isMinimized(window)!=(operation=="restore")) return reject("family-state-mismatch");
    }
    PHLWINDOW restoreFocus=nullptr;
    if(!minimize) {
        const auto root=std::find_if(family->begin(),family->end(),[&](const auto& window){return !window->parent() || std::ranges::find(*family,window->parent())==family->end();});
        if(root==family->end()) return reject("invalid-family-root");
        const auto predicted=WarlockNavigationModal::focusRecipient(*root,!activate,navigating);
        if(!predicted.has_value() || !*predicted || (*predicted)->m_ruleApplicator->noFocus().valueOrDefault()) return reject("ambiguous-or-ineligible-restore-focus");
        restoreFocus=*predicted;
    }
    const auto beforeMutationRevision=factsRevision;
    const auto oldFocus=Desktop::focusState()->window();
    const auto oldKeyboard=g_pSeatManager->m_state.keyboardFocus.lock();
    const bool focusedFamily=std::ranges::find(*family,oldFocus)!=family->end();
    const auto protectedGrab=g_pSeatManager->m_seatGrab;
    if(protectedGrab) {
        // Background minimize cannot redirect focus or mutate the grab owner.
        // Refuse unknown/own-client grabs and every focus-changing operation.
        if(!minimize || focusedFamily || !oldKeyboard || !protectedGrab->accepts(oldKeyboard)) return reject("seat-grab");
        const auto pointer=g_pSeatManager->m_state.pointerFocus.lock();
        for(const auto& window : *family) {
            const auto surface=window->wlSurface()->resource();
            if(!surface || protectedGrab->accepts(surface) || surface->client()==oldKeyboard->client() || (pointer && surface->client()==pointer->client())) return reject("seat-grab");
        }
    }
    const auto nextFocus=minimize && focusedFamily ? successor(*family) : oldFocus;
    // Reserve the full family before native callbacks; capacity refuses before mutation.
    std::vector<Elm::Geometry::Target> reserved;
    for(const auto& window:*family) {
        const auto entry=std::ranges::find_if(members,[&](const Member& e){return e.window.lock()==window;});
        if(entry==members.end() || !effectBarriers.begin({lifetime,entry->id})) {for(auto id:reserved) effectBarriers.definitive(id);return reject("native-operation-bound");}
        reserved.push_back({lifetime,entry->id});
    }
    const auto membershipCurrent=[&]() {
        const auto currentFamily=nativeFamily(targetWindow);
        if(!currentFamily.has_value() || currentFamily->size()!=family->size() || !std::ranges::all_of(*currentFamily,[&](const auto& window){return std::ranges::find(*family,window)!=family->end();})) return false;
        return destinationMonitor->m_enabled && destination->m_monitor.lock()==destinationMonitor &&
            std::ranges::all_of(*family,[&](const auto& window) {
                return window->m_isMapped && !window->isHidden() && !window->onSpecialWorkspace() && window->m_workspace==destination && window->m_monitor.lock()==destinationMonitor &&
                    std::ranges::any_of(members,[&](const Member& entry) {
                        return entry.window.lock()==window && std::ranges::any_of(reserved,[&](auto id){return id.incarnation==entry.id;});
                    });
            });
    };
    const auto release=[&]() {for(auto id:reserved) effectBarriers.definitive(id);};
    const auto receiverEligible=[&](const PHLWINDOW& window) {
        if(!window || !window->m_isMapped || !window->acceptsInput() || window->isHidden() || window->m_pinned || !window->m_workspace || !window->m_workspace->isVisible() || !g_pHyprRenderer->shouldRenderWindow(window) || window->m_ruleApplicator->noFocus().valueOrDefault()) return false;
        const auto recipient=SceneModal::focusRecipient(window);
        return recipient.has_value() && *recipient==window;
    };
    bool navigated=false, navigationChanged=false;
    const auto refuseAfterNavigation=[&](const char* reason) {
        refreshFacts();
        if(!navigationChanged) {release();return reject(reason);}
        // Refusal after navigation is definitive only with observed usable focus
        // and unchanged family state. Never compensate an uncertain window effect.
        if(!membershipCurrent() || std::ranges::any_of(*family,[&](const auto& w){return Desktop::WindowPolicy::isMinimized(w)!=(operation=="restore");}) || *output!=outputGeneration || g_pSessionLockManager->isSessionLocked() || !g_pInputManager->m_exclusiveLSes.empty() || g_pSeatManager->m_seatGrab) return session.lastReply;
        auto fallback=Desktop::focusState()->window();
        if(!receiverEligible(fallback) || std::ranges::find(*family,fallback)!=family->end()) {
            fallback=nullptr;
            for(const auto& reference:recentFocus | std::views::reverse) {
                const auto candidate=reference.lock();
                if(receiverEligible(candidate) && candidate->m_workspace==destination && std::ranges::find(*family,candidate)==family->end()) {fallback=candidate;break;}
            }
        }
        if(!fallback && previousWorkspace && previousWorkspace->m_id>0 && !previousWorkspace->m_isSpecialWorkspace && previousWorkspace->m_monitor.lock()==destinationMonitor && destinationMonitor->m_activeWorkspace==destination && destination->isVisible()) {
            destinationMonitor->changeWorkspace(previousWorkspace,false,true,true);
            if(!previousWorkspace->isVisible() || destinationMonitor->m_activeWorkspace!=previousWorkspace || *output!=outputGeneration) return session.lastReply;
            if(receiverEligible(oldFocus)) fallback=oldFocus;
        }
        if(!fallback) return session.lastReply;
        Desktop::focusState()->fullWindowFocus(fallback,Desktop::FOCUS_REASON_DESKTOP_STATE_CHANGE);
        refreshFacts();notifyEffectChange();
        if(!membershipCurrent() || *output!=outputGeneration || g_pSessionLockManager->isSessionLocked() || !g_pInputManager->m_exclusiveLSes.empty() || g_pSeatManager->m_seatGrab || std::ranges::any_of(*family,[&](const auto& w){return Desktop::WindowPolicy::isMinimized(w)!=(operation=="restore");}) || !receiverEligible(fallback) || Desktop::focusState()->window()!=fallback || g_pSeatManager->m_state.keyboardFocus.lock()!=fallback->wlSurface()->resource()) return session.lastReply;
        release();return reject(reason);
    };
    try {
        // No event-loop pumping or external dispatch occurs in this callback.
        if(navigating) {
            // Navigate the preserved owner, never changeWorkspaceOnCurrentMonitor
            // or move a family. noFocus prevents a minimized target receiving keys.
            destinationMonitor->changeWorkspace(destination,false,true,true);
            navigationChanged=destinationMonitor->m_activeWorkspace!=previousWorkspace || Desktop::focusState()->window()!=oldFocus || g_pSeatManager->m_state.keyboardFocus.lock()!=oldKeyboard;
            navigated=destination->isVisible() && destinationMonitor->m_activeWorkspace==destination;
            refreshFacts();notifyEffectChange();
            if(!navigated || !membershipCurrent() || *output!=outputGeneration || g_pSessionLockManager->isSessionLocked() || !g_pInputManager->m_exclusiveLSes.empty() || g_pSeatManager->m_seatGrab) return refuseAfterNavigation("navigation-refused");
            if(std::ranges::any_of(*family,[&](const auto& w){return Desktop::WindowPolicy::isMinimized(w)!=(operation=="restore");})) return refuseAfterNavigation("navigation-family-state-changed");
            auto root=std::find_if(family->begin(),family->end(),[&](const auto& w){return !w->parent() || std::ranges::find(*family,w->parent())==family->end();});
            const auto currentRecipient=root==family->end() ? std::optional<PHLWINDOW>{} : SceneModal::focusRecipient(*root,!activate);
            if(!currentRecipient.has_value() || *currentRecipient!=restoreFocus || restoreFocus->m_ruleApplicator->noFocus().valueOrDefault()) return refuseAfterNavigation("navigation-recipient-changed");
        }
        // Damage before exclusions so old pixels are actually repainted.
        for(const auto& window : *family) g_pHyprRenderer->damageWindow(window,true);
        if(!activate) {
            if(!Desktop::WindowPolicy::applyMinimized(*family,minimize)) return refuseAfterNavigation("state-bound");
            for(const auto& window : *family) window->setSuspended(minimize);
        }
        if(minimize) {
            const auto pointerSurface=g_pSeatManager->m_state.pointerFocus.lock();
            if(std::ranges::any_of(*family,[&](const auto& window){return window->wlSurface()->resource()==pointerSurface;}))
                g_pSeatManager->setPointerFocus(nullptr,{});
            if(focusedFamily) Desktop::focusState()->fullWindowFocus(nextFocus,Desktop::FOCUS_REASON_DESKTOP_STATE_CHANGE);
        } else {
            Desktop::focusState()->fullWindowFocus(restoreFocus,Desktop::FOCUS_REASON_DESKTOP_STATE_CHANGE);
            if(const auto focused=Desktop::focusState()->window()) Desktop::windowState()->raise(focused);
        }
        if(session.reducedMotion) settleReducedMotion(*family,previousWorkspace,destination);
        refreshFacts();
        if(factsRevision!=beforeMutationRevision) notifyEffectChange();
        if(!membershipCurrent() || *output!=outputGeneration || g_pSessionLockManager->isSessionLocked() || !g_pInputManager->m_exclusiveLSes.empty() || g_pSeatManager->m_seatGrab!=protectedGrab || (!minimize && !destination->isVisible())) return session.lastReply;
        if((minimize && focusedFamily && Desktop::focusState()->window()!=nextFocus) || (!minimize && Desktop::focusState()->window()!=restoreFocus)) return session.lastReply;
        const auto actualKeyboard=g_pSeatManager->m_state.keyboardFocus.lock();
        if(minimize && !focusedFamily) {
            if(Desktop::focusState()->window()!=oldFocus || actualKeyboard!=oldKeyboard || g_pSeatManager->m_seatGrab!=protectedGrab) return session.lastReply;
        } else {
            const auto intended=minimize ? nextFocus : restoreFocus;
            if(actualKeyboard!=(intended ? intended->wlSurface()->resource() : nullptr)) return session.lastReply;
        }
        for(auto id:reserved) effectBarriers.definitive(id);
        session.lastReply=effectOutcome(session,encoded,"Committed","applied");
        retainAcceptedMotion(session,encoded,*family,previousWorkspace,destination);
        motionTransitionObserved(session,encoded,*family,previousWorkspace,destination);
    } catch (...) { notifyEffectChange(); /* Preserve Unknown after unproven partial mutation. */ }
    return session.lastReply;
}

#include "geometry-effects.inc"

struct ParseState { bool duplicate = false; std::map<JsonObject*,std::set<std::string>> members; };
void parsedMember(JsonParser*, JsonObject* object, const gchar* member, gpointer data) {
    auto* state = static_cast<ParseState*>(data);
    try { if (!state->members[object].insert(member).second) state->duplicate = true; }
    catch (...) { state->duplicate = true; }
}
#include "source-scope.inc"
#include "capture-probe.inc"
#include "client-probe.inc"
#include "picker-preview.inc"
#include "capture-fd-server.inc"
#include "capture-resources.inc"

std::string observe(eHyprCtlOutputFormat, std::string request) {
    if (std::this_thread::get_id() != ownerThread) return error("wrong-thread");
    constexpr std::string_view prefix = "elm_observe ";
    if (!request.starts_with(prefix) || request.size() > 4096) return error("request-bound");
    // Peer PID comes from the server's SO_PEERCRED, never from request JSON.
    const pid_t peer = g_pHyprCtl->m_currentRequestParams.pid;
    const auto start = peer > 0 ? startTime(peer) : "";
    if (start.empty()) return error("unverified-peer");
    JsonParser* parser = json_parser_new();
    ParseState parseState;
    g_signal_connect(parser,"object-member",G_CALLBACK(parsedMember),&parseState);
    const auto payload = request.substr(prefix.size());
    GError* parseError = nullptr;
    if (!json_parser_load_from_data(parser,payload.c_str(),payload.size(),&parseError)) {
        if (parseError) g_error_free(parseError);
        g_object_unref(parser); return error("malformed-json");
    }
    JsonNode* root = json_parser_get_root(parser);
    std::string reply = error("request-schema");
    try {
        if (parseState.duplicate || !root || !JSON_NODE_HOLDS_OBJECT(root)) throw std::runtime_error("schema");
        JsonObject* object = json_node_get_object(root);
        JsonNode* version = json_object_get_member(object,"protocolVersion");
        JsonNode* kind = json_object_get_member(object,"kind");
        if (!version || !JSON_NODE_HOLDS_VALUE(version) || json_node_get_value_type(version) != G_TYPE_INT64 || json_node_get_int(version) != 3 ||
            !kind || !JSON_NODE_HOLDS_VALUE(kind) || json_node_get_value_type(kind) != G_TYPE_STRING) throw std::runtime_error("schema");
        const std::string operation = json_node_get_string(kind);
        if (operation == "hello" && fields(object,{"protocolVersion","kind"})) {
            // Retire dead/reused PIDs, bound registration independently of windows.
            std::erase_if(sessions,[](const auto& entry) {
                if(startTime(entry.first)==entry.second.start) return false;
                switcherSelections.erase(entry.second.id);erasePeerCaptures(entry.first);grantRegistry->detach(verifiedPeer(entry.first,entry.second.start));return true;
            });
            if(std::ranges::any_of(captureProbes,[&](const auto& item){return item.first.peer==peer && item.second.exported;})) throw std::runtime_error("preview-import-outstanding");
            erasePeerCaptures(peer);
            const auto admitted=grantRegistry->hello(verifiedPeer(peer,start));
            if(admitted.status!=Elm::GrantRetirement::Status::Admitted) throw std::runtime_error("grant-bound-or-exhausted");
            if(!sessions.contains(peer)) sessions.emplace(peer,Session{start,admitted.binding.session,admitted.binding.frontend,0,0,"","",{}});
            auto& session=sessions.at(peer);
            session.id=admitted.binding.session;session.frontend=admitted.binding.frontend;
            switcherSelections.erase(session.id);
            session.reducedMotion=true;session.motionRequest=0;session.presentationPid=parentPid(peer);session.presentationStart=startTime(session.presentationPid);
            session.motion={};
            session.geometryProtocol=0;session.geometryEnabled=false;session.geometryFrontend=0;session.geometryOperations.clear();session.retained.clear(); session.effectRequest=0; session.generation=0; session.lastPayload.clear(); session.lastReply.clear();
            reply = "{\"protocolVersion\":3,\"kind\":\"attached\",\"binding\":" + binding(session) +
                ",\"previewFdAddress\":"+quote(previewFdAddress)+",\"compositor\":{\"pid\":" + std::to_string(getpid()) + ",\"instance\":" + quote(g_pCompositor->m_instanceSignature) +
                ",\"coreHash\":" + quote(__hyprland_api_get_hash()) + "},\"capabilities\":{\"observe\":true,\"effects\":true,\"minimizedState\":true,\"effectProtocol\":1,\"operations\":[\"minimize\",\"restore\",\"activate\"],\"canonicalScene\":false,\"taskbarProjectionProtocol\":1,\"effectInvalidationProtocol\":1}}";
        } else if (operation=="preview-incarnation-retirement-state-request" && fields(object,{"protocolVersion","kind","binding","requestId","subjectIncarnation"})) {
            const auto bound=objectMember(object,"binding");
            const auto requestId=counter(object,"requestId"),subject=counter(object,"subjectIncarnation");
            if(!bound || !requestId || !subject || !fields(bound,{"lifetime","session","frontend"})) throw std::runtime_error("incarnation-retirement-schema");
            const auto native=counter(bound,"lifetime"),sessionId=counter(bound,"session"),frontend=counter(bound,"frontend");
            const auto found=sessions.find(peer);
            if(!native || !sessionId || !frontend || found==sessions.end() || found->second.start!=start || *native!=lifetime || *sessionId!=found->second.id || *frontend!=found->second.frontend || !grantRegistry->callerMatches(verifiedPeer(peer,start),{lifetime,*sessionId,*frontend})) reply=error("binding-mismatch");
            else if(incarnationRetirementSequence==std::numeric_limits<uint64_t>::max()) reply=error("incarnation-retirement-sequence-exhausted");
            else {
                // Presence in the native membership table, including minimized
                // or suspended members, prevents permanent retirement. No
                // mapped-window catalog or source-scope exception is consulted.
                const bool owned=std::any_of(members.begin(),members.end(),[&](const Member& member){return member.id==*subject;});
                const auto state=preview::retirement::observe(*subject,incarnation,owned);
                ++incarnationRetirementSequence;
                reply="{\"protocolVersion\":3,\"kind\":\"preview-incarnation-retirement-state\",\"retirementProtocol\":1,\"binding\":"+binding(found->second)+",\"requestId\":"+quote(std::to_string(*requestId))+",\"subjectIncarnation\":"+quote(std::to_string(*subject))+",\"sequence\":"+quote(std::to_string(incarnationRetirementSequence))+",\"clock\":"+quote(std::to_string(lifetime))+",\"now\":"+quote(std::to_string(preview::capture::nativeNow()))+",\"issuedThrough\":"+quote(std::to_string(incarnation))+",\"state\":"+quote(preview::retirement::name(state))+"}";
            }
        } else if ((operation=="binding-retire-request" || operation=="binding-retirement-state-request") && fields(object,{"protocolVersion","kind","binding","requestId","queriedBinding"})) {
            const auto bound=objectMember(object,"binding"),queried=objectMember(object,"queriedBinding");
            const auto requestId=counter(object,"requestId");
            if(!bound || !queried || !requestId || !fields(bound,{"lifetime","session","frontend"}) || !fields(queried,{"lifetime","session","frontend"})) throw std::runtime_error("retirement-schema");
            const auto native=counter(bound,"lifetime"),sessionId=counter(bound,"session"),frontend=counter(bound,"frontend");
            const auto queriedNative=counter(queried,"lifetime"),queriedSession=counter(queried,"session"),queriedFrontend=counter(queried,"frontend");
            if(!native || !sessionId || !frontend || !queriedNative || !queriedSession || !queriedFrontend) throw std::runtime_error("retirement-schema");
            const auto found=sessions.find(peer);const auto caller=verifiedPeer(peer,start);
            const Elm::GrantRetirement::Binding callerBinding{*native,*sessionId,*frontend},targetBinding{*queriedNative,*queriedSession,*queriedFrontend};
            if(found==sessions.end() || found->second.start!=start || !grantRegistry->callerMatches(caller,callerBinding)) reply=error("binding-mismatch");
            else if(*queriedNative!=lifetime) reply=error("retirement-lifetime-mismatch");
            else if(retirementSequence==std::numeric_limits<uint64_t>::max()) reply=error("retirement-sequence-exhausted");
            else if(operation=="binding-retire-request" && callerBinding==targetBinding) reply=error("retirement-current-caller");
            else {
                using State=Elm::GrantRetirement::RetirementState;
                auto state=grantRegistry->retirementState(caller,callerBinding,targetBinding);
                if(state==State::Refused) reply=error("retirement-state-refused");
                else if(state==State::Future && operation=="binding-retire-request") reply=error("retirement-future-grant");
                else {
                    if(operation=="binding-retire-request" && state==State::Registered) {
                        if(std::ranges::any_of(captureProbes,[&](const auto& item){return item.second.session==targetBinding.session && item.second.frontend==targetBinding.frontend && item.second.exported;})) throw std::runtime_error("preview-import-outstanding");
                        if(grantRegistry->retire(caller,callerBinding,targetBinding)!=Elm::GrantRetirement::Status::Admitted) throw std::runtime_error("retirement-refused");
                        std::erase_if(captureProbes,[&](const auto& entry) {return entry.second.session==targetBinding.session && entry.second.frontend==targetBinding.frontend;});
                        std::erase_if(sessions,[&](const auto& entry) { return entry.second.id==targetBinding.session && entry.second.frontend==targetBinding.frontend; });
                        state=grantRegistry->retirementState(caller,callerBinding,targetBinding);
                        if(state!=State::Retired) throw std::runtime_error("retirement-incomplete");
                    }
                    ++retirementSequence;
                    const auto queriedBinding="{\"lifetime\":"+quote(std::to_string(*queriedNative))+",\"session\":"+quote(std::to_string(*queriedSession))+",\"frontend\":"+quote(std::to_string(*queriedFrontend))+"}";
                    reply="{\"protocolVersion\":3,\"kind\":\"binding-retirement\",\"retirementProtocol\":1,\"operation\":"+quote(operation=="binding-retire-request"?"retire":"observe")+",\"binding\":"+binding(found->second)+",\"requestId\":"+quote(std::to_string(*requestId))+",\"queriedBinding\":"+queriedBinding+",\"sequence\":"+quote(std::to_string(retirementSequence))+",\"grantState\":"+quote(state==State::Retired?"Retired":state==State::Registered?"Registered":"Future")+"}";
                }
            }
        } else if (operation=="preview-client-resource-state-request" || operation=="preview-client-resource-release-request" || operation=="preview-client-resource-retire-request") {
            reply=clientResources(peer,start,operation,object);
        } else if(operation.starts_with("preview-picker-family-")) {
            reply=pickerFamilyProbe(peer,start,operation,object);
        } else if ((operation.starts_with("preview-client-") || (operation=="preview-popup-scope-request" || operation=="preview-family-scope-request" || operation=="preview-family-style-scope-request" || operation=="preview-family-style-crop-scope-request" || operation=="preview-family-backdrop-crop-scope-request" || operation=="preview-family-effect-facts-request"))) {
            reply=clientProbe(peer,start,operation,object);
        } else if ((operation.starts_with("preview-capture-probe-") || operation=="preview-popup-scoped-request" || operation=="preview-popup-state-request" || operation=="preview-popup-retire-request" || operation=="preview-family-scoped-request" || operation=="preview-family-state-request" || operation=="preview-family-retire-request" || operation=="preview-family-crop-scoped-request" || operation=="preview-family-crop-state-request" || operation=="preview-family-crop-retire-request" || operation=="preview-family-style-crop-scoped-request" || operation=="preview-family-style-crop-state-request" || operation=="preview-family-style-crop-retire-request" || operation=="preview-family-backdrop-crop-scoped-request" || operation=="preview-family-backdrop-crop-state-request" || operation=="preview-family-backdrop-crop-retire-request")) {
            reply=previewProbe(peer,start,operation,object);
        } else if (operation=="binding-registration-request" && fields(object,{"protocolVersion","kind","binding","requestId","queriedBinding"})) {
            const auto bound=objectMember(object,"binding"),queried=objectMember(object,"queriedBinding");
            const auto requestId=counter(object,"requestId");
            if(!bound || !queried || !requestId || !fields(bound,{"lifetime","session","frontend"}) || !fields(queried,{"lifetime","session","frontend"})) throw std::runtime_error("registration-schema");
            const auto native=counter(bound,"lifetime"),sessionId=counter(bound,"session"),frontend=counter(bound,"frontend");
            const auto queriedNative=counter(queried,"lifetime"),queriedSession=counter(queried,"session"),queriedFrontend=counter(queried,"frontend");
            if(!native || !sessionId || !frontend || !queriedNative || !queriedSession || !queriedFrontend) throw std::runtime_error("registration-schema");
            const auto found=sessions.find(peer);
            if(found==sessions.end() || found->second.start!=start || *native!=lifetime || *sessionId!=found->second.id || *frontend!=found->second.frontend || !grantRegistry->callerMatches(verifiedPeer(peer,start),{lifetime,*sessionId,*frontend})) reply=error("binding-mismatch");
            else if(*queriedNative!=lifetime) reply=error("registration-lifetime-mismatch");
            else {
                const bool registered=grantRegistry->registered({lifetime,*queriedSession,*queriedFrontend});
                const auto queriedBinding="{\"lifetime\":"+quote(std::to_string(*queriedNative))+",\"session\":"+quote(std::to_string(*queriedSession))+",\"frontend\":"+quote(std::to_string(*queriedFrontend))+"}";
                reply="{\"protocolVersion\":3,\"kind\":\"binding-registration\",\"registrationProtocol\":1,\"binding\":"+binding(found->second)+",\"requestId\":"+quote(std::to_string(*requestId))+",\"queriedBinding\":"+queriedBinding+",\"registered\":"+(registered?"true":"false")+"}";
            }
        } else if ((operation=="geometry-attach" || operation=="geometry-facts-request") &&
            (operation=="geometry-attach" ? fields(object,{"protocolVersion","kind","geometryProtocol","binding","requestId"}) : fields(object,{"protocolVersion","kind","geometryProtocol","binding","requestId","minimumWatermark"}))) {
            const auto bound=objectMember(object,"binding");
            const auto geometryProtocol=json_object_get_member(object,"geometryProtocol");
            const auto requestId=counter(object,"requestId");
            if(!bound || !fields(bound,{"lifetime","session","frontend"}) || !requestId || !geometryProtocol || !JSON_NODE_HOLDS_VALUE(geometryProtocol) || json_node_get_value_type(geometryProtocol)!=G_TYPE_INT64 || (json_node_get_int(geometryProtocol)!=1 && json_node_get_int(geometryProtocol)!=2)) throw std::runtime_error("geometry-schema");
            const auto native=counter(bound,"lifetime"),sessionId=counter(bound,"session"),frontend=counter(bound,"frontend");
            const auto found=sessions.find(peer);
            if(!native || !sessionId || !frontend || found==sessions.end() || found->second.start!=start || *native!=lifetime || *sessionId!=found->second.id || *frontend!=found->second.frontend || !grantRegistry->callerMatches(verifiedPeer(peer,start),{lifetime,*sessionId,*frontend})) reply=error("binding-mismatch");
            else if(operation=="geometry-attach") {
                found->second.geometryProtocol=json_node_get_int(geometryProtocol);found->second.geometryEnabled=true;found->second.geometryFrontend=found->second.frontend;found->second.geometryOperations={"maximize","restore-geometry"};if(found->second.geometryProtocol==2){found->second.geometryOperations.insert("snap");found->second.geometryOperations.insert("transfer-workspace");}
                reply="{\"protocolVersion\":3,\"kind\":\"geometry-attached\",\"geometryProtocol\":"+std::to_string(found->second.geometryProtocol)+",\"binding\":"+binding(found->second)+",\"requestId\":"+quote(std::to_string(*requestId))+",\"capabilities\":{\"observe\":true,\"effects\":true,\"effectProtocol\":2,\"operations\":"+(found->second.geometryProtocol==2?"[\"maximize\",\"restore-geometry\",\"snap\",\"transfer-workspace\"]":"[\"maximize\",\"restore-geometry\"]")+",\"placementCapacity\":256,\"canonicalScene\":false}}";
            } else if(!found->second.geometryEnabled || found->second.geometryFrontend!=found->second.frontend || found->second.geometryProtocol!=json_node_get_int(geometryProtocol)) reply=error("geometry-negotiation-required");
            else {
                const auto floor=counter(object,"minimumWatermark",true);
                if(!floor || geometrySequence==std::numeric_limits<uint64_t>::max() || *floor>geometrySequence+1) reply=error("geometry-watermark-unavailable");
                else {
                    const auto facts=refreshGeometryFacts(found->second.geometryProtocol);++geometrySequence;
                    reply="{\"protocolVersion\":3,\"kind\":\"geometry-facts\",\"geometryProtocol\":"+std::to_string(found->second.geometryProtocol)+",\"binding\":"+binding(found->second)+",\"requestId\":"+quote(std::to_string(*requestId))+",\"sequence\":"+quote(std::to_string(geometrySequence))+",\"revision\":"+quote(std::to_string(geometryRevision))+",\"outputGeneration\":"+quote(std::to_string(outputGeneration))+",\"facts\":"+facts+"}";
                }
            }
        } else if(operation=="motion-profile-set" && fields(object,{"protocolVersion","kind","binding","requestId","profile"})) {
            const auto bound=objectMember(object,"binding");const auto requestId=counter(object,"requestId");const auto found=sessions.find(peer);const auto profileNode=json_object_get_member(object,"profile");const std::string profile=profileNode && json_node_get_value_type(profileNode)==G_TYPE_STRING ? json_node_get_string(profileNode) : "";
            if(!bound || !fields(bound,{"lifetime","session","frontend"}) || !requestId || (profile!="reduced" && profile!="full"))throw std::runtime_error("motion-schema");
            const auto native=counter(bound,"lifetime"),sessionId=counter(bound,"session"),frontend=counter(bound,"frontend");
            if(!native || !sessionId || !frontend || found==sessions.end() || found->second.start!=start || *native!=lifetime || *sessionId!=found->second.id || *frontend!=found->second.frontend || !grantRegistry->callerMatches(verifiedPeer(peer,start),{lifetime,*sessionId,*frontend}))reply=error("binding-mismatch");
            else if(*requestId<=found->second.motionRequest)reply=error("motion-request-retired");
            else {found->second.motionRequest=*requestId;found->second.reducedMotion=profile=="reduced";found->second.motion.settle=found->second.reducedMotion;reply="{\"protocolVersion\":3,\"kind\":\"motion-profile\",\"binding\":"+binding(found->second)+",\"requestId\":"+quote(std::to_string(*requestId))+",\"profile\":"+quote(profile)+"}";}
        } else if(operation=="pointer-ownership-request" && fields(object,{"protocolVersion","kind","binding","requestId"})) {
            const auto bound=objectMember(object,"binding");const auto requestId=counter(object,"requestId");const auto found=sessions.find(peer);
            if(!bound || !fields(bound,{"lifetime","session","frontend"}) || !requestId)throw std::runtime_error("pointer-schema");
            const auto native=counter(bound,"lifetime"),sessionId=counter(bound,"session"),frontend=counter(bound,"frontend");
            if(!native || !sessionId || !frontend || found==sessions.end() || found->second.start!=start || *native!=lifetime || *sessionId!=found->second.id || *frontend!=found->second.frontend || !grantRegistry->callerMatches(verifiedPeer(peer,start),{lifetime,*sessionId,*frontend}))reply=error("binding-mismatch");
            else reply=pointerOwnership(found->second,*requestId);
        } else if(operation=="shell-shortcuts-request" && fields(object,{"protocolVersion","kind","binding","requestId"})) {
            const auto bound=objectMember(object,"binding");const auto requestId=counter(object,"requestId");const auto found=sessions.find(peer);
            if(!bound || !fields(bound,{"lifetime","session","frontend"}) || !requestId)throw std::runtime_error("shortcut-schema");
            const auto native=counter(bound,"lifetime"),sessionId=counter(bound,"session"),frontend=counter(bound,"frontend");
            if(!native || !sessionId || !frontend || found==sessions.end() || found->second.start!=start || *native!=lifetime || *sessionId!=found->second.id || *frontend!=found->second.frontend || !grantRegistry->callerMatches(verifiedPeer(peer,start),{lifetime,*sessionId,*frontend})) reply=error("binding-mismatch");
            else {
                if(shellShortcutSession!=*sessionId || shellShortcutFrontend!=*frontend) {
                    const bool alive=std::ranges::any_of(sessions,[&](const auto& entry){return entry.second.id==shellShortcutSession && entry.second.frontend==shellShortcutFrontend && startTime(entry.first)==entry.second.start;});
                    if(alive)throw std::runtime_error("shortcut-owner-busy");
                    shellShortcuts.clear();shellShortcutSerial=0;shellShortcutSession=*sessionId;shellShortcutFrontend=*frontend;
                }
                reply=shellShortcutJournal(found->second,*requestId);
            }
        } else if(((operation=="switcher-journal-request" || operation=="switcher-journal-observe-request") && fields(object,{"protocolVersion","kind","binding","requestId"})) ||
                  (operation=="switcher-selection-request" && fields(object,{"protocolVersion","kind","binding","requestId","chord","root"})) ||
                  (operation=="switcher-cancel-request" && fields(object,{"protocolVersion","kind","binding","requestId","chord"}))) {
            auto* bound=objectMember(object,"binding");const auto requestId=counter(object,"requestId");
            const auto found=sessions.find(peer);
            if(!bound || !fields(bound,{"lifetime","session","frontend"}) || !requestId)throw std::runtime_error("switcher-schema");
            const auto native=counter(bound,"lifetime"),sessionId=counter(bound,"session"),frontend=counter(bound,"frontend");
            if(!native || !sessionId || !frontend || found==sessions.end() || found->second.start!=start || *native!=lifetime || *sessionId!=found->second.id || *frontend!=found->second.frontend || !grantRegistry->callerMatches(verifiedPeer(peer,start),{lifetime,*sessionId,*frontend}))reply=error("binding-mismatch");
            else {
                if(operation!="switcher-journal-observe-request" && switcherOwnerSession && (switcherOwnerSession!=*sessionId || switcherOwnerFrontend!=*frontend)) {
                    const bool alive=std::ranges::any_of(sessions,[&](const auto& entry){return entry.second.id==switcherOwnerSession && entry.second.frontend==switcherOwnerFrontend && startTime(entry.first)==entry.second.start;});
                    if(alive)throw std::runtime_error("switcher-owner-busy");
                    cancelSwitcher();switcherOwnerSession=switcherOwnerFrontend=0;
                }
                if(operation=="switcher-journal-request" || operation=="switcher-journal-observe-request") {
                    if(operation=="switcher-journal-request"){switcherOwnerSession=*sessionId;switcherOwnerFrontend=*frontend;}
                    reply="{\"protocolVersion\":3,\"kind\":\"switcher-journal\",\"binding\":"+binding(found->second)+",\"requestId\":"+quote(std::to_string(*requestId))+",\"chord\":"+switcherJournal(found->second,operation=="switcher-journal-observe-request")+"}";
                } else if(operation=="switcher-cancel-request") {
                    const auto chord=counter(object,"chord");if(!chord)throw std::runtime_error("switcher-cancel-schema");
                    if(*chord==switcherChord.generation && switcherChord.ownerSession==*sessionId && switcherChord.ownerFrontend==*frontend)cancelSwitcher();
                    reply="{\"protocolVersion\":3,\"kind\":\"switcher-journal\",\"binding\":"+binding(found->second)+",\"requestId\":"+quote(std::to_string(*requestId))+",\"chord\":"+switcherJournal(found->second)+"}";
                } else {
                    const auto chord=counter(object,"chord"),root=counter(object,"root");
                    if(!chord || !root)throw std::runtime_error("switcher-selection-schema");
                    const auto prior=switcherSelections.find(*sessionId);
                    if(prior==switcherSelections.end() || *requestId>prior->second.request)switcherSelections[*sessionId]={*requestId,*chord,*root};
                    else if(*requestId==prior->second.request && (prior->second.generation!=*chord || prior->second.root!=*root))prior->second.root=0;
                    reply="{\"protocolVersion\":3,\"kind\":\"switcher-selection\",\"binding\":"+binding(found->second)+",\"requestId\":"+quote(std::to_string(*requestId))+"}";
                }
            }
        } else if(operation=="window-effect" && fields(object,{"protocolVersion","kind","binding","effectProtocol","intent"})) {
            const auto bound=objectMember(object,"binding");
            const auto found=sessions.find(peer);const auto effectProtocol=json_object_get_member(object,"effectProtocol");
            if(!bound || !fields(bound,{"lifetime","session","frontend"}) || !effectProtocol || !JSON_NODE_HOLDS_VALUE(effectProtocol) || json_node_get_value_type(effectProtocol)!=G_TYPE_INT64 || (json_node_get_int(effectProtocol)!=1 && json_node_get_int(effectProtocol)!=2)) throw std::runtime_error("effect-schema");
            const auto native=counter(bound,"lifetime"),sessionId=counter(bound,"session"),frontend=counter(bound,"frontend");
            if(!native || !sessionId || !frontend || found==sessions.end() || found->second.start!=start || *native!=lifetime || *sessionId!=found->second.id || *frontend!=found->second.frontend || !grantRegistry->callerMatches(verifiedPeer(peer,start),{lifetime,*sessionId,*frontend})) reply=error("binding-mismatch");
            else if(json_node_get_int(effectProtocol)==2) {
                if(!found->second.geometryEnabled) reply=error("geometry-negotiation-required");
                else reply=performGeometryEffect(found->second,object);
            } else reply=performEffect(found->second,object,payload);
        } else if ((operation == "snapshot-request" || operation == "scene-facts-request" || operation == "activation-history-request" || operation == "render-trace-request" || operation == "retain-render-trace-request" || operation == "retained-render-trace-request") && (fields(object,{"protocolVersion","kind","binding","requestId","minimumWatermark"}) || (operation=="scene-facts-request" && fields(object,{"protocolVersion","kind","binding","requestId","minimumWatermark","attentionProtocol"})))) {
            const auto attentionVersion=json_object_get_member(object,"attentionProtocol");
            const bool attention=attentionVersion!=nullptr;
            if(attention && (!JSON_NODE_HOLDS_VALUE(attentionVersion) || json_node_get_value_type(attentionVersion)!=G_TYPE_INT64 || json_node_get_int(attentionVersion)!=1)) throw std::runtime_error("attention-version");
            const bool history = operation == "activation-history-request";
            const bool facts = operation == "scene-facts-request" || history;
            const bool trace = operation == "render-trace-request" || operation == "retain-render-trace-request" || operation == "retained-render-trace-request";
            auto& activeSequence = facts ? factsSequence : sequence;
            auto& activeRevision = facts ? factsRevision : revision;
            auto& previous = facts ? previousFacts : previousProjection;
            JsonObject* bound = objectMember(object,"binding");
            const auto requestId = counter(object,"requestId"), floor = counter(object,"minimumWatermark",true);
            if (!bound || !fields(bound,{"lifetime","session","frontend"}) || !requestId || !floor) throw std::runtime_error("schema");
            const auto native = counter(bound,"lifetime"), sessionId = counter(bound,"session"), frontend = counter(bound,"frontend");
            const auto found = sessions.find(peer);
            if (!native || !sessionId || !frontend || found == sessions.end() || found->second.start != start ||
                *native != lifetime || *sessionId != found->second.id || *frontend != found->second.frontend || !grantRegistry->callerMatches(verifiedPeer(peer,start),{lifetime,*sessionId,*frontend})) {
                reply = error("binding-mismatch");
            } else if(trace) {
                refreshOutputs();
                auto& retained=found->second.retained;
                if(operation=="retain-render-trace-request") retained=Render::SceneTrace::snapshots();
                if(operation=="retained-render-trace-request" && retained.empty()) throw std::runtime_error("retained-unavailable");
                const bool held=operation!="render-trace-request";
                reply="{\"protocolVersion\":3,\"kind\":\"render-trace\",\"traceProtocol\":3,\"retained\":"+std::string(held?"true":"false")+",\"binding\":"+binding(found->second)+",\"requestId\":"+quote(std::to_string(*requestId))+",\"outputGeneration\":"+quote(std::to_string(outputGeneration))+",\"frames\":"+renderTrace(held?retained:Render::SceneTrace::snapshots())+"}";
            } else if (activeSequence == std::numeric_limits<uint64_t>::max() || *floor > activeSequence + 1) {
                reply = error("watermark-unavailable");
            } else {
                // Single synchronous event-thread callback: no blocking child query,
                // nested dispatch, event-loop pumping or native mutation.
                const auto value = facts ? refreshFacts() : projection();
                if (value != previous) {
                    if (activeRevision == std::numeric_limits<uint64_t>::max()) throw std::runtime_error("revision-exhausted");
                    ++activeRevision; previous = value;
                }
                ++activeSequence;
                if(history) {
                    reply="{\"protocolVersion\":3,\"kind\":\"activation-history\",\"binding\":"+binding(found->second)+",\"requestId\":"+quote(std::to_string(*requestId))+",\"context\":{\"lifetime\":"+quote(std::to_string(lifetime))+",\"epoch\":"+quote(std::to_string(found->second.frontend))+",\"output\":"+quote(std::to_string(outputGeneration))+",\"revision\":"+quote(std::to_string(factsRevision))+"},\"roots\":"+activationRoots()+"}";
                } else reply = "{\"protocolVersion\":3,\"kind\":" + quote(facts ? "scene-facts" : "snapshot") + ",\"binding\":" + binding(found->second) +
                    ",\"requestId\":\"" + std::to_string(*requestId) + "\",\"sequence\":\"" + std::to_string(activeSequence) +
                    "\",\"revision\":\"" + std::to_string(activeRevision) + "\"," + (attention ? "\"attentionProtocol\":1," : "") + (facts ? "\"outputGeneration\":"+quote(std::to_string(outputGeneration))+",\"facts\":" : "\"windows\":") + (facts && !attention ? sceneFacts(false) : value) + "}";
            }
        }
    } catch (...) { /* bounded refusal; no IPC exception escapes into compositor */ }
    g_object_unref(parser); return reply;
}
}
APICALL EXPORT std::string PLUGIN_API_VERSION() { return HYPRLAND_API_VERSION; }
APICALL EXPORT PLUGIN_DESCRIPTION_INFO PLUGIN_INIT(HANDLE handle) {
    if (std::string(__hyprland_api_get_hash()) != std::string(__hyprland_api_get_client_hash())) throw std::runtime_error("Owning header mismatch");
    pluginHandle = handle; ownerThread = std::this_thread::get_id(); lifetime = randomIdentity();
    captureProbes.clear();captureBudget=std::make_unique<preview::capture::Budget>(128ULL*1024*1024,2);
    grantRegistry=std::make_unique<Elm::GrantRetirement::Registry>(lifetime);retirementSequence=0;incarnationRetirementSequence=0;captureResourceSequence=0;
    Render::SceneTrace::clearBindings();
    previewSources.clear();clientTrees.clear();popupTrees.clear();familySources.clear();familyStyles.clear();incarnation = sequence = revision = outputGeneration = 0; previousOutputs.clear(); recentFocus.clear(); activationHistory.clear(); previousProjection.clear(); members.clear(); sessions.clear();
    switcherChord={};switcherSerial=0;switcherAlts.clear();switcherTab=switcherStepAvailable=false;switcherSelections.clear();switcherOwnerSession=switcherOwnerFrontend=0;
    factsSequence = factsRevision = 0; previousFacts.clear();
    geometryPlacements={};effectBarriers={};geometryWorkspaces={};geometryOutputs={};geometryAreas.clear();geometryAreaRevision=geometrySequence=geometryRevision=0;previousGeometry.clear();
    for (const auto& window : Desktop::windowState()->windows()) if (window->m_isMapped) birth(window);
    opened = Event::bus()->m_events.window.open.listen([](PHLWINDOW window) { try { birth(window); } catch (...) { members.clear(); Render::SceneTrace::clearBindings(); } });
    closed = Event::bus()->m_events.window.close.listen([](PHLWINDOW window) { forget(window); });
    activated = Event::bus()->m_events.window.active.listen([](PHLWINDOW window, Desktop::eFocusReason) {
        recordActivation(window);
    });
    if (const auto current=Desktop::focusState()->window()) recordActivation(current);
    shellShortcuts.clear();shellShortcutSerial=shellShortcutSession=shellShortcutFrontend=0;
    pointerSerial=1;pointerState="idle";pointerOwner="null";
    pointerFrames=Event::bus()->m_events.render.pre.listen([](PHLMONITOR){try{refreshPointerOwnership();settleAcceptedMotion();settleShellMotion();}catch(...){}});
    switcherKeys=Event::bus()->m_events.input.keyboard.key.listen(switcherKey);
    if(!HyprlandAPI::addLuaFunction(handle,"warlock","apps_menu",appsMenu) || !HyprlandAPI::addLuaFunction(handle,"warlock","system_menu",systemMenu) || !HyprlandAPI::addLuaFunction(handle,"warlock","notification_history",notificationHistory))throw std::runtime_error("Shell shortcut binding registration failed");
    if(!HyprlandAPI::addLuaFunction(handle,"warlock","switcher_forward",switcherForward) || !HyprlandAPI::addLuaFunction(handle,"warlock","switcher_reverse",switcherReverse))throw std::runtime_error("Switcher binding registration failed");
    command = HyprlandAPI::registerHyprCtlCommand(handle,{"elm_observe ",false,observe});
    if (!command) throw std::runtime_error("Authority command registration failed");
    previewPrivacy=previewRendering=1;previewObservation=0;
    previewLocked=g_pSessionLockManager->m_events.lock.listen([]{cancelSwitcher();shellShortcuts.clear();notifyShellShortcuts();revokePreview(true);});
    previewReloaded=Event::bus()->m_events.config.preReload.listen([]{cancelSwitcher();shellShortcuts.clear();notifyShellShortcuts();switcherAlts.clear();switcherTab=switcherStepAvailable=false;revokePreview(false);});
    previewOutputRemoved=Event::bus()->m_events.monitor.removed.listen([](PHLMONITOR){revokePreview(false);});
    startPreviewFdServer();
    return {"elm-observation-authority","Native first-class minimize/restore authority experiment","local","0.2"};
}
APICALL EXPORT void PLUGIN_EXIT() {
    shellShortcuts.clear();shellShortcutSerial=shellShortcutSession=shellShortcutFrontend=0;
    pointerFrames.reset();
    switcherKeys.reset();switcherSelections.clear();switcherAlts.clear();switcherChord={};switcherOwnerSession=switcherOwnerFrontend=0;
    stopPreviewFdServer();previewLocked.reset();previewReloaded.reset();previewOutputRemoved.reset();
    opened.reset(); closed.reset(); activated.reset(); recentFocus.clear();activationHistory.clear();
    if (command) HyprlandAPI::unregisterHyprCtlCommand(pluginHandle,command);
    command.reset();previewSources.clear();clientTrees.clear();popupTrees.clear();familySources.clear();familyStyles.clear();captureProbes.clear();captureBudget.reset(); members.clear(); sessions.clear();grantRegistry.reset(); Render::SceneTrace::clearBindings();
    geometryPlacements={};effectBarriers={};geometryWorkspaces={};geometryOutputs={};geometryAreas.clear();geometryAreaRevision=geometrySequence=geometryRevision=0;previousGeometry.clear();
}
