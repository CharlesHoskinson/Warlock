module fixture_completion_test {
 import fixture_completion.* from "./fixture_completion"
 action check(p:bool):bool=all{assert(p),s'=s}
 action returns:bool=fire(NativeReturn(s.receipt)).then(fire(NativeReturn(s.receipt))).then(fire(NativeReturn(s.receipt)))
 run emptyPendingCounterexampleTest=init.then(fire(Context(1))).then(check(not(s.pending) and s.current and not(complete(s))))
 run actualCorrectedWaitRejectsPartialPreparationTest=init.then(fire(Context(1))).then(fire(Observe)).then(check(not(s.observed)))
 run allThreeNativeReturnsStillNeedCleanupTest=init.then(fire(Context(1))).then(returns).then(fire(Observe)).then(check(not(s.observed)))
 run latestCleanupIsFullInverseTest=init.then(fire(Context(1))).then(returns).then(fire(Cleanup(1))).then(fire(Observe)).then(check(s.observed and complete(s)))
 run oldContextCannotCompleteNewReceiptTest=init.then(fire(Reserve)).then(fire(Context(1))).then(fire(Observe)).then(check(s.pending and not(s.observed)))
 run oldCleanupCannotCompleteNewReceiptTest=init.then(fire(Context(1))).then(returns).then(fire(Cleanup(1))).then(fire(Reserve)).then(fire(Cleanup(1))).then(fire(Observe)).then(check(not(s.observed) and s.current))
 run partialNativeResultsCannotPublishCleanupTest=init.then(fire(Context(1))).then(fire(NativeReturn(1))).then(fire(Cleanup(1))).then(fire(Observe)).then(check(not(s.observed) and not(s.cleanupAck)))
}
