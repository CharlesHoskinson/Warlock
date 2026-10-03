#include "NativePinState.hpp"
#include "CorePolicyBuild.hpp"
#include "../WindowState.hpp"
#include "../../view/Window.hpp"
#include "../../view/Group.hpp"
#include "../../../layout/space/Space.hpp"
#include "../../../protocols/XDGShell.hpp"
#include "../../../protocols/XDGDialog.hpp"
#include <algorithm>
#include <limits>
#include <cmath>
#include "../../../event/EventBus.hpp"
#include "../../../managers/fullscreen/handler/FullscreenHandler.hpp"
#include "../../../render/Renderer.hpp"
#include <hyprutils/utils/ScopeGuard.hpp>
#include <unordered_set>

using namespace Desktop::Pin;

UP<CNativePinState>& Desktop::Pin::state() {
    static UP<CNativePinState> instance = makeUnique<CNativePinState>();
    return instance;
}

uint32_t Desktop::Pin::capabilityVersion() {
    return NATIVE_PIN_POLICY_VERSION;
}

bool Desktop::Pin::eligible(PHLWINDOW window) {
    return state()->live(window) && validMapped(window) && !window->isHidden() && window->m_workspace && window->m_workspace->m_space && window->m_monitor &&
        window->m_monitor == window->m_workspace->m_monitor && !window->onSpecialWorkspace();
}

CNativePinState::CNativePinState() {
    m_open       = Event::bus()->m_events.window.open.listen([this](PHLWINDOW w) {
        m_closed.erase(w);
        refreshFamily();
    });
    m_close      = Event::bus()->m_events.window.close.listen([this](PHLWINDOW w) {
        m_closed.insert(w);
        retire(w);
        refreshFamily();
    });
    m_pin        = Event::bus()->m_events.window.pin.listen([this](PHLWINDOW) { refreshFamily(); });
    m_floating   = Event::bus()->m_events.window.floating.listen([this](PHLWINDOW) { refreshFamily(); });
    m_fullscreen = Event::bus()->m_events.window.fullscreen.listen([this](PHLWINDOW) { refreshFamily(); });
    m_workspace  = Event::bus()->m_events.window.moveToWorkspace.listen([this](PHLWINDOW, PHLWORKSPACE) { refreshFamily(); });
}

bool CNativePinState::live(PHLWINDOW window) const {
    return window && !m_closed.contains(window);
}

static bool validBox(const Layout::STargetBox& box) {
    const auto valid = [](const CBox& b) { return std::isfinite(b.x) && std::isfinite(b.y) && std::isfinite(b.w) && std::isfinite(b.h) && b.w > 0 && b.h > 0; };
    return valid(box.logicalBox) && ((box.visualBox.w == 0 && box.visualBox.h == 0 && std::isfinite(box.visualBox.x) && std::isfinite(box.visualBox.y)) || valid(box.visualBox));
}

void CNativePinState::reap() {
    std::erase_if(m_closed, [](const auto& window) { return !window; });
    std::erase_if(m_transferOutcomes, [](const auto& entry) { return !entry.first; });
    std::erase_if(m_records, [](const auto& entry) { return !entry.first || !entry.second.owner || !entry.second.nativeTarget; });
}

bool CNativePinState::capture(PHLWINDOW window, bool layoutHandled) {
    reap();
    if (!eligible(window) || !window->m_target || !window->layoutTarget() || !window->layoutTarget()->space() || m_nextGeneration == std::numeric_limits<uint64_t>::max())
        return false;
    const auto target = window->layoutTarget();
    const auto box    = target->geometrySnapshot();
    if (target->window() != window || target->space()->workspace() != window->m_workspace || !validBox(box))
        return false;
    const bool origin = maxOrigin(window);
    m_records.insert_or_assign(target,
                               SNativeMaxRestore{.owner         = window,
                                                 .group         = window->m_group,
                                                 .members       = window->m_group ? window->m_group->windows() : std::vector<PHLWINDOWREF>{window},
                                                 .nativeTarget  = window->m_target,
                                                 .layoutTarget  = target,
                                                 .space         = target->space(),
                                                 .output        = window->m_monitor,
                                                 .outputOrigin  = window->m_monitor->m_position,
                                                 .box           = box,
                                                 .floating      = target->floating(),
                                                 .pinOrigin     = origin || window->m_pinned,
                                                 .pinManaged    = origin || window->m_pinned,
                                                 .layoutHandled = layoutHandled,
                                                 .generation    = m_nextGeneration++});
    return true;
}

