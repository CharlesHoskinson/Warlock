module recovery_ownership_test {
 import recovery_ownership.* from "./recovery_ownership"
 action check(p:bool):bool=all{assert(p),s'=s}
 action captured=fire(Reserve).then(fire(Acquire(true))).then(fire(Gate({exact:true,durable:true})))
 run gateBeforeDurableRecordCannotLaunchTest=init.then(fire(Reserve)).then(fire(Acquire(true))).then(fire(Gate({exact:true,durable:false}))).then(fire(Release)).then(check(not(s.released)))
 run durableGatedRecordMayLaunchTest=init.then(captured).then(fire(Release)).then(check(s.released and allProps))
 run reusedPIDCannotBeSignaledTest=init.then(captured).then(fire(Crash)).then(fire(Observe({sameStart:false,material:true}))).then(fire(Signal)).then(check(not(s.signal) and s.gone))
 run changedExecutableCannotBeSignaledTest=init.then(captured).then(fire(Crash)).then(fire(Observe({sameStart:true,material:false}))).then(fire(Signal)).then(check(not(s.signal)))
 run exactOwnedOrphanMayBeSignaledTest=init.then(captured).then(fire(Crash)).then(fire(Observe({sameStart:true,material:true}))).then(fire(Signal)).then(check(s.signal and allProps))
 run liveRendererCannotDeleteSourcesTest=init.then(captured).then(fire(Crash)).then(fire(Directory({same:true,private:true}))).then(fire(Delete)).then(check(not(s.deleted)))
 run replacedActorDirectoryCannotBeDeletedTest=init.then(captured).then(fire(Crash)).then(fire(Gone)).then(fire(Directory({same:false,private:true}))).then(fire(Delete)).then(check(not(s.deleted)))
 run unexpectedActorMaterialRefusesClosureTest=init.then(captured).then(fire(Crash)).then(fire(Gone)).then(fire(Directory({same:true,private:false}))).then(fire(Delete)).then(check(not(s.deleted)))
 run exactGoneOwnedResourcesMayCloseTest=init.then(captured).then(fire(Crash)).then(fire(Gone)).then(fire(Directory({same:true,private:true}))).then(fire(Delete)).then(fire(Close)).then(check(s.closed and allProps))
}
