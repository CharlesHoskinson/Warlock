module bar_keyboard_return {
  // ELM-UX-023: shared_context_event routes an exact previously admitted GTK
  // key replay back to its live original bar engine. WebKitGTK's native replay
  // flag is consumed there; policy proof, held keys and window effects do not
  // advance. Popup grabs can redirect the replay although its immutable native
  // window/device/type/time/hardware signature still names the original sender.
  // Abstract that complete signature as an integer and receiver generation.
  // Native GTK/WebKit timing, clock wrap and real recipients remain separate.
  type State = { active: bool, generation: int, capturedGeneration: int,
    sig: int, routedSig: int, popup: bool, pending: bool, proofs: int,
    routed: int, delivered: int, rejected: int, violations: int }
  var s: State
  pure def exact(st: State, signature: int, generation: int): bool =
    st.active and signature == st.sig and generation == st.generation
      and generation == st.capturedGeneration
  action init = s' = { active: true, generation: 1, capturedGeneration: 1,
    sig: 0, routedSig: 0, popup: false, pending: false, proofs: 0,
    routed: 0, delivered: 0, rejected: 0, violations: 0 }
  action physicalModifier = all { s.active and not(s.popup),
    s' = { ...s, sig: s.sig + 1, capturedGeneration: s.generation,
      pending: true, proofs: s.proofs + 1 } }
  action openPopup = all { s.active, s' = { ...s, popup: true } }
  action routeReplay(signature: int, generation: int): bool =
    s' = if (exact(s, signature, generation) and signature > s.routedSig)
      { ...s, routedSig: signature, pending: false, routed: s.routed + 1 }
    else { ...s, rejected: s.rejected + 1 }
  action dismiss = all { s.active and s.popup, s' = { ...s, popup: false } }
  action home = all { s.active and not(s.popup),
    s' = if (s.pending) s else { ...s, delivered: s.delivered + 1 } }
  action retireOwner = s' = { ...s, active: false, popup: false }
  action replaceOwner = s' = { ...s, active: true, popup: false,
    generation: s.generation + 1, pending: false }
  action step = any { physicalModifier, openPopup, routeReplay(s.sig, s.generation),
    routeReplay(s.sig + 1, s.generation), routeReplay(s.sig, s.generation + 1),
    dismiss, home, retireOwner, replaceOwner }
  val safety = s.violations == 0 and s.routed <= s.proofs and s.routedSig <= s.sig
  val repeatedReturn = s.routed >= 2 and s.delivered >= 2
  val originalReplayCompleted = s.routed > 0 and not(s.pending) and s.active
  val foreignReplayRefused = s.rejected > 0
}
