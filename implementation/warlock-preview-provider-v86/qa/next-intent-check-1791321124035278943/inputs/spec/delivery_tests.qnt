module delivery_tests {
 import delivery.* from "./delivery"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run viewGrowthCannotAck=init.then(fire(CancelNew)).then(fire(CloseNew)).then(fire(FenceNew)).then(fire(DestroyNew)).then(fire(AckNew)).then(check(s.new==4 and projection(s).newReceipts==0 and projection(s).records==2))
 run explicitJournalGrowth=init.then(fire(CancelNew)).then(fire(CloseNew)).then(fire(FenceNew)).then(fire(DestroyNew)).then(fire(Extend)).then(check(projection(s).newReceipts==2)).then(fire(AckNew)).then(check(s.new==5 and projection(s).records==1 and projection(s).readers==1))
 run oldOwnershipSurvives=init.then(fire(Extend)).then(fire(CancelOld)).then(fire(CloseOld)).then(check(projection(s).charge==64)).then(fire(FenceOld)).then(fire(DestroyOld)).then(fire(AckOld)).then(check(s.old==5 and s.new==0 and projection(s).charge==32))
 run wrongPopupNoAdmission=init.then(fire(WrongPopup)).then(fire(CancelNew)).then(fire(CloseNew)).then(fire(FenceNew)).then(fire(DestroyNew)).then(fire(AckNew)).then(check(not(s.admitted) and s.new==4))
 run replacedReceiverRetainsJournal=init.then(fire(Extend)).then(fire(Replace)).then(fire(CancelNew)).then(fire(CloseNew)).then(fire(FenceNew)).then(fire(DestroyNew)).then(fire(AckNew)).then(check(s.new==4 and projection(s).records==2 and projection(s).newReceipts==0))
 run repeatedExtensionKeepsCleanup=init.then(fire(Extend)).then(fire(CancelOld)).then(fire(CloseOld)).then(fire(FenceOld)).then(fire(DestroyOld)).then(fire(Extend)).then(fire(Extend)).then(check(s.old==4 and projection(s).oldReceipts==2)).then(fire(AckOld)).then(check(projection(s).records==1))
}
