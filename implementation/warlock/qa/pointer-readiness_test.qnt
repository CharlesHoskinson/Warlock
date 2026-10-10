module pointer_readiness_test {
  import pointer_readiness.* from "./pointer-readiness"
  run initialUnknownTest=init.then(fire(Shell)).then(all {assert(initializedBlocked and safety),s'=s})
  run currentIdleTest=init.then(fire(ObserveIdle)).then(fire(Shell)).then(all {assert(freshShellReached and safety),s'=s})
  run activeRetiresTest=init.then(fire(ObserveIdle)).then(fire(Shell)).then(fire(Begin)).then(fire(Shell)).then(all {assert(not(s.opened) and safety),s'=s})
  run reboundUnknownTest=init.then(fire(ObserveIdle)).then(fire(Rebind)).then(fire(Shell)).then(all {assert(not(s.opened) and safety),s'=s})
  run foreignCannotReleaseTest=init.then(fire(Begin)).then(fire(Rebind)).then(fire(Stale)).then(fire(Shell)).then(all {assert(not(s.opened) and safety),s'=s})
  run releaseNoReplayTest=init.then(fire(Begin)).then(fire(Shell)).then(fire(Release)).then(all {assert(releasedPermits and safety),s'=s}).then(fire(Shell)).then(all {assert(freshShellReached),s'=s})
}
