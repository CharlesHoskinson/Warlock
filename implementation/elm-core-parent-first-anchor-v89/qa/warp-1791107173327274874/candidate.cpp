#include <cmath>
#include <functional>
#include <iostream>
#include <memory>
#include <string>
#include <vector>
#include <hyprutils/memory/SharedPtr.hpp>
#include <hyprutils/memory/WeakPtr.hpp>
#include <hyprutils/utils/ScopeGuard.hpp>
#include "ParentNormalizedPosition.hpp"
using namespace Hyprutils::Memory;
using namespace Pointer;
using namespace Hyprutils::Utils;
#define SP CSharedPointer
#define WP CWeakPointer
struct Point {double x=0,y=0;};
struct CBox{};
namespace Desktop::View {struct CWindow {};}
namespace Aquamarine {
 enum class ParentInputStatus {Ready,Inactive,Unsupported};
 struct IOutput {int id=1;};
 struct IPointer {ParentInputStatus status=ParentInputStatus::Ready;struct SWarpEvent {unsigned timeMs=1;Point absolute;WP<IOutput> output;};};
 ParentInputStatus parentPointerInputStatus(IPointer* source,IOutput*) {return source->status;}
}
struct IPointer {SP<Aquamarine::IPointer> source=makeShared<Aquamarine::IPointer>();SP<Aquamarine::IPointer> aq(){return source;}
 struct SMotionAbsoluteEvent {unsigned timeMs=1;Point absolute;SP<IPointer> device;};};
struct Compositor {bool m_isShuttingDown=false;};
Compositor compositor;Compositor* g_pCompositor=&compositor;
struct ParentPointerPosition {
    WP<IPointer> device;
    WP<Aquamarine::IOutput> output;
    ParentPolicy::NormalizedPosition normalized;
    CBox appliedBox;
    bool dispatching = false;
    bool hitTestQueued = false;
    bool surfaceHitTestPending = false;
    WP<Desktop::View::CWindow> committedWindow;
    void clear() { device = {}; output = {}; normalized.clear(); appliedBox = {}; dispatching = false; surfaceHitTestPending = false; committedWindow = {}; }
};
struct Input {Point point,last;int focus=0,warps=0,refreshes=0;bool allow=true;std::vector<std::string> order;std::function<void()> refreshCallback;
 void onMouseWarp(IPointer::SMotionAbsoluteEvent e){++warps;order.push_back("warp");point=e.absolute;if((std::floor(last.x)!=std::floor(point.x)||std::floor(last.y)!=std::floor(point.y))&&allow)focus=1;last=point;}
 void simulateMouseMovement(){++refreshes;order.push_back("refresh");if(allow)focus=1;if(refreshCallback)refreshCallback();}
};
Input input;Input* g_pInputManager=&input;
bool dispatchParentWarp(const WP<IPointer>& weak, const std::shared_ptr<ParentPointerPosition>& parentPosition,
                        const Aquamarine::IPointer::SWarpEvent& event) {
    if (!g_pCompositor || g_pCompositor->m_isShuttingDown || !g_pInputManager)
        return false;
    const auto device = weak.lock();
    const auto output = event.output.lock();
    const auto source = device ? device->aq() : nullptr;
    if (!device || !output || !source || Aquamarine::parentPointerInputStatus(source.get(), output.get()) != Aquamarine::ParentInputStatus::Ready ||
        !parentPosition->normalized.remember(event.absolute.x,event.absolute.y)) {
        parentPosition->clear(); return false;
    }
    const bool newSource = parentPosition->device != device || parentPosition->output != output;
    parentPosition->device = device;
    parentPosition->output = output;
    parentPosition->dispatching = true;
    CScopeGuard finish([parentPosition] { parentPosition->dispatching = false; });
    g_pInputManager->onMouseWarp(IPointer::SMotionAbsoluteEvent{
        .timeMs = event.timeMs, .absolute = event.absolute, .device = device,
    });
    // A replacement parent device can enter at the same floored point. Normal
    // mouseMoveUnified() deduplicates that coordinate after capability loss;
    // refresh ordinary hit testing once for this new live device/output anchor.
    if (newSource)
        g_pInputManager->simulateMouseMovement();
    return true;
}
struct Fixture {SP<IPointer> device=makeShared<IPointer>();SP<Aquamarine::IOutput> output=makeShared<Aquamarine::IOutput>();std::shared_ptr<ParentPointerPosition> position=std::make_shared<ParentPointerPosition>();
 Fixture(){input=Input{};compositor=Compositor{};g_pCompositor=&compositor;g_pInputManager=&input;}
 bool warp(double x=.5,double y=.5){return dispatchParentWarp(WP<IPointer>(device),position,{.timeMs=1,.absolute={x,y},.output=output});}
};
int checks=0;void check(bool ok,const char* name){++checks;if(!ok){std::cerr<<"FAIL "<<name<<'\n';std::exit(1);}}
int main(){
 {Fixture f;input.last={.5,.5};check(f.warp(),"first admitted");check(input.focus==1,"stationary first source gets focus");check(input.order==std::vector<std::string>{"warp","refresh"},"warp precedes ordinary refresh");check(!f.position->dispatching,"dispatch guard settles");}
 {Fixture f;f.warp();input.focus=2;int n=input.refreshes;f.warp();check(input.focus==2,"ordinary same source preserves programmatic focus");check(input.refreshes==n,"ordinary same source no extra refresh");}
 {Fixture f;f.warp();input.focus=0;auto old=f.device;f.device=makeShared<IPointer>();f.warp();check(input.focus==1,"replacement retained old source gets focus at same point");check(input.refreshes==2,"replacement refresh exactly once");}
 {Fixture f;f.warp();input.focus=0;f.position->clear();f.device=makeShared<IPointer>();f.warp();check(input.focus==1,"retired source replacement stationary focus");}
 {Fixture f;f.warp();input.focus=0;f.output=makeShared<Aquamarine::IOutput>();f.warp();check(input.focus==1,"changed owning output stationary focus");}
 {Fixture f;f.device.reset();check(!f.warp(),"dead device refused");check(input.warps==0&&input.refreshes==0,"dead device no dispatch");}
 {Fixture f;f.output.reset();check(!f.warp(),"dead output refused");check(input.warps==0,"dead output no warp");}
 {Fixture f;f.device->source.reset();check(!f.warp(),"missing AQ source refused");}
 {Fixture f;f.device->source->status=Aquamarine::ParentInputStatus::Inactive;check(!f.warp(),"inactive parent refused");check(input.warps==0&&input.refreshes==0,"inactive no native routing");}
 {Fixture f;check(!f.warp(NAN,.5),"nonfinite refused");check(!f.position->normalized.point&&input.refreshes==0,"bad point clears anchor");}
 {Fixture f;compositor.m_isShuttingDown=true;check(!f.warp(),"shutdown refused");}
 {Fixture f;g_pCompositor=nullptr;check(!f.warp(),"missing compositor refused");}
 {Fixture f;g_pInputManager=nullptr;check(!f.warp(),"missing input manager refused");}
 {Fixture f;input.allow=false;input.focus=2;f.warp();check(input.focus==2&&input.refreshes==1,"ordinary policy/grab retained by refresh");}
 {Fixture f;input.refreshCallback=[&]{f.position->clear();};f.warp();check(!f.position->normalized.point&&!f.position->dispatching,"reentrant retirement not resurrected");}
 std::cout<<"checks: "<<checks<<'\n';
}
