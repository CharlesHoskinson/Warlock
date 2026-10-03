module attention_target_test {
  import attention_target.* from "./attention_target"
  run uniqueImplicitTargetTest = init.then(fire(Start))
    .then(all {assert(selected==1 and saved==0),fire(Urgent)})
  run explicitPreferenceOverridesNewerOtherInstanceTest = init.then(fire(Add(2)))
    .then(fire(Prefer(1))).then(fire(Start))
    .then(all {assert(selected==1 and queryTarget==1 and streamTarget==1),fire(Urgent)})
  run absentPreferredDoesNotFallbackTest = init.then(fire(Prefer(3))).then(fire(Start))
    .then(all {assert(selected==3 and not(instances.contains(3))),fire(Disconnect)})
  run ambiguousUnknownLeavesPersistenceUntouchedTest = init.then(fire(Add(2))).then(fire(Start))
    .then(all {assert(selected==0 and saved==9),fire(Urgent)})
    .then(all {assert(saved==9),fire(Disconnect)})
  run noInstanceLeavesPersistenceUntouchedTest = init.then(fire(Remove(1))).then(fire(Start))
    .then(all {assert(selected==0 and saved==9),fire(Urgent)})
  run newInstanceCannotRetargetRunningObserverTest = init.then(fire(Start)).then(fire(Urgent))
    .then(fire(Add(2))).then(fire(Remove(1)))
    .then(all {assert(selected==1 and streamTarget==1 and queryTarget==1),fire(Disconnect)})
    .then(all {assert(saved==0 and selected==1),fire(Urgent)})
}
