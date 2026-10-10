module committed_press {
  // ELM-REN-015/max-input-region, additional no-activation exception.
  // One serialized native seat, two overlapping MAX roots, one button.
  // Atomic shape/commit/press/release steps; no timing, ABI, grab, layer,
  // lock, constraint, popup, transform, presentation or actual seat proof.
  type State = { ready: bool, eligible: List[bool], cached: int,
    focused: int, owner: int, suppressed: bool,
    presses: int, releases: int, refused: int, swallowed: int,
    lastPress: int, lastRelease: int, wrongPress: int, wrongRelease: int }
  var s: State
  pure def recipient(now: State): int =
    if (now.eligible[1]) 1 else if (now.eligible[0]) 0 else -1
  action init = s' = { ready: true, eligible: [true, true], cached: 1,
    focused: 1, owner: -1, suppressed: false,
    presses: 0, releases: 0, refused: 0, swallowed: 0,
    lastPress: -1, lastRelease: -1, wrongPress: 0, wrongRelease: 0 }
  // Admission models only the ordinary MAX branch. For an admitted press the
  // existing native refocus/seat path is assumed to select the eligible root;
  // cached-surface mismatch for an eligible root is a separate obligation.
  pure def refuse(now: State): bool = not(now.ready) or recipient(now) == -1
  pure def pressUpdate(now: State): State =
    if (refuse(now)) { ...now, suppressed: true, refused: now.refused + 1 }
    else { ...now, owner: recipient(now), focused: recipient(now),
      lastPress: recipient(now), presses: now.presses + 1 }
  pure def releaseUpdate(now: State): State =
    if (now.suppressed) { ...now, suppressed: false, swallowed: now.swallowed + 1 }
    else { ...now, lastRelease: now.owner, owner: -1,
      releases: now.releases + 1 }
  action shape(lower: bool, upper: bool): bool = s' = { ...s,
    eligible: [lower, upper], ready: false }
  action commit = s' = { ...s, ready: true }
  action cache(id: int): bool = s' = { ...s, cached: id }
  action press = all { s.owner == -1, not(s.suppressed), s' = pressUpdate(s) }
  action release = all { s.owner != -1 or s.suppressed, s' = releaseUpdate(s) }
  // Counterexample to the old fallthrough: ready/no-hit still sends to cache.
  action legacyNoHitPress = all { s.ready, recipient(s) == -1,
    s.owner == -1, not(s.suppressed), s.cached != -1,
    s' = { ...s, owner: s.cached, focused: s.cached,
      lastPress: s.cached, presses: s.presses + 1, wrongPress: s.wrongPress + 1 } }
  action step = any { shape(true,true), shape(true,false), shape(false,false),
    commit, cache(0), cache(1), cache(-1), press, release }
  val safety = s.wrongPress == 0 and s.wrongRelease == 0 and
    s.presses - s.releases == (if (s.owner == -1) 0 else 1) and
    s.refused - s.swallowed == (if (s.suppressed) 1 else 0) and
    not(s.suppressed and s.owner != -1)
  val lowerReceived = s.lastPress == 0 and s.presses > 0
  val noHitSuppressed = s.ready and recipient(s) == -1 and s.suppressed and s.presses == 0
  val releaseAfterShape = s.lastRelease != -1 and not(s.ready)
  val suppressedRelease = s.swallowed > 0 and s.presses == 0
}
