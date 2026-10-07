module concrete_current_failure_drain {
 import current_failure_drain.* from "./current_failure_drain"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run actualOriginalEarlyExitViolatesCustody=init.then(fire(Fault)).then(check(not(safe(earlyExit(s)))))
 run actualCurrentFailureQuarantinesOwnedScope=init.then(fire(Fault)).then(check(s.failed and s.closing and s.owned and not(s.exited)))
 run actualLaterNativeRetirementSettlesCustody=init.then(fire(Fault)).then(fire(NativeSettled)).then(check(s.failed and not(s.owned) and not(s.closed or s.exited)))
 run actualOriginalStrictClose=init.then(fire(Fault)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(check(s.failed and s.closed and not(s.owned or s.exited)))
 run actualFailureExitAfterStrictClose=init.then(fire(Fault)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Exit)).then(check(s.failed and s.closed and s.exited and not(s.owned)))
}
