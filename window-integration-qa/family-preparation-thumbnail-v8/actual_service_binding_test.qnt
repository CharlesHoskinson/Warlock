module actual_service_binding_test {
 import actual_service_binding.* from "./actual_service_binding"
 val modules={moduleToken:1,ownerToken:1,outer:23,baseline:23,recovery:23,actual:23,complete:true,paths:true,hashes:true,modes:true,linked:true,durable:true}
 val ledger={ledgerToken:1,ownerToken:1,currentOwner:true,currentSource:true,currentRoot:true,nonempty:true,complete:true,closed:true,published:true,fault:false,diskEqual:true}
 action check(p:bool):bool=all{assert(p),s'=s}
 action original:bool=fire(Original({baseline:true,fault:true}))
 action positive:bool=fire(Bind(modules)).then(fire(Queries(ledger))).then(original).then(fire(Finish({moduleToken:1,ledgerToken:1,ownerToken:1,modulesSame:true,ledgerSame:true}))).then(fire(AcceptBaseline))
 run actualV3StaleInnerObserverRefusedTest=init.then(fire(Bind({...modules,baseline:17,actual:17}))).then(original).then(fire(AcceptBaseline)).then(check(s.refused and not(s.baselineAccepted)))
 run declaredOuterCannotReplaceLoadedModuleTest=init.then(fire(Bind({...modules,actual:19}))).then(check(s.refused))
 run recoveryObserverCannotRemainStaleTest=init.then(fire(Bind({...modules,recovery:17}))).then(check(s.refused))
 run missingActualModuleRefusedTest=init.then(fire(Bind({...modules,complete:false}))).then(check(s.refused))
 run aliasOrWrongPathRefusedTest=init.then(fire(Bind({...modules,paths:false}))).then(check(s.refused))
 run wrongSourceHashRefusedTest=init.then(fire(Bind({...modules,hashes:false}))).then(check(s.refused))
 run wrongSourceModeRefusedTest=init.then(fire(Bind({...modules,modes:false}))).then(check(s.refused))
 run newlyImportedUnlinkedModuleCannotSubstituteTest=init.then(fire(Bind({...modules,linked:false}))).then(check(s.refused))
 run undurableRawBindingCannotAcceptTest=init.then(fire(Bind({...modules,durable:false}))).then(check(s.refused))
 run oldServiceLedgerRefusedTest=init.then(fire(Bind(modules))).then(fire(Queries({...ledger,currentOwner:false}))).then(check(s.refused))
 run absentLedgerRefusedTest=init.then(fire(Bind(modules))).then(fire(Queries({...ledger,nonempty:false}))).then(check(s.refused))
 run unclosedLedgerCannotAcceptTest=init.then(fire(Bind(modules))).then(fire(Queries({...ledger,closed:false}))).then(check(s.refused))
 run pendingOrPartialLedgerCannotAcceptTest=init.then(fire(Bind(modules))).then(fire(Queries({...ledger,complete:false}))).then(check(s.refused))
 run ledgerDiskMismatchCannotAcceptTest=init.then(fire(Bind(modules))).then(fire(Queries({...ledger,diskEqual:false}))).then(check(s.refused))
 run finalSourceReplacementRefusedTest=init.then(fire(Bind(modules))).then(fire(Queries(ledger))).then(fire(Finish({moduleToken:1,ledgerToken:1,ownerToken:1,modulesSame:false,ledgerSame:true}))).then(check(s.refused))
 run originalBaselineCannotBeWaivedTest=init.then(fire(Bind(modules))).then(fire(Queries(ledger))).then(fire(Finish({moduleToken:1,ledgerToken:1,ownerToken:1,modulesSame:true,ledgerSame:true}))).then(fire(AcceptBaseline)).then(check(not(s.baselineAccepted)))
 run faultNeedsSamePacketAcceptedBaselineTest=init.then(fire(Bind(modules))).then(fire(Queries(ledger))).then(original).then(fire(Finish({moduleToken:1,ledgerToken:1,ownerToken:1,modulesSame:true,ledgerSame:true}))).then(fire(AcceptFault)).then(check(not(s.faultAccepted)))
 run exactOriginalBaselineAndFaultFullInverseTest=init.then(positive).then(fire(AcceptFault)).then(check(s.baselineAccepted and s.faultAccepted))
 run refusalCannotBeOverwrittenByLaterValidBindingTest=init.then(fire(Bind({...modules,actual:17}))).then(positive).then(check(s.refused and not(s.baselineAccepted)))
 run stillValidModuleReplacementIsNotCapturedWitnessTest=init.then(fire(Bind(modules))).then(fire(Bind({...modules,moduleToken:2}))).then(check(s.refused))
 run stillValidOwnerReplacementCannotUseOldLedgerTest=init.then(fire(Bind(modules))).then(fire(Queries({...ledger,ownerToken:2}))).then(check(s.refused))
 run freshFinalModuleTokenMustEqualCapturedTest=init.then(fire(Bind(modules))).then(fire(Queries(ledger))).then(fire(Finish({moduleToken:2,ledgerToken:1,ownerToken:1,modulesSame:true,ledgerSame:true}))).then(check(s.refused))
 run freshFinalLedgerTokenMustEqualCapturedBatchTest=init.then(fire(Bind(modules))).then(fire(Queries(ledger))).then(fire(Finish({moduleToken:1,ledgerToken:2,ownerToken:1,modulesSame:true,ledgerSame:true}))).then(check(s.refused))
 run freshFinalOwnerTokenCannotReplaceCaptureTest=init.then(fire(Bind(modules))).then(fire(Queries(ledger))).then(fire(Finish({moduleToken:1,ledgerToken:1,ownerToken:2,modulesSame:true,ledgerSame:true}))).then(check(s.refused))
 run newLedgerBatchRevokesPartialFinalProofTest=init.then(positive).then(fire(Queries({...ledger,ledgerToken:2}))).then(fire(AcceptBaseline)).then(check(not(s.baselineAccepted) and not(s.final)))
}
