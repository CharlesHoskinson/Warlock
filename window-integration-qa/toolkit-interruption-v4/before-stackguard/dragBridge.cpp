#include "dragBridge.hpp"
#include "globals.hpp"
#include "barDeco.hpp"

#include <hyprland/src/event/EventBus.hpp>
#include <hyprland/src/desktop/view/Window.hpp>
#include <hyprland/src/desktop/state/WindowState.hpp>
#include <hyprland/src/desktop/state/FocusState.hpp>
#include <hyprland/src/desktop/view/Group.hpp>
#include <hyprland/src/helpers/MiscFunctions.hpp>
#include <hyprland/src/config/lua/ConfigManager.hpp>
#include <hyprland/src/config/lua/objects/LuaWindow.hpp>
#include <hyprland/src/layout/supplementary/DragController.hpp>
#include <hyprland/src/layout/LayoutManager.hpp>
#include <hyprland/src/managers/eventLoop/EventLoopManager.hpp>
#include <hyprland/src/plugins/HookSystem.hpp>
#include <hyprland/src/protocols/core/DataDevice.hpp>
#include <hyprland/src/helpers/time/Time.hpp>
#include <linux/input-event-codes.h>
extern "C" {
#include <lua.h>
}

namespace {
using Controller = Layout::Supplementary::CDragStateController;
using CustomEvent = Event::CEventBus::CCustomEvent;
using BeginFn = void (*)(Controller*, SP<Layout::ITarget>, eMouseBindMode, std::optional<Layout::eRectCorner>, bool);
using EndFn = void (*)(Controller*);
using DecoInputFn = bool (*)(Desktop::View::CWindow*, eInputType, const Vector2D&, std::any);
using GroupAddFn = void (*)(Desktop::View::CGroup*, PHLWINDOW, std::optional<size_t>);
using FullFocusFn = void (*)(Desktop::CFocusState*, PHLWINDOW, Desktop::eFocusReason, SP<CWLSurfaceResource>, bool);

CFunctionHook* beginHook = nullptr;
CFunctionHook* endHook = nullptr;
CFunctionHook* decoInputHook = nullptr;
CFunctionHook* groupAddHook = nullptr;
CFunctionHook* fullFocusHook = nullptr;
SP<CustomEvent> beginEvent, finishEvent, retireEvent;
bool keepCurrentGeometry = false;
SP<Config::Values::CBoolValue> enabled;
CHyprSignalListener buttonListener;
CHyprSignalListener reloadListener;
UP<SEventLoopDoLaterLock> clearInputContext;
uint32_t releasedButton = 0;
PHLWINDOWREF draggedOwner;
// Exact native lifetime and target, independent of current keyboard focus.
struct GestureCapture {
    PHLWINDOWREF owner;
    WP<Layout::ITarget> target;
    uint64_t stableID = 0;
    CBox origin;
    eMouseBindMode mode = MBIND_INVALID;
    uint32_t button = BTN_LEFT;
};
std::optional<GestureCapture> gesture;
bool isResize(eMouseBindMode mode) {
    return mode == MBIND_RESIZE || mode == MBIND_RESIZE_FORCE_RATIO || mode == MBIND_RESIZE_BLOCK_RATIO;
}
bool sameGesture(const SP<Layout::ITarget>& target) {
    if (!gesture || !target || gesture->target.lock() != target)
        return false;
    const auto owner = gesture->owner.lock();
    return owner && target->window() == owner && owner->m_stableID == gesture->stableID;
}
std::optional<GestureCapture> cancellation;
struct CancellationScope {
    std::optional<GestureCapture> previous;
    explicit CancellationScope(std::optional<GestureCapture> current) : previous(cancellation) {
        cancellation = std::move(current);
    }
    ~CancellationScope() { cancellation = std::move(previous); }
};
bool cancelledOwner(const PHLWINDOW& owner) {
    if (!cancellation || !validMapped(owner))
        return false;
    const auto target = cancellation->target.lock();
    return cancellation->owner.lock() == owner && owner->m_stableID == cancellation->stableID &&
        target && target->window() == owner;
}
bool hookedDecoInput(Desktop::View::CWindow* receiver, eInputType type, const Vector2D& coords, std::any payload) {
    const auto dragged = std::any_cast<PHLWINDOW>(&payload);
    if (type == INPUT_TYPE_DRAG_END && dragged && cancelledOwner(*dragged))
        return false; // No drop callback; core cleanup still proceeds.
    return reinterpret_cast<DecoInputFn>(decoInputHook->m_original)(receiver, type, coords, std::move(payload));
}
void hookedGroupAdd(Desktop::View::CGroup* group, PHLWINDOW owner, std::optional<size_t> index) {
    if (cancelledOwner(owner))
        return;
    reinterpret_cast<GroupAddFn>(groupAddHook->m_original)(group, owner, index);
}
void hookedFullFocus(Desktop::CFocusState* state, PHLWINDOW owner, Desktop::eFocusReason reason,
                     SP<CWLSurfaceResource> surface, bool forceFSCycle) {
    if (reason == Desktop::FOCUS_REASON_DESKTOP_STATE_CHANGE && cancelledOwner(owner) && state->window() != owner)
        return; // Respect the newer actual focus; do not send corrective focus.
    reinterpret_cast<FullFocusFn>(fullFocusHook->m_original)(state, owner, reason, surface, forceFSCycle);
}
// Call while the end hook and Lua lifecycle event remain installed.
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
uint32_t lastPressedButton = BTN_LEFT;
uint32_t dragButton = BTN_LEFT;

PHLWINDOWREF captionOwner;
std::optional<Vector2D> captionPress;

void emit(const SP<CustomEvent>& event, const PHLWINDOW& owner, bool released = false) {
    if (!event || !owner)
        return;
    std::vector<CustomEvent::ValidVariant> args = {PHLWINDOWREF{owner}};
    if (event == finishEvent)
        args.emplace_back(released);
    else if (event == beginEvent) {
        const auto press = captionOwner.lock() == owner && captionPress ? *captionPress : g_pInputManager->getMouseCoordsInternal();
        args.emplace_back(press.x);
        args.emplace_back(press.y);
    }
    (void)event->emit(args);
}

void hookedBegin(Controller* controller, SP<Layout::ITarget> target, eMouseBindMode mode,
                 std::optional<Layout::eRectCorner> edge, bool exclusive) {
    const auto owner = target ? target->window() : nullptr;
    if (enabled && enabled->value() && !controller->target() && validMapped(owner) && owner->m_isFloating &&
        (mode == MBIND_MOVE || isResize(mode)))
        gesture = GestureCapture{owner, target, owner->m_stableID, target->position(), mode, lastPressedButton};
    const auto initialDelta = captionOwner.lock() == owner && captionPress ?
        std::optional<Vector2D>{g_pInputManager->getMouseCoordsInternal() - *captionPress} : std::nullopt;
    const bool track = enabled && enabled->value() && !controller->target() && mode == MBIND_MOVE && validMapped(owner) && owner->m_isFloating;
    if (track) {
        draggedOwner = owner;
        dragButton = lastPressedButton;
        // Lua unsnaps and captures normal geometry before the controller records
        // its starting box. No subprocess or mouse-move timing is involved.
        emit(beginEvent, owner);
    }
    // The caption starts native dragging on its first motion. Lua has captured
    // the original rectangle and restored normal size about the press point.
    // Apply the first displacement before core records its new drag geometry.
    // Subsequent native deltas then retain the original pressed offset.
    if (track && initialDelta && validMapped(owner)) {
        auto box = target->position();
        box.translate(*initialDelta);
        target->setPositionGlobal(box);
    }
    reinterpret_cast<BeginFn>(beginHook->m_original)(controller, target, mode, edge, exclusive);
    if (track && (!controller->target() || controller->mode() != MBIND_MOVE)) {
        draggedOwner.reset();
        emit(finishEvent, owner, false);
    }
}

void hookedEnd(Controller* controller) {
    const auto target = controller->target();
    const auto owner = target ? target->window() : nullptr;
    const auto retiring = sameGesture(target) ? gesture : std::nullopt;
    const bool keepGeometry = retiring && keepCurrentGeometry;
    if (retiring)
        gesture.reset(); // Retire before core callbacks can reenter.
    const bool track = owner && draggedOwner.lock() == owner && controller->mode() == MBIND_MOVE;
    const bool released = releasedButton == (retiring ? retiring->button : dragButton);
    if (track)
        draggedOwner.reset();
    {
        // Scope exactly the delegated core end. Lua callbacks after it regain
        // ordinary authority. Nested/reentrant ends restore the previous scope.
        CancellationScope cancel(retiring && !released ? retiring : std::nullopt);
        reinterpret_cast<EndFn>(endHook->m_original)(controller);
    }
    // Core dragEnd commits resized geometry. An interruption must restore the
    // press rectangle, only for the captured still-live visible exact target.
    // Move restoration continues through its existing synchronous Lua event.
    if (retiring && !released && !keepGeometry && isResize(retiring->mode) && validMapped(owner) &&
        !owner->isHidden() && owner->m_stableID == retiring->stableID &&
        retiring->owner.lock() == owner && retiring->target.lock() == target)
        g_layoutManager->setTargetGeom(retiring->origin, target);
    // Snapping must happen after native drag cleanup, otherwise it is overwritten
    // by the controller's final geometry update.
    if (track && validMapped(owner))
        emit(keepGeometry ? retireEvent : finishEvent, owner, released);
}

CFunctionHook* install(const std::string& name, const void* replacement) {
    auto matches = HyprlandAPI::findFunctionsByName(PHANDLE, name.substr(name.rfind("::") + 2));
    std::erase_if(matches, [&](const auto& match) { return match.demangled.find(name + "(") == std::string::npos; });
    if (matches.size() != 1)
        throw std::runtime_error("hyprbars drag bridge: expected one " + name);
    auto hook = HyprlandAPI::createFunctionHook(PHANDLE, matches.front().address, replacement);
    if (!hook || !hook->hook())
        throw std::runtime_error("hyprbars drag bridge: hook failed for " + name);
    return hook;
}
}

