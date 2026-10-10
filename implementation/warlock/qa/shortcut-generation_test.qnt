module shortcut_generation_test {
  import shortcut_generation.* from "./shortcut-generation"
  action check(condition: bool): bool = all {assert(condition),native'=native,view'=view,observed'=observed,ready'=ready,held'=held,seen'=seen,opened'=opened,retiredAdoption'=retiredAdoption}
  run delayedOldReplyTest = init.then(press).then(retire).then(replace).then(reconcile).then(deliver).then(check(staleConsumed and safety))
  run unreconciledReplyConsumedTest = init.then(press).then(retire).then(replace).then(deliver).then(reconcile).then(deliver).then(check(staleConsumed and safety))
  run oldObservationCannotReviveTest = init.then(press).then(retire).then(replace).then(oldObservation).then(check(not(ready))).then(deliver).then(check(staleConsumed and safety))
  run freshReplacementWorksTest = init.then(press).then(retire).then(replace).then(reconcile).then(deliver).then(freshPress).then(deliver).then(check(freshOpened and safety))
  run duplicateCannotReplayTest = init.then(press).then(retire).then(replace).then(reconcile).then(deliver).then(deliver).then(check(staleConsumed and safety))
  run legacyCounterexampleTest = init.then(press).then(retire).then(replace).then(reconcile).then(deliverLegacy).then(check(retiredAdoption and opened))
}
