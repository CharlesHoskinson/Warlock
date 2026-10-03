module family_query_test {
 import family_query.* from "./family_query"
 action check(p:bool):bool=all{assert(p),s'=s}
 action collision=fire(EndpointQuery).then(fire(WatchdogLock)).then(fire(EndpointHelper)).then(fire(WatchdogQuery))
 action resolve=fire(CompleteWatchdog).then(fire(EndpointHelper)).then(fire(CompleteEndpoint))
 run retainedOldMutexCycleTest=init.then(fire(OldMutex)).then(collision).then(check(cycle))
 run correctedQueryCannotHoldFamilyWhileWaitingForManagerTest=init.then(collision).then(check(s.family==0 and not(cycle)))
 run watchdogCanFinishBeforeWaitingEndpointHelperTest=init.then(collision).then(fire(CompleteWatchdog)).then(check(s.watchdogDone and s.manager==0))
 run endpointCanFinishAfterUnchangedWatchdogDeadlineTest=init.then(collision).then(resolve).then(check(s.endpointDone and s.watchdogDone and allProps))
 run currentExactCompletedObservationRetainsEffectGuardTest=init.then(collision).then(resolve).then(fire(NativeEffect)).then(check(s.write))
 run replacedReceiptDuringReadOnlyQueryCannotWriteTest=init.then(collision).then(fire(ReplaceReceipt)).then(resolve).then(fire(NativeEffect)).then(check(not(s.write)))
 run closedOrChangedFamilyObservationCannotWriteTest=init.then(collision).then(fire(BadObservation)).then(resolve).then(fire(NativeEffect)).then(check(not(s.write)))
 run incompleteQueryCannotWriteTest=init.then(fire(EndpointQuery)).then(fire(NativeEffect)).then(check(not(s.write)))
 run oneThreadCannotOverwriteOtherEvidenceTest=init.then(fire(Evidence(1))).then(fire(Evidence(2))).then(check(s.tls0==1 and s.tls1==11 and allProps))
 run threadEvidenceTracksItsOwnCurrentObservationTest=init.then(fire(Evidence(1))).then(fire(ReplaceReceipt)).then(fire(Evidence(2))).then(check(s.tls0==1 and s.tls1==12))
 run noWholeKeeperStopOrNewEndpointNeededToResolveTest=init.then(collision).then(resolve).then(check(s.endpointDone and s.watchdogDone and s.current==1))
}
