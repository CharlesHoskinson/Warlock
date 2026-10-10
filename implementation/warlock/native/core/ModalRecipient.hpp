// Shared native family recipient selection for shell and committed MAX activation.
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
namespace WarlockModal {
// Private activation-only traversal flag; ordinary pointer hits exclude blocked parents.
inline constexpr uint16_t INCLUDE_BLOCKED_PARENT = 1 << 15;
// Return no recipient on cyclic/ambiguous modal constraints, without changing
// fullscreen, pointer routing or keyboard focus. No click is synthesized.
inline std::optional<PHLWINDOW> focusRecipient(const PHLWINDOW& root, bool restoring = false, bool navigating = false,
    const std::vector<PHLWINDOW>* committedOrder = nullptr) {
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
    const auto& order = committedOrder ? *committedOrder : Desktop::windowState()->windows();
    for (const auto& window : order) {
        // A live modal remains a family constraint when its input is blocked
        // or no_focus is set. Removing it here would erase a deeper recipient
        // (or sibling ambiguity) and incorrectly fall back to an ancestor.
        if (window == root || (!restoring && Desktop::WindowPolicy::isMinimized(window)) || !Desktop::View::validMapped(window) || window->isHidden() || !window->m_workspace || (!window->m_workspace->isVisible() && !(navigating && window->m_workspace==root->m_workspace && window->m_monitor.lock()==root->m_monitor.lock())))
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
    const auto recipient = deepest.empty() ? root : deepest.front();
    if (!Desktop::View::validMapped(recipient) || recipient->isHidden() || !recipient->m_workspace ||
        (!recipient->m_workspace->isVisible() && !(navigating && recipient->m_workspace==root->m_workspace && recipient->m_monitor.lock()==root->m_monitor.lock())) ||
        (restoring ? recipient->isInputBlocked() : !recipient->acceptsInput()) || recipient->m_ruleApplicator->noFocus().valueOrDefault())
        return std::nullopt;
    return recipient;
}

}
