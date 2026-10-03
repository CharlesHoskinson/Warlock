module motion_test {
  import motion.* from "./motion"
  run reductionDuringMotionTest=init.then(fire(Animate(16))).then(fire(Tick(1))).then(fire(Reduce(true)))
    .then(all{assert(s.position==16 and not(s.running) and allProps),fire(Submit)})
    .then(fire(Present)).then(all{assert(s.displayed.reduced and s.displayed.position==16 and allProps),fire(Tick(1))})
  run oldTickAfterRetargetTest=init.then(fire(Animate(16))).then(fire(Tick(1))).then(fire(Animate(0))).then(fire(Tick(1)))
    .then(all{assert(s.position==1 and s.target==0 and not(s.tickAccepted) and allProps),fire(Tick(2))})
    .then(all{assert(s.position==0 and not(s.running) and allProps),fire(Submit)})
  run reversalKeepsRenderedPositionTest=init.then(fire(Animate(16))).then(fire(Tick(1))).then(fire(Tick(1))).then(fire(Animate(0)))
    .then(all{assert(s.position==2 and s.target==0 and s.running and allProps),fire(Tick(2))})
  run closeAndReuseRejectsOldTickTest=init.then(fire(Animate(16))).then(fire(Tick(1))).then(fire(Close)).then(fire(Open)).then(fire(Tick(1)))
    .then(all{assert(s.identity==2 and s.position==0 and not(s.tickAccepted) and allProps),fire(Submit)})
  run reducedTargetHasNoTweenTest=init.then(fire(Reduce(true))).then(fire(Animate(16))).then(fire(Submit)).then(fire(Present))
    .then(all{assert(s.position==16 and s.displayed.position==16 and s.displayed.reduced and allProps),fire(Animate(0))})
    .then(all{assert(s.position==0 and not(s.running) and allProps),fire(Submit)})
  run queuedOldFrameMayPresentAfterReductionTest=init.then(fire(Animate(16))).then(fire(Tick(1))).then(fire(Submit)).then(fire(Reduce(true))).then(fire(Present))
    .then(all{assert(s.displayed.position==1 and not(s.displayed.reduced) and s.position==16 and allProps),fire(Submit)})
    .then(fire(Present)).then(all{assert(s.displayed.position==16 and s.displayed.reduced and allProps),fire(Tick(1))})
}
