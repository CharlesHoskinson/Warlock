module terminal_process_receipts_test {
 import terminal_process_receipts.* from "./terminal_process_receipts"
 run actualRequestStartExitRequiredTest=init.then(fire(Request)).then(fire(Start(1))).then(fire(Quiesce)).then(fire(Drain)).then(all { s'=s, assert(not(s.drained)) }).then(fire(Exit(1))).then(fire(Drain)).then(all { s'=s, assert(s.drained and allProps) })
 run failedToStartCannotInferNormalFromNotRunningTest=init.then(fire(Request)).then(fire(Quiesce)).then(fire(Drain)).then(all { s'=s, assert(not(s.drained) and s.active==0) }).then(fire(MissingStart)).then(fire(Drain)).then(all { s'=s, assert(s.failed and not(s.drained)) })
 run queuedActionCanStartAfterQuiesceWithOriginalBudgetTest=init.then(fire(Queue)).then(fire(Quiesce)).then(fire(Drain)).then(all { s'=s, assert(not(s.drained)) }).then(fire(RequestQueued)).then(fire(Start(1))).then(fire(Exit(1))).then(fire(Drain)).then(all { s'=s, assert(s.drained) })
 run freshPollingAfterQuiesceRefusesTest=init.then(fire(Quiesce)).then(fire(Request)).then(fire(Drain)).then(all { s'=s, assert(s.failed and not(s.drained)) })
 run newQueuedActionAfterQuiesceRefusesTest=init.then(fire(Quiesce)).then(fire(Queue)).then(fire(Drain)).then(all { s'=s, assert(s.failed and not(s.drained)) })
 run wrongOrDuplicateGenerationCannotBorrowExitTest=init.then(fire(Request)).then(fire(Start(1))).then(fire(Exit(0))).then(fire(Quiesce)).then(fire(Drain)).then(all { s'=s, assert(s.failed and not(s.drained)) })
 run normalHistoricalReceiptCannotCloseNewRequestTest=init.then(fire(Request)).then(fire(Start(1))).then(fire(Exit(1))).then(fire(Request)).then(fire(Quiesce)).then(fire(Drain)).then(all { s'=s, assert(not(s.drained) and s.requested==2 and s.ended==1) })
 run exit120IsNeverNormalCompletionTest=init.then(fire(Request)).then(fire(Start(1))).then(fire(AbnormalExit)).then(fire(Quiesce)).then(fire(Drain)).then(all { s'=s, assert(s.failed and not(s.drained)) })
 run identityOrEpochChangeRevokesDrainTest=init.then(fire(Quiesce)).then(fire(Drain)).then(fire(ChangedOwner)).then(all { s'=s, assert(s.failed and not(s.drained)) })
 run resetCannotEraseReceiptFailureTest=init.then(fire(Request)).then(fire(ResetEpoch)).then(fire(Quiesce)).then(fire(Drain)).then(all { s'=s, assert(s.failed and s.requested==1 and not(s.drained)) })
}
