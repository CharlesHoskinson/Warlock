module actor_control_tests {
 import actor_control.* from "./actor_control"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 action remove=fire(Ready).then(fire(DeliverReady)).then(fire(ConfirmJob)).then(fire(Poll))
 action final=remove.then(fire(FinalAck)).then(fire(DeliverFinal))
 run rawReadinessCannotQueryOrMutate=init.then(fire(RawReady)).then(check(s.last== -1 and s.frames==1))
 run nativeReadinessBeforePhysicalEffect=init.then(fire(Ready)).then(check(s.issued==3 and s.frames==1 and not(s.accepted)))
 run oldAckConfirmationPrecedesRemoval=init.then(fire(Ready)).then(fire(DeliverReady)).then(fire(Poll)).then(check(not(s.removed) and s.jobs==1 and s.frames==1))
 run actualAggregateReclaimsOnlyJobCredits=init.then(remove).then(check(s.frames==0 and s.jobs==0 and s.actor and s.tickets==1 and s.reserved==2))
 run rawFinalAckCannotMutatePrefix=init.then(remove).then(fire(FinalAck)).then(fire(RawFinal)).then(check(s.last== -1 and s.journal==1 and not(s.acked)))
 run finalEffectBeforeActorCreditRelease=init.then(remove).then(fire(FinalAck)).then(fire(Collect)).then(check(s.last==0 and s.actor))
 run finalConfirmationBeforeActorCreditRelease=init.then(final).then(fire(Collect)).then(check(s.last==0 and s.actor and s.journal==0))
 run confirmedFinalReclaimsActorCredits=init.then(final).then(fire(ConfirmAll)).then(fire(Collect)).then(check(not(s.actor) and s.tickets==0 and s.previous==0 and s.reserved==1))
 run bindingCloseWaitsForActorDelivery=init.then(final).then(fire(Close)).then(check(not(s.closed) and s.last==0))
 run allIndependentBarriersPermitClose=init.then(final).then(fire(ConfirmAll)).then(fire(Collect)).then(fire(Close)).then(fire(Close)).then(check(s.closed and s.reserved==0 and s.issued==4))
 run confirmedUnknownEffectKeepsActor=init.then(remove).then(fire(FinalAck)).then(fire(UnknownFinal)).then(fire(ConfirmAll)).then(fire(Collect)).then(fire(Close)).then(check(s.unknown and s.actor and s.journal==1 and not(s.closed)))
 run duplicateUnknownTicketCannotReinvoke=init.then(remove).then(fire(FinalAck)).then(fire(UnknownFinal)).then(fire(DeliverFinal)).then(check(s.last==2 and s.unknown and not(s.acked)))
 run wrongObservationHasNoActorCredit=init.then(fire(WrongObservation)).then(check(s.last== -1 and s.issued==2))
 run futureFinalAckHasNoActorCredit=init.then(remove).then(fire(FutureFinal)).then(check(s.last== -1 and s.issued==3))
 run foreignActorReceiverHasNoCredit=init.then(fire(ForeignReceiver)).then(check(s.last== -1 and s.issued==2))
}
