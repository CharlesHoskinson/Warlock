module retirement_async_tests {
 import retirement_async.* from "./retirement_async"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run completionBehindSiblingObservation=init.then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(ObserveSecond)).then(fire(FinalFirst)).then(check(not(s.first) and s.second))
 run completionBehindSiblingCompletion=init.then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(ObserveSecond)).then(fire(FinalSecond)).then(fire(FinalFirst)).then(check(not(s.first) and not(s.second)))
 run pendingJobCannotForget=init.then(fire(ObserveFirst)).then(fire(FinalFirst)).then(check(s.first and s.knownFirst and not(s.readyFirst)))
 run foreignCompletionNoAuthority=init.then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(ForeignFinal)).then(check(s.first and s.readyFirst))
 run ackBeforeReady=init.then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(check(s.commands==["first:acknowledge","first:retire-ready"]))
 run replayedCompletionInert=init.then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(FinalFirst)).then(fire(FinalFirst)).then(fire(DuplicateTerminal)).then(check(not(s.first) and s.commands==[]))
 run olderCompletionCannotRewindCutoff=init.then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(ObserveSecond)).then(fire(FinalSecond)).then(fire(FinalFirst)).then(fire(MidSeedFresh)).then(check(not(s.fresh) and s.cutoff==104))
 run freshActorAfterReorderedCompletion=init.then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(ObserveSecond)).then(fire(FinalSecond)).then(fire(FinalFirst)).then(fire(OldSeedFirst)).then(fire(OldSeedSecond)).then(fire(FreshSeed)).then(check(not(s.first) and not(s.second) and s.fresh))
 run olderObservationAfterSiblingCompletion=init.then(fire(ObserveSecond)).then(fire(FinalSecond)).then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(FinalFirst)).then(check(not(s.first) and not(s.second)))
 run observationBeforeOwnClockCannotClose=init.then(fire(OldObservation)).then(check(s.first and not(s.pendingFirst) and s.knownFirst))
}
