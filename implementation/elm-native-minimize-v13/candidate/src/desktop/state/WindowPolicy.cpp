#include "WindowPolicy.hpp"
#include "desktop/view/Window.hpp"
#include <algorithm>
#include <ranges>
namespace Desktop::WindowPolicy {
namespace {
    std::vector<PHLWINDOWREF> minimizedWindows;
    void prune() {
        std::erase_if(minimizedWindows, [](const auto& reference) {
            const auto window = reference.lock();
            return !window || !window->m_isMapped;
        });
    }
}
bool isMinimized(const PHLWINDOW& window) {
    prune();
    return window && std::ranges::any_of(minimizedWindows, [&](const auto& reference) { return reference.lock() == window; });
}
bool applyMinimized(const std::vector<PHLWINDOW>& family, bool minimized) {
    // Validate and prepare all storage before changing any family's state.
    if (family.empty() || family.size() > 256)
        return false;
    for (size_t i = 0; i < family.size(); ++i)
        if (!family[i] || !family[i]->m_isMapped || std::find(family.begin(), family.begin() + i, family[i]) != family.begin() + i)
            return false;
    prune();
    auto candidate = minimizedWindows;
    std::erase_if(candidate, [&](const auto& reference) { return std::ranges::find(family, reference.lock()) != family.end(); });
    if (minimized) {
        if (candidate.size() + family.size() > 256)
            return false;
        candidate.reserve(candidate.size() + family.size());
        for (const auto& window : family)
            candidate.emplace_back(window);
    }
    minimizedWindows.swap(candidate);
    return true;
}
}
