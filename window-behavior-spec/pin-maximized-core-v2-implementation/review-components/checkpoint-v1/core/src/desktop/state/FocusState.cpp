#include "pin/NativePinState.hpp"
#include "FocusState.hpp"
#include "../view/Window.hpp"
#include "../../Compositor.hpp"
#include "../../protocols/XDGShell.hpp"
#include "../../render/Renderer.hpp"
#include "../../managers/EventManager.hpp"
#include "../../managers/input/InputManager.hpp"
#include "../../managers/SeatManager.hpp"
#include "../../xwayland/XSurface.hpp"
#include "../../protocols/PointerConstraints.hpp"
#include "animation/WorkspaceAnimationController.hpp"
#include "../../managers/fullscreen/FullscreenController.hpp"
#include "../../layout/LayoutManager.hpp"
#include "../../event/EventBus.hpp"

using namespace Desktop;

#define COMMA ,

SP<CFocusState> Desktop::focusState() {
    static SP<CFocusState> state = makeShared<CFocusState>();
    return state;
}

Desktop::CFocusState::CFocusState() = default;

struct SFullscreenWorkspaceFocusResult {
    PHLWINDOW overrideFocusWindow = nullptr;
};

static SFullscreenWorkspaceFocusResult onFullscreenWorkspaceFocusWindow(PHLWINDOW pWindow, bool forceFSCycle) {
    const auto FSWINDOW        = Fullscreen::controller()->getFullscreenWindow(pWindow->m_workspace);
    const auto FSMODE_INTERNAL = Fullscreen::controller()->getFullscreenModes(pWindow->m_workspace).internal;
    const auto LAYOUT_HANDLED  = Fullscreen::controller()->layoutManagedFS(FSWINDOW);

    if (pWindow == FSWINDOW)
        return {}; // no conflict

    if (pWindow->m_isFloating) {
        // if the window is floating, just bring it to the top
        pWindow->m_allowedOverFullscreen = true;
        pWindow->updateFullscreenInputState();
        Animation::Workspace::setFullscreenFloatingFade(pWindow, 1.F);
        g_pHyprRenderer->damageWindow(pWindow);
        return {};
    }

    static auto PONFOCUSUNDERFS = CConfigValue<Config::INTEGER>("misc:on_focus_under_fullscreen");

    switch (*PONFOCUSUNDERFS) {
        case 0:
            // focus the fullscreen window instead
            return {.overrideFocusWindow = FSWINDOW};
        case 2:
            // undo fs, unless we force a cycle
            if (!forceFSCycle) {
                Fullscreen::controller()->setFullscreenMode(FSWINDOW, Fullscreen::FSMODE_NONE);
                break;
            }
            [[fallthrough]];
        case 1:
            // replace fullscreen using the layoutHandled mode from prev FS window
            Fullscreen::controller()->setFullscreenMode(FSWINDOW, Fullscreen::FSMODE_NONE);
            Fullscreen::controller()->setFullscreenMode(pWindow, FSMODE_INTERNAL, std::nullopt, LAYOUT_HANDLED);
            break;

        default: Log::logger->log(Log::ERR, "Invalid misc:on_focus_under_fullscreen mode: {}", *PONFOCUSUNDERFS); break;
    }

    return {};
}

void CFocusState::fullWindowFocus(PHLWINDOW window, eFocusReason reason, SP<CWLSurfaceResource> surface, bool forceFSCycle) {
    fullWindowFocusResult(window, reason, surface, forceFSCycle);
}

static bool routesExplicitModal(eFocusReason reason) {
    return Desktop::isHardInputFocusReason(reason) || reason == FOCUS_REASON_DISPATCH_FOCUSWINDOW || reason == FOCUS_REASON_SWITCH_TO_WINDOW_SOFT;
}

