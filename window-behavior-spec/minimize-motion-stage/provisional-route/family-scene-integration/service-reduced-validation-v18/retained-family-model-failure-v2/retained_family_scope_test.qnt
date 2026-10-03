module retained_family_scope_test {
 import retained_family_scope.* from "./retained_family_scope"
 action check(p:bool):bool=all{assert(p),s'=s}
 run sameCompleteFreshFamilyMayCommitTest=init.then(fire(Cancel)).then(fire(Ack)).then(fire(Observe({receipt:2,generation:3}))).then(fire(Validate({receipt:2,generation:3}))).then(fire(Effect)).then(check(s.effects==1 and allProps))
 run closedNoncapturedMemberRefusesTest=init.then(fire(Cancel)).then(fire(FamilyChanged(closed))).then(fire(Ack)).then(fire(Observe({receipt:2,generation:3}))).then(fire(Validate({receipt:2,generation:3}))).then(fire(Effect)).then(check(s.failed and s.effects==0 and allProps))
 run sameCountPIDReuseRefusesTest=init.then(fire(Cancel)).then(fire(Ack)).then(fire(FamilyChanged(reused))).then(fire(Observe({receipt:2,generation:3}))).then(fire(Validate({receipt:2,generation:3}))).then(fire(Effect)).then(check(s.failed and s.effects==0 and allProps))
 run foreignAddedMemberRefusesTest=init.then(fire(Cancel)).then(fire(Ack)).then(fire(FamilyChanged(added))).then(fire(Observe({receipt:2,generation:3}))).then(fire(Validate({receipt:2,generation:3}))).then(fire(Effect)).then(check(s.failed and s.effects==0 and allProps))
 run oldWorkerCannotSupplyFreshFamilyTest=init.then(fire(Cancel)).then(fire(Ack)).then(fire(Observe({receipt:2,generation:2}))).then(fire(Validate({receipt:2,generation:3}))).then(check(not(s.validated) and not(s.freshRead) and allProps))
 run pendingContextCannotBorrowScopeTest=init.then(fire(NewReceipt)).then(fire(Cancel)).then(fire(Ack)).then(fire(Observe({receipt:3,generation:3}))).then(fire(Validate({receipt:3,generation:3}))).then(fire(Effect)).then(check(s.contextPending and s.effects==0 and allProps))
 run successorKeepsOriginalExpectedFamilyTest=init.then(fire(Cancel)).then(fire(NewReceipt)).then(fire(FamilyChanged(closed))).then(fire(Ack)).then(fire(Context(3))).then(fire(Observe({receipt:3,generation:3}))).then(fire(Validate({receipt:3,generation:3}))).then(check(s.failed and s.expected==original and allProps))
 run exactAckDoesNotValidateOldDataTest=init.then(fire(Cancel)).then(fire(Ack)).then(fire(Validate({receipt:2,generation:3}))).then(check(not(s.validated) and allProps))
 run changedAfterReadCannotCommitTest=init.then(fire(Cancel)).then(fire(Ack)).then(fire(Observe({receipt:2,generation:3}))).then(fire(Validate({receipt:2,generation:3}))).then(fire(FamilyChanged(reused))).then(fire(Effect)).then(check(s.effects==0 and allProps))
 run actualOldClearedExpectationCounterexampleTest=init.then(fire(Cancel)).then(fire(FamilyChanged(closed))).then(fire(OldClearAck)).then(fire(Observe({receipt:2,generation:3}))).then(fire(Validate({receipt:2,generation:3}))).then(fire(Effect)).then(check(s.effects==1 and not(allProps)))
}
