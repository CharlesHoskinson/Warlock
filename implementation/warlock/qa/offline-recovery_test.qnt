module offline_recovery_test {
  import offline_recovery.* from "./offline-recovery"
  run initialPredecessorTest = init.then(startSelected).then(all {
    assert(predecessorStarted and safety), s'=s})
  run failedHostRollbackTest = init.then(activate).then(startSelected)
    .then(hostExit).then(stageRollback).then(commitRollback(Applied))
    .then(startSelected).then(all {assert(failedHostRecovered and
      s.rollbacks==1 and safety),s'=s})
  run damagedCandidateDoesNotBlockRecoveryTest = init.then(activate)
    .then(damageCandidate).then(stageRollback).then(commitRollback(Applied))
    .then(startSelected).then(all {assert(damagedCandidateRecovered and
      failedHostRecovered and safety),s'=s})
  run activeHostCannotSwitchTest = init.then(activate).then(startSelected)
    .then(all {assert(not(canStage(s)) and not(canStart(s)) and safety),s'=s})
  run missingPriorCannotRollbackTest = init.then(activate).then(damagePrior)
    .then(all {assert(not(canStage(s)) and s.route==Candidate and safety),s'=s})
  run privateStagingNeverChangesSelectionTest = init.then(activate)
    .then(stageRollback).then(all {assert(s.route==Candidate and
      s.preferences==CandidateValues and not(canStart(s)) and safety),s'=s})
  run stagingCrashKeepsOldPreferencesTest = init.then(activate)
    .then(startSelected).then(hostExit).then(stageRollback)
    .then(crashBeforeCommit).then(all {assert(stagingCrashRetainsCandidate
      and s.preferences==CandidateValues and safety),s'=s})
  run unknownCannotStartOrReplayTest = init.then(activate)
    .then(stageRollback).then(commitRollback(Unknown)).then(all {
      assert(uncertainSelectionObserved and not(canStart(s)) and
        not(canStage(s)) and safety),s'=s})
  run readReconcilesUnknownTest = init.then(activate).then(stageRollback)
    .then(commitRollback(Unknown)).then(observe).then(startSelected)
    .then(all {assert(failedHostRecovered and s.rollbacks==1 and safety),s'=s})
  run repeatedRollbackIsNoOpTest = init.then(activate).then(stageRollback)
    .then(commitRollback(Applied)).then(all {assert(not(canStage(s)) and
      s.rollbacks==1 and s.generation==3 and safety),s'=s})
}
