// Typed environment for production parent-routing fragments, not a compositor.
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <memory>
#include <optional>
#include <ranges>
#include <unordered_map>
#include <vector>
#include "NestedLifecycle.hpp"
#include "ParentNormalizedPosition.hpp"
#include <aquamarine/input/ParentInput.hpp>
template<class T> using SP = std::shared_ptr<T>;
template<class T> struct WP : std::weak_ptr<T> {
    using std::weak_ptr<T>::weak_ptr;
    WP() = default;
    bool operator==(const SP<T>& value) const { return this->lock() == value; }
};
struct Vector2D {
    double x = 0, y = 0;
    Vector2D operator+(Vector2D rhs) const { return {x + rhs.x, y + rhs.y}; }
    Vector2D operator*(Vector2D rhs) const { return {x * rhs.x, y * rhs.y}; }
};
struct CBox {
    double x = 0, y = 0, w = 0, h = 0;
    CBox() = default;
    CBox(double x_, double y_, double w_, double h_) : x(x_), y(y_), w(w_), h(h_) {}
    CBox(Vector2D p, Vector2D size) : CBox(p.x, p.y, size.x, size.y) {}
    Vector2D pos() const { return {x, y}; }
    Vector2D size() const { return {w, h}; }
    bool operator==(const CBox&) const = default;
};
namespace Aquamarine {
struct IOutput { virtual ~IOutput() = default; };
struct IPointer {
    virtual ~IPointer() = default;
    struct SWarpEvent { unsigned timeMs; Vector2D absolute; WP<IOutput> output; };
};
struct CWaylandOutput : IOutput { NestedPolicy::ConfigureLifecycle lifecycle; };
struct CWaylandBackend { std::weak_ptr<CWaylandOutput> focusedOutput; };
struct CWaylandPointer : IPointer {
    std::weak_ptr<CWaylandBackend> backend;
    bool inputAllowedOn(const IOutput* output) const;
};
}
static bool mappingReady(Aquamarine::CWaylandOutput* output) { return output->lifecycle.presentation.inputAllowed(); }
Aquamarine::ParentInputStatus Aquamarine::parentPointerInputStatus(const IPointer* pointer, const IOutput* output) {
    const auto parentPointer = dynamic_cast<const CWaylandPointer*>(pointer);
    if (!parentPointer) return ParentInputStatus::Unsupported;
    return parentPointer->inputAllowedOn(output) ? ParentInputStatus::Ready : ParentInputStatus::Inactive;
}

bool Aquamarine::CWaylandPointer::inputAllowedOn(const IOutput* output) const {
    const auto parent = backend.lock();
    if (!parent || !output) return false;
    const auto focused = parent->focusedOutput.lock();
    return focused && mappingReady(focused.get());
}