SWindowFocusResult CFocusState::fullWindowFocusResult(PHLWINDOW pWindow, eFocusReason reason, SP<CWLSurfaceResource> surface, bool forceFSCycle) {
    SWindowFocusResult result;
    result.requested = pWindow;
    result.coreBefore = window();
    result.seatBefore = g_pSeatManager->m_state.keyboardFocus.lock();
    static auto PMODALPARENTBLOCKING = CConfigValue<Config::INTEGER>("general:modal_parent_blocking");
    PHLWINDOW routeRoot = pWindow;

    if (pWindow && !pWindow->m_workspace)
        return result;
    if (pWindow && *PMODALPARENTBLOCKING && routesExplicitModal(reason)) {
        // Preserve the requested owner's refusal policy before selecting a native descendant.
        if (pWindow->m_ruleApplicator->noFocus().valueOrDefault())
            return result;
        pWindow = Pin::deepestModal(pWindow);
        if (!pWindow)
            return result;
        if (pWindow != result.requested)
            surface.reset();
    }

    if (pWindow) {
        const auto FSWINDOW = Fullscreen::controller()->getFullscreenWindow(pWindow->m_workspace);
        const bool PROTECTED_MAX = FSWINDOW && FSWINDOW->m_pinned && Fullscreen::controller()->getFullscreenModes(FSWINDOW).internal == Fullscreen::FSMODE_MAXIMIZED;
        if (FSWINDOW && !Fullscreen::controller()->layoutManagedFS(FSWINDOW) && !PROTECTED_MAX) {
            const auto decision = onFullscreenWorkspaceFocusWindow(pWindow, forceFSCycle);
            if (decision.overrideFocusWindow) {
                routeRoot = decision.overrideFocusWindow;
                pWindow = routeRoot;
                surface.reset();
                if (*PMODALPARENTBLOCKING && routesExplicitModal(reason)) {
                    pWindow = Pin::deepestModal(routeRoot);
                    if (!pWindow)
                        return result;
                    if (pWindow != routeRoot) {
                        const auto finalDecision = onFullscreenWorkspaceFocusWindow(pWindow, forceFSCycle);
                        if (finalDecision.overrideFocusWindow)
                            return result;
                    }
                }
            }
        }
    }

    if (*PMODALPARENTBLOCKING && pWindow && pWindow->m_xdgSurface && pWindow->m_xdgSurface->m_toplevel && pWindow->m_xdgSurface->m_toplevel->anyChildModal())
        return result;

    result.target = pWindow;
    result.routeRoot = routeRoot;
    result.modalRoute = routeRoot && *PMODALPARENTBLOCKING && routesExplicitModal(reason);
    result.expectedSurface = pWindow ? (surface ? surface : pWindow->wlSurface()->resource()) : nullptr;
    rawWindowFocus(pWindow, reason, surface);
    // Raw focus can publish a core owner before rawSurfaceFocus refuses. Retain actual observations before acceptance.
    result.coreAfter = window();
    result.coreSurfaceAfter = this->surface();
    result.seatAfter = g_pSeatManager->m_state.keyboardFocus.lock();
    result.keyboardPresent = !!g_pSeatManager->m_keyboard;
    const bool ROUTE_CURRENT = !routeRoot || !*PMODALPARENTBLOCKING || !routesExplicitModal(reason) || Pin::deepestModal(routeRoot) == pWindow;
    result.accepted = ROUTE_CURRENT && acceptsResult(result);
    result.partial = !result.accepted && (result.coreBefore != result.coreAfter || result.seatBefore != result.seatAfter);
    return result;
}

