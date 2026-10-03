module qs_readiness {
 var phase: str
 var live: bool
 var selected: bool
 var normalStopped: bool
 var unloaded: bool
 var polls: int
 action init = all {phase'="gate",live'=true,selected'=false,normalStopped'=false,unloaded'=false,polls'=0}
 action execSame = all {phase=="gate",live,phase'="pending",live'=live,selected'=selected,normalStopped'=normalStopped,unloaded'=unloaded,polls'=polls}
 action knownStartupPending = all {phase=="pending",live,polls<5,phase'=phase,live'=live,selected'=selected,normalStopped'=normalStopped,unloaded'=unloaded,polls'=polls+1}
 action ready = all {phase=="pending",live,phase'="ready",live'=live,selected'=selected,normalStopped'=normalStopped,unloaded'=unloaded,polls'=polls}
 action unknownReply = all {live,phase'="failed",live'=live,selected'=selected,normalStopped'=normalStopped,unloaded'=unloaded,polls'=polls}
 action selectExact = all {live,phase!="gate",phase'=phase,live'=live,selected'=true,normalStopped'=normalStopped,unloaded'=unloaded,polls'=polls}
 action normalKill = all {live,selected,phase'="stopped",live'=false,selected'=selected,normalStopped'=true,unloaded'=unloaded,polls'=polls}
 action normalNativeUnload = all {normalStopped,not(live),phase'=phase,live'=live,selected'=selected,normalStopped'=normalStopped,unloaded'=true,polls'=polls}
 action idle = all {phase'=phase,live'=live,selected'=selected,normalStopped'=normalStopped,unloaded'=unloaded,polls'=polls}
 action step = any {execSame,knownStartupPending,ready,unknownReply,selectExact,normalKill,normalNativeUnload,idle}
 val invariant = all {polls>=0,polls<=5,normalStopped implies not(live),unloaded implies all {normalStopped,not(live)}}
 run exactSameLifetimeThenReadyTest = init.then(execSame).then(knownStartupPending).then(ready).then(all {assert(invariant),idle})
 run emptyRegistryWaitsWithoutSelectingTest = init.then(execSame).then(knownStartupPending).then(all {assert(invariant),idle})
 run unknownReplyCannotBecomeReadyTest = init.then(execSame).then(unknownReply).then(all {assert(invariant),idle})
 run readinessFailureStillNormalShutdownAndUnloadTest = init.then(execSame).then(unknownReply).then(selectExact).then(normalKill).then(normalNativeUnload).then(all {assert(invariant),idle})
 run normalReadyShutdownBeforeUnloadTest = init.then(execSame).then(ready).then(selectExact).then(normalKill).then(normalNativeUnload).then(all {assert(invariant),idle})
 run missingRegistryCannotKillForeignTest = init.then(execSame).then(knownStartupPending).then(unknownReply).then(all {assert(invariant),idle})
}
