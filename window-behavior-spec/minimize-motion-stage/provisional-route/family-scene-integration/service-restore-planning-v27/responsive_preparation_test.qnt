module responsive_preparation_test {
 import responsive_preparation.* from "./responsive_preparation"
 action check(p:bool):bool=all{assert(p),s'=s}
 run blockedObservationDoesNotBlockReceiptTest=init.then(fire(Reserve(1))).then(fire(BeginObserve(1))).then(fire(Reserve(2))).then(check(s.latest==2 and s.retarget==2 and s.observing.contains(1)))
 run obsoleteObservationCannotPromoteTest=init.then(fire(Reserve(1))).then(fire(BeginObserve(1))).then(fire(Reserve(2))).then(fire(FinishObserve(1))).then(fire(Promote(1))).then(check(s.validated==0))
 run obsoleteObservationCannotWriteDestinationTest=init.then(fire(Reserve(1))).then(fire(BeginObserve(1))).then(fire(Reserve(2))).then(fire(FinishObserve(1))).then(fire(BeginEffect(1))).then(check(not(s.write)))
 run currentObservationMayPromoteTest=init.then(fire(Reserve(1))).then(fire(BeginObserve(1))).then(fire(FinishObserve(1))).then(fire(Promote(1))).then(check(s.validated==1 and allProps))
 run nativeBatchKeepsAtomicReceiptExclusionTest=init.then(fire(Reserve(1))).then(fire(BeginObserve(1))).then(fire(FinishObserve(1))).then(fire(BeginEffect(1))).then(fire(Reserve(2))).then(check(s.latest==1)).then(fire(FinishEffect)).then(fire(Reserve(2))).then(check(s.latest==2))
 run freshReceiptRevokesOldEndpointTest=init.then(fire(Reserve(1))).then(fire(BeginObserve(1))).then(fire(FinishObserve(1))).then(fire(Promote(1))).then(fire(Reserve(2))).then(fire(Endpoint(1))).then(check(not(s.write)))
 run oldFailureCannotRevokeNewReceiptTest=init.then(fire(Reserve(1))).then(fire(Reserve(2))).then(fire(BeginObserve(2))).then(fire(FinishObserve(2))).then(fire(Promote(2))).then(fire(Fail(1))).then(check(s.validated==2))
 run threeRapidReceiptsKeepLatestVisualTest=init.then(fire(Reserve(1))).then(fire(BeginObserve(1))).then(fire(Reserve(2))).then(fire(BeginObserve(2))).then(fire(Reserve(3))).then(fire(FinishObserve(1))).then(fire(FinishObserve(2))).then(check(s.latest==3 and s.retarget==3 and s.validated==0))
}