SNativeMaxProjection CNativePinState::snapshot(PHLWINDOW window) const {
    if (!window || !window->m_target || !window->layoutTarget())
        return {};
    const auto target = window->layoutTarget();
    const auto it     = m_records.find(target);
    if (it == m_records.end())
        return {};
    const auto& r = it->second;
    if (r.owner != window || r.nativeTarget != window->m_target || r.layoutTarget != target)
        return {};
    const auto members = window->m_group ? window->m_group->windows() : std::vector<PHLWINDOWREF>{window};
    const bool membersCurrent =
        r.group == window->m_group && r.members == members && std::ranges::all_of(members, [this](const auto& member) { return member && live(member.lock()); });
    const bool valid = membersCurrent && r.restoreUsable && live(window) && validMapped(window) && r.owner == window && r.nativeTarget == window->m_target && r.output &&
        r.output == window->m_monitor && r.generation > 0 && r.layoutTarget && r.layoutTarget.get() == target.get() && r.space && r.space.get() == target->space().get() &&
        target->window() == window && target->space()->workspace() == window->m_workspace && target->floating() == r.floating && validBox(r.box);
    return {.valid         = valid,
            .pinOrigin     = r.pinOrigin,
            .pinManaged    = r.pinManaged,
            .floating      = r.floating,
            .layoutHandled = r.layoutHandled,
            .generation    = r.generation,
            .target        = rc<uintptr_t>(window->m_target.get()),
            .layoutTarget  = rc<uintptr_t>(target.get()),
            .space         = rc<uintptr_t>(target->space().get()),
            .box           = r.box};
}

bool CNativePinState::admits(PHLWINDOW window) const {
    if (!window)
        return false;
    const auto r     = snapshot(window);
    const auto modes = Fullscreen::controller()->getFullscreenModes(window);
    if (modes.internal == Fullscreen::FSMODE_MAXIMIZED) {
        const auto handler = Fullscreen::controller()->getFsHandler(window, r.layoutHandled);
        if (!handler || !handler->nativeMaxRestoreValid(window->m_target))
            return false;
    }
    return admitsNative({.live          = validMapped(window),
                         .visible       = !window->isHidden(),
                         .normalSpace   = window->m_workspace && !window->onSpecialWorkspace(),
                         .restoreKnown  = r.valid,
                         .restoreOrigin = r.pinOrigin,
                         .targetExact   = eligible(window),
                         .internalMode  = modes.internal,
                         .clientMode    = modes.client});
}

bool CNativePinState::maxOrigin(PHLWINDOW window) const {
    if (!live(window) || !validMapped(window) || !window->layoutTarget())
        return false;
    const auto it = m_records.find(window->layoutTarget());
    return it != m_records.end() && it->second.owner == window && it->second.nativeTarget == window->m_target && it->second.layoutTarget == window->layoutTarget() &&
        it->second.pinOrigin;
}

void CNativePinState::setOrigin(PHLWINDOW window, bool pinned) {
    if (!window || !window->layoutTarget())
        return;
    const auto it = m_records.find(window->layoutTarget());
    if (it != m_records.end() && it->second.owner == window && it->second.nativeTarget == window->m_target && it->second.layoutTarget == window->layoutTarget()) {
        it->second.pinOrigin  = pinned;
        it->second.pinManaged = true;
    }
}

