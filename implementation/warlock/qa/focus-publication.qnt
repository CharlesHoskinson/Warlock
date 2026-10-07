module focus_publication {
  // Bounded abstraction of the undelivered-focus carry. Issued focus is never
  // recreated by a publication; native target/owner/presentation proof is separate.
  var s: { pub: int, lease: int, closed: int, intent: int, pending: bool, issued: bool, valid: bool, delivered: Set[int], violations: int }
  action init = s' = { pub: 1, lease: 1, closed: 0, intent: 1, pending: true, issued: false, valid: true, delivered: Set(), violations: 0 }
  action refresh = s' = { ...s, pub: s.pub + 1, pending: s.pending and s.valid and s.lease > s.closed, issued: false }
  action issue = s' = if (s.pending and s.valid and s.lease > s.closed) { ...s, pending: false, issued: true, delivered: s.delivered.union(Set(s.intent)), violations: s.violations + (if (s.delivered.contains(s.intent)) 1 else 0) } else s
  action retire = s' = { ...s, pub: s.pub + 1, pending: false, issued: false, valid: false }
  action close = s' = { ...s, pub: s.pub + 1, closed: s.lease, pending: false, issued: false }
  action reopen = s' = { ...s, pub: s.pub + 1, lease: s.lease + 1, intent: s.intent + 1, pending: true, issued: false, valid: true }
  action staleAck = s' = s
  action step = any { refresh, issue, retire, close, reopen, staleAck }
  val safety = s.violations == 0 and (not(s.pending) or (s.valid and s.lease > s.closed))
  run pendingSurvivesPublicationTest = init.then(refresh).then(issue).then(all { assert(s.delivered == Set(1)), s' = s })
  run issuedNeverReplayedTest = init.then(issue).then(refresh).then(issue).then(all { assert(s.delivered == Set(1) and not(s.issued)), s' = s })
  run replacementCannotReceiveOldFocusTest = init.then(retire).then(refresh).then(issue).then(all { assert(s.delivered == Set()), s' = s })
  run closeCannotReviveFocusTest = init.then(close).then(refresh).then(issue).then(all { assert(s.delivered == Set()), s' = s })
  run staleAckCannotIssueFocusTest = init.then(issue).then(refresh).then(staleAck).then(all { assert(not(s.pending) and s.delivered == Set(1)), s' = s })
}
