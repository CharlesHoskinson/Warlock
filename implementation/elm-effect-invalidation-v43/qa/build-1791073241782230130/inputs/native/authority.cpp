#include <hyprland/src/desktop/rule/windowRule/WindowRuleApplicator.hpp>
#include "WindowPolicy.hpp"
#include "SceneTrace.hpp"
#include "SceneModal.hpp"
#include <hyprland/src/managers/SeatManager.hpp>
#include <hyprland/src/managers/EventManager.hpp>
#include <hyprland/src/managers/input/InputManager.hpp>
#include <hyprland/src/managers/SessionLockManager.hpp>
#include <hyprland/src/state/MonitorState.hpp>
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

namespace {
HANDLE pluginHandle;
SP<SHyprCtlCommand> command;
CHyprSignalListener opened, closed, activated;
std::vector<PHLWINDOWREF> recentFocus;
uint64_t outputGeneration=0;
std::string previousOutputs;
std::thread::id ownerThread;
uint64_t lifetime = 0, incarnation = 0, sequence = 0, revision = 0;
std::string previousProjection;
uint64_t factsSequence = 0, factsRevision = 0;
std::string previousFacts;
struct Member { PHLWINDOWREF window; uint64_t id; };
std::vector<Member> members;
struct Session { std::string start; uint64_t id; uint64_t frontend; uint64_t effectRequest=0, generation=0; std::string lastPayload, lastReply; std::vector<Render::SceneTrace::Frame> retained; };
std::map<pid_t, Session> sessions;

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
    std::erase_if(members,[&](const Member& member) { return !member.window.lock() || member.window.lock() == window; });
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
    members.push_back({window,id});
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
std::string sceneFacts() {
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
std::string effectOutcome(const Session& session, const std::string& intent, const char* status, const char* reason) {
    return "{\"protocolVersion\":3,\"kind\":\"effect-outcome\",\"effectProtocol\":1,\"binding\":"+binding(session)+
        ",\"intent\":"+intent+",\"status\":"+quote(status)+",\"reason\":"+quote(reason)+
        ",\"revision\":"+quote(std::to_string(factsRevision))+",\"outputGeneration\":"+quote(std::to_string(outputGeneration))+"}";
}
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
    const std::string fingerprint=quote(operation)+":"+std::to_string(*requestId)+":"+std::to_string(*generation)+":"+std::to_string(*target)+":"+std::to_string(*native)+":"+std::to_string(*epoch)+":"+std::to_string(*output)+":"+std::to_string(*expected);
    if(*native!=lifetime || *epoch!=session.frontend) return effectOutcome(session,encoded,"Refused","authority-mismatch");
    if(*requestId==session.effectRequest) return fingerprint==session.lastPayload ? session.lastReply : effectOutcome(session,encoded,"Refused","request-reuse");
    if(*requestId<session.effectRequest || *generation<=session.generation) return effectOutcome(session,encoded,"Refused","operation-order");
    refreshFacts();
    const auto reject=[&](const char* reason) {session.lastReply=effectOutcome(session,encoded,"Refused",reason);return session.lastReply;};
    // The journal is bounded to one request per authenticated peer/epoch. Older
    // identities refuse; exact retry returns its original terminal outcome.
    session.effectRequest=*requestId;session.generation=*generation;session.lastPayload=fingerprint;
    session.lastReply=effectOutcome(session,encoded,"Unknown","effect-unproven");
    if(operation!="minimize" && operation!="restore" && operation!="activate") return reject("unsupported-operation");
    if(*output!=outputGeneration || *expected!=factsRevision) return reject("dependency-mismatch");
    if(g_pSessionLockManager->isSessionLocked() || !g_pInputManager->m_exclusiveLSes.empty()) return reject("exclusive-input");
    if(g_pSeatManager->m_seatGrab) return reject("seat-grab");
    const auto member=std::find_if(members.begin(),members.end(),[&](const Member& entry){return entry.id==*target;});
    if(member==members.end() || !member->window.lock() || !member->window.lock()->m_isMapped) return reject("stale-incarnation");
    const auto targetWindow=member->window.lock();const auto family=nativeFamily(targetWindow);
    if(!family.has_value() || family->empty()) return reject("invalid-family");
    const bool minimize=operation=="minimize";
    const bool activate=operation=="activate";
    for(const auto& window : *family) {
        if(!window->m_workspace || window->onSpecialWorkspace() || window->isHidden() || !window->m_workspace->isVisible()) return reject("ineligible-family");
        if(Desktop::WindowPolicy::isMinimized(window)!=(operation=="restore")) return reject("family-state-mismatch");
    }
    PHLWINDOW restoreFocus=nullptr;
    if(!minimize) {
        const auto root=std::find_if(family->begin(),family->end(),[&](const auto& window){return !window->parent() || std::ranges::find(*family,window->parent())==family->end();});
        if(root==family->end()) return reject("invalid-family-root");
        const auto predicted=SceneModal::focusRecipient(*root,!activate);
        if(!predicted.has_value() || !*predicted || (*predicted)->m_ruleApplicator->noFocus().valueOrDefault()) return reject("ambiguous-or-ineligible-restore-focus");
        restoreFocus=*predicted;
    }
    const auto beforeMutationRevision=factsRevision;
    const auto oldFocus=Desktop::focusState()->window();
    const auto oldKeyboard=g_pSeatManager->m_state.keyboardFocus.lock();
    const bool focusedFamily=std::ranges::find(*family,oldFocus)!=family->end();
    const auto nextFocus=minimize && focusedFamily ? successor(*family) : oldFocus;
    try {
        // No event-loop pumping or external dispatch occurs in this callback.
        // Damage before exclusions so old pixels are actually repainted.
        for(const auto& window : *family) g_pHyprRenderer->damageWindow(window,true);
        if(!activate) {
            if(!Desktop::WindowPolicy::applyMinimized(*family,minimize)) return reject("state-bound");
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
        refreshFacts();
        if(factsRevision!=beforeMutationRevision) notifyEffectChange();
        if((minimize && focusedFamily && Desktop::focusState()->window()!=nextFocus) || (!minimize && Desktop::focusState()->window()!=restoreFocus)) return session.lastReply;
        const auto actualKeyboard=g_pSeatManager->m_state.keyboardFocus.lock();
        if(minimize && !focusedFamily) {
            if(Desktop::focusState()->window()!=oldFocus || actualKeyboard!=oldKeyboard) return session.lastReply;
        } else {
            const auto intended=minimize ? nextFocus : restoreFocus;
            if(actualKeyboard!=(intended ? intended->wlSurface()->resource() : nullptr)) return session.lastReply;
        }
        session.lastReply=effectOutcome(session,encoded,"Committed","applied");
    } catch (...) { notifyEffectChange(); /* Preserve Unknown after unproven partial mutation. */ }
    return session.lastReply;
}

struct ParseState { bool duplicate = false; std::map<JsonObject*,std::set<std::string>> members; };
void parsedMember(JsonParser*, JsonObject* object, const gchar* member, gpointer data) {
    auto* state = static_cast<ParseState*>(data);
    try { if (!state->members[object].insert(member).second) state->duplicate = true; }
    catch (...) { state->duplicate = true; }
}
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
            std::erase_if(sessions,[](const auto& entry) { return startTime(entry.first) != entry.second.start; });
            if (!sessions.contains(peer)) {
                if (sessions.size() >= 16) throw std::runtime_error("session-bound");
                sessions.emplace(peer,Session{start,randomIdentity(),0,0,0,"","",{}});
            }
            auto& session = sessions.at(peer);
            if (session.frontend == std::numeric_limits<uint64_t>::max()) throw std::runtime_error("epoch-exhausted");
            ++session.frontend;session.retained.clear(); session.effectRequest=0; session.generation=0; session.lastPayload.clear(); session.lastReply.clear();
            reply = "{\"protocolVersion\":3,\"kind\":\"attached\",\"binding\":" + binding(session) +
                ",\"compositor\":{\"pid\":" + std::to_string(getpid()) + ",\"instance\":" + quote(g_pCompositor->m_instanceSignature) +
                ",\"coreHash\":" + quote(__hyprland_api_get_hash()) + "},\"capabilities\":{\"observe\":true,\"effects\":true,\"minimizedState\":true,\"effectProtocol\":1,\"operations\":[\"minimize\",\"restore\",\"activate\"],\"canonicalScene\":false,\"taskbarProjectionProtocol\":1,\"effectInvalidationProtocol\":1}}";
        } else if(operation=="window-effect" && fields(object,{"protocolVersion","kind","binding","effectProtocol","intent"})) {
            const auto bound=objectMember(object,"binding");
            const auto found=sessions.find(peer);const auto effectProtocol=json_object_get_member(object,"effectProtocol");
            if(!bound || !fields(bound,{"lifetime","session","frontend"}) || !effectProtocol || !JSON_NODE_HOLDS_VALUE(effectProtocol) || json_node_get_value_type(effectProtocol)!=G_TYPE_INT64 || json_node_get_int(effectProtocol)!=1) throw std::runtime_error("effect-schema");
            const auto native=counter(bound,"lifetime"),sessionId=counter(bound,"session"),frontend=counter(bound,"frontend");
            if(!native || !sessionId || !frontend || found==sessions.end() || found->second.start!=start || *native!=lifetime || *sessionId!=found->second.id || *frontend!=found->second.frontend) reply=error("binding-mismatch");
            else reply=performEffect(found->second,object,payload);
        } else if ((operation == "snapshot-request" || operation == "scene-facts-request" || operation == "render-trace-request" || operation == "retain-render-trace-request" || operation == "retained-render-trace-request") && fields(object,{"protocolVersion","kind","binding","requestId","minimumWatermark"})) {
            const bool facts = operation == "scene-facts-request";
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
                *native != lifetime || *sessionId != found->second.id || *frontend != found->second.frontend) {
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
                reply = "{\"protocolVersion\":3,\"kind\":" + quote(facts ? "scene-facts" : "snapshot") + ",\"binding\":" + binding(found->second) +
                    ",\"requestId\":\"" + std::to_string(*requestId) + "\",\"sequence\":\"" + std::to_string(activeSequence) +
                    "\",\"revision\":\"" + std::to_string(activeRevision) + "\"," + (facts ? "\"outputGeneration\":"+quote(std::to_string(outputGeneration))+",\"facts\":" : "\"windows\":") + value + "}";
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
    Render::SceneTrace::clearBindings();
    incarnation = sequence = revision = outputGeneration = 0; previousOutputs.clear(); recentFocus.clear(); previousProjection.clear(); members.clear(); sessions.clear();
    factsSequence = factsRevision = 0; previousFacts.clear();
    for (const auto& window : Desktop::windowState()->windows()) if (window->m_isMapped) birth(window);
    opened = Event::bus()->m_events.window.open.listen([](PHLWINDOW window) { try { birth(window); } catch (...) { members.clear(); Render::SceneTrace::clearBindings(); } });
    closed = Event::bus()->m_events.window.close.listen([](PHLWINDOW window) { forget(window); });
    activated = Event::bus()->m_events.window.active.listen([](PHLWINDOW window, Desktop::eFocusReason) {
        std::erase_if(recentFocus,[&](const auto& reference){return !reference.lock() || reference.lock()==window;});
        if(window){ if(recentFocus.size()>=256)recentFocus.erase(recentFocus.begin());recentFocus.emplace_back(window);}
    });
    if (const auto current=Desktop::focusState()->window()) recentFocus.emplace_back(current);
    command = HyprlandAPI::registerHyprCtlCommand(handle,{"elm_observe ",false,observe});
    if (!command) throw std::runtime_error("Authority command registration failed");
    return {"elm-observation-authority","Native first-class minimize/restore authority experiment","local","0.2"};
}
APICALL EXPORT void PLUGIN_EXIT() {
    opened.reset(); closed.reset(); activated.reset(); recentFocus.clear();
    if (command) HyprlandAPI::unregisterHyprCtlCommand(pluginHandle,command);
    command.reset(); members.clear(); sessions.clear(); Render::SceneTrace::clearBindings();
}
