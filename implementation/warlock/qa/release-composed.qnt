module release_composed {
  type Phase = Idle | Reviewed | Packaged | Audited | Reported
  type State = { phase: Phase, revision: int, reviewRev: int, packageRev: int, auditRev: int,
    coverage: bool, evidence: bool, locked: bool, identity: bool, outcome: bool }
  var s: State
  action init = s' = { phase: Idle, revision: 0, reviewRev: -1, packageRev: -1, auditRev: -1,
    coverage: false, evidence: false, locked: false, identity: false, outcome: false }
  action cover = all { s.phase == Idle, s' = {...s, coverage: true} }
  action reviewEvidence = all { s.phase == Idle, s' = {...s, evidence: true} }
  action lockInputs = all { s.phase == Idle, s' = {...s, locked: true} }
  action establishIdentity = all { s.phase == Idle, s' = {...s, identity: true} }
  action review = all { s.phase == Idle, s.coverage, s.evidence, s' = {...s, phase: Reviewed, reviewRev: s.revision} }
  action package = all { s.phase == Reviewed, s.locked, s.reviewRev == s.revision, s' = {...s, phase: Packaged, packageRev: s.revision} }
  action audit = all { s.phase == Packaged, s.identity, s.packageRev == s.revision, s' = {...s, phase: Audited, auditRev: s.revision} }
  action report = all { s.phase == Audited, s' = {...s, phase: Reported, outcome: true} }
  action mutate = all { s.revision < 2, s' = {...s, revision: s.revision + 1, coverage: false, evidence: false, locked: false, identity: false} }
  action step = any { cover, reviewEvidence, lockInputs, establishIdentity, review, package, audit, report, mutate }
  val safeReceipt = not(s.outcome) or (s.auditRev == s.packageRev and s.packageRev == s.reviewRev and s.reviewRev >= 0)
  // Deliberately false under external mutation: retained as a race probe.
  val currentOutcome = not(s.outcome) or s.auditRev == s.revision
}
