module retirement_delivery_tests {
 import retirement_delivery.* from "./retirement_delivery"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run pendingCompletionCannotForget=init.then(fire(Activate)).then(fire(ObserveFirst)).then(fire(DeliverFirst1)).then(check(s.first and s.knownFirst and s.processed==0))
 run gapCannotRemoveReadyActor=init.then(fire(Activate)).then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(DeliverFirst2)).then(check(s.first and s.processed==0 and s.commands==[]))
 run nextCompletionEmitsProcessingAck=init.then(fire(Activate)).then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(DeliverFirst1)).then(check(not(s.first) and s.processed==1 and s.commands==["first:retire-delivery-ack:1"]))
 run lostProcessingAckRetriesOnlyAck=init.then(fire(Activate)).then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(DeliverFirst1)).then(fire(DeliverFirst1)).then(check(not(s.first) and s.processed==1 and s.commands==["first:retire-delivery-ack:1"]))
 run repeatedActivationCannotReset=init.then(fire(Activate)).then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(DeliverFirst1)).then(fire(Activate)).then(fire(ObserveSecond)).then(fire(DeliverSecond2)).then(check(s.processed==2 and not(s.second)))
 run retainedChannelRejectsLegacy=init.then(fire(Activate)).then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(LegacyFirst)).then(check(s.first and s.processed==0 and s.commands==[]))
 run foreignDeliveryCannotAdvance=init.then(fire(Activate)).then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(ForeignFirst1)).then(check(s.first and s.processed==0 and s.commands==[]))
 run olderNativeFactAtLaterOrdinal=init.then(fire(Activate)).then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(ObserveSecond)).then(fire(DeliverSecond1)).then(fire(DeliverFirst2)).then(check(not(s.first) and not(s.second) and s.processed==2 and s.cutoff==104))
 run duplicateAfterSiblingCompletion=init.then(fire(Activate)).then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(ObserveSecond)).then(fire(DeliverFirst1)).then(fire(DeliverSecond2)).then(fire(DeliverFirst1)).then(check(s.processed==2 and s.commands==["first:retire-delivery-ack:1"]))
 run replacementCannotReset=init.then(fire(Activate)).then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(DeliverFirst1)).then(fire(Replacement)).then(fire(GapFirst3)).then(check(s.processed==1 and s.commands==[]))
 run lateActivationPreservesLegacy=init.then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(Activate)).then(fire(DeliverFirst1)).then(check(s.first and not(s.channel))).then(fire(LegacyFirst)).then(check(not(s.first) and s.processed==0))
 run cleanupAckPrecedesReadiness=init.then(fire(Activate)).then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(check(s.commands==["first:acknowledge","first:retire-ready"]))
 run duplicateTerminalAfterReadyInert=init.then(fire(Activate)).then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(DuplicateTerminal)).then(check(s.readyFirst and s.commands==[]))
 run oldSeedCannotRecreate=init.then(fire(Activate)).then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(DeliverFirst1)).then(fire(OldSeed)).then(check(not(s.first) and s.commands==[]))
}
