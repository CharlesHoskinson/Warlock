module shutdown_preview {
  // ELM-DEL-021: shared_receive_text / preview_route_commands / strict close.
  // One native owner; command delivery and native proof validation are atomic.
  // Abstract one retained frame, one reader and its terminal journal. Routing
  // does not manufacture proof. Actual ordinal/JSON/ABI/500ms/native cleanup
  // are separate implementation observations, not guarantees of this model.
  type State = { phase: int, owned: bool, readers: int, journal: bool,
    canceled: bool, mutations: int, sealedMutations: int, rejected: int }
  var s: State
  pure def retirementKind(kind: str): bool = kind.in(Set("cancel", "release", "acknowledge"))
  pure def routable(phase: int, kind: str): bool =
    phase == 0 or (phase == 1 and retirementKind(kind))
  action init = s' = { phase: 0, owned: true, readers: 1, journal: false,
    canceled: false, mutations: 0, sealedMutations: 0, rejected: 0 }
  action beginDrain = all { s.phase == 0,
    s' = { ...s, phase: 1, sealedMutations: s.mutations } }
  action acquire = s' = if (routable(s.phase, "acquire") and not(s.owned) and not(s.journal))
    { ...s, owned: true, readers: 1, canceled: false }
    else { ...s, rejected: s.rejected + 1 }
  action desktopEffect = s' = if (routable(s.phase, "window-effect"))
    { ...s, mutations: s.mutations + 1 } else { ...s, rejected: s.rejected + 1 }
  action cancel = all { routable(s.phase, "cancel"), s' = { ...s, canceled: true } }
  action readerComplete = all { s.readers == 1, s' = { ...s, readers: 0 } }
  action release = all { routable(s.phase, "release") and s.owned and s.readers == 0,
    s' = { ...s, owned: false, journal: true } }
  action acknowledge(proved: bool): bool = all {
    routable(s.phase, "acknowledge"),
    s' = if (proved and s.journal) { ...s, journal: false } else s
  }
  action close = all { s.phase == 1 and not(s.owned) and s.readers == 0 and not(s.journal),
    s' = { ...s, phase: 2 } }
  action attemptEarlyClose = all { s.phase == 1 and (s.owned or s.readers > 0 or s.journal), s' = s }
  action step = any { beginDrain, acquire, desktopEffect, cancel, readerComplete,
    release, acknowledge(true), acknowledge(false), close, attemptEarlyClose }
  val safety = s.readers >= 0 and s.readers <= 1
    and (s.phase < 1 or s.mutations == s.sealedMutations)
    and (s.phase != 2 or (not(s.owned) and s.readers == 0 and not(s.journal)))
  val drainedClosure = s.phase == 2
  val retainedDuringDrain = s.phase == 1 and s.owned
  val terminalAwaitingAck = s.phase == 1 and s.journal
}
