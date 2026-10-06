module observation_tests {
 import observations.* from "./observations"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run contentRetainsOriginal=init.then(fire(Seed)).then(fire(Request)).then(fire(Capture)).then(fire(Content)).then(fire(ClockOnly)).then(fire(Expire)).then(fire(Drain)).then(fire(Ack)).then(check(s.records==0 and not(s.known)))
 run sceneRetainsOriginal=init.then(fire(Seed)).then(fire(Request)).then(fire(Capture)).then(fire(Scene)).then(check(s.accepted and not(s.fresh) and s.charged))
 run stoppedIsHistorical=init.then(fire(Seed)).then(fire(Request)).then(fire(Capture)).then(fire(Stopped)).then(check(s.accepted and not(s.fresh) and s.charged))
 run outputRevokes=init.then(fire(Seed)).then(fire(Request)).then(fire(Capture)).then(fire(Output)).then(fire(Drain)).then(fire(Ack)).then(check(s.records==0))
 run privacyRevokes=init.then(fire(Seed)).then(fire(Request)).then(fire(Capture)).then(fire(Privacy)).then(check(s.retiring and s.charged))
 run rendererRevokes=init.then(fire(Seed)).then(fire(Request)).then(fire(Capture)).then(fire(Rendering)).then(check(s.retiring and s.charged))
 run lockedRevokes=init.then(fire(Seed)).then(fire(Request)).then(fire(Capture)).then(fire(Locked)).then(fire(Drain)).then(fire(Ack)).then(check(s.records==0))
 run absentRevokes=init.then(fire(Seed)).then(fire(Request)).then(fire(Capture)).then(fire(Absent)).then(check(s.retiring and s.charged))
 run gpuRevokes=init.then(fire(Seed)).then(fire(Request)).then(fire(Capture)).then(fire(Gpu)).then(check(s.retiring and s.charged))
 run closedOwnerStillReceivesFacts=init.then(fire(Seed)).then(fire(Request)).then(fire(Capture)).then(fire(Close)).then(fire(Content)).then(fire(Expire)).then(fire(Drain)).then(fire(Ack)).then(check(not(s.open) and s.records==0))
 run noMetadataDecoration=init.then(fire(Seed)).then(fire(Request)).then(fire(Capture)).then(fire(ClockOnly)).then(fire(ClockOnly)).then(check(s.fresh and s.accepted))
}
