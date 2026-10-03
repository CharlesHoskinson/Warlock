module actor_resources_test {
 import actor_resources.* from "./actor_resources"
 action check(p:bool):bool=all{assert(p),s'=s}
 run capacityRefusesNewActorTest=init.then(admit).then(admit).then(admit).then(check(capacity==s.limit))
 run existingOwnerCanReverseAtCapacityTest=init.then(admit).then(admit).then(admit).then(reverse(2)).then(check(s.lastReceipt==4 and allProps))
 run pendingActorCannotDetachTest=init.then(admit).then(markPending(1)).then(check(not(removable.contains(1))))
 run displayedActorCannotDetachTest=init.then(admit).then(markVisual(1)).then(check(not(removable.contains(1))))
 run awaitingCancelActorCannotDetachTest=init.then(admit).then(markAwaiting(1)).then(check(not(removable.contains(1))))
 run normalCloseFreesOnlyAfterRetirementTest=init.then(admit).then(detach(1)).then(check(capacity==1 and not(s.owners.contains(1)))).then(normalClose(1)).then(check(capacity==0))
 run failedCloseRemainsQuarantinedTest=init.then(admit).then(detach(1)).then(failedClose(1)).then(check(capacity==1 and s.quarantined.contains(1) and allProps))
 run actorNumbersNeverReuseTest=init.then(admit).then(detach(1)).then(normalClose(1)).then(admit).then(check(s.active==Set(2) and s.serial==2))
 run shutdownRevokesPendingAdmissionBeforeDisposalTest=init.then(admit).then(markPending(1)).then(shutdown).then(check(s.closed and s.pending.size()==0 and s.owners.size()==0 and capacity==1)).then(normalClose(1)).then(check(capacity==0 and allProps))
 run shutdownNeedsVisualAndCancelSettlementTest=init.then(admit).then(markVisual(1)).then(markAwaiting(1)).then(shutdown).then(check(s.retiring.contains(1) and s.visible.contains(1) and s.awaiting.contains(1))).then(shutdownSettled(1)).then(normalClose(1)).then(check(capacity==0 and allProps))
 run shutdownFailureCannotFreeActorSlotTest=init.then(admit).then(shutdown).then(failedClose(1)).then(check(s.closed and capacity==1 and allProps))
}