namespace Pointer { namespace ParentPolicy {} }
using namespace Pointer;
struct IHID { virtual ~IHID() = default; };
struct IPointer : IHID {
    SP<Aquamarine::IPointer> source;
    SP<Aquamarine::IPointer> aq() const { return source; }
    struct SMotionAbsoluteEvent { unsigned timeMs; Vector2D absolute; SP<IHID> device; };
};
struct Monitor {
    bool m_enabled = true, mirror = false;
    SP<Aquamarine::IOutput> m_output;
    Vector2D m_position, m_size;
    CBox logicalBox() const { return {m_position, m_size}; }
    bool isMirror() const { return mirror; }
};
struct MonitorState {
    std::vector<SP<Monitor>> values;
    const auto& monitors() const { return values; }
};
static MonitorState monitorStateObject;
namespace State { static MonitorState* monitorState() { return &monitorStateObject; } }
struct InputManager {
    int warps = 0;
    bool isLocked() const { return false; }
    void onMouseWarp(const IPointer::SMotionAbsoluteEvent&);
};
static InputManager input;
static InputManager* g_pInputManager = &input;
struct Idle { void onActivity() {} };
namespace PROTO { static Idle idleObject; static Idle* idle = &idleObject; }
struct Compositor { bool m_dpmsStateOn = true; };
static Compositor compositor;
static Compositor* g_pCompositor = &compositor;
namespace Config::Actions {
    static constexpr int TOGGLE_ACTION_ENABLE = 1;
    static void dpms(int, std::nullopt_t) {}
}
namespace Time { static int steadyNow() { return 0; } static unsigned millis(int) { return 0; } }
template<class F> struct CScopeGuard { F fn; ~CScopeGuard() { fn(); } };
template<class F> CScopeGuard(F) -> CScopeGuard<F>;
class CPointerManager {
public:
    struct { std::vector<CBox> monitorBoxes; } m_currentMonitorLayout;
    struct Listener { WP<IPointer> pointer; };
    std::vector<SP<Listener>> m_pointerListeners;
    Vector2D m_pointerPos;
    void damageIfSoftware() {}
    void recheckEnteredOutputs() {}
    void onCursorMoved() {}
    void updateCursorBackend() {}
    Vector2D closestValid(Vector2D value) { return value; } // General monitor clamp is outside this contract.
    void warpTo(const Vector2D& logical);
    void warpAbsolute(Vector2D abs, SP<IHID> dev);
    void onMonitorLayoutChange();
    void detachPointer(SP<IPointer> pointer);
    void dispatch(const Aquamarine::IPointer::SWarpEvent& event, WP<IPointer> weak);
};
static CPointerManager* manager;
namespace {
struct ParentPointerPosition {
    WP<IPointer> device;
    WP<Aquamarine::IOutput> output;
    ParentPolicy::NormalizedPosition normalized;
    CBox appliedBox;
    bool dispatching = false;
    void clear() { device = {}; output = {}; normalized.clear(); appliedBox = {}; dispatching = false; }
};
std::unordered_map<CPointerManager*, std::shared_ptr<ParentPointerPosition>> parentPositions;
std::shared_ptr<ParentPointerPosition> parentPositionFor(CPointerManager* manager) {
    auto& position = parentPositions[manager];
    if (!position) position = std::make_shared<ParentPointerPosition>();
    return position;
}
}


