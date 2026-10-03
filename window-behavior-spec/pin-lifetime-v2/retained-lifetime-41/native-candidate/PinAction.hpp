#pragma once
#include <cstdint>
#include <string>
#include <exception>

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
};
struct Result {bool ok=false;std::string reason,level,code;};
struct Report {
    Phase phase=Phase::Validate;
    Snapshot before,after;
    bool desired=false,ok=false,actionsInvoked=false;
    std::string reason;
    Result backend;
};
inline bool eligible(const Snapshot&s) {return s.live&&s.normal&&!s.fullscreen;}
inline bool same(const Snapshot&a,const Snapshot&b) {
    return a.address==b.address&&a.stable==b.stable&&a.pid==b.pid&&a.epoch==b.epoch&&a.lifetime==b.lifetime&&a.session==b.session&&a.incarnation==b.incarnation;
}
template<typename Adapter> Report execute(Adapter& adapter) {
    Report r;r.before=adapter.snapshot();r.after=r.before;r.desired=!r.before.pinned;
    if(!eligible(r.before)){r.reason="Captured window unavailable/minimized/fullscreen; supported maximized policy remains open";return r;}
    auto verify=[&](bool pinExpected) {
        r.after=adapter.snapshot();
        return same(r.before,r.after)&&eligible(r.after)&&r.after.floating&&r.after.pinned==pinExpected;
    };
    auto invoke=[&](auto&& action) {
        try {return action();}
        catch(const std::exception& error) {return Result{false,error.what(),"error","exception"};}
        catch(...) {return Result{false,"Unknown backend exception","error","exception"};}
    };
    if(!r.before.floating) {
        r.phase=Phase::Float;r.actionsInvoked=true;
        const auto result=invoke([&]{return adapter.floatWindow();});r.backend=result;r.after=adapter.snapshot();
        if(!result.ok){r.reason="Native float refused: "+result.reason;return r;}
    }
    if(!verify(r.before.pinned)){r.reason="Captured identity/state/intent changed during floating phase";return r;}
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
