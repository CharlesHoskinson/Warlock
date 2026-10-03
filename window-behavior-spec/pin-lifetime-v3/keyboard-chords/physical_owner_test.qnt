module physical_owner_test {
 import physical_owner.* from "./physical_owner"
 run completeTest=init.then(fire(Observe(good))).then(fire(Begin)).then(fire(End(0))).then(fire(Observe(good))).then(check(accepted))
 run noBeforeTest=init.then(fire(Begin)).then(check(failed and not(running)))
 run noAfterTest=init.then(fire(Observe(good))).then(fire(Begin)).then(fire(End(0))).then(check(not(accepted)))
 run wrongSeatTest=init.then(fire(Observe({...good,seat:false}))).then(fire(Begin)).then(check(failed and not(running)))
 run wrongCoreTest=init.then(fire(Observe({...good,core:false}))).then(fire(Begin)).then(check(failed and not(running)))
 run noSurfaceTest=init.then(fire(Observe({...good,surface:false}))).then(check(failed))
 run changedLifeTest=init.then(fire(Observe(good))).then(fire(Begin)).then(fire(End(0))).then(fire(Observe({...good,life:false}))).then(check(failed and not(accepted)))
 run failedExitTest=init.then(fire(Observe(good))).then(fire(Begin)).then(fire(End(1))).then(fire(Observe(good))).then(check(failed and not(accepted)))
 run noRetryTest=init.then(fire(Observe(good))).then(fire(Begin)).then(fire(End(1))).then(fire(Observe(good))).then(fire(Begin)).then(check(failed and not(running)))
 run replacedSelectorTest=init.then(fire(Observe(good))).then(fire(Begin)).then(fire(End(0))).then(fire(Observe({...good,selector:false}))).then(check(failed and not(accepted)))
}
