module producer_startup_test {
 import producer_startup.* from "./producer_startup"
 action safe=all{assert(invariant),env'=env,running'=running,ready'=ready,sent'=sent}
 action noInput=all{assert(not(sent)),env'=env,running'=running,ready'=ready,sent'=sent}
 run beforeReadyTest=init.then(start(good)).then(input).then(noInput)
 run actualSyncTest=init.then(start(good)).then(sync(true)).then(input).then(safe)
 run failedSyncTest=init.then(start(good)).then(sync(false)).then(input).then(noInput)
 run mainRuntimeTest=init.then(start(good.with("privatePath",false))).then(sync(true)).then(input).then(noInput)
 run foreignDirectoriesTest=init.then(start(good.with("ownedDirs",false))).then(sync(true)).then(input).then(noInput)
 run explicitFlagTest=init.then(start(good.with("explicit",false))).then(sync(true)).then(input).then(noInput)
 run absentScopeTest=init.then(start(good.with("scope",false))).then(sync(true)).then(input).then(noInput)
 run invalidCoreTest=init.then(start(good.with("core",false))).then(sync(true)).then(input).then(noInput)
 run foreignSocketTest=init.then(start(good.with("ownSocket",false))).then(sync(true)).then(input).then(noInput)
 run replacedPeerTest=init.then(start(good.with("samePeer",false))).then(sync(true)).then(input).then(noInput)
 run stalePIDTest=init.then(start(good.with("liveStart",false))).then(sync(true)).then(input).then(noInput)
 run inheritedFDTest=init.then(start(good.with("noFallback",false))).then(sync(true)).then(input).then(noInput)
 run stoppedTest=init.then(start(good)).then(sync(true)).then(stop).then(input).then(noInput)
}
