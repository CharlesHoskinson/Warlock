module preseed_completion_test {
 import preseed_completion.* from "./preseed_completion"
 action check(v:bool):bool=all{assert(v),s'=s}
 run genuineOldCueBeforeFinallyTest=init.then(fire(Reject)).then(check(oldReady(s)and s.removed==0 and not(ready(s))))
 run newPredicateWaitsForLocalReleaseTest=init.then(fire(Reject)).then(fire(CheckTerminal)).then(check(not(s.accepted)and not(s.timedOut)))
 run actualCompleteBeforeSameDeadlineTest=init.then(fire(Reject)).then(fire(EnterFinally)).then(fire(Tick(2))).then(fire(ReleaseLocal)).then(fire(CheckTerminal)).then(check(s.accepted and allProps))
 run releaseWithoutLogicalFailureNotAcceptedTest=init.then(fire(EnterFinally)).then(fire(ReleaseLocal)).then(fire(CheckTerminal)).then(check(not(s.accepted)))
 run originalThreeSecondExpiryRefusesTest=init.then(fire(Reject)).then(fire(EnterFinally)).then(fire(Tick(3))).then(fire(CheckTerminal)).then(check(s.timedOut and not(s.accepted)))
 run noLateCompletionAfterTimeoutTest=init.then(fire(Reject)).then(fire(EnterFinally)).then(fire(Tick(3))).then(fire(CheckTerminal)).then(fire(ReleaseLocal)).then(fire(CheckTerminal)).then(check(s.timedOut and not(s.accepted)))
 run fullCleanupCueStillRequiresZeroSeedAndExactFailureTest=init.then(fire(Reject)).then(fire(EnterFinally)).then(fire(ReleaseLocal)).then(fire(CheckTerminal)).then(check(s.deadlineFailure and not(s.seed)and s.created==s.removed and allProps))
 run noResetOnRepeatedPollTest=init.then(fire(Reject)).then(fire(Tick(2))).then(fire(CheckTerminal)).then(fire(Tick(1))).then(fire(CheckTerminal)).then(check(s.timedOut and s.now==3))
}
