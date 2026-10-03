#pragma once
#include <cstdint>
#include <string>
#include <exception>
#include <array>
#include <cmath>

// Pure transaction policy. The native adapter retains the strong owner and
// calls only owning core actions; CPU tests inject synchronous callback faults.
namespace PinAction {
enum class Phase {Validate,Float,Pin,Raise,Complete};
struct Snapshot {
    uintptr_t address=0;
    uint64_t stable=0,epoch=0,lifetime=0;
    std::string session,incarnation;
    int pid=0;
    bool live=false,normal=false,floating=false,pinned=false,fullscreen=false;
    int internalMode=0,clientMode=0;
    uint32_t capability=0;
    bool ownedUnpinReady=false,nativeAdmission=false,restoreKnown=false,restoreOrigin=false,restoreManaged=false,restoreFloating=false,layoutHandled=false;
    uint64_t restoreGeneration=0;
    uintptr_t target=0,layoutTarget=0,space=0,workspace=0,monitor=0;
    std::array<double,4> geometry{};
    std::array<double,8> restoreGeometry{};
};
struct Result {bool ok=false;std::string reason,level,code;};
struct Report {
    Phase phase=Phase::Validate;
    Snapshot before,after;
    bool desired=false,ok=false,actionsInvoked=false;
    std::string reason;
    Result backend;
};
inline bool nativePath(const Snapshot&s) {
    for (const auto value : s.geometry) if (!std::isfinite(value)) return false;
    for (const auto value : s.restoreGeometry) if (!std::isfinite(value)) return false;
    if (s.geometry[2]<=0||s.geometry[3]<=0||s.restoreGeometry[2]<=0||s.restoreGeometry[3]<=0||s.restoreFloating!=s.floating||s.fullscreen!=(s.internalMode!=0)) return false;
    return s.capability==1&&s.nativeAdmission&&s.restoreKnown&&s.restoreGeneration>0&&s.target&&s.layoutTarget&&s.space&&s.workspace&&s.monitor&&
        s.clientMode>=0&&s.clientMode<=1&&(s.internalMode==1||(s.internalMode==0&&s.restoreOrigin));
}
inline bool eligible(const Snapshot&s) {
    return s.live&&s.normal&&(!s.restoreOrigin||nativePath(s))&&s.internalMode>=0&&s.internalMode<=1&&s.clientMode>=0&&s.clientMode<=1&&
        ((!s.fullscreen&&s.internalMode==0)||nativePath(s));
}
inline bool nativeContextSame(const Snapshot&a,const Snapshot&b) {
    return a.internalMode==b.internalMode&&a.clientMode==b.clientMode&&a.fullscreen==b.fullscreen&&a.floating==b.floating&&a.capability==b.capability&&
        a.restoreKnown&&b.restoreKnown&&a.restoreGeneration==b.restoreGeneration&&a.restoreFloating==b.restoreFloating&&a.layoutHandled==b.layoutHandled&&
        a.target==b.target&&a.layoutTarget==b.layoutTarget&&a.space==b.space&&a.workspace==b.workspace&&a.monitor==b.monitor&&
        a.geometry==b.geometry&&a.restoreGeometry==b.restoreGeometry;
}
inline bool same(const Snapshot&a,const Snapshot&b) {
    return a.address==b.address&&a.stable==b.stable&&a.pid==b.pid&&a.epoch==b.epoch&&a.lifetime==b.lifetime&&a.session==b.session&&a.incarnation==b.incarnation;
}
inline bool ownedUnpinPath(const Snapshot& s) {
    return s.live&&s.normal&&s.pinned&&s.capability==1&&s.ownedUnpinReady&&s.restoreOrigin&&s.restoreManaged&&s.restoreGeneration>0&&
        s.target&&s.layoutTarget&&s.space&&s.workspace&&s.monitor;
}
inline bool intentContextSame(const Snapshot&a,const Snapshot&b) {
    return a.internalMode==b.internalMode&&a.clientMode==b.clientMode&&a.fullscreen==b.fullscreen&&a.floating==b.floating&&a.capability==b.capability&&
        a.restoreKnown==b.restoreKnown&&a.restoreGeneration==b.restoreGeneration&&a.restoreFloating==b.restoreFloating&&
        a.layoutHandled==b.layoutHandled&&a.target==b.target&&a.layoutTarget==b.layoutTarget&&a.space==b.space&&a.workspace==b.workspace&&a.monitor==b.monitor&&
        a.geometry==b.geometry&&a.restoreGeometry==b.restoreGeometry;
}
inline bool completedState(const Snapshot&before,const Snapshot&after,bool desired) {
    if (!same(before,after)||!after.live||!after.normal||after.pinned!=desired)
        return false;
    if (ownedUnpinPath(before)&&!desired)
        return intentContextSame(before,after)&&!after.restoreOrigin&&after.restoreManaged&&!after.ownedUnpinReady;
    if (nativePath(before))
        return nativeContextSame(before,after)&&after.restoreOrigin==desired&&after.restoreManaged&&
            (after.internalMode==1||desired ? after.nativeAdmission : true);
    return eligible(after)&&after.floating&&after.internalMode==before.internalMode&&after.clientMode==before.clientMode;
}
template<typename Adapter> Report execute(Adapter& adapter) {
    Report r;r.before=adapter.snapshot();r.after=r.before;r.desired=!r.before.pinned;
    if(!eligible(r.before)&&!ownedUnpinPath(r.before)){r.reason="Captured window unavailable or native mode/restore ownership unsupported";return r;}
    auto verify=[&](bool pinExpected) {
        r.after=adapter.snapshot();
        return completedState(r.before,r.after,pinExpected);
    };
    auto invoke=[&](auto&& action) {
        try {return action();}
        catch(const std::exception& error) {return Result{false,error.what(),"error","exception"};}
        catch(...) {return Result{false,"Unknown backend exception","error","exception"};}
    };
    if(!r.before.floating&&!nativePath(r.before)&&!ownedUnpinPath(r.before)) {
        r.phase=Phase::Float;r.actionsInvoked=true;
        const auto result=invoke([&]{return adapter.floatWindow();});r.backend=result;r.after=adapter.snapshot();
        if(!result.ok){r.reason="Native float refused: "+result.reason;return r;}
    }
    r.after=adapter.snapshot();
    const bool prepared = ownedUnpinPath(r.before) ? same(r.before,r.after)&&r.after.live&&r.after.normal&&r.after.ownedUnpinReady&&intentContextSame(r.before,r.after)&&
        r.after.pinned==r.before.pinned&&r.after.restoreOrigin==r.before.restoreOrigin&&r.after.restoreManaged==r.before.restoreManaged : nativePath(r.before) ? same(r.before,r.after)&&r.after.live&&r.after.normal&&r.after.nativeAdmission&&nativeContextSame(r.before,r.after)&&
        r.after.pinned==r.before.pinned&&r.after.restoreOrigin==r.before.restoreOrigin&&r.after.restoreManaged==r.before.restoreManaged :
        completedState(r.before,r.after,r.before.pinned);
    if(!prepared){r.reason="Captured identity/state/intent changed during preparation phase";return r;}
    r.phase=Phase::Pin;r.actionsInvoked=true;
    const auto pin=invoke([&]{return adapter.pinWindow(r.desired);});r.backend=pin;r.after=adapter.snapshot();
    if(!pin.ok){r.reason="Native pin refused: "+pin.reason;return r;}
    if(!verify(r.desired)){r.reason="Captured identity/state/intent changed during native pin callback";return r;}
    if(r.desired) {
        r.phase=Phase::Raise;
        const auto raise=invoke([&]{return adapter.raiseWindow();});r.backend=raise;r.after=adapter.snapshot();
        if(!raise.ok){r.reason="Pin phase reached; native raise refused: "+raise.reason;return r;}
        if(!verify(r.desired)){r.reason="Captured identity/state/intent changed during native raise callback";return r;}
    }
    r.phase=Phase::Complete;r.ok=true;return r;
}
}