void initDragBridge() {
  try {
    enabled = makeShared<Config::Values::CBoolValue>("plugin:hyprbars:drag_bridge", "Synchronous compositor drag lifecycle bridge", true);
    HyprlandAPI::addConfigValueV2(PHANDLE, enabled);
    beginEvent = makeShared<CustomEvent>("hyprbars.drag_start", std::vector<CustomEvent::eType>{CustomEvent::TYPE_WINDOW, CustomEvent::TYPE_DOUBLE, CustomEvent::TYPE_DOUBLE});
    finishEvent = makeShared<CustomEvent>("hyprbars.drag_finish", std::vector<CustomEvent::eType>{CustomEvent::TYPE_WINDOW, CustomEvent::TYPE_BOOL});
    retireEvent = makeShared<CustomEvent>("hyprbars.drag_retire_current", std::vector<CustomEvent::eType>{CustomEvent::TYPE_WINDOW});
    if (!Event::bus()->addPluginEvent(beginEvent) || !Event::bus()->addPluginEvent(finishEvent) || !Event::bus()->addPluginEvent(retireEvent))
        throw std::runtime_error("hyprbars drag bridge: custom event registration failed");
    // Register before titlebar listeners so their release-triggered native drag
    // cleanup sees this frame's physical release reason.
    buttonListener = Event::bus()->m_events.input.mouse.button.listen([](IPointer::SButtonEvent e, Event::SCallbackInfo&) {
        releasedButton = e.state == WL_POINTER_BUTTON_STATE_RELEASED ? e.button : 0;
        if (e.state == WL_POINTER_BUTTON_STATE_PRESSED)
            lastPressedButton = e.button;
        clearInputContext = g_pEventLoopManager->doLaterLock([] { releasedButton = 0; });
    });
    beginHook = install("CDragStateController::dragBegin", reinterpret_cast<void*>(hookedBegin));
    endHook = install("CDragStateController::dragEnd", reinterpret_cast<void*>(hookedEnd));
    decoInputHook = install("CWindow::checkInputOnDecos", reinterpret_cast<void*>(hookedDecoInput));
    groupAddHook = install("CGroup::add", reinterpret_cast<void*>(hookedGroupAdd));
    fullFocusHook = install("CFocusState::fullWindowFocus", reinterpret_cast<void*>(hookedFullFocus));
    reloadListener = Event::bus()->m_events.config.preReload.listen([] {
        retireCapturedGesture();
        captionOwner.reset();
        captionPress.reset();
    });
  } catch (...) {
    exitDragBridge();
    throw;
  }
}

