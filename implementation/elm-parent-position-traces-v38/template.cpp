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
#include <nlohmann/json.hpp>
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
// PRODUCTION_QUERY
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
// PRODUCTION_STATE
// PRODUCTION_WARP_TO
void CPointerManager::warpAbsolute(Vector2D abs, SP<IHID> dev) {
    const auto& MONITORS = State::monitorState()->monitors();
    CBox mappedArea;
    // PRODUCTION_OUTPUT_PROJECTION
}
// PRODUCTION_LAYOUT
// PRODUCTION_DETACH
void CPointerManager::dispatch(const Aquamarine::IPointer::SWarpEvent& event, WP<IPointer> weak) {
    const auto parentPosition = parentPositionFor(this);
    static const bool dpmsEnabled = false;
    const auto PMOUSEDPMS = &dpmsEnabled;
    // PRODUCTION_DISPATCH
}
void InputManager::onMouseWarp(const IPointer::SMotionAbsoluteEvent& event) {
    manager->warpAbsolute(event.absolute, event.device);
    if (parentPositionFor(manager)->normalized.point) ++warps;
}
using json = nlohmann::json;
int main(int argc, char** argv) {
    if (argc != 2) return 2;
    std::ifstream file(argv[1]); json traces; file >> traces;
    int states = 0;
    for (const auto& trace : traces) {
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
        for (const auto& expected : trace.at("states")) {
            const auto& event = expected.at("event");
            const auto kind = event.at("kind").get<std::string>();
            const int o = event.at("output"), x = event.at("x"), y = event.at("y");
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
            const bool forwarded = expected.at("forwarded");
            const bool coordinates = (!forwarded && kind != "supersede") ||
                (mgr.m_pointerPos.x == expected.at("px").get<double>() && mgr.m_pointerPos.y == expected.at("py").get<double>());
            if (anchor != expected.at("anchor") || input.warps != expected.at("warps") || !coordinates ||
                (anchor && (position->normalized.point->x != expected.at("nx").get<double>()/4 || position->normalized.point->y != expected.at("ny").get<double>()/4))) {
                std::cerr << trace.at("name") << " state " << states << " kind " << kind
                          << " actual anchor/warps/xy " << anchor << '/' << input.warps << '/' << mgr.m_pointerPos.x << '/' << mgr.m_pointerPos.y
                          << " expected " << expected << '\n'; return 1;
            }
            ++states;
        }
        parentPositions.erase(&mgr);
    }
    std::cout << "states: " << states << '\n';
}