std::optional<SNativeMaxRestore> CNativePinState::record(PHLWINDOW window) const {
    if (!snapshot(window).valid)
        return std::nullopt;
    return m_records.at(window->layoutTarget());
}

bool CNativePinState::restore(PHLWINDOW window) {
    const auto r = record(window);
    if (!r || !r->pinManaged || Fullscreen::controller()->getFullscreenModes(window).internal != Fullscreen::FSMODE_NONE)
        return false;
    // Use the same owning layout target, including its current group member. No floating toggle or synthetic maximization.
    if (r->layoutHandled && Fullscreen::controller()->getFullscreenHandlerName(window) == Fullscreen::FULLSCREEN_HANDLER_SCROLLING)
        return snapshot(window).valid; // The scrolling owner restores its column, row and camera, not a synthetic target box.
    window->layoutTarget()->rememberFloatingSize(r->box.logicalBox.size());
    window->layoutTarget()->setPositionGlobal(r->box);
    return snapshot(window).valid;
}

void CNativePinState::rebind(PHLWINDOW window, const SNativeMaxRestore& record) {
    if (!eligible(window) || !window->layoutTarget() || record.owner != window || record.nativeTarget != window->m_target || window->layoutTarget()->window() != window ||
        m_nextGeneration == std::numeric_limits<uint64_t>::max())
        return;
    auto next         = record;
    next.layoutTarget = window->layoutTarget();
    next.space        = window->layoutTarget()->space();
    next.output       = window->m_monitor;
    next.outputOrigin = window->m_monitor->m_position;
    next.generation   = m_nextGeneration++;
    m_records.insert_or_assign(window->layoutTarget(), next);
}

void CNativePinState::retire(PHLWINDOW window) {
    if (!window || !window->layoutTarget())
        return;
    const auto it = m_records.find(window->layoutTarget());
    if (it != m_records.end() && it->second.owner == window && it->second.nativeTarget == window->m_target)
        m_records.erase(it);
}

static bool isModal(PHLWINDOW window) {
    const auto dialog = window && window->m_xdgSurface && window->m_xdgSurface->m_toplevel ? window->m_xdgSurface->m_toplevel->m_dialog : nullptr;
    return window && (window->isModal() || (dialog && dialog->modal));
}

bool Desktop::Pin::familyEdge(PHLWINDOW child, PHLWINDOW parent) {
    return eligible(child) && eligible(parent) && child->parent() == parent && child->m_workspace == parent->m_workspace && child->m_monitor == parent->m_monitor &&
        (isModal(child) || (child->m_isX11 && parent->m_isX11));
}

bool Desktop::Pin::effective(PHLWINDOW window) {
    if (!eligible(window))
        return false;
    if (window->m_pinned)
        return true;
    if (!familyEdge(window, window->parent()))
        return false;
    std::unordered_set<uintptr_t> seen;
    auto                          current = window;
    while (current && seen.size() < 512) {
        if (!seen.insert(rc<uintptr_t>(current.get())).second)
            return false;
        if (current->m_pinned)
            return true;
        const auto parent = current->parent();
        if (!familyEdge(current, parent))
            return false;
        current = parent;
    }
    return false;
}

std::vector<PHLWINDOW> Desktop::Pin::band() {
    std::vector<PHLWINDOW> members;
    for (const auto& window : Desktop::windowState()->windows()) {
        if (effective(window))
            members.push_back(window);
    }
    std::vector<SBandNode> nodes;
    for (const auto& w : members) {
        const auto parent = w->parent();
        const auto it     = familyEdge(w, parent) ? std::ranges::find(members, parent) : members.end();
        nodes.push_back({.key = rc<uintptr_t>(w.get()), .parent = it != members.end() ? sc<int>(std::distance(members.begin(), it)) : -1});
    }
    const auto ordered = orderBand(nodes);
    if (!ordered)
        return {};
    std::vector<PHLWINDOW> result;
    for (const auto index : *ordered)
        result.push_back(members[index]);
    return result;
}

