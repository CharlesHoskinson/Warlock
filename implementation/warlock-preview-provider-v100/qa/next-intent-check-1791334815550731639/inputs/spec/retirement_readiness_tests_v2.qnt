module retirement_readiness_tests {
 import retirement_readiness.* from "./retirement_readiness_v2"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run observationDoesNotInventReadiness=init.then(fire(Observe)).then(check(s.retained and not(s.ready) and s.issued==0))
 run exactReadinessRetained=init.then(fire(Observe)).then(fire(Ready)).then(check(s.ready and s.last and s.issued==0))
 run repeatedObservationRetainsReady=init.then(fire(Observe)).then(fire(Ready)).then(fire(Observe)).then(check(s.ready and s.issued==0))
 run abandonedPreparationHasNoOrdinal=init.then(fire(Observe)).then(fire(Ready)).then(fire(Abandon)).then(check(s.ready and not(s.complete) and s.issued==0))
 run completedRecordLeavesReadyQueue=init.then(fire(Observe)).then(fire(Ready)).then(fire(Commit)).then(check(s.complete and s.issued==1))
 run gapAcknowledgmentKeepsRecord=init.then(fire(Observe)).then(fire(Ready)).then(fire(Commit)).then(fire(GapAck)).then(check(s.complete and s.acked==0 and not(s.last)))
 run compactPrefixSurvivesConfirmation=init.then(fire(Observe)).then(fire(Ready)).then(fire(Commit)).then(fire(Ack)).then(fire(Ack)).then(check(s.finished and not(s.retained) and s.acked==1 and s.last))
 run foreignEpochCannotReadReady=init.then(fire(Observe)).then(fire(Ready)).then(fire(WrongEpoch)).then(check(s.ready and not(s.last) and s.issued==0))
}
