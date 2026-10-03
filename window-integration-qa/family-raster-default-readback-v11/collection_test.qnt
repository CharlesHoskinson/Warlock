module collection_test {
  import collection.* from "./collection"
  action check(p: bool): bool = all {
    assert(p), observed'=observed, bad'=bad, fatal'=fatal,
    finished'=finished, accepted'=accepted
  }
  run partialCannotPassTest = init.then(observe(0,true,true)).then(finish).then(check(not(accepted)))
  run failedImageSurvivesOtherPassTest = init.then(observe(0,true,false)).then(observe(1,true,true)).then(check(bad==Set(0) and observed==Set(0,1))).then(finish).then(check(not(accepted)))
  run duplicateCannotRewriteFailureTest = init.then(observe(0,true,false)).then(observe(0,true,true)).then(check(fatal and bad==Set(0))).then(finish).then(check(not(accepted)))
  run invalidBindingStopsAcceptanceTest = init.then(observe(0,false,true)).then(finish).then(check(fatal and observed==Set() and not(accepted)))
  run outsideSlotCannotPassTest = init.then(observe(26,true,true)).then(finish).then(check(fatal and not(accepted)))
  run all26FinalAndCausalMustPassTest = init.then(observe(0,true,true)).then(observe(1,true,true)).then(observe(2,true,true)).then(observe(3,true,true)).then(observe(4,true,true)).then(observe(5,true,true)).then(observe(6,true,true)).then(observe(7,true,true)).then(observe(8,true,true)).then(observe(9,true,true)).then(observe(10,true,true)).then(observe(11,true,true)).then(observe(12,true,true)).then(observe(13,true,true)).then(observe(14,true,true)).then(observe(15,true,true)).then(observe(16,true,true)).then(observe(17,true,true)).then(observe(18,true,true)).then(observe(19,true,true)).then(observe(20,true,true)).then(observe(21,true,true)).then(observe(22,true,true)).then(observe(23,true,true)).then(observe(24,true,true)).then(observe(25,true,true)).then(finish).then(check(accepted))
  run retainedCausalFailureCannotPassTest = init.then(observe(0,true,true)).then(observe(1,true,true)).then(observe(2,true,true)).then(observe(3,true,true)).then(observe(4,true,true)).then(observe(5,true,true)).then(observe(6,true,true)).then(observe(7,true,true)).then(observe(8,true,true)).then(observe(9,true,false)).then(observe(10,true,true)).then(observe(11,true,true)).then(observe(12,true,true)).then(observe(13,true,true)).then(observe(14,true,true)).then(observe(15,true,true)).then(observe(16,true,true)).then(observe(17,true,true)).then(observe(18,true,true)).then(observe(19,true,true)).then(observe(20,true,true)).then(observe(21,true,true)).then(observe(22,true,true)).then(observe(23,true,true)).then(observe(24,true,true)).then(observe(25,true,true)).then(finish).then(check(not(accepted) and bad==Set(9)))
}