PHLWINDOW Desktop::Pin::deepestModal(PHLWINDOW owner) {
    if (!state()->live(owner) || !validMapped(owner) || owner->isHidden())
        return nullptr;
    std::unordered_set<uintptr_t> seen;
    auto                          current = owner;
    const auto&                   windows = Desktop::windowState()->windows();
    while (seen.size() < 512) {
        if (!seen.insert(rc<uintptr_t>(current.get())).second)
            return nullptr;
        PHLWINDOW next;
        for (const auto& child : windows | std::views::reverse) {
            if (familyEdge(child, current) && isModal(child)) {
                next = child;
                break;
            }
        }
        if (!next)
            return current;
        current = next;
    }
    return nullptr;
}

bool CNativePinState::ownedUnpinReady(PHLWINDOW window) const {
    if (!live(window) || !validMapped(window) || window->isHidden() || !window->m_pinned || !window->m_workspace || window->onSpecialWorkspace() || !window->m_monitor ||
        !window->layoutTarget() || window->layoutTarget()->window() != window)
        return false;
    const auto it = m_records.find(window->layoutTarget());
    return it != m_records.end() && it->second.owner == window && it->second.nativeTarget == window->m_target && it->second.layoutTarget == window->layoutTarget() &&
        it->second.generation > 0 && it->second.pinOrigin && it->second.pinManaged;
}

std::optional<SNativeTransferOutcome> CNativePinState::transferOutcome(PHLWINDOW window) const {
    const auto it = m_transferOutcomes.find(window);
    return it == m_transferOutcomes.end() ? std::nullopt : std::optional<SNativeTransferOutcome>{it->second};
}

std::optional<SNativeMaxTransfer> CNativePinState::beginTransfer(PHLWINDOW window, const SP<Layout::CSpace>& destination) {
    const auto restoreRecord = record(window);
    if (!restoreRecord || !restoreRecord->pinManaged || !destination || destination == window->layoutTarget()->space() || !destination->workspace() ||
        destination->workspace()->m_isSpecialWorkspace || !destination->workspace()->m_monitor || m_transferring.contains(window) ||
        m_nextOperation == std::numeric_limits<uint64_t>::max())
        return std::nullopt;
    const auto modes = Fullscreen::controller()->getFullscreenModes(window);
    if (modes.internal > Fullscreen::FSMODE_MAXIMIZED || modes.client > Fullscreen::FSMODE_MAXIMIZED)
        return std::nullopt;
    const auto handler   = Fullscreen::controller()->getFsHandler(window, restoreRecord->layoutHandled);
    const auto algorithm = window->layoutTarget()->space()->algorithm();
    if (!handler || !algorithm)
        return std::nullopt;
    SNativeMaxTransfer transfer{.owner                = window,
                                .target               = window->layoutTarget(),
                                .nativeTarget         = window->m_target,
                                .sourceSpace          = window->layoutTarget()->space(),
                                .destination          = destination,
                                .destinationWorkspace = destination->workspace(),
                                .destinationOutput    = destination->workspace()->m_monitor.lock(),
                                .restore              = *restoreRecord,
                                .modes                = modes,
                                .sourceAlgorithm      = algorithm,
                                .sourceHandler        = handler,
                                .operation            = m_nextOperation++};
    m_transferring.emplace(window, transfer.operation);
    // Preserve the source record until the owning move has an observed terminal outcome.
    // The strong algorithm retains its unique handler; the weak handler is borrowed, never lock().
    transfer.target->rememberFloatingSize(transfer.restore.box.logicalBox.size());
    return transfer;
}

bool CNativePinState::transferring(PHLWINDOW window) const {
    return m_transferring.contains(window);
}

