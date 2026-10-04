module stream_test {
  import stream.* from "./stream"
  run increasingTest = init.then(fire(Start)).then(fire(Receive({epoch:1,sequence:1})))
    .then(all {assert(accepted and sequence == 1), fire(Receive({epoch:1,sequence:2}))})
    .then(all {assert(accepted and sequence == 2), fire(Stop)})
  run duplicateTest = init.then(fire(Start)).then(fire(Receive({epoch:1,sequence:1}))).then(fire(Receive({epoch:1,sequence:1})))
    .then(all {assert(not(accepted) and sequence == 1), fire(Stop)})
  run foreignEpochTest = init.then(fire(Start)).then(fire(Receive({epoch:1,sequence:2}))).then(fire(Receive({epoch:2,sequence:3})))
    .then(all {assert(not(accepted) and epoch == 1 and sequence == 2), fire(Stop)})
  run stoppedTest = init.then(fire(Start)).then(fire(Receive({epoch:1,sequence:1}))).then(fire(Stop)).then(fire(Receive({epoch:1,sequence:2})))
    .then(all {assert(not(accepted) and sequence == 0), fire(Start)})
  run restartTest = init.then(fire(Start)).then(fire(Receive({epoch:1,sequence:2}))).then(fire(Stop)).then(fire(Start)).then(fire(Receive({epoch:2,sequence:1})))
    .then(all {assert(accepted and epoch == 2 and sequence == 1), fire(Stop)})
}
