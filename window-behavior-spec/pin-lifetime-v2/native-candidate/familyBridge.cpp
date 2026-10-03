#include "familyBridge.hpp"
#include "dragBridge.hpp"
#include "globals.hpp"
#include "ancestorHit.hpp"
#include "modalRegionAuthority.hpp"
#include <hyprland/src/protocols/core/Compositor.hpp>
#include <hyprland/src/desktop/state/WindowState.hpp>
#include <hyprland/src/desktop/state/ViewState.hpp>
#include <hyprland/src/desktop/state/FocusState.hpp>
#include <hyprland/src/desktop/state/GlobalWindowController.hpp>
#include <hyprland/src/desktop/history/WindowHistoryTracker.hpp>
#include <hyprland/src/desktop/view/Window.hpp>
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
#include <hyprland/src/plugins/HookSystem.hpp>
#include <hyprland/src/event/EventBus.hpp>
#include <hyprland/src/managers/eventLoop/EventLoopManager.hpp>
#include <format>
#include <unordered_set>
extern "C" {
#include <lua.h>
}

namespace {
using FocusFn = void (*)(Desktop::CFocusState*, PHLWINDOW, Desktop::eFocusReason, SP<CWLSurfaceResource>);
using HitFn = PHLWINDOW (*)(const Desktop::CViewHitTester*, const Vector2D&, uint16_t, PHLWINDOW);
using RaiseFn = void (*)(Desktop::CWindowState*, PHLWINDOW);
CFunctionHook* focusHook = nullptr;
CFunctionHook* hitHook = nullptr;
CFunctionHook* raiseHook = nullptr;
CHyprSignalListener modalButtonListener;
CHyprSignalListener pinnedWorkspaceListener;
UP<SEventLoopDoLaterLock> initialPinnedSync;
std::unordered_set<uint32_t> consumedButtons;

bool isModal(const PHLWINDOW& window) {
    const auto dialog = window->m_xdgSurface && window->m_xdgSurface->m_toplevel ? window->m_xdgSurface->m_toplevel->m_dialog.lock() : nullptr;
    return window->isModal() || (dialog && dialog->modal);
}

PHLWINDOW modalTarget(PHLWINDOW window) {
    std::unordered_set<Desktop::View::CWindow*> visited;
    while (Desktop::View::validMapped(window) && visited.insert(window.get()).second) {
        PHLWINDOW child;
        // Focus history picks the active branch if an app has several dialogs.
        for (const auto& reference : Desktop::History::windowTracker()->fullHistory() | std::views::reverse) {
            const auto candidate = reference.lock();
            if (Desktop::View::validMapped(candidate) && candidate != window && candidate->m_workspace == window->m_workspace &&
                candidate->parent() == window && isModal(candidate)) {
                child = candidate;
                break;
            }
        }
        if (!child)
            break;
        window = child;
    }
    return window;
}

bool modalPointHasAuthority(const PHLWINDOW& owner, const Vector2D& position) {
    if (!validMapped(owner) || !owner->acceptsInput() || !owner->wlSurface())
        return false;
    const auto surfaceBox = owner->wlSurface()->getSurfaceBoxGlobal();
    if (!surfaceBox)
        return false;
    if (surfaceBox->containsPoint(position)) {
        return ModalRegionAuthority::bodyInput(owner->m_isX11, owner->m_X11SurfaceScaledBy,
            [&] {
                Vector2D local;
                return bool(Desktop::viewState()->hitTest().windowSurfaceAt(position, owner, local));
            },
            [&](double scale) {
                const auto resource = owner->wlSurface()->resource();
                if (!resource)
                    return false;
                const auto local = (position - owner->position(Desktop::View::IGeometric::GEOMETRIC_CURRENT)) * scale;
                return bool(resource->at(local, true).first);
            });
    }
    // Only compositor-owned decoration extent; never client-body holes.
    return owner->getWindowBoxUnified(Desktop::View::RESERVED_EXTENTS).containsPoint(position);
}

void syncPinnedFamilies(const PHLWORKSPACE& workspace) {
    if (!workspace || workspace->m_isSpecialWorkspace)
        return;
    // Called after the core's pinned-window loop. Moving targets can change
    // stacking, so retain a snapshot rather than iterating the live order.
    const auto windows = Desktop::windowState()->windows();
    std::unordered_set<Desktop::View::CWindow*> roots;
    bool moved = false;
    for (const auto& pinned : windows) {
        if (!validMapped(pinned) || !pinned->m_pinned || pinned->m_workspace != workspace)
            continue;
        auto root = pinned;
        std::unordered_set<Desktop::View::CWindow*> ancestors;
        while (validMapped(root) && ancestors.insert(root.get()).second) {
            const auto parent = root->parent();
            if (!validMapped(parent) || !parent->m_workspace || parent->m_workspace->m_isSpecialWorkspace)
                break;
            root = parent;
        }
        if (!roots.insert(root.get()).second)
            continue;
        for (const auto& member : windows) {
            if (!validMapped(member) || !member->m_workspace || member->m_workspace->m_isSpecialWorkspace || member->m_workspace == workspace)
                continue;
            auto ancestor = member;
            std::unordered_set<Desktop::View::CWindow*> visited;
            while (validMapped(ancestor) && ancestor != root && visited.insert(ancestor.get()).second)
                ancestor = ancestor->parent();
            if (ancestor != root)
                continue;
            // Use the controller: window.moveToWorkspace alone does not move
            // its layout target, monitor or client suspension state.
            Desktop::globalWindowController()->moveWindowToWorkspace(member, workspace);
            moved = true;
        }
    }
    if (!moved)
        return;
    const auto focused = Desktop::focusState()->window();
    const auto target = modalTarget(focused);
    if (target != focused && target && target->m_workspace == workspace)
        Desktop::focusState()->fullWindowFocus(target, Desktop::FOCUS_REASON_WORKSPACE_CHANGE);
    // Re-hit stationary pointers after previously hidden dialogs become visible.
    g_pInputManager->simulateMouseMovement();
}

void hookedFocus(Desktop::CFocusState* state, PHLWINDOW window, Desktop::eFocusReason reason, SP<CWLSurfaceResource> surface) {
    if (preserveCapturedGestureFocus(window, state->window(), reason))
        return;
    const auto target = modalTarget(window);
    if (target != window) {
        window = target;
        surface = nullptr; // An owner's surface must not receive the child's keyboard focus.
    }
    reinterpret_cast<FocusFn>(focusHook->m_original)(state, window, reason, surface);
}

PHLWINDOW hookedHit(const Desktop::CViewHitTester* tester, const Vector2D& position, uint16_t properties, PHLWINDOW ignored) {
    const auto owner = reinterpret_cast<HitFn>(hitHook->m_original)(tester, position, properties, ignored);
    if (!owner || !owner->m_pinned)
        return owner;
    const auto target = modalTarget(owner);
    // Pinned-owner priority must not mask its own visible dialog. Outside the
    // dialog, the owner still owns the hit and its disabled click is consumed.
    if (target != owner && target != ignored && target->acceptsInput() &&
        (!(properties & Desktop::View::FOCUS_PRIORITY) || target->priorityFocus()) &&
        target->getWindowBoxUnified(properties).containsPoint(position))
        return target;
    return owner;
}

void hookedRaise(Desktop::CWindowState* state, PHLWINDOW owner) {
    const auto original = reinterpret_cast<RaiseFn>(raiseHook->m_original);
    original(state, owner);
    const auto target = modalTarget(owner);
    if (!owner || target == owner)
        return;
    std::vector<PHLWINDOW> chain;
    std::unordered_set<Desktop::View::CWindow*> visited;
    auto child = target;
    while (child && child != owner && visited.insert(child.get()).second) {
        chain.push_back(child);
        child = child->parent();
    }
    if (child != owner)
        return;
    // Raise each intermediate dialog, then the deepest modal. Raising an owner
    // from the pin listener must never put it in front of its disabled children.
    for (const auto& dialog : chain | std::views::reverse)
        original(state, dialog);
}

CFunctionHook* installFamilyHook(const std::string& basename, const std::string& method, const std::string& symbolPrefix, const void* replacement) {
    auto matches = HyprlandAPI::findFunctionsByName(PHANDLE, basename);
    std::string found;
    for (const auto& match : matches)
        found += " [" + match.signature + " => " + match.demangled + "]";
    // The API caches separate nm and demangled-nm outputs. On an existing
    // session they can disagree by a row, so validate the actual ELF symbol.
    // The plugin's compositor ABI hash gate still runs before installing hooks.
    std::erase_if(matches, [&](const auto& match) { return !match.signature.starts_with(symbolPrefix); });
    if (matches.size() != 1)
        throw std::runtime_error("hyprbars family bridge: expected one " + method + found);
    auto hook = HyprlandAPI::createFunctionHook(PHANDLE, matches.front().address, replacement);
    if (!hook || !hook->hook())
        throw std::runtime_error("hyprbars family bridge: hook failed for " + method);
    return hook;
}
}