bool CNativePinState::finishTransfer(const SNativeMaxTransfer& transfer) {
    const auto window = transfer.owner;
    const auto active = m_transferring.find(window);
    if (active == m_transferring.end() || active->second != transfer.operation)
        return false;
    uint64_t reboundGeneration = 0;
    auto     current           = [&] {
        const auto row     = m_records.find(transfer.target);
        const auto members = window->m_group ? window->m_group->windows() : std::vector<PHLWINDOWREF>{window};
        return window->m_group == transfer.restore.group && members == transfer.restore.members &&
            std::ranges::all_of(members, [this](const auto& member) { return member && live(member.lock()); }) && row != m_records.end() && row->second.owner == window &&
            row->second.generation == transfer.restore.generation && row->second.restoreUsable && eligible(window) && window->m_target == transfer.nativeTarget &&
            window->layoutTarget() == transfer.target && transfer.target->window() == window && transfer.target->space() == transfer.destination &&
            transfer.destination->workspace() == transfer.destinationWorkspace && transfer.destinationWorkspace == window->m_workspace &&
            transfer.destinationWorkspace->m_monitor == transfer.destinationOutput && window->m_monitor == transfer.destinationOutput &&
            transfer.target->floating() == transfer.restore.floating;
    };
    auto finish = [&](bool accepted, const std::string& reason) {
        // Map-only retirement never writes a closed/replaced owner or its layout peers.
        if (transfer.sourceHandler)
            transfer.sourceHandler->detachFullscreenRecord(transfer.nativeTarget);
        SNativeTransferOutcome outcome{
            .operation = transfer.operation, .generation = transfer.restore.generation, .accepted = accepted, .before = transfer.modes, .reason = reason};
        if (live(window) && validMapped(window) && window->m_target == transfer.nativeTarget && window->layoutTarget() == transfer.target && transfer.target->window() == window) {
            outcome.actualModesKnown = true;
            outcome.actual           = Fullscreen::controller()->getFullscreenModes(window);
            outcome.target           = rc<uintptr_t>(transfer.target.get());
            outcome.space            = rc<uintptr_t>(transfer.target->space().get());
            outcome.workspace        = rc<uintptr_t>(window->m_workspace.get());
            outcome.output           = rc<uintptr_t>(window->m_monitor.get());
            if (!accepted)
                invalidateReturn(window);
        }
        if (accepted &&
            (!outcome.actualModesKnown || outcome.actual.internal != transfer.modes.internal || outcome.actual.client != transfer.modes.client || !snapshot(window).valid)) {
            accepted         = false;
            outcome.accepted = false;
            outcome.reason   = "Final actual owning mode/return observation refused";
            if (outcome.actualModesKnown)
                invalidateReturn(window);
        }
        // Refusal belongs to this captured row even if the group currently selects
        // another owner. A later reselect cannot revive a rejected return witness.
        // This updates metadata only; never window geometry, modes or pin bits.
        const auto captured = m_records.find(transfer.target);
        if (!accepted && captured != m_records.end() && captured->second.owner == transfer.owner && captured->second.nativeTarget == transfer.nativeTarget &&
            (captured->second.generation == transfer.restore.generation || (reboundGeneration && captured->second.generation == reboundGeneration)))
            captured->second.restoreUsable = false;
        m_transferring.erase(window);
        m_transferOutcomes.insert_or_assign(window, outcome);
        return accepted;
    };
    const auto row = m_records.find(transfer.target);
    if (!current() || row == m_records.end() || row->second.owner != window || row->second.generation != transfer.restore.generation || !row->second.restoreUsable)
        return finish(false, "Current owning transfer scope changed");
    const auto handler = Fullscreen::controller()->getFsHandler(window, transfer.restore.layoutHandled);
    if (!handler)
        return finish(false, "Destination native handler unavailable");
    auto       next   = transfer.restore;
    const auto offset = window->m_monitor->m_position - next.outputOrigin;
    next.box.logicalBox.translate(offset);
    if (!next.box.visualBox.empty())
        next.box.visualBox.translate(offset);
    if (transfer.modes.internal == Fullscreen::FSMODE_MAXIMIZED) {
        const auto outcome = handler->requestFullscreen({.target = window->m_target, .currentMode = Fullscreen::FSMODE_NONE, .mode = Fullscreen::FSMODE_MAXIMIZED});
        if (outcome == Fullscreen::FULLSCREEN_REQUEST_FAILED || !current())
            return finish(false, "Destination native MAX request refused or scope changed");
        next.layoutHandled = outcome == Fullscreen::FULLSCREEN_REQUEST_LAYOUT_HANDLED;
    } else {
        transfer.target->setPositionGlobal(next.box);
        if (!current())
            return finish(false, "Destination normal layout callback changed scope");
    }
    handler->setTargetFullscreenModeClient(window->m_target, transfer.modes.client);
    if (!current())
        return finish(false, "Destination native client-state callback changed scope");
    const auto actual = Fullscreen::controller()->getFullscreenModes(window);
    if (actual.internal != transfer.modes.internal || actual.client != transfer.modes.client)
        return finish(false, "Destination native modes differ from captured transfer");
    rebind(window, next);
    reboundGeneration = snapshot(window).generation;
    if (!snapshot(window).valid)
        return finish(false, "Destination restore ownership unavailable");
    return finish(true, "Native owning transfer completed");
}

