module menu_focus {
  // Desktop.window keeps the admitted inactive-minimize origin while its group
  // is blocked. Only a fresh eligible observation emits Focus, once. Native
  // keyboard/pointer delivery remains a separately observed product oracle.
  var s: { pending: bool, blocked: bool, current: bool, eligible: bool, generation: int, delivered: Set[int], violations: int }
  action init = s' = { pending: false, blocked: false, current: true, eligible: true, generation: 0, delivered: Set(), violations: 0 }
  action inactiveMinimize = all {
    not(s.pending) and s.current and s.eligible,
    s' = { ...s, pending: true, blocked: true, generation: s.generation + 1 }
  }
  action activeMinimize = all {
    not(s.pending),
    s' = { ...s, blocked: true }
  }
  action invalidSelection = s' = s
  action settle = s' = { ...s, blocked: false }
  action staleRead = s' = s
  action currentRead = s' = if (s.pending and not(s.blocked)) {
    ...s, pending: false,
    delivered: if (s.current and s.eligible) s.delivered.union(Set(s.generation)) else s.delivered,
    violations: s.violations + (if (s.current and s.eligible and s.delivered.contains(s.generation)) 1 else 0)
  } else s
  action retireOrigin = s' = { ...s, pending: false, current: false }
  action removeGroup = s' = { ...s, eligible: false }
  action step = any { inactiveMinimize, activeMinimize, invalidSelection, settle, staleRead, currentRead, retireOrigin, removeGroup }
  val safety = s.violations == 0 and (not(s.pending) or s.current)
  run unresolvedWaitsTest = init.then(inactiveMinimize).then(currentRead).then(all { assert(s.pending and s.delivered == Set()), s' = s })
  run currentSettlementReturnsOnceTest = init.then(inactiveMinimize).then(settle).then(staleRead).then(all { assert(s.delivered == Set()), s' = s }).then(currentRead).then(currentRead).then(all { assert(s.delivered == Set(1) and not(s.pending)), s' = s })
  run activeMinimizeCannotStealSuccessorTest = init.then(activeMinimize).then(settle).then(currentRead).then(all { assert(s.delivered == Set()), s' = s })
  run retiredOriginCannotReceiveFocusTest = init.then(inactiveMinimize).then(retireOrigin).then(settle).then(currentRead).then(all { assert(s.delivered == Set()), s' = s })
  run removedGroupCannotReceiveFocusTest = init.then(inactiveMinimize).then(removeGroup).then(settle).then(currentRead).then(all { assert(s.delivered == Set() and not(s.pending)), s' = s })
  run invalidSelectionCannotCreateIntentTest = init.then(invalidSelection).then(settle).then(currentRead).then(all { assert(not(s.pending) and s.delivered == Set()), s' = s })
}
