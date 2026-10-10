module overviewRecoveryTests {
  import overviewRecovery.* from "./overview-recovery"
  action check(ok:bool):bool=all {assert(ok and safety),s'=s}
  run correlatedRefusalRestoresFilterOnceTest = init.then(choose).then(issue).then(refusal).then(recover).then(duplicate).then(check(s.returns==1 and s.returnWorkspace==2 and s.sends==1))
  run unknownNeverReturnsOrReplaysTest = init.then(choose).then(issue).then(unknown).then(currentReady).then(check(s.phase==Issued and s.returns==0 and s.sends==1))
  run foreignReceiptDoesNotRestoreTest = init.then(choose).then(issue).then(foreignReceipt).then(check(s.phase==Issued and s.returns==0))
  run refusalWaitsForCurrentReadinessTest = init.then(choose).then(issue).then(busy).then(refusal).then(check(s.phase==Ready and s.returns==0)).then(currentReady).then(recover).then(check(s.returns==1))
  run anotherInterfaceCancelsReturnTest = init.then(choose).then(issue).then(refusal).then(occupied).then(vacated).then(check(s.phase==Idle and s.returns==0 and s.sends==1))
  run replacementAuthorityCancelsReturnTest = init.then(choose).then(issue).then(refusal).then(replacement).then(check(s.phase==Idle and s.returns==0))
  run committedActionKeepsOverviewClosedTest = init.then(choose).then(issue).then(commit).then(check(s.phase==Idle and s.returns==0 and s.sends==1))
  run cancelledChoiceKeepsOverviewClosedTest = init.then(choose).then(cancel).then(check(s.phase==Idle and s.returns==0 and s.sends==0))
}
