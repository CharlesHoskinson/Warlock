// Initial ordering scaffold only; stale and cancellation races are stage 2.
module dom_opener {
  type State = {
    policy: str, captured: bool, nativeRelease: bool, documentRelease: bool,
    sent: bool, forwarded: bool,
  }
  var s: State
  action init: bool = s' = { policy: "unset", captured: false, nativeRelease: false,
    documentRelease: false, sent: false, forwarded: false }
  // Old JS sends immediately at keydown; candidate captures only.
  action captureOld: bool = all {
    s.policy == "unset", s' = { ...s, policy: "old", captured: true, sent: true },
  }
  action captureCandidate: bool = all {
    s.policy == "unset", s' = { ...s, policy: "candidate", captured: true },
  }
  // Native receipt is distinct from delivery to the original DOM document.
  action gdkRelease: bool = all {
    s.captured, not(s.nativeRelease),
    s' = { ...s, nativeRelease: true },
  }
  // Stage 1 assumes trusted release, matching key/code, focused control and
  // unchanged root/publication/lease. Candidate sends only at this event.
  action documentKeyup: bool = all {
    s.captured, s.nativeRelease, not(s.documentRelease),
    s' = { ...s, documentRelease: true,
      sent: if (s.policy == "candidate") true else s.sent },
  }
  // Current native/DOM proof is assumed valid at this initial stage.
  action nativeVerifyAndForward: bool = all {
    s.sent, not(s.forwarded), s' = { ...s, forwarded: true },
  }
  action step: bool = any { captureOld, captureCandidate, gdkRelease, documentKeyup, nativeVerifyAndForward }
  val candidateReleaseVerified: bool = s.policy == "candidate" and s.documentRelease and s.forwarded
  val oldBeforeDocumentKeyup: bool = s.policy == "old" and s.forwarded and not(s.documentRelease)
  val noOldBeforeDocumentKeyup: bool = not(oldBeforeDocumentKeyup)
  val candidateOnlyAfterDocumentKeyup: bool = s.policy == "candidate" and s.forwarded implies s.documentRelease
}