void exitDragBridge() {
    // Normal unload ends the exact owned move/resize before removing hooks and
    // custom lifecycle events. Unrelated/tiled/current replacement targets stay
    // under core authority.
    if (endHook)
        retireCapturedGesture();
    clearInputContext.reset();
    buttonListener.reset();
    reloadListener.reset();
    draggedOwner.reset();
    captionOwner.reset();
    captionPress.reset();
    if (beginHook)
        HyprlandAPI::removeFunctionHook(PHANDLE, beginHook);
    if (endHook)
        HyprlandAPI::removeFunctionHook(PHANDLE, endHook);
    if (decoInputHook)
        HyprlandAPI::removeFunctionHook(PHANDLE, decoInputHook);
    if (groupAddHook)
        HyprlandAPI::removeFunctionHook(PHANDLE, groupAddHook);
    if (fullFocusHook)
        HyprlandAPI::removeFunctionHook(PHANDLE, fullFocusHook);
    beginHook = endHook = decoInputHook = groupAddHook = fullFocusHook = nullptr;
    (void)Event::bus()->removePluginEvent("hyprbars.drag_start");
    (void)Event::bus()->removePluginEvent("hyprbars.drag_finish");
    (void)Event::bus()->removePluginEvent("hyprbars.drag_retire_current");
    beginEvent.reset();
    finishEvent.reset();
    retireEvent.reset();
}

