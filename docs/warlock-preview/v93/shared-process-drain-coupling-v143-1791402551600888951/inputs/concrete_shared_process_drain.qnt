module concrete_shared_process_drain {
 import shared_process_drain.* from "./shared_process_drain"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run actualLegacyPrematureRecovery=init.then(fire(Signal)).then(check(not(safe(earlyRecovery(s)))))
 run actualProcessSignalsPreserveKnownDuties=init.then(fire(Signal)).then(fire(Signal)).then(check(s.failed and s.processFailed and s.closing and s.owned and not(s.recovery)))
 run actualOriginalStrictNativeClose=init.then(fire(Signal)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(check(s.failed and s.closed and not(s.owned or s.recovery)))
 run actualGTKRecoveryOnlyAfterClose=init.then(fire(Signal)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Recovery)).then(check(s.failed and s.closed and s.recovery and not(s.owned)))
 run actualFailureExitAfterRecovery=init.then(fire(Signal)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Recovery)).then(fire(Exit)).then(check(s.failed and s.closed and s.recovery and s.exited))
 run actualNoOriginalIdentityReset=init.then(fire(Signal)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Recovery)).then(check(s.policy==1 and s.epoch==1 and s.navigation==1 and s.snapshot==1))
}
