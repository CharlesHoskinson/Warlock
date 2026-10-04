#include <memory>
#include <iostream>
#include <cstdlib>
#include "NestedLifecycle.hpp"
#include <aquamarine/input/ParentInput.hpp>
namespace Aquamarine {
struct IOutput { virtual ~IOutput() = default; };
struct IPointer { virtual ~IPointer() = default; };
struct CWaylandOutput : IOutput { NestedPolicy::ConfigureLifecycle lifecycle; };
struct CWaylandBackend { std::weak_ptr<CWaylandOutput> focusedOutput; };
struct CWaylandPointer : IPointer {
    std::weak_ptr<CWaylandBackend> backend;
    bool inputAllowedOn(const IOutput* output) const;
};
}
using namespace Aquamarine;
static bool mappingReady(CWaylandOutput* output) { return output->lifecycle.presentation.inputAllowed(); }
Aquamarine::ParentInputStatus Aquamarine::parentPointerInputStatus(const IPointer* pointer, const IOutput* output) {
    const auto parentPointer = dynamic_cast<const CWaylandPointer*>(pointer);
    if (!parentPointer) return ParentInputStatus::Unsupported;
    return parentPointer->inputAllowedOn(output) ? ParentInputStatus::Ready : ParentInputStatus::Inactive;
}

bool Aquamarine::CWaylandPointer::inputAllowedOn(const IOutput* output) const {
    const auto parent = backend.lock();
    if (!parent || !output) return false;
    const auto focused = parent->focusedOutput.lock();
    return focused && focused.get() == output && mappingReady(focused.get());
}


static int checks=0;
static void check(bool value) { if(!value){std::cerr<<"failed "<<checks+1<<'\n';std::exit(1);} ++checks; }
int main() {
    auto backend=std::make_shared<CWaylandBackend>();
    auto a=std::make_shared<CWaylandOutput>(), b=std::make_shared<CWaylandOutput>();
    CWaylandPointer p; p.backend=backend;
    IPointer foreign;
    check(parentPointerInputStatus(nullptr,a.get())==ParentInputStatus::Unsupported);
    check(parentPointerInputStatus(&foreign,a.get())==ParentInputStatus::Unsupported);
    check(parentPointerInputStatus(&p,nullptr)==ParentInputStatus::Inactive);
    check(!p.inputAllowedOn(a.get()));
    backend->focusedOutput=a;
    check(!p.inputAllowedOn(a.get()));
    a->lifecycle.stageSize(800,600);check(a->lifecycle.acknowledge());check(a->lifecycle.announce());
    check(!p.inputAllowedOn(a.get()));
    check(a->lifecycle.presentation.queueCommit(a->lifecycle.presentation.acked.generation,800,600));
    check(p.inputAllowedOn(a.get()));
    check(parentPointerInputStatus(&p,a.get())==ParentInputStatus::Ready);
    check(!p.inputAllowedOn(b.get()));
    backend->focusedOutput=b;check(!p.inputAllowedOn(a.get()));
    backend->focusedOutput.reset();check(!p.inputAllowedOn(a.get()));
    backend->focusedOutput=a;
    a->lifecycle.stageSize(640,480);check(!p.inputAllowedOn(a.get()));
    check(a->lifecycle.acknowledge());check(!p.inputAllowedOn(a.get()));
    check(a->lifecycle.presentation.queueCommit(a->lifecycle.presentation.acked.generation,640,480));check(p.inputAllowedOn(a.get()));
    a->lifecycle.destroy();check(!p.inputAllowedOn(a.get()));
    b->lifecycle.stageSize(800,600);check(b->lifecycle.acknowledge());check(b->lifecycle.announce());
    check(b->lifecycle.presentation.queueCommit(b->lifecycle.presentation.acked.generation,800,600));
    backend->focusedOutput=b;check(p.inputAllowedOn(b.get()));
    backend.reset();check(!p.inputAllowedOn(b.get()));
    std::cout<<"checks: "<<checks<<'\n';
}
