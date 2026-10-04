#include "ParentPointerFocus.hpp"
#include <algorithm>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <memory>
#include <optional>
#include <unordered_map>
#include <vector>
struct CBox { int generation=1; bool operator==(const CBox&) const = default; };
struct CPointerManager {};
namespace Aquamarine {
struct IOutput {};
struct IPointer {};
enum class ParentInputStatus { Ready, Inactive };
static bool ready=true;
static ParentInputStatus parentPointerInputStatus(const IPointer*, const IOutput*) { return ready ? ParentInputStatus::Ready : ParentInputStatus::Inactive; }
}
struct IPointer {
    std::shared_ptr<Aquamarine::IPointer> source=std::make_shared<Aquamarine::IPointer>();
    auto aq() { return source; }
};
struct ParentPointerPosition {
    std::weak_ptr<IPointer> device;
    std::weak_ptr<Aquamarine::IOutput> output;
    struct { std::optional<int> point=1; } normalized;
    CBox appliedBox;
    bool dispatching=false, hitTestQueued=false;
};
static std::unordered_map<CPointerManager*, std::shared_ptr<ParentPointerPosition>> positions;
static auto parentPositionFor(CPointerManager* manager) {
    auto& p=positions[manager]; if(!p) p=std::make_shared<ParentPointerPosition>();return p;
}
namespace Pointer {
static std::unique_ptr<CPointerManager> singleton=std::make_unique<CPointerManager>();
static auto& mgr() { return singleton; }
}
struct Monitor {
    bool m_enabled=true, mirror=false;
    std::shared_ptr<Aquamarine::IOutput> m_output;
    CBox box;
    bool isMirror() { return mirror; }
    CBox logicalBox() { return box; }
};
namespace State {
struct MonitorState {
    std::vector<std::shared_ptr<Monitor>> list;
    auto& monitors() { return list; }
};
static MonitorState singleton;
static auto* monitorState() { return &singleton; }
}
struct Compositor { bool m_isShuttingDown=false; };
static Compositor compositor;
static Compositor* g_pCompositor=&compositor;
struct InputManager {
    int repicks=0;
    bool windowsMoved=false, focused=false;
    void simulateMouseMovement() { ++repicks;focused=windowsMoved; }
};
static InputManager input;
static InputManager* g_pInputManager=&input;
struct EventLoop {
    std::vector<std::function<void()>> tasks;
    void doLater(std::function<void()> fn) { tasks.push_back(fn); }
    void drain() { auto copy=std::move(tasks);tasks.clear();for(auto& fn:copy)fn(); }
};
static EventLoop loop;
static EventLoop* g_pEventLoopManager=&loop;
void scheduleParentHitTest(CPointerManager* manager) {
    const auto position = parentPositionFor(manager);
    if (!g_pEventLoopManager || !position->normalized.point || position->hitTestQueued)
        return;
    position->hitTestQueued = true;
    const std::weak_ptr<ParentPointerPosition> weak = position;
    g_pEventLoopManager->doLater([weak] {
        const auto position = weak.lock();
        if (!position) return;
        position->hitTestQueued = false;
        if (!g_pCompositor || g_pCompositor->m_isShuttingDown || !g_pInputManager ||
            !position->normalized.point || position->dispatching)
            return;
        auto& manager = Pointer::mgr();
        if (!manager || parentPositionFor(manager.get()) != position)
            return;
        const auto device = position->device.lock();
        const auto output = position->output.lock();
        const auto source = device ? device->aq() : nullptr;
        if (!device || !output || !source || Aquamarine::parentPointerInputStatus(source.get(), output.get()) != Aquamarine::ParentInputStatus::Ready)
            return;
        const auto& monitors = State::monitorState()->monitors();
        const auto monitor = std::ranges::find_if(monitors, [output](const auto& m) {
            return m->m_enabled && !m->isMirror() && m->m_output == output;
        });
        if (monitor == monitors.end())
            return;
        // Monitor layout listeners also move workspace surfaces. Pick the live
        // surface after that dispatch completes, even if cursor pixels did not
        // change. No stored coordinate, raw owner, or button is queued here.
        g_pInputManager->simulateMouseMovement();
    });
}
void Pointer::refreshParentHitTest() {
    if (!g_pCompositor || g_pCompositor->m_isShuttingDown)
        return;
    const auto& manager = Pointer::mgr();
    if (manager)
        scheduleParentHitTest(manager.get());
}
static int checks=0;
static void check(bool value) { ++checks;if(!value){std::cerr<<"failed "<<checks<<'\n';std::exit(1);} }
int main() {
    auto device=std::make_shared<IPointer>();auto output=std::make_shared<Aquamarine::IOutput>();
    auto monitor=std::make_shared<Monitor>();monitor->m_output=output;State::singleton.list={monitor};
    auto position=parentPositionFor(Pointer::mgr().get());position->device=device;position->output=output;
    auto schedule=[&]{scheduleParentHitTest(Pointer::mgr().get());};
    // The synchronous picker ran before surfaces moved. The deferred picker
    // must repair it without changing the already-correct pointer coordinate.
    schedule();schedule();check(loop.tasks.size()==1 && position->hitTestQueued);
    input.windowsMoved=true;loop.drain();check(input.focused && input.repicks==1 && !position->hitTestQueued);
    schedule();position->normalized.point.reset();loop.drain();check(input.repicks==1);
    position->normalized.point=1;schedule();Aquamarine::ready=false;loop.drain();check(input.repicks==1);Aquamarine::ready=true;
    schedule();device.reset();loop.drain();check(input.repicks==1);
    device=std::make_shared<IPointer>();position->device=device;
    schedule();position->output.reset();loop.drain();check(input.repicks==1);position->output=output;
    schedule();State::singleton.list.clear();loop.drain();check(input.repicks==1);State::singleton.list={monitor};
    schedule();monitor->m_enabled=false;loop.drain();check(input.repicks==1);monitor->m_enabled=true;
    schedule();monitor->mirror=true;loop.drain();check(input.repicks==1);monitor->mirror=false;
    schedule();monitor->box.generation=2;loop.drain();check(input.repicks==1);monitor->box.generation=1;
    schedule();device->source.reset();loop.drain();check(input.repicks==1);device->source=std::make_shared<Aquamarine::IPointer>();
    schedule();g_pCompositor=nullptr;loop.drain();check(input.repicks==1);g_pCompositor=&compositor;
    schedule();compositor.m_isShuttingDown=true;loop.drain();check(input.repicks==1);compositor.m_isShuttingDown=false;
    schedule();g_pInputManager=nullptr;loop.drain();check(input.repicks==1);g_pInputManager=&input;
    schedule();position->dispatching=true;loop.drain();check(input.repicks==1);position->dispatching=false;
    schedule();auto old=std::move(Pointer::mgr());Pointer::mgr()=std::make_unique<CPointerManager>();
    loop.drain();check(input.repicks==1);Pointer::mgr()=std::move(old);
    schedule();positions[Pointer::mgr().get()]=std::make_shared<ParentPointerPosition>();
    loop.drain();check(input.repicks==1);positions[Pointer::mgr().get()]=position;
    g_pEventLoopManager=nullptr;schedule();check(loop.tasks.empty() && !position->hitTestQueued);g_pEventLoopManager=&loop;
    position->normalized.point.reset();schedule();check(loop.tasks.empty());position->normalized.point=1;
    schedule();position->normalized.point.reset();position->normalized.point=2;
    loop.drain();check(input.repicks==2 && input.focused); // live latest anchor, no stored old coordinate
    schedule();position.reset();positions.clear();loop.drain();check(input.repicks==2); // expired queued owner
    position=parentPositionFor(Pointer::mgr().get());position->device=device;position->output=output;
    input.windowsMoved=false;input.focused=false;
    schedule();loop.drain();check(input.repicks==3 && !input.focused);
    input.windowsMoved=true;Pointer::refreshParentHitTest();Pointer::refreshParentHitTest();check(loop.tasks.size()==1);
    loop.drain();check(input.repicks==4 && input.focused);
    std::cout<<"checks: "<<checks<<'\n';
}
