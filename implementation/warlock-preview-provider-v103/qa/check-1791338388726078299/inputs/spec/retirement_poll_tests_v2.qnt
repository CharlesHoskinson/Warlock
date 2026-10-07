module retirement_poll_tests {
 import retirement_poll.* from "./retirement_poll_v2"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 action two:bool=init.then(fire(Observe(1))).then(fire(Observe(2))).then(fire(Ready(1))).then(fire(Ready(2)))
 run unacceptedObservationExcluded=init.then(fire(Observe(1))).then(fire(Poll)).then(check(s.selected==0 and s.after==0))
 run firstExactReadySelected=two.then(fire(Poll)).then(check(s.selected==1))
 run blockedFirstDoesNotStarveNeighbor=two.then(fire(Poll)).then(fire(Poll)).then(check(s.selected==2))
 run roundRobinWraps=two.then(fire(Poll)).then(fire(Poll)).then(fire(Poll)).then(check(s.selected==1))
 run completedRowExcluded=two.then(fire(Poll)).then(fire(Complete(2))).then(fire(Poll)).then(check(s.selected==1 and s.issued==1))
 run confirmedRowExcluded=two.then(fire(Poll)).then(fire(Complete(1))).then(fire(Ack)).then(fire(Poll)).then(check(s.selected==2 and s.acked==1))
 run emptyPollRetainsCursor=init.then(fire(Observe(3))).then(fire(Ready(3))).then(fire(Poll)).then(fire(Complete(3))).then(fire(Ack)).then(fire(Poll)).then(check(s.selected==0 and s.after==3 and s.acked==1))
 run foreignEpochDoesNotRotate=two.then(fire(Poll)).then(fire(WrongEpoch)).then(fire(Poll)).then(check(s.selected==2 and s.after==2))
 run lateReadyEntersRotation=two.then(fire(Poll)).then(fire(Observe(3))).then(fire(Ready(3))).then(fire(Poll)).then(fire(Poll)).then(check(s.selected==3))
 run threeContinuousRowsAreVisited=two.then(fire(Observe(3))).then(fire(Ready(3))).then(fire(Poll)).then(check(s.selected==1)).then(fire(Poll)).then(check(s.selected==2)).then(fire(Poll)).then(check(s.selected==3)).then(fire(Poll)).then(check(s.selected==1))
}