void initFamilyBridge() {
    try {
        focusHook = installFamilyHook("rawWindowFocus", "CFocusState::rawWindowFocus", "_ZN7Desktop11CFocusState14rawWindowFocusE", reinterpret_cast<void*>(hookedFocus));
        hitHook = installFamilyHook("windowAt", "CViewHitTester::windowAt", "_ZNK7Desktop14CViewHitTester8windowAtE", reinterpret_cast<void*>(hookedHit));
        raiseHook = installFamilyHook("raise", "CWindowState::raise", "_ZN7Desktop12CWindowState5raiseE", reinterpret_cast<void*>(hookedRaise));
        pinnedWorkspaceListener = Event::bus()->m_events.workspace.active.listen([](PHLWORKSPACE workspace) {
            syncPinnedFamilies(workspace);
        });
        // Existing pinned families may already be split by an older build.
        // Wait until plugin initialization completes before touching targets.
        initialPinnedSync = g_pEventLoopManager->doLaterLock([] {
            const auto windows = Desktop::windowState()->windows();
            std::unordered_set<CWorkspace*> workspaces;
            for (const auto& window : windows)
                if (validMapped(window) && window->m_pinned && window->m_workspace && workspaces.insert(window->m_workspace.get()).second)
                    syncPinnedFamilies(window->m_workspace);
        });
        modalButtonListener = Event::bus()->m_events.input.mouse.button.listen([](IPointer::SButtonEvent event, Event::SCallbackInfo& info) {
            if (event.state == WL_POINTER_BUTTON_STATE_RELEASED) {
                if (consumedButtons.erase(event.button))
                    info.cancelled = true;
                return;
            }
            if (info.cancelled || g_pSessionLockManager->isSessionLocked() || !g_pInputManager->m_exclusiveLSes.empty() ||
                g_pInputManager->getClickMode() != CLICKMODE_DEFAULT || g_pInputManager->isConstrained() || g_pInputManager->hasHeldButtons() ||
                g_pSeatManager->m_seatGrab || PROTO::inputCapture->isCaptured() || PROTO::data->dndActive() || g_layoutManager->dragController()->target())
                return;
            auto pointerSurface = g_pSeatManager->m_state.pointerFocus.lock();
            auto pointerOwner = Desktop::viewState()->query().type(Desktop::View::VIEW_TYPE_WINDOW).surface(pointerSurface).runWindow();
            const auto position = g_pInputManager->getMouseCoordsInternal();
            constexpr auto properties = Desktop::View::ALLOW_FLOATING | Desktop::View::RESERVED_EXTENTS | Desktop::View::INPUT_EXTENTS;
            const auto filteredOwner = Desktop::viewState()->hitTest().windowAt(position, properties);
            auto owner = filteredOwner;
            bool recoveredAncestor = false;
            // The core intentionally removes XDG ancestors shadowed by a modal.
            // Discover the top geometry winner without changing global hit/hover.
            if (!pointerSurface || pointerOwner) {
                const auto geometric = modalGeometricWindowAt(position, properties);
                const auto deepest = modalTarget(geometric);
                if (validMapped(geometric) && geometric->acceptsInput() && deepest != geometric && validMapped(deepest) &&
                    deepest->acceptsInput() && deepest->m_workspace && deepest->m_workspace->isVisible() &&
                    (!pointerOwner || pointerOwner == filteredOwner)) {
                    if (modalPointHasAuthority(geometric, position)) {
                        owner = geometric;
                        recoveredAncestor = true;
                    }
                }
            }
            // A newly presented dialog can already own keyboard focus while the
            // stationary pointer still targets its owner (or a destroyed dialog).
            // Core click handling only refocuses when keyboard focus changes.
            // Refresh pointer focus before this first press, without changing
            // keyboard focus or bypassing layer, grab, capture and drag guards.
            if (owner && isModal(owner) && pointerOwner != owner && (!pointerSurface || pointerOwner)) {
                g_pInputManager->simulateMouseMovement();
                pointerSurface = g_pSeatManager->m_state.pointerFocus.lock();
                pointerOwner = Desktop::viewState()->query().type(Desktop::View::VIEW_TYPE_WINDOW).surface(pointerSurface).runWindow();
            }
            // A layer, IME popup or non-window surface owns its own input.
            if (pointerSurface && !pointerOwner)
                return;
            if (!owner || (!recoveredAncestor && pointerOwner && pointerOwner != owner))
                return;
            if (recoveredAncestor && (modalGeometricWindowAt(position, properties) != owner ||
                (pointerOwner && pointerOwner != Desktop::viewState()->hitTest().windowAt(position, properties))))
                return;
            const auto target = modalTarget(owner);
            if (target == owner || !validMapped(target) || !target->acceptsInput() || !target->m_workspace || !target->m_workspace->isVisible() ||
                !modalPointHasAuthority(owner, position))
                return;
            consumedButtons.insert(event.button);
            info.cancelled = true;
            Desktop::windowState()->raise(owner);
            Desktop::focusState()->fullWindowFocus(target, Desktop::FOCUS_REASON_CLICK);
            Desktop::windowState()->raise(target);
        });
    } catch (...) {
        exitFamilyBridge();
        throw;
    }
}

