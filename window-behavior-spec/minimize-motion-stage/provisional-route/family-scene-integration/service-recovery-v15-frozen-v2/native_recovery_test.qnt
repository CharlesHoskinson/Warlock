module native_recovery_test {
 import native_recovery.* from "./native_recovery"
 action check(p:bool):bool=all{assert(p),s'=s}
 action load=fire(Load({session:true,provenance:true,receipt:2}))
 action observe=fire(Observe({exact:true,family:true,context:true,receipt:2}))
 run journalValidationAloneNeverAuthorizesSettlementTest=init.then(load).then(fire(Settle)).then(check(not(s.effect)))
 run oldVisualResourceMustRetireBeforeNativeWriteTest=init.then(load).then(fire(Prepare(true))).then(observe).then(fire(Settle)).then(check(not(s.effect)))
 run durabilityRequiredBeforeFreshObservationTest=init.then(load).then(fire(RetireResources(true))).then(observe).then(fire(Settle)).then(check(not(s.effect)))
 run olderReceiptCannotCommitTest=init.then(load).then(fire(RetireResources(true))).then(fire(Prepare(true))).then(fire(Observe({exact:true,family:true,context:true,receipt:1}))).then(fire(Settle)).then(check(not(s.effect)))
 run latestFreshCompleteProofMaySettleTest=init.then(load).then(fire(RetireResources(true))).then(fire(Prepare(true))).then(observe).then(fire(Settle)).then(check(s.effect and s.effectReceipt==2))
 run reusedIdentityCannotSettleTest=init.then(load).then(fire(RetireResources(true))).then(fire(Prepare(true))).then(fire(Observe({exact:false,family:true,context:true,receipt:2}))).then(fire(Settle)).then(check(not(s.effect)))
 run familyChangeCannotSettleTest=init.then(load).then(fire(RetireResources(true))).then(fire(Prepare(true))).then(fire(Observe({exact:true,family:false,context:true,receipt:2}))).then(fire(Settle)).then(check(not(s.effect)))
 run outputChangeCannotSettleTest=init.then(load).then(fire(RetireResources(true))).then(fire(Prepare(true))).then(fire(Observe({exact:true,family:true,context:false,receipt:2}))).then(fire(Settle)).then(check(not(s.effect)))
 run revocationRemovesFreshAuthorityTest=init.then(load).then(fire(RetireResources(true))).then(fire(Prepare(true))).then(observe).then(fire(Revoke)).then(fire(Settle)).then(check(not(s.effect)))
 run repeatedCrashNeedsNewResourceAndNativeProofTest=init.then(load).then(fire(RetireResources(true))).then(fire(Prepare(true))).then(observe).then(fire(Crash)).then(load).then(fire(Settle)).then(check(not(s.effect)))
 run unresolvedRecoveryNeverListensTest=init.then(load).then(fire(Listen)).then(check(not(s.listening)))
 run observationWithoutSettlementCannotClearJournalTest=init.then(load).then(fire(RetireResources(true))).then(fire(Prepare(true))).then(observe).then(fire(Clear)).then(fire(Listen)).then(check(not(s.cleared) and not(s.listening)))
 run oldJournalWithoutProvenanceStillRefusesTest=init.then(fire(Load({session:true,provenance:false,receipt:2}))).then(fire(Settle)).then(fire(Listen)).then(check(not(s.loaded) and not(s.effect) and not(s.listening)))
}
