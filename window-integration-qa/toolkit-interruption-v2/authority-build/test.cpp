
#include <cassert>
#include <cstdint>
#include <memory>
#include <optional>
#include <stdexcept>
#include <iostream>
template<class T>using SP=std::shared_ptr<T>;
template<class T>using WP=std::weak_ptr<T>;
struct Owner{uint64_t m_stableID;};
using PHLWINDOWREF=WP<Owner>;
struct CBox{double x=0,y=0,w=0,h=0;};
enum eMouseBindMode{MBIND_INVALID,MBIND_MOVE,MBIND_RESIZE};
constexpr uint32_t BTN_LEFT=272;
namespace Layout{struct ITarget{SP<Owner> owner;SP<Owner> window(){return owner;}};}
struct Controller{SP<Layout::ITarget> current;SP<Layout::ITarget> target(){return current;}};
bool keepCurrentGeometry=false;
uint32_t releasedButton=BTN_LEFT;
struct Manager{
 std::unique_ptr<Controller> c=std::make_unique<Controller>();int ends=0;bool keepObserved=false;bool throws=false;
 const std::unique_ptr<Controller>& dragController(){return c;}
 void endDragTarget(){++ends;keepObserved=keepCurrentGeometry;if(throws)throw std::runtime_error("core end failed");c->current.reset();}
};
auto g_layoutManager=std::make_unique<Manager>();
struct GestureCapture {
    PHLWINDOWREF owner;
    WP<Layout::ITarget> target;
    uint64_t stableID = 0;
    CBox origin;
    eMouseBindMode mode = MBIND_INVALID;
    uint32_t button = BTN_LEFT;
};
std::optional<GestureCapture> gesture;
bool sameGesture(const SP<Layout::ITarget>& target) {
    if (!gesture || !target || gesture->target.lock() != target)
        return false;
    const auto owner = gesture->owner.lock();
    return owner && target->window() == owner && owner->m_stableID == gesture->stableID;
}
void retireCapturedGesture(bool keepGeometry = false) {
    const auto& controller = g_layoutManager->dragController();
    if (sameGesture(controller->target())) {
        releasedButton = 0;
        const bool previous = keepCurrentGeometry;
        keepCurrentGeometry = keepGeometry;
        try {
            g_layoutManager->endDragTarget();
        } catch (...) {
            keepCurrentGeometry = previous;
            throw;
        }
        keepCurrentGeometry = previous;
    }
    gesture.reset();
}
int main(){
 auto owner=std::make_shared<Owner>(Owner{11});
 auto target=std::make_shared<Layout::ITarget>(Layout::ITarget{owner});
 auto bind=[&]{gesture=GestureCapture{owner,target,11,{},MBIND_MOVE,BTN_LEFT};g_layoutManager->c->current=target;};
 bind();assert(sameGesture(target));
 assert(!sameGesture(nullptr));
 auto other=std::make_shared<Layout::ITarget>(Layout::ITarget{owner});assert(!sameGesture(other));
 auto replacement=std::make_shared<Owner>(Owner{11});target->owner=replacement;assert(!sameGesture(target));target->owner=owner;
 owner->m_stableID=12;assert(!sameGesture(target));owner->m_stableID=11;
 bind();retireCapturedGesture();assert(g_layoutManager->ends==1&&!g_layoutManager->keepObserved&&!gesture&&!g_layoutManager->c->current&&releasedButton==0);
 bind();retireCapturedGesture(true);assert(g_layoutManager->ends==2&&g_layoutManager->keepObserved&&!keepCurrentGeometry);
 bind();g_layoutManager->c->current=other;retireCapturedGesture();assert(g_layoutManager->ends==2&&g_layoutManager->c->current==other&&!gesture);
 bind();g_layoutManager->throws=true;try{retireCapturedGesture(true);assert(false);}catch(const std::runtime_error&){}assert(!keepCurrentGeometry&&gesture&&g_layoutManager->c->current==target);g_layoutManager->throws=false;
 bind();target->owner.reset();owner.reset();assert(!sameGesture(target));retireCapturedGesture();assert(g_layoutManager->ends==3&&g_layoutManager->c->current==target);
 // Capture a weak target then destroy that target: no replacement adoption.
 gesture.reset();target.reset();g_layoutManager->c->current.reset();assert(!sameGesture(other));
 std::cout<<"11 exact-function authority cases PASS\n";
}