bool Desktop::Pin::effective(PHLWINDOWREF window) {
    return effective(window.lock());
}

void CNativePinState::refreshFamily() {
    if (m_refreshing)
        return;
    m_refreshing = true;
    Hyprutils::Utils::CScopeGuard    reset([this] { m_refreshing = false; });
    std::unordered_set<PHLWINDOWREF> next;
    for (const auto& window : Desktop::windowState()->windows()) {
        const bool protectedNow = effective(window);
        if (protectedNow)
            next.insert(window);
        if (!eligible(window) || (!protectedNow && !m_protected.contains(window)))
            continue;
        const bool visible =
            protectedNow || !Fullscreen::controller()->hasFullscreen(window->m_workspace) || Fullscreen::controller()->isFullscreen(window) || window->isAllowedOverFullscreen();
        *window->alpha(Desktop::View::WINDOW_ALPHA_FULLSCREEN) = visible ? 1.F : 0.F;
        window->updateFullscreenInputState();
        g_pHyprRenderer->damageWindow(window, true);
    }
    m_protected = std::move(next);
}

std::string_view Desktop::Pin::policyBuildIdentity() {
    return NATIVE_PIN_CORE_SOURCE_ID;
}

bool CNativePinState::rebaseOutput(PHLWINDOW window) {
    if (!eligible(window) || !window->layoutTarget() || m_nextGeneration == std::numeric_limits<uint64_t>::max())
        return false;
    const auto it = m_records.find(window->layoutTarget());
    if (it == m_records.end() || it->second.owner != window || !it->second.pinManaged || it->second.space != window->layoutTarget()->space() ||
        it->second.floating != window->layoutTarget()->floating())
        return false;
    auto       next   = it->second;
    const auto offset = window->m_monitor->m_position - next.outputOrigin;
    next.box.logicalBox.translate(offset);
    if (!next.box.visualBox.empty())
        next.box.visualBox.translate(offset);
    rebind(window, next);
    return snapshot(window).valid;
}

bool CNativePinState::synchronize(PHLWINDOW window) {
    const auto restore = record(window);
    if (!restore || !restore->pinManaged || Fullscreen::controller()->getFullscreenModes(window).internal != Fullscreen::FSMODE_MAXIMIZED)
        return false;
    const auto handler = Fullscreen::controller()->getFsHandler(window, restore->layoutHandled);
    if (!handler)
        return false;
    handler->setTargetSizeAndPosition(window->m_target);
    return snapshot(window).valid;
}

void CNativePinState::invalidateReturn(PHLWINDOW window) {
    if (!window || !window->layoutTarget())
        return;
    const auto it = m_records.find(window->layoutTarget());
    if (it != m_records.end() && it->second.owner == window && it->second.nativeTarget == window->m_target)
        it->second.restoreUsable = false;
}
