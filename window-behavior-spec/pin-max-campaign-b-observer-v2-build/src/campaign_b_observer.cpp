// Draft for exact source review. No build/load authority. No setters or event hooks.
#include <plugins/PluginAPI.hpp>
#include <desktop/state/WindowState.hpp>
#include <desktop/state/ViewState.hpp>
#include <desktop/state/FocusState.hpp>
#include <desktop/state/pin/NativePinState.hpp>
#include <desktop/view/Window.hpp>
#include <desktop/view/Group.hpp>
#include <desktop/Workspace.hpp>
#include <layout/algorithm/Algorithm.hpp>
#include <layout/algorithm/FloatingAlgorithm.hpp>
#include <layout/algorithm/tiled/scrolling/ScrollingAlgorithm.hpp>
#include <layout/algorithm/tiled/scrolling/ScrollTapeController.hpp>
#include <layout/target/Target.hpp>
#include <layout/space/Space.hpp>
#include <managers/fullscreen/FullscreenController.hpp>
#include <managers/fullscreen/handler/FullscreenHandler.hpp>
#include <managers/input/InputManager.hpp>
#include <output/Monitor.hpp>
#include <json-c/json.h>
#include <charconv>
#include <chrono>
#include <cmath>
#include <fstream>
#include <format>
#include <sstream>
#include <cstring>
#include <limits>
#include <memory>
#include <regex>
#include <stdexcept>
#include <sys/resource.h>
#include <sys/stat.h>
#include <unistd.h>
extern "C" {
#include <lua.h>
#include <lauxlib.h>
}

static constexpr std::string_view POLICY   = "59a1485d5f900db177414814bae9577898d687d17f2dc6a533ecec40a21590d3";
static HANDLE                     handle   = nullptr;
static uint64_t                   sequence = 0;
using Json                                 = std::unique_ptr<json_object, decltype(&json_object_put)>;

