module switcherFocusTest {
  import switcherFocus.* from "./switcher-focus"
  run unchangedNoFocusTest=init.then(observeSame).then(observeSame).then(all {assert(s.selected==2 and s.focuses==0 and s.target==0),s'=s})
  run relabelNoFocusTest=init.then(relabel).then(relabel).then(all {assert(s.label==1 and s.selected==2 and s.focuses==0),s'=s})
  run retireFocusOnceTest=init.then(retireSelected).then(observeSame).then(all {assert(s.selected==1 and s.focuses==1 and s.target==0),s'=s})
  run foreignArrivalExcludedTest=init.then(observe(Set(1,3,4))).then(all {assert(s.live==Set(1,3) and s.selected==1 and s.target==1 and s.focuses==1),s'=s})
  run unavailableCannotRejoinTest=init.then(retireSelected).then(observe(Set(1,2,3,4))).then(all {assert(s.live==Set(1,3) and s.selected==1 and s.focuses==1 and s.target==0),s'=s})
  run emptyDismissalNoFocusTest=init.then(observe(Set())).then(all {assert(s.closed and s.selected==0 and s.target==0 and s.focuses==0),s'=s})
  run replacementCannotReopenTest=init.then(observe(Set())).then(all {s'=reconcile(s,Set(1,2,3,4),1)}).then(all {assert(s.closed and s.selected==0 and s.focuses==0),s'=s})
  run eachSurvivorFocusOnceTest=init.then(retireSelected).then(retireSelected).then(retireSelected).then(all {assert(s.closed and s.focuses==2 and s.changes==3 and s.target==0),s'=s})
  run physicalStepFocusOnceTest=init.then(physicalStep(1)).then(physicalStep(1)).then(all {assert(s.selected==1 and s.focuses==1 and s.target==0),s'=s})
  run retiredStepCannotFocusTest=init.then(retireSelected).then(all {s'=choose(s,2)}).then(all {assert(s.selected==1 and s.focuses==1 and s.target==0),s'=s})
}
