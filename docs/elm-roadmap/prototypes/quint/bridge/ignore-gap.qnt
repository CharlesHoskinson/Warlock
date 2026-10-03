module bridge {
  type State = {
    epoch: int, incarnation: int, revision: int, seq: int, barrier: bool,
    reqId: int, reqEpoch: int, reqIncarnation: int, reqRevision: int,
    reqDeadline: int, clock: int, status: str, used: Set[int],
    effects: int, commits: Set[int], unsafe: bool, dependency: str,
    depEpoch: int, depIncarnation: int, depRevision: int,
    dependentEffects: int, badDependency: bool
  }
  var s: State
  action init = s' = {
    epoch: 1, incarnation: 1, revision: 1, seq: 0, barrier: false,
    reqId: 0, reqEpoch: 0, reqIncarnation: 0, reqRevision: 0,
    reqDeadline: 0, clock: 0, status: "Idle", used: Set(),
    effects: 0, commits: Set(), unsafe: false, dependency: "Pending",
    depEpoch: 1, depIncarnation: 1, depRevision: 1,
    dependentEffects: 0, badDependency: false
  }
  pure def terminal(status) = Set("Committed", "Refused", "Cancelled", "Unknown").contains(status)
  val fresh = s.reqEpoch == s.epoch and s.reqIncarnation == s.incarnation and s.reqRevision == s.revision
  val admissible = fresh and not(s.barrier) and s.clock < s.reqDeadline and not(s.commits.contains(s.reqId))
  action request(id) = all {
    s.status != "Pending", id > 0,
    s' = if (s.used.contains(id) or s.barrier) s.with("status", "Refused")
      else { ...s, reqId: id, reqEpoch: s.epoch, reqIncarnation: s.incarnation,
        reqRevision: s.revision, reqDeadline: s.clock + 3, status: "Pending", used: s.used.union(Set(id)) }
  }
  // One atomic native linearization point; cancellation after commit cannot undo it.
  action commit = all {
    s.status == "Pending",
    s' = if (admissible) { ...s, status: "Committed", effects: s.effects + 1,
      commits: s.commits.union(Set(s.reqId)), unsafe: s.unsafe or not(admissible) }
      else s.with("status", "Refused")
  }
  action cancel = s' = if (s.status == "Pending") s.with("status", "Cancelled") else s
  // Losing a receipt is uncertainty, not permission to replay or dispatch dependencies.
  action loseReceipt = all { s.status == "Committed", s' = s.with("status", "Unknown") }
  action restart = s' = { ...s, epoch: s.epoch + 1, barrier: true,
    status: if (s.status == "Pending") "Unknown" else s.status, dependency: "Unknown" }
  action advanceEpoch = s' = s.with("epoch", s.epoch + 1)
  action replaceWindow = s' = { ...s, incarnation: s.incarnation + 1 }
  action mutateDependency = s' = s.with("revision", s.revision + 1)
  action delta(n) = all {
    n > s.seq,
    s' = if (s.barrier or false) s.with("barrier", true) else s.with("seq", n)
  }
  action snapshot(n) = all { n >= s.seq, s' = { ...s, seq: n, barrier: false } }
  action tick = s' = s.with("clock", s.clock + 1)
  action prerequisite(outcome) = all {
    Set("Pending", "Committed", "Refused", "Cancelled", "Unknown").contains(outcome),
    s' = { ...s, dependency: outcome, depEpoch: s.epoch, depIncarnation: s.incarnation, depRevision: s.revision }
  }
  val dependencyReady = s.dependency == "Committed" and not(s.barrier) and s.depEpoch == s.epoch and s.depIncarnation == s.incarnation and s.depRevision == s.revision
  action dispatchDependent = s' = if (dependencyReady)
    { ...s, dependentEffects: s.dependentEffects + 1,
      badDependency: s.badDependency or not(dependencyReady) }
    else s
  action noop = s' = s
  action step = any {
    request(1), request(2), commit, cancel, loseReceipt, restart,
    advanceEpoch, replaceWindow, mutateDependency, delta(s.seq + 1), delta(s.seq + 2),
    snapshot(s.seq + 2), tick, prerequisite("Committed"), prerequisite("Unknown"),
    prerequisite("Refused"), dispatchDependent, noop
  }
  val safety = not(s.unsafe) and not(s.badDependency) and s.effects == s.commits.size()
  run freshCommitTest = init.then(request(1)).then(commit).then(all { assert(s.status == "Committed" and s.effects == 1), noop })
  run incarnationReuseTest = init.then(request(1)).then(replaceWindow).then(commit).then(all { assert(s.status == "Refused" and s.effects == 0), noop })
  run revisionChangeTest = init.then(request(1)).then(mutateDependency).then(commit).then(all { assert(s.status == "Refused"), noop })
  run nativeEpochChangedTest = init.then(request(1)).then(advanceEpoch).then(commit).then(all { assert(s.status == "Refused" and s.effects == 0), noop })
  run epochRestartTest = init.then(request(1)).then(restart).then(snapshot(2)).then(all { assert(s.status == "Unknown" and s.effects == 0), noop })
  run gapBarrierTest = init.then(request(1)).then(delta(2)).then(commit).then(all { assert(s.status == "Refused" and s.seq == 0), noop })
  run snapshotFreshRequestTest = init.then(delta(2)).then(snapshot(2)).then(request(1)).then(commit).then(all { assert(s.status == "Committed"), noop })
  run cancelBeforeCommitTest = init.then(request(1)).then(cancel).then(all { assert(s.status == "Cancelled" and s.effects == 0), noop })
  run cancelAfterCommitTest = init.then(request(1)).then(commit).then(cancel).then(all { assert(s.status == "Committed" and s.effects == 1), noop })
  run duplicateCommitTest = init.then(request(1)).then(commit).then(request(1)).then(all { assert(s.status == "Refused" and s.effects == 1), noop })
  run expiredDeadlineTest = init.then(request(1)).then(tick).then(tick).then(tick).then(commit).then(all { assert(s.status == "Refused" and s.effects == 0), noop })
  run unknownDependencyTest = init.then(prerequisite("Unknown")).then(dispatchDependent).then(all { assert(s.dependentEffects == 0), noop })
  run committedDependencyTest = init.then(prerequisite("Committed")).then(dispatchDependent).then(all { assert(s.dependentEffects == 1), noop })
  run staleDependencyTest = init.then(prerequisite("Committed")).then(replaceWindow).then(dispatchDependent).then(all { assert(s.dependentEffects == 0), noop })
  run refusedDependencyTest = init.then(prerequisite("Refused")).then(dispatchDependent).then(all { assert(s.dependentEffects == 0), noop })
  run cancelledDependencyTest = init.then(prerequisite("Cancelled")).then(dispatchDependent).then(all { assert(s.dependentEffects == 0), noop })
  run pendingDependencyTest = init.then(prerequisite("Pending")).then(dispatchDependent).then(all { assert(s.dependentEffects == 0), noop })
  run lostReceiptNoReplayTest = init.then(request(1)).then(commit).then(loseReceipt).then(request(1)).then(all { assert(s.status == "Refused" and s.effects == 1), noop })
}
