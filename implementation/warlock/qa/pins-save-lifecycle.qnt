module pins_save_lifecycle {
  // One Elm authority; read issuance and delivery are separate atomic steps.
  // IDs 1..8 are opaque, fresh labels within an abstract binding epoch.
  // Revision 1..3 represents ordering only, not the UInt64 implementation.
  var s: { phase: str, next: int, reads: Set[int], recovery: int,
    write: int, base: int, proposal: int, revision: int, order: int,
    available: bool, sent: Set[int], intents: int, last: str,
    saved: Set[int], recovered: Set[int], beforeWrite: Set[int] }

  action init = s' = { phase: "Idle", next: 1, reads: Set(), recovery: 0,
    write: 0, base: 0, proposal: 0, revision: 1, order: 1,
    available: true, sent: Set(), intents: 0, last: "init",
    saved: Set(), recovered: Set(), beforeWrite: Set() }

  action readStart = all {
    s.next <= 8,
    s' = { ...s, next: s.next + 1, reads: s.reads.union(Set(s.next)),
      recovery: if (s.phase == "Unknown") s.next else s.recovery, last: "readStart" }
  }
  action intent(value: int): bool = all {
    s.phase == "Idle", s.available, s.next <= 8, s.revision < 3,
    Set(1, 2).contains(value), value != s.order,
    s' = { ...s, phase: "Saving", write: s.next, base: s.revision,
      proposal: value, next: s.next + 1, sent: s.sent.union(Set(s.next)),
      intents: s.intents + 1, beforeWrite: s.reads, last: "intent" }
  }
  // A delivery is independently typed/validated before this action. None is
  // represented by present=false. A stale recovery snapshot cannot settle.
  action readResult(id: int, present: bool, rev: int, value: int): bool = all {
    s.reads.contains(id), Set(1, 2, 3).contains(rev), Set(1, 2).contains(value),
    s' = if (s.phase == "Saving" or (s.phase == "Unknown" and
          (s.recovery != id or (present and rev < s.revision))))
      { ...s, reads: s.reads.exclude(Set(id)),
        recovery: if (s.recovery == id) 0 else s.recovery,
        last: if (s.phase == "Saving" and s.beforeWrite.contains(id)) "predecessorHeld" else "readHeld" }
    else if (s.phase == "Unknown")
      { ...s, phase: "Idle", recovery: 0, reads: s.reads.exclude(Set(id)),
        available: present, revision: if (present) rev else s.revision,
        order: if (present) value else s.order,
        recovered: s.recovered.union(Set(s.write)), write: 0, base: 0,
        proposal: 0, last: "recovered" }
    else if (present and rev < s.revision)
      { ...s, reads: s.reads.exclude(Set(id)), last: "staleRead" }
    else
      { ...s, reads: s.reads.exclude(Set(id)), available: present,
        revision: if (present) rev else s.revision,
        order: if (present) value else s.order, last: "observed" }
  }
  action saved(id: int, rev: int, value: int): bool = all {
    Set(1, 2, 3).contains(rev), Set(1, 2).contains(value),
    s' = if (s.phase != "Idle" and id == s.write and
      value == s.proposal and rev > s.base and rev > s.revision)
      { ...s, phase: "Idle", revision: rev, order: value, available: true,
        saved: s.saved.union(Set(id)), write: 0, base: 0, proposal: 0,
        recovery: 0, last: "saved" }
    else if (s.phase == "Saving" and id == s.write)
      { ...s, phase: "Unknown", recovery: 0, last: "invalidSaved" }
    else { ...s, last: "wrongSaved" }
  }
  action refused(id: int): bool = all {
    s' = if (s.phase != "Idle" and id == s.write)
      { ...s, phase: "Idle", write: 0, base: 0, proposal: 0,
        recovery: 0, last: "refused" }
    else { ...s, last: "wrongRefused" }
  }
  action unknown(id: int): bool = all {
    s' = if (s.phase == "Saving" and id == s.write)
      { ...s, phase: "Unknown", recovery: 0, last: "unknown" }
    else { ...s, last: "duplicateUnknown" }
  }
  // A typed nullable Saved payload supplies no confirmation. Foreign IDs are
  // inert; repeated matching failures never erase an already-issued recovery.
  action nullSavedProof(id: int): bool = unknown(id)
  // A rejected boundary is observable, but cannot mutate policy or dispatch.
  action invalidInput = s' = { ...s, last: "invalid" }
  // New binding epoch, only after all modeled reads and the write are retired.
  // Old-epoch messages are foreign and must enter invalidInput, not these actions.
  action reset = all { s.phase == "Idle", s.reads == Set(), init }

  action step = {
    nondet id = Set(1, 2, 3, 4, 5, 6, 7, 8).oneOf()
    nondet present = Set(true, false).oneOf()
    nondet revision = Set(1, 2, 3).oneOf()
    nondet value = Set(1, 2).oneOf()
    any { readStart, intent(value), readResult(id, present, revision, value),
      saved(id, revision, value), refused(id), unknown(id), nullSavedProof(id), invalidInput, reset }
  }
  val singleAuthority = (s.phase == "Idle") == (s.write == 0) and
    (s.phase == "Unknown" or s.recovery == 0) and
    (s.recovery == 0 or s.reads.contains(s.recovery))
  val noReplay = s.sent.size() == s.intents and s.saved.intersect(s.recovered) == Set()
  val revisionCAS = s.revision >= 1 and s.revision <= 3 and
    (s.phase == "Idle" or (s.base == s.revision and s.base < 3))
  val requestCorrelation = (s.write == 0 or s.sent.contains(s.write)) and
    (s.recovery == 0 or not(s.sent.contains(s.recovery)))
  val safety = singleAuthority and noReplay and revisionCAS and requestCorrelation
  val savingWitness = s.phase == "Saving"
  val predecessorReadRefusedAsSettlementWitness = s.phase == "Saving" and s.last == "predecessorHeld"
  val matchedSavedWitness = s.last == "saved"
  val unknownHeldWitness = s.phase == "Unknown"
  val newRecoveryReadWitness = s.phase == "Unknown" and s.recovery != 0
  val recoveredFreshIntentWitness = s.phase == "Saving" and s.recovered.size() > 0
  val noReplayWitness = s.recovered.size() > 0 and s.sent.size() == s.intents
}
