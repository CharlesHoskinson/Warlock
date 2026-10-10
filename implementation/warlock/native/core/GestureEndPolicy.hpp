#pragma once
#include "layout/target/Target.hpp"
#include "desktop/view/Window.hpp"

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
struct Capture {
    const Layout::Supplementary::CDragStateController* controller = nullptr;
    WP<Layout::ITarget> target;
    PHLWINDOWREF window;
    WP<Layout::CSpace> space;
};
inline Capture captured;
inline void begin(const Layout::Supplementary::CDragStateController* controller, const SP<Layout::ITarget>& target) {
    captured = {controller, target, target->window(), target->space()};
}
inline SP<Layout::CSpace> takeOrigin(const Layout::Supplementary::CDragStateController* controller, const SP<Layout::ITarget>& target) {
    const auto origin = captured;
    if (captured.controller == controller)
        captured = {};
    if (!target || origin.controller != controller || origin.target.lock() != target || origin.window.lock() != target->window())
        return nullptr;
    return origin.space.lock();
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