static Json object() {
    return Json(json_object_new_object(), json_object_put);
}
static Json array() {
    return Json(json_object_new_array(), json_object_put);
}
static void put(json_object* parent, const char* key, Json value) {
    json_object_object_add(parent, key, value.release());
}
static Json text(const std::string& value) {
    return Json(json_object_new_string_len(value.data(), value.size()), json_object_put);
}
static Json boolean(bool value) {
    return Json(json_object_new_boolean(value), json_object_put);
}
static Json integer(int64_t value) {
    return Json(json_object_new_int64(value), json_object_put);
}
static Json nullValue() {
    return Json(nullptr, json_object_put);
}
static Json decimal(double value) {
    if (!std::isfinite(value))
        throw std::runtime_error("Nonfinite native observation");
    return text(std::format("{:.17g}", value));
}
static Json pointer(uintptr_t value) {
    return text(std::format("0x{:x}", value));
}
static Json box(const CBox& value) {
    auto row = array();
    for (const auto component : {value.x, value.y, value.w, value.h})
        json_object_array_add(row.get(), decimal(component).release());
    return row;
}
static std::string startTime() {
    std::ifstream     file("/proc/self/stat");
    const std::string raw((std::istreambuf_iterator<char>(file)), {});
    const auto        end = raw.find_last_of(')');
    if (end == std::string::npos)
        throw std::runtime_error("Current compositor stat unavailable");
    std::istringstream tail(raw.substr(end + 1));
    std::string        field;
    for (size_t i = 0; i <= 19; ++i)
        if (!(tail >> field))
            throw std::runtime_error("Incomplete current compositor stat");
    if (!std::regex_match(field, std::regex("[1-9][0-9]*")))
        throw std::runtime_error("Invalid compositor lifetime");
    return field;
}
static void authorize() {
    const char* value = getenv("XDG_RUNTIME_DIR");
    if (!value || !std::regex_match(value, std::regex("/run/user/" + std::to_string(getuid()) + "/wqa/[0-9a-f]{4}")))
        throw std::runtime_error("Private QA runtime required");
    struct stat info{};
    if (lstat(value, &info) || !S_ISDIR(info.st_mode) || info.st_uid != getuid() || (info.st_mode & 0777) != 0700)
        throw std::runtime_error("Owned QA runtime required");
    std::ifstream     file("/proc/self/cgroup");
    const std::string group((std::istreambuf_iterator<char>(file)), {});
    if (group.find("/qa-harness.slice/qa-harness-") == std::string::npos)
        throw std::runtime_error("QA scope required");
    struct rlimit limit{};
    if (getrlimit(RLIMIT_CORE, &limit) || limit.rlim_cur != 1 || limit.rlim_max != 1)
        throw std::runtime_error("QA core limit required");
    if (std::string(__hyprland_api_get_hash()) != __hyprland_api_get_client_hash() || Desktop::Pin::policyBuildIdentity() != POLICY)
        throw std::runtime_error("Exact owning ABI/policy required");
}
static Json identity(const PHLWINDOW& window) {
    if (!window)
        return nullValue();
    auto row = object();
    put(row.get(), "address", pointer(rc<uintptr_t>(window.get())));
    put(row.get(), "stableId", text(std::format("{:x}", window->m_stableID)));
    put(row.get(), "pid", integer(window->getPID()));
    return row;
}
static PHLWINDOW select(uintptr_t address, uint64_t stableId, int pid) {
    PHLWINDOW result;
    for (const auto& window : Desktop::windowState()->windows()) {
        if (rc<uintptr_t>(window.get()) != address || window->m_stableID != stableId || window->getPID() != pid)
            continue;
        if (result || !Desktop::View::validMapped(window))
            throw std::runtime_error("Current unique mapped lifetime required");
        result = window;
    }
    if (!result)
        throw std::runtime_error("Selected public lifetime absent or replaced");
    return result;
}
static Json scroll(const SP<Layout::ITarget>& target, const SP<Layout::ITarget>& nativeTarget, const SP<Layout::CAlgorithm>& algorithm) {
    if (!target || target->floating() || !algorithm || !algorithm->tiledAlgo())
        return nullValue();
    // Algorithm owns its unique tiled instance throughout this synchronous read.
    // No WeakPtr::lock on a uniquely owned handler/algorithm.
    const auto* native = dynamic_cast<const Layout::Tiled::CScrollingAlgorithm*>(algorithm->tiledAlgo().get());
    if (!native)
        return nullValue();
    const auto selected = native->dataFor(nativeTarget, true);
    const auto column   = selected ? selected->column.lock() : nullptr;
    const auto owner    = column ? column->scrollingData.lock() : nullptr;
    if (!selected || !column || !owner || !owner->controller || owner->columns.size() > 64)
        throw std::runtime_error("Complete bounded actual scrolling owner required");
    const auto& controller = *owner->controller;
    if (controller.stripCount() != owner->columns.size())
        throw std::runtime_error("Actual scrolling column/controller count differs");
    auto   columns = array();
    size_t total   = 0;
    for (size_t columnIndex = 0; columnIndex < owner->columns.size(); ++columnIndex) {
        const auto col = owner->columns[columnIndex];
        if (!col || col->scrollingData != owner || (total += col->targetDatas.size()) > 256)
            throw std::runtime_error("Current bounded scrolling rows required");
        const auto& strip = controller.getStrip(columnIndex);
        if (col->self != col || strip.userData != col || strip.targetSizes.size() != col->targetDatas.size())
            throw std::runtime_error("Exact actual scrolling controller row mapping required");
        auto entry = object();
        put(entry.get(), "column", pointer(rc<uintptr_t>(col.get())));
        put(entry.get(), "width", decimal(col->getColumnWidth()));
        auto rows = array();
        for (size_t i = 0; i < col->targetDatas.size(); ++i) {
            const auto data   = col->targetDatas[i];
            const auto member = data ? data->target.lock() : nullptr;
            if (!data || !member || data->column != col || member->space() != target->space())
                throw std::runtime_error("Actual scrolling member scope changed");
            auto row = object();
            put(row.get(), "data", pointer(rc<uintptr_t>(data.get())));
            put(row.get(), "target", pointer(rc<uintptr_t>(member.get())));
            put(row.get(), "owner", identity(member->window()));
            put(row.get(), "size", decimal(col->getTargetSize(i)));
            put(row.get(), "layoutBox", box(data->layoutBox));
            json_object_array_add(rows.get(), row.release());
        }
        put(entry.get(), "rows", std::move(rows));
        json_object_array_add(columns.get(), entry.release());
    }
    auto result = object();
    put(result.get(), "owner", pointer(rc<uintptr_t>(owner.get())));
    put(result.get(), "controller", pointer(rc<uintptr_t>(owner->controller.get())));
    put(result.get(), "selectedData", pointer(rc<uintptr_t>(selected.get())));
    put(result.get(), "selectedColumn", pointer(rc<uintptr_t>(column.get())));
    put(result.get(), "offset", decimal(controller.getOffset()));
    put(result.get(), "direction", integer(controller.getDirection()));
    put(result.get(), "columns", std::move(columns));
    return result;
}
static Json transfer(const PHLWINDOW& window) {
    const auto outcome = Desktop::Pin::state()->transferOutcome(window);
    if (!outcome)
        return nullValue();
    auto row = object();
    put(row.get(), "operation", text(std::to_string(outcome->operation)));
    put(row.get(), "generation", text(std::to_string(outcome->generation)));
    put(row.get(), "accepted", boolean(outcome->accepted));
    put(row.get(), "actualModesKnown", boolean(outcome->actualModesKnown));
    put(row.get(), "beforeInternal", integer(outcome->before.internal));
    put(row.get(), "beforeClient", integer(outcome->before.client));
    put(row.get(), "actualInternal", integer(outcome->actual.internal));
    put(row.get(), "actualClient", integer(outcome->actual.client));
    put(row.get(), "target", pointer(outcome->target));
    put(row.get(), "space", pointer(outcome->space));
    put(row.get(), "workspace", pointer(outcome->workspace));
    put(row.get(), "output", pointer(outcome->output));
    put(row.get(), "reason", text(outcome->reason));
    return row;
}
static WP<Fullscreen::IFullscreenHandler> rawHandler(const PHLWINDOW& window, const SP<Layout::CAlgorithm>& algorithm) {
    if (!window || !algorithm || !algorithm->tiledAlgo() || !algorithm->floatingAlgo())
        throw std::runtime_error("Complete strong owning fullscreen algorithms required");
    // Same selection as getFsHandler(window), via getFullscreenHandlerName and
    // layoutManagedFS: floating always owns its raw handler; otherwise choose the
    // default when it reports covering fullscreen or any client mode, else layout.
    const auto layout   = algorithm->tiledAlgo()->getFSHandler();
    const auto fallback = algorithm->tiledAlgo()->IModeAlgorithm::getFSHandler();
    const auto floating = algorithm->floatingAlgo()->getFSHandler();
    if (!layout || !fallback || !floating)
        throw std::runtime_error("Current raw owning fullscreen handlers required");
    if (window->m_isFloating)
        return floating;
    const auto name = fallback->isFullscreen(window->m_target) || fallback->getFullscreenModes(window->m_target).client != Fullscreen::FSMODE_NONE ?
        fallback->getFullscreenHandlerName() :
        layout->getFullscreenHandlerName();
    if (name == Fullscreen::FULLSCREEN_HANDLER_NONE)
        throw std::runtime_error("Unknown owning fullscreen handler classification");
    return (name & Fullscreen::FULLSCREEN_HANDLER_LAYOUT) ? layout : fallback;
}
static Json snapshot(const PHLWINDOW& window) {
    const auto target    = window->layoutTarget();
    const auto space     = target ? target->space() : nullptr;
    const auto algorithm = space ? space->algorithm() : nullptr;
    if (!target || !space || !algorithm || space->workspace() != window->m_workspace)
        throw std::runtime_error("Current owning layout scope unavailable");
    const auto workspace    = window->m_workspace;
    const auto output       = window->m_monitor.lock();
    const auto groupOwner   = window->m_group;
    const auto nativeTarget = window->m_target;
    if (!output || workspace->m_monitor != output || !nativeTarget)
        throw std::runtime_error("Exact current output/native target required");
    const auto current = Desktop::Pin::state()->snapshot(window);
    const auto handler = rawHandler(window, algorithm);
    if (!handler)
        throw std::runtime_error("Current owning fullscreen handler required");
    // Borrow the unique handler beneath the strongly retained owning algorithm. Never lock it.
    const auto modes  = handler->getFullscreenModes(nativeTarget);
    const auto cursor = g_pInputManager->getMouseCoordsInternal();
    auto       row    = object();
    put(row.get(), "owner", identity(window));
    put(row.get(), "mapped", boolean(window->m_isMapped));
    put(row.get(), "hidden", boolean(window->isHidden()));
    put(row.get(), "acceptsInput", boolean(window->acceptsInput()));
    put(row.get(), "noFocus", boolean(window->m_ruleApplicator->noFocus().valueOrDefault()));
    put(row.get(), "priorityFocus", boolean(window->priorityFocus()));
    put(row.get(), "pinned", boolean(window->m_pinned));
    put(row.get(), "floating", boolean(target->floating()));
    put(row.get(), "internalMode", integer(modes.internal));
    put(row.get(), "clientMode", integer(modes.client));
    put(row.get(), "fullscreenHandler", pointer(rc<uintptr_t>(handler.get())));
    put(row.get(), "target", pointer(rc<uintptr_t>(target.get())));
    put(row.get(), "space", pointer(rc<uintptr_t>(space.get())));
    put(row.get(), "workspace", pointer(rc<uintptr_t>(workspace.get())));
    put(row.get(), "output", pointer(rc<uintptr_t>(output.get())));
    put(row.get(), "logicalBox", box(target->geometrySnapshot().logicalBox));
    put(row.get(), "visualBox", box(target->geometrySnapshot().visualBox));
    put(row.get(), "restoreValid", boolean(current.valid));
    put(row.get(), "restoreGeneration", text(std::to_string(current.generation)));
    put(row.get(), "restoreLogicalBox", box(current.box.logicalBox));
    put(row.get(), "restoreVisualBox", box(current.box.visualBox));
    put(row.get(), "restoreFloating", boolean(current.floating));
    put(row.get(), "restoreLayoutHandled", boolean(current.layoutHandled));
    put(row.get(), "restoreTarget", pointer(current.target));
    put(row.get(), "restoreLayoutTarget", pointer(current.layoutTarget));
    put(row.get(), "restoreSpace", pointer(current.space));
    put(row.get(), "restoreOrigin", boolean(current.pinOrigin));
    put(row.get(), "restoreManaged", boolean(current.pinManaged));
    put(row.get(), "ownedUnpinReady", boolean(Desktop::Pin::state()->ownedUnpinReady(window)));
    auto group = array();
    if (groupOwner) {
        const auto members = groupOwner->windows();
        if (members.size() > 64)
            throw std::runtime_error("Bounded current group required");
        for (const auto& member : members) {
            const auto live = member.lock();
            if (!live || !Desktop::View::validMapped(live))
                throw std::runtime_error("Current group member absent");
            json_object_array_add(group.get(), identity(live).release());
        }
    }
    put(row.get(), "group", pointer(rc<uintptr_t>(groupOwner.get())));
    put(row.get(), "groupMembers", std::move(group));
    auto point = array();
    json_object_array_add(point.get(), decimal(cursor.x).release());
    json_object_array_add(point.get(), decimal(cursor.y).release());
    put(row.get(), "cursor", std::move(point));
    put(row.get(), "coreFocus", identity(Desktop::focusState()->window()));
    put(row.get(), "scroll", scroll(target, nativeTarget, algorithm));
    put(row.get(), "transfer", transfer(window));
    if (window->layoutTarget() != target || target->space() != space || space->algorithm() != algorithm || space->workspace() != workspace || window->m_workspace != workspace ||
        window->m_monitor != output || workspace->m_monitor != output || window->m_group != groupOwner || window->m_target != nativeTarget)
        throw std::runtime_error("Owning scope changed during read");
    const auto postHandler = rawHandler(window, algorithm);
    if (!postHandler || postHandler != handler)
        throw std::runtime_error("Owning fullscreen handler changed during read");
    const auto postModes   = postHandler->getFullscreenModes(nativeTarget);
    const auto postRestore = Desktop::Pin::state()->snapshot(window);
    if (postModes.internal != modes.internal || postModes.client != modes.client || postRestore.valid != current.valid || postRestore.generation != current.generation ||
        postRestore.pinOrigin != current.pinOrigin || postRestore.pinManaged != current.pinManaged || postRestore.floating != current.floating ||
        postRestore.layoutHandled != current.layoutHandled || postRestore.target != current.target || postRestore.layoutTarget != current.layoutTarget ||
        postRestore.space != current.space || postRestore.box.logicalBox != current.box.logicalBox || postRestore.box.visualBox != current.box.visualBox)
        throw std::runtime_error("Native modes/restore projection changed during read");
    return row;
}
static uint64_t hex(lua_State* L, int index, bool pointerValue) {
    if (lua_type(L, index) != LUA_TSTRING)
        throw std::runtime_error("Exact hexadecimal identity string required");
    size_t      length = 0;
    const char* raw    = lua_tolstring(L, index, &length);
    if (!raw || length > 18)
        throw std::runtime_error("Bounded exact public identity string required");
    const std::string value(raw, length);
    if (!std::regex_match(value, std::regex(pointerValue ? "0x[1-9a-f][0-9a-f]{0,15}" : "0|[1-9a-f][0-9a-f]{0,15}")))
        throw std::runtime_error("Canonical public identity required");
    uint64_t   result = 0;
    const auto begin  = value.data() + (pointerValue ? 2 : 0);
    const auto parsed = std::from_chars(begin, value.data() + value.size(), result, 16);
    if (parsed.ec != std::errc{} || parsed.ptr != value.data() + value.size())
        throw std::runtime_error("Public identity overflow");
    return result;
}
static int observe(lua_State* L, bool hitQuery) {
    auto envelope = object();
    put(envelope.get(), "schema", integer(1));
    put(envelope.get(), "queryKind", text(hitQuery ? "windowAtStimulus" : "metadata"));
    put(envelope.get(), "queryProperties", nullValue());
    put(envelope.get(), "ignoreOwner", nullValue());
    put(envelope.get(), "hitOwner", nullValue());
    put(envelope.get(), "body", nullValue());
    put(envelope.get(), "postBody", nullValue());
    put(envelope.get(), "corePolicyBuild", text(std::string(POLICY)));
    put(envelope.get(), "compositorPid", integer(getpid()));
    put(envelope.get(), "compositorPgid", integer(getpgrp()));
    put(envelope.get(), "compositorStart", nullValue());
    put(envelope.get(), "session", nullValue());
    put(envelope.get(), "sequence", nullValue());
    put(envelope.get(), "observedNs", text(std::to_string(std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now().time_since_epoch()).count())));
    try {
        authorize();
        put(envelope.get(), "compositorStart", text(startTime()));
        const char* session = getenv("HYPRLAND_INSTANCE_SIGNATURE");
        if (!session || !std::regex_match(session, std::regex("[A-Za-z0-9_]+")))
            throw std::runtime_error("Actual native instance required");
        put(envelope.get(), "session", text(session));
        if (lua_gettop(L) != (hitQuery ? 5 : 3) || !lua_isinteger(L, 3) || lua_tointeger(L, 3) <= 0 || lua_tointeger(L, 3) > INT32_MAX ||
            (hitQuery && (!lua_isinteger(L, 4) || lua_tointeger(L, 4) < 0 || lua_tointeger(L, 4) > 4 || lua_type(L, 5) != LUA_TBOOLEAN)))
            throw std::runtime_error("Fixed exact typed query arguments required");
        if (sequence == std::numeric_limits<uint64_t>::max())
            throw std::runtime_error("Observation sequence exhausted");
        const auto         address   = hex(L, 1, true);
        const auto         stable    = hex(L, 2, false);
        const auto         window    = select(address, stable, lua_tointeger(L, 3));
        constexpr uint16_t EXTENTS   = Desktop::View::RESERVED_EXTENTS | Desktop::View::INPUT_EXTENTS;
        constexpr uint16_t MASKS[]   = {EXTENTS | Desktop::View::ALLOW_FLOATING, EXTENTS | Desktop::View::ALLOW_FLOATING | Desktop::View::FLOATING_ONLY,
                                        EXTENTS | Desktop::View::ALLOW_FLOATING | Desktop::View::FOCUS_PRIORITY,
                                        EXTENTS | Desktop::View::ALLOW_FLOATING | Desktop::View::SKIP_FULLSCREEN_PRIORITY, EXTENTS};
        auto               before    = snapshot(window);
        const auto         beforeRaw = std::string(json_object_to_json_string_ext(before.get(), JSON_C_TO_STRING_PLAIN));
        put(envelope.get(), "body", std::move(before));
        if (hitQuery) {
            const auto properties = MASKS[lua_tointeger(L, 4)];
            const auto ignore     = lua_toboolean(L, 5) ? window : nullptr;
            put(envelope.get(), "queryProperties", integer(properties));
            put(envelope.get(), "ignoreOwner", identity(ignore));
            // Labelled native query stimulus. Its inherited controller helpers may
            // correct stale fullscreen state; this is not a pure metadata read.
            const auto hit = Desktop::viewState()->hitTest().windowAt(g_pInputManager->getMouseCoordsInternal(), properties, ignore);
            put(envelope.get(), "hitOwner", identity(hit));
        }
        auto       after    = snapshot(window);
        const auto afterRaw = std::string(json_object_to_json_string_ext(after.get(), JSON_C_TO_STRING_PLAIN));
        put(envelope.get(), "postBody", std::move(after));
        if (select(address, stable, lua_tointeger(L, 3)) != window || beforeRaw != afterRaw)
            throw std::runtime_error("Selected owning observation changed across query");
        put(envelope.get(), "sequence", text(std::to_string(++sequence)));
        put(envelope.get(), "ok", boolean(true));
        put(envelope.get(), "error", nullValue());
    } catch (const std::exception& error) {
        put(envelope.get(), "ok", boolean(false));
        put(envelope.get(), "error", text(error.what()));
    }
    const auto raw = json_object_to_json_string_ext(envelope.get(), JSON_C_TO_STRING_PLAIN);
    if (!raw || std::strlen(raw) > 131072)
        return luaL_error(L, "Bounded complete observation required");
    lua_pushlstring(L, raw, std::strlen(raw));
    return 1;
}
static int observeMetadata(lua_State* L) {
    return observe(L, false);
}
static int queryHit(lua_State* L) {
    return observe(L, true);
}

APICALL EXPORT std::string PLUGIN_API_VERSION() {
    return HYPRLAND_API_VERSION;
}
APICALL EXPORT PLUGIN_DESCRIPTION_INFO PLUGIN_INIT(HANDLE h) {
    authorize();
    handle = h;
    HyprlandAPI::addLuaFunction(handle, "pin_campaign_b", "observe", observeMetadata);
    HyprlandAPI::addLuaFunction(handle, "pin_campaign_b", "query_hit", queryHit);
    return {"pin_campaign_b", "Draft private owning metadata and labelled native hit-query stimulus", "QA", "1"};
}
APICALL EXPORT void PLUGIN_EXIT() {
    sequence = 0;
}
