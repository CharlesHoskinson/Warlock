#include <hyprland/src/plugins/PluginAPI.hpp>
#include <hyprland/src/Compositor.hpp>
#include <hyprland/src/debug/HyprCtl.hpp>
#include <hyprland/src/desktop/state/WindowState.hpp>
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
#include <thread>

namespace {
HANDLE pluginHandle;
SP<SHyprCtlCommand> command;
CHyprSignalListener opened, closed;
std::thread::id ownerThread;
uint64_t lifetime = 0, incarnation = 0, sequence = 0, revision = 0;
std::string previousProjection;
struct Member { PHLWINDOWREF window; uint64_t id; };
std::vector<Member> members;
struct Session { std::string start; uint64_t id; uint64_t frontend; };
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
    std::erase_if(members,[&](const Member& member) { return !member.window.lock() || member.window.lock() == window; });
}
void birth(const PHLWINDOW& window) {
    forget(window);
    if (incarnation == std::numeric_limits<uint64_t>::max()) throw std::runtime_error("Incarnation exhausted");
    members.push_back({window, ++incarnation});
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
        result += "{\"incarnation\":\"" + std::to_string(found->id) + "\",\"label\":" + quote(label(window->m_title)) + ",\"minimized\":null}";
    }
    return result + "]";
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
    const auto payload = request.substr(prefix.size());
    GError* parseError = nullptr;
    if (!json_parser_load_from_data(parser,payload.c_str(),payload.size(),&parseError)) {
        if (parseError) g_error_free(parseError);
        g_object_unref(parser); return error("malformed-json");
    }
    JsonNode* root = json_parser_get_root(parser);
    std::string reply = error("request-schema");
    try {
        if (!root || !JSON_NODE_HOLDS_OBJECT(root)) throw std::runtime_error("schema");
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
                sessions.emplace(peer,Session{start,randomIdentity(),0});
            }
            auto& session = sessions.at(peer);
            if (session.frontend == std::numeric_limits<uint64_t>::max()) throw std::runtime_error("epoch-exhausted");
            ++session.frontend;
            reply = "{\"protocolVersion\":3,\"kind\":\"attached\",\"binding\":" + binding(session) +
                ",\"compositor\":{\"pid\":" + std::to_string(getpid()) + ",\"instance\":" + quote(g_pCompositor->m_instanceSignature) +
                ",\"coreHash\":" + quote(__hyprland_api_get_hash()) + "},\"capabilities\":{\"observe\":true,\"effects\":false,\"minimizedState\":false}}";
        } else if (operation == "snapshot-request" && fields(object,{"protocolVersion","kind","binding","requestId","minimumWatermark"})) {
            JsonObject* bound = objectMember(object,"binding");
            const auto requestId = counter(object,"requestId"), floor = counter(object,"minimumWatermark",true);
            if (!bound || !fields(bound,{"lifetime","session","frontend"}) || !requestId || !floor) throw std::runtime_error("schema");
            const auto native = counter(bound,"lifetime"), sessionId = counter(bound,"session"), frontend = counter(bound,"frontend");
            const auto found = sessions.find(peer);
            if (!native || !sessionId || !frontend || found == sessions.end() || found->second.start != start ||
                *native != lifetime || *sessionId != found->second.id || *frontend != found->second.frontend) {
                reply = error("binding-mismatch");
            } else if (sequence == std::numeric_limits<uint64_t>::max() || *floor > sequence + 1) {
                reply = error("watermark-unavailable");
            } else {
                // Single synchronous event-thread callback: no blocking child query,
                // nested dispatch, event-loop pumping or native mutation.
                const auto windows = projection();
                if (windows != previousProjection) {
                    if (revision == std::numeric_limits<uint64_t>::max()) throw std::runtime_error("revision-exhausted");
                    ++revision; previousProjection = windows;
                }
                ++sequence;
                reply = "{\"protocolVersion\":3,\"kind\":\"snapshot\",\"binding\":" + binding(found->second) +
                    ",\"requestId\":\"" + std::to_string(*requestId) + "\",\"sequence\":\"" + std::to_string(sequence) +
                    "\",\"revision\":\"" + std::to_string(revision) + "\",\"windows\":" + windows + "}";
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
    incarnation = sequence = revision = 0; previousProjection.clear(); members.clear(); sessions.clear();
    for (const auto& window : Desktop::windowState()->windows()) if (window->m_isMapped) birth(window);
    opened = Event::bus()->m_events.window.open.listen([](PHLWINDOW window) { try { birth(window); } catch (...) { members.clear(); } });
    closed = Event::bus()->m_events.window.close.listen([](PHLWINDOW window) { forget(window); });
    command = HyprlandAPI::registerHyprCtlCommand(handle,{"elm_observe ",false,observe});
    if (!command) throw std::runtime_error("Authority command registration failed");
    return {"elm-observation-authority","Read-only coherent incarnation projection","local","0.1"};
}
APICALL EXPORT void PLUGIN_EXIT() {
    opened.reset(); closed.reset();
    if (command) HyprlandAPI::unregisterHyprCtlCommand(pluginHandle,command);
    command.reset(); members.clear(); sessions.clear();
}
