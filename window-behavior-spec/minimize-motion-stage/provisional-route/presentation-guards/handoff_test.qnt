module handoff_test {
 import handoff.* from "./handoff"
 run undisplayedComputedTickCannotBecomeOriginTest=init.then(fire(Tick)).then(fire(Tick)).then(fire(Reserve(true))).then(all{assert(s.origins==List(4,5) and s.computed==List(4,5) and allProps),fire(Tick)})
 run asynchronousFragmentsKeepOwnActualOriginsTest=init.then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Submit(0))).then(fire(Present(0))).then(fire(Reserve(true))).then(all{assert(s.origins.nth(0)==6 and s.origins.nth(1)==5 and allProps),fire(Tick)})
 run missingFragmentCannotInventHandoffTest=init.then(fire(Forget(1))).then(fire(Tick)).then(fire(Reserve(true))).then(all{assert(s.rejected and s.epoch==1 and allProps),fire(Tick)})
 run pendingOldFrameMustDrainBeforeReserveTest=init.then(fire(Tick)).then(fire(Submit(0))).then(fire(Reserve(true))).then(all{assert(s.rejected and s.epoch==1 and allProps),fire(Present(0))}).then(fire(Reserve(true))).then(all{assert(not(s.rejected) and s.epoch==2 and s.origins==s.shown and allProps),fire(Tick)})
 run malformedWholeTokenCannotReserveTest=init.then(fire(Reserve(false))).then(all{assert(s.rejected and s.epoch==1 and allProps),fire(Tick)})
}
