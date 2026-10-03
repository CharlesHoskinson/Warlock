module refusal_fixture_test {
 import refusal_fixture.* from "./refusal_fixture"
 action check(v:bool):bool=all{assert(v),s'=s}
 run timeoutDeliveredTest=init.then(fire(Deadline)).then(fire(WorkerTimeout)).then(fire(Close)).then(fire(Accept)).then(check(s.accepted))
 run earlierOrderedStoppedDeliveredTest=init.then(fire(Deadline)).then(fire(WorkerTimeout)).then(fire(OrderedStopped)).then(fire(Close)).then(fire(Accept)).then(check(s.accepted and allProps))
 run beforeDeadlineStoppedNotAcceptedTest=init.then(fire(OrderedStopped)).then(fire(Close)).then(fire(Accept)).then(check(not(s.accepted)))
 run liveReaderNeverAcceptedTest=init.then(fire(Deadline)).then(fire(WorkerTimeout)).then(fire(Accept)).then(check(not(s.accepted)))
 run unknownErrorNeverAcceptedTest=init.then(fire(Deadline)).then(fire(WorkerTimeout)).then(fire(Other)).then(fire(Close)).then(fire(Accept)).then(check(not(s.accepted)))
 run noTimeoutCauseNeverAcceptedTest=init.then(fire(Deadline)).then(fire(Close)).then(fire(OrderedStopped)).then(fire(Accept)).then(check(not(s.accepted)))
 run capturedMemberCopyRetainsOldTupleTest=init.then(fire(CaptureCopy)).then(fire(PeerReplace)).then(check(s.captured==1 and s.peer==2 and s.captured!=s.peer))
 run unchangedPeerMatchesCapturedTupleTest=init.then(fire(CaptureCopy)).then(check(s.captured==s.peer))
}
