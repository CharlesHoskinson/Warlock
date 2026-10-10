module exit_fullscreen {
  // REN-017, Effects.beginGeometry/Provider.withGeometry/native geometry effect.
  // One captured target and one effect. Native lifetime/context correlation,
  // locks/grabs, barriers and journal outcome are abstract booleans/statuses;
  // actual pixels/GTK input/ABI/exit/AT require the original protected journey.
  type State = { mode: int, eligible: bool, current: bool, negotiated: bool,
    blocked: bool, status: int, mutations: int, pin: bool, focus: int }
  var s: State
  pure def available(x: State): bool = x.mode == 2 and x.eligible and x.current
    and x.negotiated and not(x.blocked) and x.status == 0
  action init = s' = { mode: 2, eligible: true, current: true, negotiated: true,
    blocked: false, status: 0, mutations: 0, pin: true, focus: 1 }
  action maxMode = all { s.status == 0, s' = { ...s, mode: 1 } }
  action ordinaryMode = all { s.status == 0, s' = { ...s, mode: 0 } }
  action block = s' = { ...s, blocked: true }
  action stale = s' = { ...s, current: false }
  action ineligible = s' = { ...s, eligible: false }
  action unsupported = s' = { ...s, negotiated: false }
  action invoke = s' = if (available(s)) { ...s, status: 1 } else s
  action nativeFinish = all { s.status == 1,
    s' = if (s.mode == 2 and s.eligible and s.current and not(s.blocked))
      { ...s, mode: 0, status: 3, mutations: s.mutations + 1 }
      else { ...s, status: 4 } }
  action uncertainAfterMutation = all { s.status == 1 and s.current and s.eligible and not(s.blocked),
    s' = { ...s, mode: 0, status: 2, mutations: s.mutations + 1 } }
  action unknownBeforeMutation = all { s.status == 1, s' = { ...s, status: 2 } }
  action menuRead = s' = s
  action pinnedFocus = s' = { ...s, focus: 2 }
  action ownerFocus = s' = { ...s, focus: 1 }
  action step = any { maxMode, ordinaryMode, block, stale, ineligible, unsupported,
    invoke, nativeFinish, uncertainAfterMutation, unknownBeforeMutation, menuRead, pinnedFocus, ownerFocus }
  val safety = s.mutations <= 1 and s.pin and (s.status != 3 or s.mode == 0)
    and (s.mutations == 0 or s.mode == 0)
  val committedExit = s.status == 3 and s.mode == 0 and s.mutations == 1
  val unknownRetained = s.status == 2
  val pinnedFullscreenFocus = s.mode == 2 and s.focus == 2 and s.mutations == 0
}
