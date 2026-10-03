module transport_dispatch_test {
 import transport_dispatch.* from "./transport_dispatch"
 action check(p:bool):bool=all{assert(p),s'=s}
 run blockedCallbackStillDrainsFramesTest=init.then(fire(WriteCallback)).then(fire(Drain)).then(fire(Dispatch)).then(fire(WriteFrame)).then(fire(WriteFrame)).then(fire(Drain)).then(fire(Drain)).then(check(s.busy and s.pipe.length()==0 and s.drained==3))
 run supersededQueuedCallbackHasNoNativeEffectTest=init.then(fire(WriteCallback)).then(fire(Drain)).then(fire(Dispatch)).then(fire(Reserve)).then(fire(Finish)).then(check(not(s.effect)))
 run exhaustionRetiresActorWithoutNativeEffectTest=init.then(fire(WriteCallback)).then(fire(Drain)).then(fire(Dispatch)).then(fire(WriteCallback)).then(fire(Drain)).then(fire(WriteCallback)).then(fire(Drain)).then(fire(WriteCallback)).then(fire(Drain)).then(fire(Finish)).then(check(s.failed and not(s.alive) and not(s.effect)))
 run zeroExitWhileCallbackBlockedIsNotNormalTest=init.then(fire(WriteCallback)).then(fire(Drain)).then(fire(Dispatch)).then(fire(Close)).then(check(not(s.normal)))
 run cleanDrainedShutdownIsNormalTest=init.then(fire(WriteFrame)).then(fire(Drain)).then(fire(Close)).then(check(s.normal))
}
