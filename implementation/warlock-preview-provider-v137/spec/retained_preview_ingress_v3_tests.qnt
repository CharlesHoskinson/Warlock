module retained_preview_ingress_v3_tests {
 import retained_preview_ingress_v3.* from "./retained_preview_ingress_v3"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run lossBeforeIssuanceRetainsOriginal=init.then(fire(Retry)).then(check(s.pending==["acquire"] and s.commands==["acquire"] and s.known))
 run issuedFactDoesNotSettleUnknown=init.then(fire(Issue)).then(check(s.pending==[] and s.known and s.held))
 run changedPurposeRetainsIntent=init.then(fire(WrongTicket)).then(check(s.pending==["acquire"] and s.known))
 run foreignOuterRetainsIntent=init.then(fire(ForeignTicket)).then(check(s.pending==["acquire"]))
 run foreignInnerRetainsIntent=init.then(fire(ForeignInnerTicket)).then(check(s.pending==["acquire"]))
 run repeatedGrantRetainsIntent=init.then(fire(RepeatGrant)).then(check(s.pending==["acquire"]))
 run fullQueueRetainsQuarantineCleanup=init.then(fire(Quarantine)).then(check(s.pending==["acquire"] and s.deferred==["reconcile","cancel"] and not(s.demand) and s.known))
 run blockedInputCannotOverwriteCleanup=init.then(fire(Quarantine)).then(fire(Seed)).then(fire(Terminal)).then(check(s.deferred==["reconcile","cancel"] and s.known and not(s.seeded)))
 run foreignRetryCannotTransferCleanup=init.then(fire(Quarantine)).then(fire(Issue)).then(fire(ForeignRetry)).then(check(s.pending==[] and s.deferred==["reconcile","cancel"]))
 run boundedRetryKeepsOriginalOrder=init.then(fire(Quarantine)).then(fire(Issue)).then(fire(Retry)).then(check(s.pending==["reconcile"] and s.deferred==["cancel"]))
 run deferredCancellationAdmitsAfterOriginalIssuance=init.then(fire(Quarantine)).then(fire(Issue)).then(fire(Retry)).then(fire(Issue)).then(fire(Retry)).then(check(s.pending==["cancel"] and s.deferred==[] and s.known))
 run terminalAckPrecedesDeferredReadiness=init.then(fire(Issue)).then(fire(Seed)).then(fire(Issue)).then(fire(Terminal)).then(check(s.pending==["acknowledge"] and s.deferred==["detach-ready"] and not(s.known)))
 run lostReadinessBeforeIssuanceRetries=init.then(fire(Issue)).then(fire(Seed)).then(fire(Issue)).then(fire(Terminal)).then(fire(Issue)).then(fire(Retry)).then(fire(Retry)).then(check(s.pending==["detach-ready"] and s.commands==["detach-ready"]))
 run unissuedProcessingCannotClose=init.then(fire(Issue)).then(fire(Seed)).then(fire(Issue)).then(fire(Terminal)).then(fire(Issue)).then(fire(Retry)).then(fire(Issue)).then(fire(Complete)).then(fire(Close)).then(check(not(s.closed) and not(s.held) and s.pending==["detach-delivery-ack"]))
 run emptyIngressAllowsTrustedClose=init.then(fire(Issue)).then(fire(Seed)).then(fire(Issue)).then(fire(Terminal)).then(fire(Issue)).then(fire(Retry)).then(fire(Issue)).then(fire(Complete)).then(fire(Issue)).then(fire(Close)).then(check(s.closed and s.pending==[]))
 run greaterRealmRequiresIngressAndNativeClose=init.then(fire(Issue)).then(fire(Seed)).then(fire(Issue)).then(fire(Terminal)).then(fire(Issue)).then(fire(Retry)).then(fire(Issue)).then(fire(Complete)).then(fire(NextGrant)).then(check(s.epoch==1)).then(fire(Issue)).then(fire(Close)).then(fire(NextGrant)).then(check(s.epoch==2 and not(s.closed) and s.pending==[]))
}