void CPointerManager::warpTo(const Vector2D& logical) {
    parentPositionFor(this)->clear();
    damageIfSoftware();

    m_pointerPos = closestValid(logical);

    if (!g_pInputManager->isLocked()) {
        recheckEnteredOutputs();
        onCursorMoved();
    }

    damageIfSoftware();
}
void CPointerManager::warpAbsolute(Vector2D abs, SP<IHID> dev) {
    const auto& MONITORS = State::monitorState()->monitors();
    CBox mappedArea;
        const auto parentPosition = parentPositionFor(this);
    const auto sourceOutput = parentPosition->output.lock();
    std::optional<Vector2D> parentPoint;
    if (parentPosition->dispatching && parentPosition->device.lock() == dev && sourceOutput) {
        const auto monitor = std::ranges::find_if(MONITORS, [sourceOutput](const auto& m) {
            return m->m_enabled && !m->isMirror() && m->m_output == sourceOutput;
        });
        if (monitor == MONITORS.end()) { parentPosition->clear(); return; }
        mappedArea = (*monitor)->logicalBox();
        const auto point = parentPosition->normalized.project({mappedArea.x,mappedArea.y,mappedArea.w,mappedArea.h});
        if (!point) { parentPosition->clear(); return; }
        parentPosition->appliedBox = mappedArea;
        parentPoint = Vector2D{point->x,point->y};
    } else {
        // A physical/tablet/relative or programmatic source supersedes the parent anchor.
        parentPosition->clear();
    }

    damageIfSoftware();

    if (parentPoint) {
        m_pointerPos = *parentPoint;
    } else if (std::isnan(abs.x) || std::isnan(abs.y)) {
        m_pointerPos.x = std::isnan(abs.x) ? m_pointerPos.x : mappedArea.x + mappedArea.w * abs.x;
        m_pointerPos.y = std::isnan(abs.y) ? m_pointerPos.y : mappedArea.y + mappedArea.h * abs.y;
    } else
        m_pointerPos = mappedArea.pos() + mappedArea.size() * abs;


}
void CPointerManager::onMonitorLayoutChange() {
    m_currentMonitorLayout.monitorBoxes.clear();
    for (auto const& m : State::monitorState()->monitors()) {
        if (m->isMirror() || !m->m_enabled || !m->m_output)
            continue;

        m_currentMonitorLayout.monitorBoxes.emplace_back(m->m_position, m->m_size);
    }

    damageIfSoftware();

    const auto parentPosition = parentPositionFor(this);
    if (parentPosition->normalized.point && !parentPosition->dispatching) {
        const auto device = parentPosition->device.lock();
        const auto output = parentPosition->output.lock();
        const auto source = device ? device->aq() : nullptr;
        const auto& monitors = State::monitorState()->monitors();
        const auto monitor = std::ranges::find_if(monitors, [output](const auto& m) {
            return output && m->m_enabled && !m->isMirror() && m->m_output == output;
        });
        if (!device || !output || !source || Aquamarine::parentPointerInputStatus(source.get(),output.get()) != Aquamarine::ParentInputStatus::Ready || monitor == monitors.end()) {
            parentPosition->clear();
        } else if ((*monitor)->logicalBox() != parentPosition->appliedBox) {
            // Route the new logical point through normal hit testing and pointer focus.
            // No press/release is synthesized, and no new physical motion is required.
            parentPosition->dispatching = true;
            CScopeGuard finish([parentPosition] { parentPosition->dispatching = false; });
            const auto point = *parentPosition->normalized.point;
            g_pInputManager->onMouseWarp(IPointer::SMotionAbsoluteEvent{
                .timeMs = Time::millis(Time::steadyNow()), .absolute = {point.x,point.y}, .device = device,
            });
        }
    }
    m_pointerPos = closestValid(m_pointerPos);
    updateCursorBackend();
    recheckEnteredOutputs();

    damageIfSoftware();
}
void CPointerManager::detachPointer(SP<IPointer> pointer) {
    const auto position = parentPositionFor(this);
    if (position->device.expired() || position->device == pointer) position->clear();
    std::erase_if(m_pointerListeners, [pointer](const auto& e) { return e->pointer.expired() || e->pointer == pointer; });
}
void CPointerManager::dispatch(const Aquamarine::IPointer::SWarpEvent& event, WP<IPointer> weak) {
    const auto parentPosition = parentPositionFor(this);
    static const bool dpmsEnabled = false;
    const auto PMOUSEDPMS = &dpmsEnabled;
    
            const auto device = weak.lock();
            const auto output = event.output.lock();
            const auto source = device ? device->aq() : nullptr;
                if (!device || !output || !source || Aquamarine::parentPointerInputStatus(source.get(),output.get()) != Aquamarine::ParentInputStatus::Ready ||
                !parentPosition->normalized.remember(event.absolute.x,event.absolute.y)) {
                parentPosition->clear(); return;
            }
            parentPosition->device = device;
            parentPosition->output = output;
            parentPosition->dispatching = true;
            CScopeGuard finish([parentPosition] { parentPosition->dispatching = false; });
            g_pInputManager->onMouseWarp(IPointer::SMotionAbsoluteEvent{
                .timeMs = event.timeMs, .absolute = event.absolute, .device = device,
            });
            PROTO::idle->onActivity();
            if (!g_pCompositor->m_dpmsStateOn && *PMOUSEDPMS)
                Config::Actions::dpms(Config::Actions::TOGGLE_ACTION_ENABLE, std::nullopt);
        
}
void InputManager::onMouseWarp(const IPointer::SMotionAbsoluteEvent& event) {
    manager->warpAbsolute(event.absolute, event.device);
    if (parentPositionFor(manager)->normalized.point) ++warps;
}
struct Expected {
    const char* kind; int output,x,y,anchor,nx,ny,px,py,warps; bool forwarded;
};
struct Trace { const char* name; std::vector<Expected> states; };
#include "traces.inc"
int main() {
    int states = 0;
    for (const auto& trace : TRACES) {
        CPointerManager mgr; manager = &mgr; input.warps = 0;
        parentPositions[manager] = std::make_shared<ParentPointerPosition>();
        auto backend = std::make_shared<Aquamarine::CWaylandBackend>();
        auto pointer = std::make_shared<Aquamarine::CWaylandPointer>(); pointer->backend = backend;
        auto device = std::make_shared<IPointer>(); device->source = pointer;
        mgr.m_pointerListeners.push_back(std::make_shared<CPointerManager::Listener>(CPointerManager::Listener{device}));
        std::vector<SP<Aquamarine::CWaylandOutput>> outputs(3);
        monitorStateObject.values.clear();
        for (int o : {1, 2}) {
            outputs[o] = std::make_shared<Aquamarine::CWaylandOutput>();
            auto& lifecycle = outputs[o]->lifecycle;
            lifecycle.stageSize(800, 600); lifecycle.acknowledge(); lifecycle.announce();
            lifecycle.presentation.queueCommit(1, 800, 600);
            auto monitor = std::make_shared<Monitor>(); monitor->m_output = outputs[o];
            monitor->m_position = {o == 1 ? 0.0 : 1000.0, 0};
            monitor->m_size = {o == 1 ? 800.0 : 400.0, o == 1 ? 600.0 : 300.0};
            monitorStateObject.values.push_back(monitor);
        }
        backend->focusedOutput = outputs[1];
        for (const auto& expected : trace.states) {
            const std::string kind = expected.kind;
            const int o = expected.output, x = expected.x, y = expected.y;
            if (kind == "focus") { if (backend) backend->focusedOutput = o ? outputs[o] : nullptr; }
            else if (kind == "stage") outputs[o]->lifecycle.stageSize(800, 600);
            else if (kind == "ack") outputs[o]->lifecycle.acknowledge();
            else if (kind == "commit") outputs[o]->lifecycle.presentation.queueCommit(x, 800, 600);
            else if (kind == "retire") outputs[o]->lifecycle.destroy();
            else if (kind == "deviceLost") { device.reset(); mgr.detachPointer(nullptr); }
            else if (kind == "backendLost") backend.reset();
            else if (kind == "supersede") mgr.warpTo({double(x), double(y)});
            else if (kind == "flag") { auto m = monitorStateObject.values[o-1]; m->mirror = x; m->m_enabled = y; }
            else if (kind == "layout") {
                auto m = monitorStateObject.values[o-1]; m->m_position = {double(y), 0}; m->m_size = {double(x), x*0.75};
                mgr.onMonitorLayoutChange();
            } else if (kind == "motion") mgr.dispatch({0, {x/4.0, y/4.0}, SP<Aquamarine::IOutput>(outputs[o])}, device);
            else if (kind != "noop") return 3;
            const auto position = parentPositionFor(&mgr);
            int anchor = 0;
            for (int candidate : {1, 2}) if (position->output.lock() == outputs[candidate] && position->normalized.point) anchor = candidate;
            const bool forwarded = expected.forwarded;
            const bool coordinates = (!forwarded && kind != "supersede") ||
                (mgr.m_pointerPos.x == double(expected.px) && mgr.m_pointerPos.y == double(expected.py));
            if (anchor != expected.anchor || input.warps != expected.warps || !coordinates ||
                (anchor && (position->normalized.point->x != double(expected.nx)/4 || position->normalized.point->y != double(expected.ny)/4))) {
                std::cerr << trace.name << " state " << states << " kind " << kind
                          << " actual anchor/warps/xy " << anchor << '/' << input.warps << '/' << mgr.m_pointerPos.x << '/' << mgr.m_pointerPos.y
                          << " expected anchor/warps/xy " << expected.anchor << '/' << expected.warps << '/' << expected.px << '/' << expected.py << '\n'; return 1;
            }
            ++states;
        }
        parentPositions.erase(&mgr);
    }
    std::cout << "states: " << states << '\n';
}