void exitFamilyBridge() {
    initialPinnedSync.reset();
    pinnedWorkspaceListener.reset();
    modalButtonListener.reset();
    consumedButtons.clear();
    if (raiseHook)
        HyprlandAPI::removeFunctionHook(PHANDLE, raiseHook);
    if (hitHook)
        HyprlandAPI::removeFunctionHook(PHANDLE, hitHook);
    if (focusHook)
        HyprlandAPI::removeFunctionHook(PHANDLE, focusHook);
    focusHook = nullptr;
    hitHook = raiseHook = nullptr;
}

int luaModalFocusBridgeAvailable(lua_State* state) {
    lua_pushboolean(state, focusHook && hitHook && raiseHook);
    return 1;
}

int luaWindowFamilies(lua_State* state) {
    // Snapshot contains compositor identities only. Never infer families from
    // process IDs or app classes: an app may have independent top-level windows.
    std::string json = "[";
    bool first = true;
    for (const auto& window : Desktop::windowState()->windows()) {
        if (!window || !window->m_isMapped)
            continue;
        const auto parent = window->parent();
        auto dialog = window->m_xdgSurface && window->m_xdgSurface->m_toplevel ? window->m_xdgSurface->m_toplevel->m_dialog.lock() : nullptr;
        if (!first)
            json += ",";
        first = false;
        json += std::format(R"({{"address":"0x{:x}","stableId":"{:x}","pid":{},"parent":"{}","parentStableId":"{}","modal":{}}})",
            reinterpret_cast<uintptr_t>(window.get()), window->m_stableID, window->getPID(),
            parent ? std::format("0x{:x}", reinterpret_cast<uintptr_t>(parent.get())) : "",
            parent ? std::format("{:x}", parent->m_stableID) : "", (window->isModal() || (dialog && dialog->modal)) ? "true" : "false");
    }
    json += "]";
    lua_pushlstring(state, json.data(), json.size());
    return 1;
}
