module preoffer_retirement {
  // ELM-DEL-021/ELM-QA-011, FamilyProducer::command/retireUnoffered.
  // One exact job and its descriptor/exportOwned; coherent native stale facts and
  // lock-delayed retirement are abstracted. Transport/ABI/deadlines/actual FD
  // completion and WebKit delivery still require native evidence.
  type State = { phase: int, mapping: bool, exportOwned: bool, producer: bool,
    reservation: bool, journal: bool, locked: bool, sourceCurrent: bool,
    captures: int, offered: bool, closed: bool }
  var s: State
  pure def retired(x: State): bool = not(x.mapping) and not(x.exportOwned) and not(x.producer)
  action init = s' = { phase: 0, mapping: false, exportOwned: false, producer: false,
    reservation: true, journal: false, locked: false, sourceCurrent: true,
    captures: 0, offered: false, closed: false }
  action capture = all { s.phase == 0,
    s' = { ...s, phase: 1, mapping: true, exportOwned: true, producer: true, captures: 1 } }
  action sourceChanges = all { s.phase == 1, s' = { ...s, sourceCurrent: false } }
  action refuseStale = all { s.phase == 1 and not(s.sourceCurrent), s' = { ...s, phase: 2 } }
  action cancel = all { s.phase == 1, s' = { ...s, phase: 2 } }
  action lock = all { s.phase == 2, s' = { ...s, locked: true } }
  action unlock = s' = { ...s, locked: false }
  action closeMapping = all { s.phase == 2 and s.mapping, s' = { ...s, mapping: false } }
  action releaseExport = all { s.phase == 2 and not(s.mapping) and s.exportOwned,
    s' = { ...s, exportOwned: false } }
  action retireProducer = all { s.phase == 2 and not(s.mapping) and not(s.exportOwned) and not(s.locked),
    s' = { ...s, producer: false } }
  action publishRefusal = all { s.phase == 2 and retired(s),
    s' = { ...s, phase: 3, journal: true } }
  action acknowledge(exact: bool): bool = all { s.phase == 3,
    s' = if (exact) { ...s, phase: 4, journal: false, reservation: false } else s }
  action close = all { not(s.reservation) and not(s.journal) and retired(s),
    s' = { ...s, closed: true } }
  action attemptEarlyClose = all { s.reservation or s.journal or not(retired(s)), s' = s }
  action step = any { capture, sourceChanges, refuseStale, cancel, lock, unlock,
    closeMapping, releaseExport, retireProducer, publishRefusal, acknowledge(true),
    acknowledge(false), close, attemptEarlyClose }
  val safety = s.captures <= 1 and not(s.offered)
    and (s.phase < 3 or retired(s))
    and (not(s.closed) or (retired(s) and not(s.journal) and not(s.reservation)))
    and (s.exportOwned or not(s.mapping))
  val completedStaleRetirement = s.closed and not(s.sourceCurrent)
  val retainedLockedProducer = s.phase == 2 and s.locked and s.producer and not(s.mapping) and not(s.exportOwned)
  val awaitingExactAcknowledgement = s.phase == 3 and s.journal and s.reservation
}
