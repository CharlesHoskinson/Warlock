// Proposed frontend behavior, not an implementation proof. See README.
module dom_opener {
  type Scope = { document: int, control: int, root: int, publication: int, lease: int, epoch: int, enabled: bool, connected: bool }
  type State = {
    current: Scope, captured: Scope, key: str, code: str, shifted: bool,
    phase: str, now: int, capturedAt: int, gdk: bool,
    sent: int, forwarded: int, nativeRejected: bool, emittedAt: int, verifiedAt: int, shiftBeforeKeyup: bool,
  }
  var s: State
  pure def sameDomScope(a: Scope, b: Scope): bool =
    a.document == b.document and a.control == b.control and a.root == b.root and
    a.publication == b.publication and a.lease == b.lease and
    a.enabled and a.connected and b.enabled and b.connected
  pure def sameNativeScope(a: Scope, b: Scope): bool = sameDomScope(a, b) and a.epoch == b.epoch
  action init: bool = {
    val scope = { document: 1, control: 1, root: 1, publication: 1, lease: 1, epoch: 1, enabled: true, connected: true }
    s' = { current: scope, captured: scope, key: "", code: "", shifted: false,
      phase: "idle", now: 1, capturedAt: 0, gdk: false,
      sent: 0, forwarded: 0, nativeRejected: false, emittedAt: 0, verifiedAt: 0, shiftBeforeKeyup: false }
  }
  action capture(key: str, code: str, shift: bool): bool = all {
    s.phase == "idle", (key == "ContextMenu" or (key == "F10" and shift)),
    s' = { ...s, phase: "captured", captured: s.current, key: key, code: code,
      shifted: shift, capturedAt: s.now },
  }
  // Native GDK admission is separate from delivery to the DOM.
  action nativeRelease: bool = all {
    s.phase == "captured", not(s.gdk), s' = { ...s, gdk: true },
  }
  // Shift can be released before or after F10. F10's own key/code remain fixed.
  action shiftUp: bool = all {
    s.key == "F10", s.shifted, s.phase != "done", s' = { ...s, shifted: false },
  }
  // An observed document keyup consumes the pending capture even if invalid.
  // Its shift modifier is deliberately not used to match the captured F10.
  action documentKeyup(key: str, code: str, trusted: bool, ctrl: bool, alt: bool, meta: bool): bool = all {
    s.phase == "captured", s.gdk,
    s' = if (trusted and not(ctrl) and not(alt) and not(meta) and key == s.key and code == s.code and sameDomScope(s.current, s.captured))
      { ...s, phase: "sent", sent: s.sent + 1, emittedAt: s.now, shiftBeforeKeyup: s.key == "F10" and not(s.shifted) }
      else { ...s, phase: "cancelled" },
  }
  action duplicateKeyup: bool = all {
    s.phase == "sent" or s.phase == "done" or s.phase == "cancelled",
    s' = s,
  }
  // Each environmental mutation is independent of the release and verification.
  action mutate(which: str): bool = all {
    s.phase == "captured" or s.phase == "sent",
    Set("document", "control", "root", "publication", "lease", "epoch", "disabled", "disconnected").contains(which),
    s' = { ...s, current: {
      ...s.current,
      document: if (which == "document") 2 else s.current.document,
      control: if (which == "control") 2 else s.current.control,
      root: if (which == "root") 2 else s.current.root,
      publication: if (which == "publication") 2 else s.current.publication,
      lease: if (which == "lease") 2 else s.current.lease,
      epoch: if (which == "epoch") 2 else s.current.epoch,
      enabled: if (which == "disabled") false else s.current.enabled,
      connected: if (which == "disconnected") false else s.current.connected } },
  }
  // Blur, composition, scroll, drag, new press and explicit cancel invalidate
  // the frontend capture; after send only modeled native-invalidating events apply.
  action cancel(reason: str): bool = all {
    s.phase == "captured" or s.phase == "sent",
    Set("blur", "composition", "scroll", "drag", "newPress", "cancel").contains(reason),
    (s.phase == "captured" or Set("blur", "scroll", "newPress").contains(reason)),
    s' = if (s.phase == "captured") { ...s, phase: "cancelled" }
      else { ...s, current: { ...s.current, epoch: 2 } },
  }
  // Time in microseconds: capture deadline is original capturedAt + 500000.
  action elapse(delta: int): bool = all {
    s.phase == "captured" or s.phase == "sent", delta > 0,
    s' = { ...s, now: s.now + delta },
  }
  action verify(domVerified: bool): bool = all {
    s.phase == "sent",
    s' = if (domVerified and sameNativeScope(s.current, s.captured) and
      s.now >= s.capturedAt and s.now - s.capturedAt <= 500000)
      { ...s, phase: "done", forwarded: s.forwarded + 1, verifiedAt: s.now }
      else { ...s, phase: "done", nativeRejected: true, verifiedAt: s.now },
  }
  val oneShot: bool = s.sent <= 1 and s.forwarded <= 1 and s.forwarded <= s.sent
  val noRenewal: bool = s.capturedAt == 0 or s.capturedAt == 1
  val forwardWasFresh: bool = s.forwarded == 1 implies s.verifiedAt - s.capturedAt <= 500000 and s.gdk
  val safety: bool = oneShot and noRenewal and forwardWasFresh
  val reachedForward: bool = s.forwarded == 1
  val reachedSend: bool = s.sent == 1
  val reachedReject: bool = s.nativeRejected
  val reachedCancel: bool = s.phase == "cancelled"
  val reachedShiftFirst: bool = s.key == "F10" and s.forwarded == 1 and s.shiftBeforeKeyup
  action step: bool = {
    nondet which = Set("control", "root", "publication", "lease", "epoch", "disabled", "disconnected").oneOf()
    any { capture("ContextMenu", "ContextMenu", false), capture("F10", "F10", true), nativeRelease, shiftUp,
      documentKeyup(s.key, s.code, true, false, false, false), documentKeyup(s.key, "foreign", true, false, false, false),
      mutate(which), cancel("blur"), elapse(500001), verify(true), verify(false), duplicateKeyup }
  }
}
