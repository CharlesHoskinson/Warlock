module shared_process_drain_tests {
 import shared_process_drain.* from "./shared_process_drain"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run originalEarlyRecoveryUnsafe=init.then(fire(Signal)).then(check(not(safe(earlyRecovery(s)))))
 run processSignalRetainsNativeCustody=init.then(fire(Signal)).then(fire(Recovery)).then(check(s.processFailed and s.failed and s.closing and s.owned and not(s.recovery)))
 run deliveryErrorCannotExitKnownCustody=init.then(fire(DeliveryError)).then(fire(Exit)).then(check(s.failed and s.owned and not(s.processFailed or s.exited)))
 run strictClosePrecedesGTKRecovery=init.then(fire(Signal)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Recovery)).then(check(s.closed and s.recovery and not(s.owned)))
 run duplicateSignalsDoNotCancelDrain=init.then(fire(Signal)).then(fire(DeliveryError)).then(fire(Signal)).then(fire(LaterIntent)).then(check(s.failed and s.processFailed and s.closing and s.owned))
 run unknownPreventsRecoveryOrExit=init.then(fire(Signal)).then(fire(Unknown)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Recovery)).then(fire(Exit)).then(check(s.unknown and s.owned and not(s.closed or s.recovery or s.exited)))
 run knownFailureOutcomeRetained=init.then(fire(Signal)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Recovery)).then(fire(Exit)).then(check(s.failed and s.processFailed and s.closed and s.exited))
 run noPolicyGrantOrClockReset=init.then(fire(DeliveryError)).then(fire(Signal)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Recovery)).then(check(s.policy==1 and s.epoch==1 and s.navigation==1 and s.snapshot==1))
 run staleEventDoesNotSettle=init.then(fire(Signal)).then(fire(OldEvent)).then(fire(StrictRetire)).then(check(s.owned and not(s.closed)))
}
