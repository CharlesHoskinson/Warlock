module press_receipt_test {
 import press_receipt.* from "./press_receipt"
 action check(p:bool):bool=all{assert(p),owner'=owner,generation'=generation,label'=label,
   pressed'=pressed,pending'=pending,receipt'=receipt,accepted'=accepted,receiptOwner'=receiptOwner,receiptGeneration'=receiptGeneration}
 run captureBeforeReactiveMutationTest=init.then(fire(Down(good))).then(fire(Mutate(2))).then(fire(Click(clicked))).then(check(accepted and receipt==1 and label==2))
 run pressedFalseDoesNotLoseSameClickTest=init.then(fire(Down(good))).then(fire(PressedFalse)).then(fire(Mutate(2))).then(fire(Click(clicked))).then(check(accepted and receipt==1))
 run noPressRefusedTest=init.then(fire(Click(clicked))).then(check(not(accepted)))
 run queryIsNeverPressAuthorityTest=init.then(fire(Query(1))).then(fire(Click(clicked))).then(check(not(accepted)))
 run canceledRefusedTest=init.then(fire(Down(good))).then(fire(Cancel)).then(fire(Click(clicked))).then(check(not(accepted)))
 run destroyedRefusedTest=init.then(fire(Down(good))).then(fire(Destroy)).then(fire(Click(clicked))).then(check(not(accepted)))
 run replacedComponentRefusedTest=init.then(fire(Down(good))).then(fire(Replace)).then(fire(Click(clicked))).then(check(not(accepted)))
 run newPressRevokesOldGenerationTest=init.then(fire(Down(good))).then(fire(Down({...good,generation:2}))).then(fire(Click(clicked))).then(check(not(accepted)))
 run newPressCanClickItsOwnGenerationTest=init.then(fire(Down(good))).then(fire(Down({...good,generation:2,identity:2}))).then(fire(Click({...clicked,generation:2}))).then(check(accepted and receipt==2))
 run duplicateClickRefusedTest=init.then(fire(Down(good))).then(fire(Click(clicked))).then(fire(Click(clicked))).then(check(not(accepted)))
 run wrongOwnerRefusedTest=init.then(fire(Down(good))).then(fire(Click({...clicked,owner:2}))).then(check(not(accepted)))
 run wrongButtonRefusedTest=init.then(fire(Down(good))).then(fire(Click({...clicked,button:2}))).then(check(not(accepted)))
 run wrongModifiersRefusedTest=init.then(fire(Down(good))).then(fire(Click({...clicked,modifiers:1}))).then(check(not(accepted)))
 run syntheticClickRefusedTest=init.then(fire(Down(good))).then(fire(Click({...clicked,actual:false}))).then(check(not(accepted)))
 run syntheticPressRefusedTest=init.then(fire(Down({...good,actual:false}))).then(fire(Click(clicked))).then(check(not(accepted)))
 run invisibleDisabledPressRefusedTest=init.then(fire(Down({...good,eligible:false}))).then(fire(Click(clicked))).then(check(not(accepted)))
 run unsupportedPressButtonRefusedTest=init.then(fire(Down({...good,button:2}))).then(fire(Click({...clicked,button:2}))).then(check(not(accepted)))
 run modifiedPressRefusedTest=init.then(fire(Down({...good,modifiers:1}))).then(fire(Click({...clicked,modifiers:1}))).then(check(not(accepted)))
 run emptyIdentityRefusedTest=init.then(fire(Down({...good,identity:0}))).then(fire(Click(clicked))).then(check(not(accepted)))
 run repeatedGenerationRefusedTest=init.then(fire(Down(good))).then(fire(Down(good))).then(fire(Click(clicked))).then(check(not(accepted)))
}
