module demand_tests {
 import demand.* from "./demand"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run latestRevisionTest=init.then(fire(Start)).then(fire(Content)).then(fire(Content)).then(fire(Finish)).then(fire(Tick)).then(fire(Tick)).then(fire(Start)).then(check(s.captured==3 and s.floor==2 and s.owners==2))
 run pacingPreventsSpinTest=init.then(fire(Start)).then(fire(Finish)).then(fire(Content)).then(fire(Start)).then(fire(Tick)).then(fire(Start)).then(check(s.floor==1 and s.lastStart==1))
 run closeDoesNotRetireTest=init.then(fire(Start)).then(fire(Close)).then(check(s.owners==1 and s.busy and not(s.visible)))
 run closeDropsPendingTest=init.then(fire(Start)).then(fire(Content)).then(fire(Close)).then(fire(Finish)).then(fire(Tick)).then(fire(Tick)).then(fire(Start)).then(check(s.floor==1 and s.captured==1 and s.owners==1))
 run newLeaseReopenTest=init.then(fire(Start)).then(fire(Close)).then(fire(Finish)).then(fire(Drain)).then(fire(Reopen)).then(fire(Tick)).then(fire(Tick)).then(fire(Start)).then(check(s.floor==2 and s.lease==2 and s.issuedLease==2 and s.owners==1))
 run finishNotRetirementTest=init.then(fire(Start)).then(fire(Finish)).then(check(s.owners==1 and not(s.busy)))
 run heldCapacityNotReusedTest=init.then(fire(Start)).then(fire(Finish)).then(fire(Content)).then(fire(Tick)).then(fire(Tick)).then(fire(Start)).then(fire(Finish)).then(fire(Content)).then(fire(Tick)).then(fire(Tick)).then(fire(Start)).then(check(s.floor==2 and s.owners==2 and s.captured==2))
 run drainAllowsLatestTest=init.then(fire(Start)).then(fire(Finish)).then(fire(Content)).then(fire(Tick)).then(fire(Tick)).then(fire(Start)).then(fire(Finish)).then(fire(Content)).then(fire(Tick)).then(fire(Tick)).then(fire(Drain)).then(fire(Start)).then(check(s.floor==3 and s.captured==3 and s.owners==1))
 run idleDoesNotCaptureTest=init.then(fire(Tick)).then(fire(Tick)).then(check(s.floor==0 and s.owners==0 and not(s.busy)))
 run sameRevisionNotReplayedTest=init.then(fire(Start)).then(fire(Finish)).then(fire(Tick)).then(fire(Tick)).then(fire(Start)).then(check(s.floor==1 and s.owners==1 and s.captured==1))
}
