#include "pinBridge.hpp"
#include <hyprland/src/config/shared/actions/ConfigActions.hpp>
#include <hyprland/src/config/lua/objects/LuaWindow.hpp>
#include <hyprland/src/desktop/state/WindowState.hpp>
#include <hyprland/src/managers/fullscreen/FullscreenController.hpp>
extern "C" {
#include <lua.h>
}

using namespace Desktop::View;

static bool eligible(const PHLWINDOW& owner) {
    return validMapped(owner) && !owner->isHidden() && owner->m_workspace &&
        !owner->m_workspace->m_isSpecialWorkspace;
}

bool toggleCapturedPin(const PHLWINDOW& owner, std::string& reason) {
    if (!eligible(owner)) {
        reason = "Captured window is unavailable or minimized";
        return false;
    }
    // Core currently rejects maximized/fullscreen pinning. Do not float or
    // destroy geometry before reporting this unsupported state.
    if (Fullscreen::controller()->isFullscreen(owner)) {
        reason = "Maximized/fullscreen pinning needs a supported native policy";
        return false;
    }
    const auto stable = owner->m_stableID;
    const bool desired = !owner->m_pinned;
    if (!owner->m_isFloating) {
        const auto result = Config::Actions::floatWindow(Config::Actions::TOGGLE_ACTION_ENABLE, owner);
        if (!result) {
            reason = "Native floating action refused";
            return false;
        }
    }
    // Native actions emit callbacks. Recheck the same owning object after an
    // action; a callback closing/minimizing it must not promote stale intent.
    if (!eligible(owner) || owner->m_stableID != stable || !owner->m_isFloating) {
        reason = "Captured window changed during native floating action";
        return false;
    }
    const auto result = Config::Actions::pinWindow(
        desired ? Config::Actions::TOGGLE_ACTION_ENABLE : Config::Actions::TOGGLE_ACTION_DISABLE, owner);
    if (!result || !eligible(owner) || owner->m_stableID != stable || owner->m_pinned != desired) {
        reason = "Native pin action refused or captured window changed";
        return false;
    }
    // V22's existing family/focus bridge owns modal-aware raising. Calling its
    // normal core raise route preserves the independently pinned peer policy.
    if (desired) {
        const auto raised = Config::Actions::alterZOrder("top", owner);
        if (!raised) {
            reason = "Pin changed; native raise refused";
            return false;
        }
    }
    reason.clear();
    return true;
}

int luaPinCapturedWindow(lua_State* state) {
    PHLWINDOW selected;
    if (lua_gettop(state) == 1 && lua_type(state, 1) == LUA_TUSERDATA && lua_getmetatable(state, 1)) {
        const int suppliedMetatable = lua_gettop(state);
        // Match the public native Lua wrapper/equality. Never inspect or cast
        // userdata storage, and never recover by an address string.
        for (const auto& owner : Desktop::windowState()->windows()) {
            if (!owner)
                continue;
            Config::Lua::Objects::CLuaWindow::push(state, owner);
            const int candidate = lua_gettop(state);
            if (!lua_getmetatable(state, candidate)) {
                lua_pop(state, 1);
                continue;
            }
            const bool nativeMetatable = lua_rawequal(state, suppliedMetatable, -1);
            lua_pop(state, 1);
            const bool exact = nativeMetatable && lua_compare(state, 1, candidate, LUA_OPEQ);
            lua_pop(state, 1);
            if (exact) {
                selected = owner;
                break;
            }
        }
    }
    std::string reason;
    const bool ok = toggleCapturedPin(selected, reason);
    lua_pushboolean(state, ok);
    lua_pushlstring(state, reason.data(), reason.size());
    return 2;
}
