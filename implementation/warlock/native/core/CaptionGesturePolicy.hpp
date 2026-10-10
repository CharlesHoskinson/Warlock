#pragma once
#include "ModalRecipient.hpp"
#include "layout/LayoutManager.hpp"
#include "layout/supplementary/DragController.hpp"
#include "managers/SeatManager.hpp"
#include "managers/SessionLockManager.hpp"
#include "managers/input/InputManager.hpp"

namespace WarlockCaption {
// XDGShell has already validated and consumed the client's seat/surface press
// serial. Recheck current policy here; a press never reserves future eligibility.
// A gesture belongs to the requesting surface and cannot be redirected to a modal.
inline bool eligibleRequest(const PHLWINDOW& window) {
    if (!window || g_layoutManager->dragController()->target() ||
        g_pSessionLockManager->isSessionLocked() || !g_pInputManager->m_exclusiveLSes.empty() || g_pSeatManager->m_seatGrab)
        return false;

    const auto recipient = WarlockModal::focusRecipient(window);
    return recipient && *recipient == window;
}
}
