module current_failure_drain_tests {
 import current_failure_drain.* from "./current_failure_drain"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run originalEarlyExitLeavesCustody=init.then(fire(Fault)).then(check(not(safe(earlyExit(s)))))
 run currentFailureRetainsCustody=init.then(fire(Fault)).then(fire(Exit)).then(check(s.failed and s.closing and s.owned and not(s.exited)))
 run nativeReceiptsPrecedeStrictCloseAndExit=init.then(fire(Fault)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Exit)).then(check(s.failed and s.closed and s.exited and not(s.owned)))
 run laterIntentCannotCancelFailure=init.then(fire(Fault)).then(fire(LaterIntent)).then(check(s.failed and s.closing and s.owned))
 run rendererDisposalCannotSettle=init.then(fire(Fault)).then(fire(StaleError)).then(fire(StrictRetire)).then(fire(Exit)).then(check(s.owned and not(s.closed or s.exited)))
 run unknownNeverNormalExit=init.then(fire(Unknown)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Exit)).then(check(s.failed and s.unknown and s.owned and not(s.closed or s.exited)))
 run staleOldErrorDoesNotFailCurrent=init.then(fire(StaleError)).then(check(not(s.failed) and s.owned))
 run noGrantOrPolicyReset=init.then(fire(Fault)).then(fire(LaterIntent)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Exit)).then(check(s.epoch==1 and s.policy==1 and s.failed))
}