int luaDragBridgeAvailable(lua_State* state) {
    // Hyprland 0.56 recreates its Lua event handler on reload without reconnecting
    // existing custom events. Rebind this manager before the config subscribes.
    if (auto* manager = Config::Lua::CConfigManager::fromLuaState(state); manager && manager->m_eventHandler) {
        for (const auto& event : {beginEvent, finishEvent, retireEvent}) {
            if (!event)
                continue;
            (void)manager->m_eventHandler->removeCustomEvent(event->m_name);
            (void)manager->m_eventHandler->addCustomEvent(event);
        }
    }
    lua_pushboolean(state, beginHook && endHook && enabled && enabled->value());
    return 1;
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
        const auto bar = barRef.lock();
        if (bar && bar->getOwner() == owner)
            cancelledIntent = bar->retireCaptionIntent() || cancelledIntent;
    }
    lua_pushboolean(state, !matched || !g_layoutManager->dragController()->target());
    lua_pushboolean(state, matched || cancelledIntent);
    return 2;
}

int luaWindowLifetime(lua_State* state) {
    // Use the public native Lua wrapper/equality, never its userdata layout.
    // Close emits before mapped is cleared; do not recover by string address.
    if (lua_gettop(state) != 1 || lua_type(state, 1) != LUA_TUSERDATA || !lua_getmetatable(state, 1)) {
        lua_pushnil(state); return 1;
    }
    const int suppliedMetatable = lua_gettop(state);
    for (const auto& owner : Desktop::windowState()->windows()) {
        if (!owner)
            continue;
        Config::Lua::Objects::CLuaWindow::push(state, owner);
        const int candidate = lua_gettop(state);
        lua_getmetatable(state, candidate);
        const bool nativeMetatable = lua_rawequal(state, suppliedMetatable, -1);
        lua_pop(state, 1);
        const bool exactNativeObject = nativeMetatable && lua_compare(state, 1, candidate, LUA_OPEQ);
        lua_pop(state, 1);
        if (!exactNativeObject)
            continue;
        const auto address = std::format("0x{:x}", reinterpret_cast<uintptr_t>(owner.get()));
        const auto stableID = std::format("{:x}", owner->m_stableID);
        lua_pushlstring(state, address.data(), address.size());
        lua_pushlstring(state, stableID.data(), stableID.size());
        lua_pushinteger(state, owner->getPID());
        return 3;
    }
    lua_pushnil(state);
    return 1;
}

int luaFileDragActive(lua_State* state) {
    // Public compositor state only; no payload or clipboard access.
    lua_pushboolean(state, PROTO::data && PROTO::data->dndActive());
    lua_pushinteger(state, Time::millis(Time::steadyNow()));
    return 2;
}

bool startCaptionDrag(const PHLWINDOW& owner, const Vector2D& press) {
    if (!beginHook || !endHook || !enabled || !enabled->value() || !validMapped(owner) || !owner->m_isFloating || g_layoutManager->dragController()->target())
        return false;
    captionOwner = owner;
    captionPress = press;
    // Resolve the target from the pressed caption, even if the first motion
    // crosses another window or leaves all window hit regions.
    try {
        g_layoutManager->beginDragTarget(owner->layoutTarget(), MBIND_MOVE);
    } catch (...) {
        captionOwner.reset();
        captionPress.reset();
        throw;
    }
    captionOwner.reset();
    captionPress.reset();
    return g_layoutManager->dragController()->target() && g_layoutManager->dragController()->target()->window() == owner;
}
