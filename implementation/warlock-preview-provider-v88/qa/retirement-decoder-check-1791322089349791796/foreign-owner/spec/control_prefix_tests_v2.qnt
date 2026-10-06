module control_prefix_tests {
 import control_prefix.* from "./control_prefix_v2"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run gapCannotDeliverReady=init.then(fire(Begin2)).then(check(not(s.inFlight) and s.delivered==0))
 run ackBeforeReady=init.then(fire(Begin1)).then(fire(Finish)).then(fire(Begin2)).then(fire(Finish)).then(check(s.delivered==2))
 run reentrantReadyCannotOvertake=init.then(fire(Begin1)).then(fire(Begin2)).then(check(s.inFlight and s.offered==1 and s.delivered==0)).then(fire(Finish)).then(check(s.delivered==1))
 run reentrantSamePacketCannotReenter=init.then(fire(Begin1)).then(fire(Begin1)).then(check(s.begun==1 and s.inFlight and s.delivered==0))
 run replayCannotStartTwice=init.then(fire(Begin1)).then(fire(Finish)).then(fire(Begin1)).then(check(not(s.inFlight) and s.delivered==1))
 run missingMiddleCannotAdvance=init.then(fire(Begin1)).then(fire(Finish)).then(fire(Begin3)).then(check(not(s.inFlight) and s.delivered==1))
 run finalOrdinalThenNoWrap=init.then(fire(Boundary)).then(fire(BeginMax)).then(fire(Finish)).then(fire(Wrap)).then(check(s.delivered==maximum and not(s.inFlight)))
}