bool CFocusState::acceptsResult(const SWindowFocusResult& result) const {
    const auto target = result.target;
    const auto expected = result.expectedSurface;
    if (!target || !expected || !expected->good() || !Pin::state()->live(target) || !validMapped(target) || target->isHidden() || target->m_ruleApplicator->noFocus().valueOrDefault())
        return false;
    if (result.requested && (!Pin::state()->live(result.requested) || !validMapped(result.requested) || result.requested->m_ruleApplicator->noFocus().valueOrDefault()))
        return false;
    if (result.modalRoute && (!Pin::state()->live(result.routeRoot) || !validMapped(result.routeRoot) || result.routeRoot->m_ruleApplicator->noFocus().valueOrDefault() || Pin::deepestModal(result.routeRoot) != target))
        return false;
    if (target->m_isX11 && target->isX11OverrideRedirect() && (!target->m_xwaylandSurface || !target->m_xwaylandSurface->wantsFocus()))
        return false;
    const bool unlocked = !g_pSessionLockManager->isSessionLocked() || g_pSessionLockManager->isSurfaceSessionLock(expected);
    const bool layerAllows = target->priorityFocus() || g_pInputManager->m_exclusiveLSes.empty();
    const bool seatAllows = !g_pSeatManager->m_seatGrab || g_pSeatManager->m_seatGrab->accepts(expected);
    const bool ownerCurrent = target->m_workspace && target->m_workspace->isVisible() && target->wlSurface()->resource() == expected;
    return Pin::acceptsFocus({.coreOwnerExact = m_focusWindow == target, .coreSurfaceExact = m_focusSurface == expected,
        .seatSurfaceExact = g_pSeatManager->m_state.keyboardFocus == expected, .keyboardPresent = !!g_pSeatManager->m_keyboard,
        .guardsCurrent = unlocked && layerAllows && seatAllows, .ownerCurrent = ownerCurrent});
}

