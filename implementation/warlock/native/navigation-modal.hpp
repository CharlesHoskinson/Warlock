// Native preflight of a family on its preserved ordinary workspace.
#include "WindowPolicy.hpp"
#pragma once
#include "desktop/state/WindowState.hpp"
#include "desktop/view/Window.hpp"
#include "desktop/Workspace.hpp"
#include "protocols/XDGShell.hpp"
#include "protocols/XDGDialog.hpp"
#include <algorithm>
#include <optional>
#include <vector>
namespace WarlockNavigationModal {
// Private diagnostic hit mode; ordinary hit tests still exclude blocked parents.
inline constexpr uint16_t INCLUDE_BLOCKED_PARENT = 1 << 15;
// Return no recipient on cyclic/ambiguous modal constraints, without changing
// fullscreen, pointer routing or keyboard focus. No click is synthesized.
inline std::optional<PHLWINDOW> focusRecipient(const PHLWINDOW& root, bool restoring = false, bool navigating = false) {
    const auto descendsFrom = [](PHLWINDOW candidate, const PHLWINDOW& owner) -> std::optional<bool> {
        std::vector<PHLWINDOW> seen;
        while (candidate) {
            if (seen.size() >= 256 || std::ranges::find(seen, candidate) != seen.end())
                return std::nullopt;
            seen.push_back(candidate);
            candidate = candidate->parent();
            if (candidate == owner)
                return true;
        }
        return false;
    };
    // Validate the requested family's own ancestry before selecting a child.
    if (!descendsFrom(root, nullptr).has_value())
        return std::nullopt;
    std::vector<PHLWINDOW> modals;
    for (const auto& window : Desktop::windowState()->windows()) {
        if (window == root || (!restoring && Desktop::WindowPolicy::isMinimized(window)) || !Desktop::View::validMapped(window) || window->isHidden() || !window->m_workspace || (!window->m_workspace->isVisible() && !(navigating && window->m_workspace==root->m_workspace && window->m_monitor.lock()==root->m_monitor.lock())) || (restoring ? window->isInputBlocked() : !window->acceptsInput()))
            continue;
        const bool waylandModal = window->m_xdgSurface && window->m_xdgSurface->m_toplevel && window->m_xdgSurface->m_toplevel->m_dialog &&
            window->m_xdgSurface->m_toplevel->m_dialog->modal;
        if (!window->isModal() && !waylandModal)
            continue;
        const auto descendant = descendsFrom(window, root);
        if (!descendant.has_value())
            return std::nullopt;
        if (*descendant)
            modals.push_back(window);
    }
    std::vector<PHLWINDOW> deepest;
    for (const auto& candidate : modals) {
        bool blocked = false;
        for (const auto& other : modals) {
            if (candidate == other)
                continue;
            const auto descendant = descendsFrom(other, candidate);
            if (!descendant.has_value())
                return std::nullopt;
            if (*descendant) {
                blocked = true;
                break;
            }
        }
        if (!blocked)
            deepest.push_back(candidate);
    }
    if (deepest.size() > 1)
        return std::nullopt;
    return deepest.empty() ? root : deepest.front();
}

}
