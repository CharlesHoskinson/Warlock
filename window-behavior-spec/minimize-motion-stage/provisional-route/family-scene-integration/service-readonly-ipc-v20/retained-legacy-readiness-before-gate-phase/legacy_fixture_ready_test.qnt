module legacy_fixture_ready_test {
 import legacy_fixture_ready.* from "./legacy_fixture_ready"
 val good={live:true,lifetime:1,env:1,argv:1,exe:1,source:1,fd:1,complete:true,error:false,expired:false}
 action check(p:bool):bool=all{assert(p),s'=s}
 run emptyKernelDataNeverReadyTest=init.then(fire(See({...good,complete:false,env:0,argv:0}))).then(fire(Release)).then(check(not(s.ready) and not(s.released)))
 run emptyThenFreshFullVerificationTest=init.then(fire(See({...good,complete:false,env:0,argv:0}))).then(fire(See(good))).then(fire(Verify(true))).then(fire(Release)).then(check(s.released))
 run nonemptyMismatchLatchesTest=init.then(fire(See({...good,env:2}))).then(fire(See(good))).then(check(s.fault and not(s.ready)))
 run argvMismatchRefusesTest=init.then(fire(See({...good,argv:2}))).then(check(s.fault))
 run sourceReplacementRefusesTest=init.then(fire(See({...good,source:2}))).then(check(s.fault))
 run descriptorReplacementRefusesTest=init.then(fire(See({...good,fd:2}))).then(check(s.fault))
 run reusedLifetimeRefusesTest=init.then(fire(See({...good,lifetime:2}))).then(check(s.fault))
 run absoluteDeadlineRefusesLaterReadyTest=init.then(fire(See({...good,expired:true}))).then(fire(See(good))).then(check(s.fault and not(s.ready)))
 run unknownKernelErrorRefusesTest=init.then(fire(See({...good,error:true}))).then(check(s.fault))
 run readyCannotReplaceExistingFullGuardTest=init.then(fire(See(good))).then(fire(Verify(false))).then(fire(Release)).then(check(s.fault and not(s.released)))
}
