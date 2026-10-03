module reduction_validation_test {
  import reduction_validation.* from "./reduction_validation"
  action check(p:bool):bool=all{assert(p),s'=s}
  run reductionPreservesBlockedInitialReceiptTest=init.then(fire(ReduceOn)).then(fire(Watchdog)).then(check(s.alive and s.commits==0 and s.receipt==1))
  run validatedInitialReducedRequestCompletesTest=init.then(fire(ReduceOn)).then(fire(Watchdog)).then(fire(Validate(1,1))).then(fire(Watchdog)).then(check(not(s.alive) and s.native==1 and s.commits==1))
  run duplicateWatchdogCannotDuplicateCommitTest=init.then(fire(ReduceOn)).then(fire(Validate(1,1))).then(fire(Watchdog)).then(fire(Watchdog)).then(check(s.commits==1))
  run reductionQueuesExactOldVisualTest=existing.then(fire(ReduceOn)).then(fire(Watchdog)).then(check(s.alive and s.retiring==2 and s.sources and s.commits==0))
  run prematureValidationCannotPassRetirementTest=existing.then(fire(ReduceOn)).then(fire(Watchdog)).then(fire(Validate(2,2))).then(check(s.validated==0 and s.commits==0))
  run cancelAckPreservesReceiptRequiresFreshTokenTest=existing.then(fire(ReduceOn)).then(fire(Watchdog)).then(fire(Ack(2))).then(check(s.alive and s.receipt==2 and s.token==3 and s.validated==0 and not(s.sources)))
  run oldValidationAfterAckRefusedTest=existing.then(fire(ReduceOn)).then(fire(Watchdog)).then(fire(Ack(2))).then(fire(Validate(2,2))).then(fire(Watchdog)).then(check(s.alive and s.commits==0))
  run freshValidationAfterAckSettlesLatestTest=existing.then(fire(ReduceOn)).then(fire(Watchdog)).then(fire(Ack(2))).then(fire(Validate(2,3))).then(fire(Watchdog)).then(check(s.native==0 and s.lastCommitReceipt==2 and s.commits==1))
  run newerReceiptRetainsOldRetirementTest=existing.then(fire(ReduceOn)).then(fire(Watchdog)).then(fire(NewRequest)).then(check(s.receipt==3 and s.retiring==2 and not(s.context)))
  run oldAckCannotSupplyNewContextTest=existing.then(fire(ReduceOn)).then(fire(Watchdog)).then(fire(NewRequest)).then(fire(Ack(2))).then(fire(Validate(3,4))).then(check(s.alive and s.validated==0 and not(s.context)))
  run latestContextAndFreshValidationOnlyTest=existing.then(fire(ReduceOn)).then(fire(Watchdog)).then(fire(NewRequest)).then(fire(Ack(2))).then(fire(Context)).then(fire(Validate(3,4))).then(fire(Watchdog)).then(check(s.commits==1 and s.lastCommitReceipt==3))
  run reductionOffCannotReviveOldVisualTest=existing.then(fire(ReduceOn)).then(fire(Watchdog)).then(fire(ReduceOff)).then(fire(StartVisual)).then(check(s.retiring==2 and s.commits==0))
  run offAfterAckNeedsFreshAnimationPreparationTest=existing.then(fire(ReduceOn)).then(fire(Watchdog)).then(fire(ReduceOff)).then(fire(Ack(2))).then(fire(Validate(2,3))).then(fire(StartVisual)).then(fire(Presented(2,3))).then(check(s.commits==1 and s.native==0))
  run wrongAckRetainsSourcesTest=existing.then(fire(ReduceOn)).then(fire(Watchdog)).then(fire(Ack(1))).then(check(s.retiring==2 and s.sources and s.alive))
  run deadlineIsExplicitFailureNotReductionTest=init.then(fire(ReduceOn)).then(fire(Watchdog)).then(fire(Deadline)).then(check(s.error and not(s.alive) and s.commits==0))
  run scopeLossCannotCommitTest=init.then(fire(Validate(1,1))).then(fire(LoseScope)).then(fire(ReduceOn)).then(fire(Watchdog)).then(check(s.error and s.commits==0))
}
