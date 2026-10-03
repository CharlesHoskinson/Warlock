module actual_service_binding_test {
 import actual_service_binding.* from "./actual_service_binding"
 val modules={outer:20,baseline:20,recovery:20,actual:20,complete:true,paths:true,hashes:true,modes:true,linked:true,durable:true}
 val ledger={currentOwner:true,currentSource:true,currentRoot:true,nonempty:true,complete:true,closed:true,published:true,fault:false,diskEqual:true}
 action check(p:bool):bool=all{assert(p),s'=s}
 action original:bool=fire(Original({baseline:true,fault:true}))
 action positive:bool=fire(Bind(modules)).then(fire(Queries(ledger))).then(original).then(fire(Finish({modulesSame:true,ledgerSame:true}))).then(fire(AcceptBaseline))
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
 run finalSourceReplacementRefusedTest=init.then(fire(Bind(modules))).then(fire(Queries(ledger))).then(fire(Finish({modulesSame:false,ledgerSame:true}))).then(check(s.refused))
 run originalBaselineCannotBeWaivedTest=init.then(fire(Bind(modules))).then(fire(Queries(ledger))).then(fire(Finish({modulesSame:true,ledgerSame:true}))).then(fire(AcceptBaseline)).then(check(not(s.baselineAccepted)))
 run faultNeedsSamePacketAcceptedBaselineTest=init.then(fire(Bind(modules))).then(fire(Queries(ledger))).then(original).then(fire(Finish({modulesSame:true,ledgerSame:true}))).then(fire(AcceptFault)).then(check(not(s.faultAccepted)))
 run exactOriginalBaselineAndFaultFullInverseTest=init.then(positive).then(fire(AcceptFault)).then(check(s.baselineAccepted and s.faultAccepted))
 run refusalCannotBeOverwrittenByLaterValidBindingTest=init.then(fire(Bind({...modules,actual:17}))).then(positive).then(check(s.refused and not(s.baselineAccepted)))
}