void CFocusState::rawWindowFocus(PHLWINDOW pWindow, eFocusReason reason, SP<CWLSurfaceResource> surface) {
    static auto PFOLLOWMOUSE        = CConfigValue<Config::INTEGER>("input:follow_mouse");
    static auto PSPECIALFALLTHROUGH = CConfigValue<Config::INTEGER>("input:special_fallthrough");

    if (pWindow == m_focusWindow && surface == m_focusSurface && m_focusSurface)
        return;

    if (!pWindow || !pWindow->priorityFocus()) {
        if (g_pSessionLockManager->isSessionLocked()) {
            Log::logger->log(Log::DEBUG, "Refusing a keyboard focus to a window because of a sessionlock");
            return;
        }

        if (!g_pInputManager->m_exclusiveLSes.empty()) {
            Log::logger->log(Log::DEBUG, "Refusing a keyboard focus to a window because of an exclusive ls");
            return;
        }
    }

    if (pWindow && pWindow->m_isX11 && pWindow->isX11OverrideRedirect() && !pWindow->m_xwaylandSurface->wantsFocus())
        return;

    // m_target on purpose, this avoids the group
    if (pWindow)
        g_layoutManager->bringTargetToTop(pWindow->m_target);

    if (!pWindow || !validMapped(pWindow)) {

        if (m_focusWindow.expired() && !pWindow)
            return;

        const auto PLASTWINDOW = m_focusWindow.lock();
        m_focusWindow.reset();

        if (PLASTWINDOW && PLASTWINDOW->m_isMapped) {
            PLASTWINDOW->m_ruleApplicator->propertiesChanged(Rule::RULE_PROP_FOCUS);
            PLASTWINDOW->updateDecorationValues();

            g_pXWaylandManager->activateWindow(PLASTWINDOW, false);
        }

        g_pSeatManager->setKeyboardFocus(nullptr);

        g_pEventManager->postEvent(SHyprIPCEvent{"activewindow", ","});
        g_pEventManager->postEvent(SHyprIPCEvent{"activewindowv2", ""});

        Event::bus()->m_events.window.active.emit(nullptr, reason);

        m_focusSurface.reset();

        g_pInputManager->recheckIdleInhibitorStatus();
        return;
    }

    if (pWindow->m_ruleApplicator->noFocus().valueOrDefault()) {
        Log::logger->log(Log::DEBUG, "Ignoring focus to nofocus window!");
        return;
    }

    if (m_focusWindow.lock() == pWindow && g_pSeatManager->m_state.keyboardFocus == surface && g_pSeatManager->m_state.keyboardFocus)
        return;

    if (pWindow->m_pinned && Pin::state()->maxOrigin(pWindow)) {
        const auto ownMonitor = pWindow->m_monitor.lock();
        if (ownMonitor && ownMonitor->m_activeWorkspace && ownMonitor->m_activeWorkspace->m_space) {
            pWindow->layoutTarget()->assignToSpace(ownMonitor->m_activeWorkspace->m_space);
            rawMonitorFocus(ownMonitor);
        }
    } else if (pWindow->m_pinned)
        pWindow->m_workspace = m_focusMonitor->m_activeWorkspace;

    const auto PMONITOR = pWindow->m_monitor.lock();

    if (!pWindow->m_workspace || !pWindow->m_workspace->isVisible()) {
        const auto PWORKSPACE = pWindow->m_workspace;
        // This is to fix incorrect feedback on the focus history.
        PWORKSPACE->m_lastFocusedWindow = pWindow;
        if (PWORKSPACE->m_isSpecialWorkspace)
            m_focusMonitor->changeWorkspace(PWORKSPACE, false, true); // if special ws, open on current monitor
        else if (PMONITOR)
            PMONITOR->changeWorkspace(PWORKSPACE, false, true);
        // changeworkspace already calls focusWindow
        return;
    }

    if (PMONITOR && !pWindow->m_pinned)
        rawMonitorFocus(PMONITOR);

    const auto PLASTWINDOW                    = m_focusWindow.lock();
    m_focusWindow                             = pWindow;
    pWindow->m_workspace->m_lastFocusedWindow = pWindow;

    /* If special fallthrough is enabled, this behavior will be disabled, as I have no better idea of nicely tracking which
       window focuses are "via keybinds" and which ones aren't. */
    if (PMONITOR && PMONITOR->m_activeSpecialWorkspace && PMONITOR->m_activeSpecialWorkspace != pWindow->m_workspace && !pWindow->m_pinned && !*PSPECIALFALLTHROUGH)
        PMONITOR->setSpecialWorkspace(nullptr);

    // we need to make the PLASTWINDOW not equal to m_pLastWindow so that RENDERDATA is correct for an unfocused window
    if (PLASTWINDOW && PLASTWINDOW->m_isMapped) {
        PLASTWINDOW->m_ruleApplicator->propertiesChanged(Rule::RULE_PROP_FOCUS);
        PLASTWINDOW->updateDecorationValues();

        if (!pWindow->m_isX11 || !pWindow->isX11OverrideRedirect())
            g_pXWaylandManager->activateWindow(PLASTWINDOW, false);
    }

    const auto PWINDOWSURFACE = surface ? surface : pWindow->wlSurface()->resource();
    rawSurfaceFocus(PWINDOWSURFACE, pWindow);

    g_pXWaylandManager->activateWindow(pWindow, true); // sets the m_pLastWindow

    pWindow->m_ruleApplicator->propertiesChanged(Rule::RULE_PROP_FOCUS);
    pWindow->onFocusAnimUpdate();
    pWindow->updateDecorationValues();

    if (pWindow->m_isUrgent)
        pWindow->m_isUrgent = false;

    // Send an event
    g_pEventManager->postEvent(SHyprIPCEvent{.event = "activewindow", .data = pWindow->m_class + "," + pWindow->m_title});
    g_pEventManager->postEvent(SHyprIPCEvent{.event = "activewindowv2", .data = std::format("{:x}", rc<uintptr_t>(pWindow.get()))});

    Event::bus()->m_events.window.active.emit(pWindow, reason);

    g_pInputManager->recheckIdleInhibitorStatus();

    if (*PFOLLOWMOUSE == 0)
        g_pInputManager->sendMotionEventsToFocused();

    if (pWindow->m_group)
        pWindow->deactivateGroupMembers();
}

