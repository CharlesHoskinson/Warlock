module terminal_confirmation_test {
 import terminal_confirmation.* from "./terminal_confirmation"
 action check(v:bool):bool=all{assert(v),s'=s}
 action archive(f:Failure):bool=fire(Observe(f)).then(fire(Publish)).then(fire(Confirm({source:true,batch:true,current:true}))).then(fire(Return))
 action refused(f:Failure):bool=archive(f).then(check(s.rawError and s.confirmationError and s.confirmed and not(s.accepted)))
 run normalCompleteArchiveAcceptsTest=init.then(archive(NoFailure)).then(check(s.accepted))
 run ownerFailureRemainsRefusedTest=init.then(refused(OwnerFailure))
 run moduleFailureRemainsRefusedTest=init.then(refused(ModuleFailure))
 run serviceFailureRemainsRefusedTest=init.then(refused(ServiceFailure))
 run genuineRefusedQueryRemainsRefusedTest=init.then(refused(LedgerFailure))
 run retainedQueryFailureRemainsRefusedTest=init.then(refused(RetainedFailure))
 run actorFailureRemainsRefusedTest=init.then(refused(ActorFailure))
 run sourceBeforeDiskFailureRemainsRefusedTest=init.then(refused(SourceFailure))
 run batchBeforeDiskFailureRemainsRefusedTest=init.then(refused(BatchFailure))
 run freshSourceMissingAfterDiskRefusesTest=init.then(fire(Observe(NoFailure))).then(fire(Publish)).then(fire(Confirm({source:false,batch:true,current:true}))).then(fire(Return)).then(check(s.confirmationError and not(s.accepted)))
 run freshBatchChangedAfterDiskRefusesTest=init.then(fire(Observe(NoFailure))).then(fire(Publish)).then(fire(Confirm({source:true,batch:false,current:true}))).then(fire(Return)).then(check(s.confirmationError and not(s.accepted)))
 run ownerLedgerModuleChangeAfterDiskRefusesTest=init.then(fire(Observe(NoFailure))).then(fire(Publish)).then(fire(Confirm({source:true,batch:true,current:false}))).then(fire(Return)).then(check(not(s.accepted)))
 run noPublishedEvidenceCannotAcceptTest=init.then(fire(Observe(NoFailure))).then(fire(Confirm({source:true,batch:true,current:true}))).then(fire(Return)).then(check(not(s.accepted)))
 run noConfirmationCannotAcceptTest=init.then(fire(Observe(NoFailure))).then(fire(Publish)).then(fire(Return)).then(check(not(s.accepted)))
 run freshGoodObservationCannotClearOriginalFailureTest=init.then(refused(LedgerFailure)).then(archive(NoFailure)).then(check(s.rawError and not(s.accepted)))
 run changedSourceCannotRetainPriorAcceptanceTest=init.then(archive(NoFailure)).then(fire(Confirm({source:false,batch:true,current:true}))).then(check(not(s.accepted) and s.confirmationError))
}
