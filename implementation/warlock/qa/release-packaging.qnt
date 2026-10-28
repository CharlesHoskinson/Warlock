module release_packaging {
  type Phase = Start | Locked | Verified | Staged | Reviewed | Reverified | Manifested | Archived | Done | Refused
  type State = { phase: Phase, lock: int, input: int, payload: int, reviewed: int, manifest: int, archive: int, old: bool, unknown: bool, unmapped: bool, metadata: bool, audited: bool, output: bool }
  var s: State
  action init = s' = { phase: Start, lock: 1, input: 1, payload: 1, reviewed: 0, manifest: 0, archive: 0, old: false, unknown: false, unmapped: false, metadata: false, audited: false, output: false }
  action lockCheck = all { s.phase == Start and not(s.old), s' = { ...s, phase: Locked } }
  action verifyInitial = all { s.phase == Locked and s.input == s.lock, s' = { ...s, phase: Verified } }
  action stage = all { s.phase == Verified and s.input == s.lock, s' = { ...s, phase: Staged, output: true, payload: s.input } }
  action review = all { s.phase == Staged and not(s.unknown) and not(s.unmapped), s' = { ...s, phase: Reviewed, reviewed: s.payload, metadata: true } }
  action verifyAgain = all { s.phase == Reviewed and s.input == s.lock, s' = { ...s, phase: Reverified } }
  action makeManifest = all { s.phase == Reverified, s' = { ...s, phase: Manifested, manifest: s.payload } }
  action makeArchive = all { s.phase == Manifested, s' = { ...s, phase: Archived, archive: s.payload } }
  action audit = all { s.phase == Archived and s.archive == s.payload and s.manifest == s.payload and s.reviewed == s.payload and s.metadata and s.input == s.lock and not(s.unknown) and not(s.unmapped), s' = { ...s, phase: Done, audited: true } }
  action mutateInput = all { s.phase != Done and s.phase != Refused, s' = { ...s, input: s.input + 1 } }
  action mutatePayload = all { s.output and s.phase != Done and s.phase != Refused, s' = { ...s, payload: s.payload + 1 } }
  action introduceUnknown = all { s.phase != Done and s.phase != Refused, s' = { ...s, unknown: true } }
  action introduceUnmapped = all { s.phase != Done and s.phase != Refused, s' = { ...s, unmapped: true } }
  action ageLock = all { s.phase == Start, s' = { ...s, old: true } }
  action mutateMetadata = all { s.metadata and s.phase != Done and s.phase != Refused, s' = { ...s, metadata: false } }
  action refuse = all { s.phase != Done and s.phase != Refused and (s.old or s.input != s.lock or s.unknown or s.unmapped or (s.phase == Archived and (s.reviewed != s.payload or s.manifest != s.payload or s.archive != s.payload or not(s.metadata)))), s' = { ...s, phase: Refused } }
  action recover = all { s.phase == Refused, s' = { ...s, phase: Start, lock: s.input, payload: s.input, reviewed: 0, manifest: 0, archive: 0, old: false, unknown: false, unmapped: false, metadata: false, audited: false, output: false } }
  val successSafe = s.phase == Done implies all { s.audited, s.metadata, s.input == s.lock, s.reviewed == s.payload, s.manifest == s.payload, s.archive == s.payload, not(s.old), not(s.unknown), not(s.unmapped) }
  val oldLockBeforeOutput = s.old implies not(s.output)
  action step = any { lockCheck, verifyInitial, stage, review, verifyAgain, makeManifest, makeArchive, audit, mutateInput, mutatePayload, introduceUnknown, introduceUnmapped, ageLock, mutateMetadata, refuse, recover }
}
