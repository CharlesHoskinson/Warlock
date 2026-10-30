// Bounded, local Elm receipt bookkeeping abstraction; see HANDOFF.md.
module ReceiptLifecycle {
  type Status = Empty | Pending | Unknown | Committed | Refused
  type Audit = {receipt: bool, key: int, terminal: bool, scene: int,
    request: int, generation: int, sends: int, otherCurrent: int, otherStatus: Status, outcome: Status}
  type State = {connected: bool, scene: int, request: int, generation: int, sends: int,
    current: int, currentStatus: Status, oldPresent: bool, oldStatus: Status, oldIssued: bool,
    newPresent: bool, newStatus: Status, newIssued: bool, audit: Audit}
  var s: State
  pure def quiet(x: State): State = {...x, audit: {...x.audit, receipt: false}}
  pure def issued(x: State, key: int): bool = if (key == 1) x.oldIssued else if (key == 2) x.newIssued else false
  pure def present(x: State, key: int): bool = if (key == 1) x.oldPresent else if (key == 2) x.newPresent else false
  // Key is an opaque full intent, including output context; binding=1 and protocol=1 are separate guards.
  pure def matches(x: State, binding: int, protocol: int, key: int): bool =
    binding == 1 and protocol == 1 and issued(x, key) and present(x, key)
  pure def auditBefore(x: State, key: int, status: Status): Audit =
    {receipt: true, key: key, terminal: status != Unknown, outcome: status, scene: x.scene,
      request: x.request, generation: x.generation, sends: x.sends,
      otherCurrent: if (x.current != key) x.current else 0, otherStatus: x.currentStatus}
  action init = s' = {connected: true, scene: 1, request: 0, generation: 0, sends: 0,
    current: 0, currentStatus: Empty, oldPresent: false, oldStatus: Empty, oldIssued: false,
    newPresent: false, newStatus: Empty, newIssued: false,
    audit: {receipt: false, key: 0, terminal: false, scene: 1, request: 0,
      generation: 0, sends: 0, otherCurrent: 0, otherStatus: Empty, outcome: Empty}}
  action beginOld = all {s.connected, s.scene == 1, s.current == 0, s.request == 0,
    s' = {...quiet(s), request: 1, generation: 1, sends: s.sends + 1,
      current: 1, currentStatus: Pending, oldPresent: true, oldStatus: Pending, oldIssued: true}}
  // Same bound lifetime/epoch; a new observed output does not imply terminal outcome.
  action changeOutput = all {s.connected, s.scene == 1,
    s' = {...quiet(s), scene: 2, currentStatus: if (s.currentStatus == Pending) Unknown else s.currentStatus}}
  // Different target: old unresolved target remains blocked, but current Unknown is not global Pending.
  action beginNew = all {s.connected, s.scene == 2, s.request == 1, s.currentStatus != Pending,
    s' = {...quiet(s), request: 2, generation: 2, sends: s.sends + 1,
      current: 2, currentStatus: Pending, newPresent: true, newStatus: Pending, newIssued: true}}
  pure def result(x: State, key: int, status: Status, broken: bool): State = {
    val terminal = status != Unknown
    val sameOutput = if (key == 1) x.scene == 1 else x.scene == 2
    val applyCurrent = x.current == key and (not(broken) or sameOutput)
    {...x, audit: auditBefore(x, key, status),
      currentStatus: if (applyCurrent) status else x.currentStatus,
      oldPresent: if (key == 1 and terminal) false else x.oldPresent,
      oldIssued: if (key == 1 and terminal) false else x.oldIssued,
      oldStatus: if (key == 1) status else x.oldStatus,
      newPresent: if (key == 2 and terminal) false else x.newPresent,
      newIssued: if (key == 2 and terminal) false else x.newIssued,
      newStatus: if (key == 2) status else x.newStatus}
  }
  action receive(binding: int, protocol: int, key: int, status: Status): bool = all {
    matches(s, binding, protocol, key), status == Committed or status == Refused or status == Unknown,
    s' = result(s, key, status, false)}
  // Separate baseline counterexample; deliberately excluded from step.
  action brokenReceiveOld = all {matches(s, 1, 1, 1), s' = result(s, 1, Committed, true)}
  action ignored(binding: int, protocol: int, key: int): bool = all {
    not(matches(s, binding, protocol, key)), s' = quiet(s)}
  action disconnect = all {s.connected,
    s' = {...quiet(s), connected: false,
      currentStatus: if (s.currentStatus == Pending) Unknown else s.currentStatus,
      oldStatus: if (s.oldPresent and s.oldStatus == Pending) Unknown else s.oldStatus,
      newStatus: if (s.newPresent and s.newStatus == Pending) Unknown else s.newStatus}}
  // Validated exact unknown observation (the validation and proof are external assumptions).
  action recoverOld = all {s.oldPresent, s.oldIssued,
    s' = {...quiet(s), oldStatus: Unknown,
      currentStatus: if (s.current == 1 and s.currentStatus == Pending) Unknown else s.currentStatus}}
  action releaseOld = all {s.oldPresent, s.oldStatus == Unknown, s.oldIssued,
    s' = {...quiet(s), oldPresent: false, oldIssued: false}}
  action step = any {beginOld, changeOutput, beginNew, receive(1, 1, 1, Committed),
    receive(1, 1, 1, Refused), receive(1, 1, 1, Unknown), receive(1, 1, 2, Committed),
    receive(1, 1, 2, Refused), receive(1, 1, 2, Unknown), ignored(2, 1, 1),
    ignored(1, 2, 1), ignored(1, 1, 3), disconnect, recoverOld, releaseOld}
  val receiptPreservesSceneCounters = s.audit.receipt implies
    s.scene == s.audit.scene and s.request == s.audit.request and s.generation == s.audit.generation and s.sends == s.audit.sends
  val otherCurrentPreserved = s.audit.receipt and s.audit.otherCurrent != 0 implies
    s.current == s.audit.otherCurrent and s.currentStatus == s.audit.otherStatus
  val exactCurrentTerminalSettled = s.audit.receipt and s.audit.terminal and s.current == s.audit.key implies
    s.currentStatus == s.audit.outcome
  val pendingHasReservation = (s.oldPresent implies s.oldIssued) and (s.newPresent implies s.newIssued)
  val bounded = s.request <= 2 and s.generation <= 2 and s.sends <= 2
}
