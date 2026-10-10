module menu_read_order_test {
  import menu_read_order.* from "./menu-read-order"
  run reorderedReadIssuesOnceTest = init.then(captureSelection).then(reorder).then(currentRead).then(settle)
    .then(all { assert(s.requests == 1 and s.issued and safety), s' = s })
  run changedPeerRefusesTest = init.then(captureSelection).then(changeWindow(2)).then(currentRead).then(settle)
    .then(all { assert(s.requests == 0 and s.rejected == 1 and safety), s' = s })
  run changedTargetRefusesTest = init.then(captureSelection).then(changeWindow(1)).then(currentRead).then(settle)
    .then(all { assert(s.requests == 0 and s.rejected == 1 and safety), s' = s })
  run changedScopeRefusesTest = init.then(captureSelection).then(changeScope).then(currentRead).then(settle)
    .then(all { assert(s.requests == 0 and s.rejected == 1 and safety), s' = s })
  run staleReadCannotIssueTest = init.then(captureSelection).then(reorder).then(staleRead)
    .then(all { assert(not(s.readReady) and s.requests == 0 and safety), s' = s })
  run unknownCannotReplayTest = init.then(captureSelection).then(reorder).then(currentRead).then(settle)
    .then(lostOutcome).then(retryUnknown).then(retryUnknown)
    .then(all { assert(s.requests == 1 and s.unknown and safety), s' = s })
}
