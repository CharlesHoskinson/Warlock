#include "../../debug/log/Logger.hpp"
#include "WindowGroupTarget.hpp"
#include "../../desktop/state/pin/NativePinState.hpp"

#include "../space/Space.hpp"
#include "../algorithm/Algorithm.hpp"
#include "WindowTarget.hpp"
#include "Target.hpp"

#include "../../render/Renderer.hpp"

using namespace Layout;

SP<CWindowGroupTarget> CWindowGroupTarget::create(SP<Desktop::View::CGroup> g) {
    auto target    = SP<CWindowGroupTarget>(new CWindowGroupTarget(g));
    target->m_self = target;
    return target;
}

CWindowGroupTarget::CWindowGroupTarget(SP<Desktop::View::CGroup> g) : m_group(g) {
    ;
}

eTargetType CWindowGroupTarget::type() {
    return TARGET_TYPE_GROUP;
}

void CWindowGroupTarget::setPositionGlobal(const STargetBox& box, uint8_t flags) {
    ITarget::setPositionGlobal(box, flags);

    updatePos(flags);
}

void CWindowGroupTarget::updatePos(uint8_t flags) {
    for (const auto& w : m_group->windows()) {
        w->m_target->setPositionGlobal(m_box, flags);
    }
}

void CWindowGroupTarget::assignToSpace(const SP<CSpace>& space, std::optional<Vector2D> focalPoint) {
    const auto transfer = Desktop::Pin::state()->beginTransfer(window(), space);
    if (transfer && space)
        m_group->updateWorkspace(space->workspace());
    if (transfer &&
        (!Desktop::Pin::state()->live(transfer->owner) || !validMapped(transfer->owner) || window() != transfer->owner || transfer->owner->layoutTarget() != transfer->target ||
         transfer->owner->m_workspace != transfer->destinationWorkspace || space->workspace() != transfer->destinationWorkspace ||
         transfer->destinationWorkspace->m_monitor != transfer->destinationOutput || transfer->owner->m_monitor != transfer->destinationOutput)) {
        Desktop::Pin::state()->finishTransfer(*transfer);
        Log::logger->log(Log::WARN, "Native MAX owning group context changed before layout continuation");
        return;
    }
    ITarget::assignToSpace(space, focalPoint);
    if (space && !transfer)
        m_group->updateWorkspace(space->workspace());
    if (transfer && !Desktop::Pin::state()->finishTransfer(*transfer)) {
        Log::logger->log(Log::WARN, "Native MAX owning group transfer refused; actual partial state retained");
        return;
    }
}

bool CWindowGroupTarget::floating() {
    return m_group->current()->m_target->floating();
}

void CWindowGroupTarget::setFloating(bool x) {
    for (const auto& w : m_group->windows()) {
        w->m_target->setFloating(x);
    }
}

std::expected<SGeometryRequested, eGeometryFailure> CWindowGroupTarget::desiredGeometry() {
    return m_group->current()->m_target->desiredGeometry();
}

PHLWINDOW CWindowGroupTarget::window() const {
    return m_group->current();
}

std::optional<Vector2D> CWindowGroupTarget::minSize() {
    return m_group->current()->minSize();
}

std::optional<Vector2D> CWindowGroupTarget::maxSize() {
    return m_group->current()->maxSize();
}

void CWindowGroupTarget::damageEntire() {
    g_pHyprRenderer->damageWindow(m_group->current());
}

void CWindowGroupTarget::warpPositionSize() {
    for (const auto& w : m_group->windows()) {
        w->m_target->warpPositionSize();
    }
}

void CWindowGroupTarget::onUpdateSpace() {
    for (const auto& w : m_group->windows()) {
        w->m_target->onUpdateSpace();
    }
}

SP<Desktop::View::CGroup> CWindowGroupTarget::getGroup() {
    return m_group.lock();
}