void CFocusState::rawSurfaceFocus(SP<CWLSurfaceResource> pSurface, PHLWINDOW pWindowOwner) {
    if (g_pSeatManager->m_state.keyboardFocus == pSurface || (pWindowOwner && g_pSeatManager->m_state.keyboardFocus == pWindowOwner->wlSurface()->resource()))
        return; // Don't focus when already focused on this.

    if (g_pSessionLockManager->isSessionLocked() && pSurface && !g_pSessionLockManager->isSurfaceSessionLock(pSurface))
        return;

    if (g_pSeatManager->m_seatGrab && !g_pSeatManager->m_seatGrab->accepts(pSurface)) {
        Log::logger->log(Log::DEBUG, "surface {:x} won't receive kb focus because grab rejected it", rc<uintptr_t>(pSurface.get()));
        return;
    }

    const auto PLASTSURF = m_focusSurface.lock();

    // Unfocus last surface if should
    if (m_focusSurface && !pWindowOwner)
        g_pXWaylandManager->activateSurface(m_focusSurface.lock(), false);

    if (!pSurface) {
        g_pSeatManager->setKeyboardFocus(nullptr);
        g_pEventManager->postEvent(SHyprIPCEvent{.event = "activewindow", .data = ","});
        g_pEventManager->postEvent(SHyprIPCEvent{.event = "activewindowv2", .data = ""});
        Event::bus()->m_events.input.keyboard.focus.emit(nullptr);
        m_focusSurface.reset();
        return;
    }

    if (g_pSeatManager->m_keyboard)
        g_pSeatManager->setKeyboardFocus(pSurface);

    if (pWindowOwner)
        Log::logger->log(Log::DEBUG, "Set keyboard focus to surface {:x}, with {}", rc<uintptr_t>(pSurface.get()), pWindowOwner);
    else
        Log::logger->log(Log::DEBUG, "Set keyboard focus to surface {:x}", rc<uintptr_t>(pSurface.get()));

    g_pXWaylandManager->activateSurface(pSurface, true);
    m_focusSurface = pSurface;

    Event::bus()->m_events.input.keyboard.focus.emit(pSurface);

    const auto SURF    = Desktop::View::CWLSurface::fromResource(pSurface);
    const auto OLDSURF = Desktop::View::CWLSurface::fromResource(PLASTSURF);

    if (OLDSURF && OLDSURF->constraint())
        OLDSURF->constraint()->deactivate();

    if (SURF && SURF->constraint())
        SURF->constraint()->activate();
}

void CFocusState::rawMonitorFocus(PHLMONITOR pMonitor) {
    if (m_focusMonitor == pMonitor)
        return;

    if (!pMonitor) {
        m_focusMonitor.reset();
        return;
    }

    const auto PWORKSPACE = pMonitor->m_activeWorkspace;

    const auto WORKSPACE_ID   = PWORKSPACE ? std::to_string(PWORKSPACE->m_id) : std::to_string(WORKSPACE_INVALID);
    const auto WORKSPACE_NAME = PWORKSPACE ? PWORKSPACE->m_name : "?";

    g_pEventManager->postEvent(SHyprIPCEvent{.event = "focusedmon", .data = pMonitor->m_name + "," + WORKSPACE_NAME});
    g_pEventManager->postEvent(SHyprIPCEvent{.event = "focusedmonv2", .data = pMonitor->m_name + "," + WORKSPACE_ID});

    Event::bus()->m_events.monitor.focused.emit(pMonitor);
    m_focusMonitor = pMonitor;
}

SP<CWLSurfaceResource> CFocusState::surface() {
    return m_focusSurface.lock();
}

PHLWINDOW CFocusState::window() {
    return m_focusWindow.lock();
}

PHLMONITOR CFocusState::monitor() {
    return m_focusMonitor.lock();
}

void CFocusState::resetWindowFocus() {
    m_focusWindow.reset();
    m_focusSurface.reset();
}

bool CFocusState::isWindowActive(PHLWINDOW pWindow) const {
    const auto FOCUSWINDOW  = m_focusWindow.lock();
    const auto FOCUSSURFACE = m_focusSurface.lock();

    if (!FOCUSWINDOW && !FOCUSSURFACE)
        return false;

    if (!pWindow || !pWindow->m_isMapped)
        return false;

    const auto PSURFACE = pWindow->wlSurface()->resource();

    return PSURFACE == FOCUSSURFACE || pWindow == FOCUSWINDOW;
}

bool Desktop::isHardInputFocusReason(eFocusReason r) {
    return r == FOCUS_REASON_NEW_WINDOW || r == FOCUS_REASON_KEYBIND || r == FOCUS_REASON_GHOSTS || r == FOCUS_REASON_CLICK || r == FOCUS_REASON_DESKTOP_STATE_CHANGE ||
        r == FOCUS_REASON_UNMAP_WINDOW_TILING || r == FOCUS_REASON_SWITCH_TO_WINDOW_HARD;
}
