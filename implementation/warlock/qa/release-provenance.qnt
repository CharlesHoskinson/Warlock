module release_provenance {
  type State = { source: int, pinnedSource: int, notice: int, pinnedNotice: int,
    hasNotice: bool, disposition: int, applicability: int, decision: int,
    observedSource: int, observedPin: int, observedNotice: int, observedNoticePin: int,
    observedHasNotice: bool, observedDisposition: int, observedApplicability: int,
    sourceChanged: bool, noticeChanged: bool, dispositionChanged: bool,
    restored: bool, applicabilityChanged: bool, reviewed: bool, refused: bool, accepted: bool }
  var s: State
  action init = s' = { source: 1, pinnedSource: 1, notice: 1, pinnedNotice: 1,
    hasNotice: true, disposition: 1, applicability: 0, decision: 0,
    observedSource: 0, observedPin: 0, observedNotice: 0, observedNoticePin: 0,
    observedHasNotice: false, observedDisposition: 0, observedApplicability: 0,
    sourceChanged: false, noticeChanged: false, dispositionChanged: false,
    restored: false, applicabilityChanged: false, reviewed: false, refused: false, accepted: false }
  action mutateSource = { nondet value = Set(0, 2).oneOf() s' = { ...s, source: value, sourceChanged: true } }
  action mutateNotice = { nondet value = Set(0, 2).oneOf() s' = { ...s, notice: value, noticeChanged: true } }
  action changeDisposition = { nondet value = Set(0, 1).oneOf() s' = { ...s, disposition: value, dispositionChanged: true } }
  action changeApplicability = { nondet present = Set(true, false).oneOf() nondet status = Set(0, 1).oneOf() s' = { ...s, hasNotice: present, applicability: status, applicabilityChanged: true } }
  action restore = s' = { ...s, source: 1, notice: 1, disposition: 1, hasNotice: true, restored: true }
  action review = { val good = s.source != 0 and s.source == s.pinnedSource and s.disposition == 1 and (if (s.hasNotice) s.notice != 0 and s.notice == s.pinnedNotice else s.applicability == 1) s' = { ...s, decision: if (good) 1 else 2, observedSource: s.source, observedPin: s.pinnedSource, observedNotice: s.notice, observedNoticePin: s.pinnedNotice, observedHasNotice: s.hasNotice, observedDisposition: s.disposition, observedApplicability: s.applicability, reviewed: true, accepted: s.accepted or good, refused: s.refused or not(good) } }
  // Decision is a snapshot, not a guarantee that mutable files remain unchanged.
  val safety = s.decision == 1 implies and {
    s.observedSource != 0, s.observedSource == s.observedPin,
    s.observedDisposition == 1,
    if (s.observedHasNotice) s.observedNotice != 0 and s.observedNotice == s.observedNoticePin
    else s.observedApplicability == 1
  }
  val sourceMutationSeen = s.sourceChanged
  val noticeMutationSeen = s.noticeChanged
  val dispositionChangeSeen = s.dispositionChanged
  val applicabilityChangeSeen = s.applicabilityChanged
  val restorationSeen = s.restored
  val acceptanceSeen = s.accepted
  val refusalSeen = s.refused
  val recoverySeen = s.refused and s.restored and s.decision == 1
  action step = any { mutateSource, mutateNotice, changeDisposition, changeApplicability, restore, review }
}
