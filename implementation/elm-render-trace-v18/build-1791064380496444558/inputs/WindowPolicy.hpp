#pragma once
#include "desktop/DesktopTypes.hpp"
#include <vector>
namespace Desktop::WindowPolicy {
    // Native process-owned first-class state; independent of scratchpads/hidden.
    bool isMinimized(const PHLWINDOW& window);
    bool applyMinimized(const std::vector<PHLWINDOW>& family, bool minimized);
}
