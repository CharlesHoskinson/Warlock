#pragma once
#include "layout/target/Target.hpp"
#include "desktop/view/Window.hpp"
#include "managers/fullscreen/FullscreenController.hpp"
#include <algorithm>
#include <optional>
#include <vector>

namespace Layout::Supplementary {
class CDragStateController;
}

namespace WarlockGestureEnd {
enum class Reason { Release, Cancel, Retire };
struct Request {
    const Layout::Supplementary::CDragStateController* controller = nullptr;
    Reason reason = Reason::Release;
};
// Native input dispatch and Window unmap are synchronous on the owning thread.
// This private, scoped reason adds no controller fields or external command.
inline Request current;
// The loaded authority retires its own saved ordinary placement after an
// actual captured MAX caption release. No frontend or new effect is involved.
inline void (*releaseMaxPlacement)(const PHLWINDOW&) = nullptr;
// Only committed native snap effects record ordinary geometry. Weak identity,
// source-space and exact placed-box matching prevent stale placement adoption.
struct SnapCapture {
    WP<Layout::ITarget> target;
    PHLWINDOWREF window;
    WP<Layout::CSpace> space;
    CBox ordinary;
    CBox placed;
};
inline std::vector<SnapCapture> snaps;
inline void pruneSnaps() {
    std::erase_if(snaps, [](const auto& snap) { return snap.target.expired() || snap.window.expired() || snap.space.expired(); });
}
inline std::optional<CBox> snappedOrdinary(const SP<Layout::ITarget>& target) {
    pruneSnaps();
    for (const auto& snap : snaps)
        if (snap.target.lock() == target && snap.window.lock() == target->window() && snap.space.lock() == target->space() && snap.placed == target->position())
            return snap.ordinary;
    return {};
}
inline bool canRememberSnap(const SP<Layout::ITarget>& target) {
    pruneSnaps();
    return snaps.size() < 256 || std::ranges::any_of(snaps, [&](const auto& snap) { return snap.target.lock() == target; });
}
inline void rememberSnap(const SP<Layout::ITarget>& target, const CBox& ordinary, const CBox& previous) {
    pruneSnaps();
    for (auto& snap : snaps) {
        if (snap.target.lock() != target)
            continue;
        const bool continuing = snap.window.lock() == target->window() && snap.space.lock() == target->space() && snap.placed == previous;
        snap = {target, target->window(), target->space(), continuing ? snap.ordinary : ordinary, target->position()};
        return;
    }
    if (snaps.size() < 256)
        snaps.push_back({target, target->window(), target->space(), ordinary, target->position()});
}
inline void forgetSnap(const SP<Layout::ITarget>& target) {
    std::erase_if(snaps, [&](const auto& snap) { return snap.target.expired() || snap.target.lock() == target; });
}
struct Capture {
    const Layout::Supplementary::CDragStateController* controller = nullptr;
    WP<Layout::ITarget> target;
    PHLWINDOWREF window;
    WP<Layout::CSpace> space;
    CBox box;
    Vector2D press;
    Vector2D floatingSize;
    Fullscreen::SFullscreenMode modes;
    std::optional<CBox> snapped;
    bool captionRestore = false;
    bool restored = false;
};
inline Capture captured;
inline void begin(const Layout::Supplementary::CDragStateController* controller, const SP<Layout::ITarget>& target, const Vector2D& press, bool captionMove) {
    captured = {controller, target, target->window(), target->space(), target->position(), press, target->lastFloatingSize(),
                Fullscreen::controller()->getFullscreenModes(target->window()), snappedOrdinary(target)};
    captured.captionRestore = captionMove && target->floating() && (captured.modes.internal != Fullscreen::FSMODE_NONE || captured.snapped.has_value());
}
inline std::optional<Capture> origin(const Layout::Supplementary::CDragStateController* controller, const SP<Layout::ITarget>& target) {
    if (!target || captured.controller != controller || captured.target.lock() != target || captured.window.lock() != target->window())
        return {};
    return captured;
}
inline std::optional<Capture> takeOrigin(const Layout::Supplementary::CDragStateController* controller, const SP<Layout::ITarget>& target) {
    const auto result = origin(controller, target);
    if (captured.controller == controller)
        captured = {};
    return result;
}
inline CBox anchored(const Capture& origin, const Vector2D& pointer, const Vector2D& size) {
    const auto fraction = std::clamp((origin.press.x - origin.box.x) / origin.box.w, 0.0, 1.0);
    return {pointer - Vector2D{fraction * size.x, origin.press.y - origin.box.y}, size};
}
inline Reason reason(const Layout::Supplementary::CDragStateController* controller) {
    return current.controller == controller ? current.reason : Reason::Release;
}
class Scope {
  public:
    Scope(const Layout::Supplementary::CDragStateController* controller, Reason reason) : previous(current) {
        current = {controller, reason};
    }
    ~Scope() { current = previous; }
    Scope(const Scope&) = delete;
    Scope& operator=(const Scope&) = delete;
  private:
    Request previous;
};
}
