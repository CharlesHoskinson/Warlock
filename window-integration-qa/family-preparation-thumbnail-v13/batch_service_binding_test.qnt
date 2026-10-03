module batch_service_binding_test {
 import batch_service_binding.* from "./batch_service_binding"
 pure val selected={outer:23,baseline:23,recovery:23,loaded:23,token:1,coverage:required,complete:true,paths:true,hashes:true,modes:true}
 pure val batch={moduleToken:1,ownerToken:7,exactClass:true,sameCommands:true,sameRoot:true,samePreview:true,callbacks:true}
 action check(p:bool):bool=all{assert(p),s'=s}
 action observed=init.then(fire(Observe(selected))).then(fire(Owner(7)))
 action linked=observed.then(fire(Link(batch)))
 action finished=linked.then(fire(Finish({moduleToken:1,ownerToken:7,callbacks:true,normalCleanup:true})))
 run exact19ModulesBatchOwnerAndOriginalGatesMayAcceptTest=finished.then(fire(Original(true))).then(fire(Accept)).then(check(s.accepted and allProps))
 run oldInnerObserverRefusesTest=init.then(fire(Observe({...selected,baseline:20}))).then(fire(Accept)).then(check(s.refused and not(s.accepted)))
 run oldRecoveryObserverRefusesTest=init.then(fire(Observe({...selected,recovery:20}))).then(fire(Accept)).then(check(s.refused and not(s.accepted)))
 run incompleteLoadedModuleInventoryRefusesTest=init.then(fire(Observe({...selected,complete:false}))).then(check(s.refused))
 run missingBatchModuleRefusesTest=init.then(fire(Observe({...selected,coverage:1.to(18)}))).then(check(s.refused))
 run foreignExtraModuleCannotSupplyCoverageTest=init.then(fire(Observe({...selected,coverage:required.union(Set(20))}))).then(check(s.refused))
 run wrongActualBatchClassRefusesTest=observed.then(fire(Link({...batch,exactClass:false}))).then(check(s.refused))
 run wrongActorCommandFacadeRefusesTest=observed.then(fire(Link({...batch,sameCommands:false}))).then(check(s.refused))
 run wrongActorSourceRootRefusesTest=observed.then(fire(Link({...batch,sameRoot:false}))).then(check(s.refused))
 run wrongPrivatePreviewRootRefusesTest=observed.then(fire(Link({...batch,samePreview:false}))).then(check(s.refused))
 run missingInstalledFinisherCallbackRefusesTest=observed.then(fire(Link({...batch,callbacks:false}))).then(check(s.refused))
 run changedActualModuleObjectsRefuseTest=linked.then(fire(Observe({...selected,token:2}))).then(check(s.refused))
 run sourceOnlyCannotAcceptNativeTest=observed.then(fire(Original(true))).then(fire(Accept)).then(check(not(s.accepted)))
 run failedOriginalBaselineCannotBeNormalizedTest=finished.then(fire(Original(false))).then(fire(Accept)).then(check(not(s.accepted)))
 run incompleteNormalLifecycleRefusesTest=linked.then(fire(Original(true))).then(fire(Finish({moduleToken:1,ownerToken:7,callbacks:true,normalCleanup:false}))).then(fire(Accept)).then(check(s.refused and not(s.accepted)))
 run changedOwnerTokenRefusesTest=linked.then(fire(Owner(8))).then(check(s.refused and not(s.accepted)))
}
