// Event-loop adapter contract. Coordinates use quarter units on finite boxes.
// No compositor/window policy, native device transport or presentation proof.
module parent {
  type Output = {live: bool, enabled: bool, mirror: bool, staged: bool,
                 ack: int, committed: int, x: int, width: int}
  type Event = {kind: str, output: int, x: int, y: int}
  type State = {a: Output, b: Output, focus: int, device: bool, backend: bool,
                anchor: int, nx: int, ny: int, appliedX: int, appliedWidth: int,
                px: int, py: int, warps: int, forwarded: bool, event: Event}
  var s: State
  pure val blank = {kind: "noop", output: 0, x: 0, y: 0}
  pure def output(st: State, o: int): Output = if (o == 1) st.a else st.b
  pure def replace(st: State, o: int, v: Output): State =
    if (o == 1) {...st, a: v} else {...st, b: v}
  pure def ready(st: State, o: int): bool = {
    val v = output(st, o)
    (o == 1 or o == 2) and st.device and st.backend and st.focus == o and
      v.live and not(v.staged) and v.ack > 0 and v.committed == v.ack
  }
  pure def usable(st: State, o: int): bool = {
    val v = output(st, o)
    ready(st, o) and v.enabled and not(v.mirror)
  }
  pure def clear(st: State): State = {...st, anchor: 0, nx: 0, ny: 0, appliedX: 0, appliedWidth: 0}
  pure def clamp(n: int): int = if (n < 0) 0 else if (n > 4) 4 else n
  pure def dispatch(st: State): State = {
    val v = output(st, st.anchor)
    {...st, px: v.width * st.nx / 4, py: v.width * 3 * st.ny / 16,
            appliedX: v.x, appliedWidth: v.width, warps: st.warps + 1, forwarded: true}
  }
  action init = s' = {
    a: {live: true, enabled: true, mirror: false, staged: false, ack: 1, committed: 1, x: 0, width: 800},
    b: {live: true, enabled: true, mirror: false, staged: false, ack: 1, committed: 1, x: 1000, width: 400},
    focus: 1, device: true, backend: true, anchor: 0, nx: 0, ny: 0,
    appliedX: 0, appliedWidth: 0, px: 0, py: 0, warps: 0, forwarded: false, event: blank
  }
  action motion(o: int, x: int, y: int): bool = {
    val st = {...s, forwarded: false, event: {kind: "motion", output: o, x: x, y: y}}
    s' = if (usable(st, o)) dispatch({...st, anchor: o, nx: clamp(x), ny: clamp(y)}) else clear(st)
  }
  action focus(o: int): bool = s' = {...s, focus: o, forwarded: false, event: {kind: "focus", output: o, x: 0, y: 0}}
  action stage(o: int): bool = {
    val v = output(s, o)
    s' = replace({...s, forwarded: false, event: {kind: "stage", output: o, x: 0, y: 0}}, o,
                 if (v.live) {...v, staged: true} else v)
  }
  action acknowledge(o: int): bool = {
    val v = output(s, o)
    s' = replace({...s, forwarded: false, event: {kind: "ack", output: o, x: 0, y: 0}}, o,
                 if (v.live) {...v, staged: false, ack: v.ack + 1} else v)
  }
  action commit(o: int, generation: int): bool = {
    val v = output(s, o)
    s' = replace({...s, forwarded: false, event: {kind: "commit", output: o, x: generation, y: 0}}, o,
                 if (v.live and not(v.staged) and generation == v.ack) {...v, committed: generation} else v)
  }
  action retire(o: int): bool = {
    val v = output(s, o)
    s' = replace({...s, forwarded: false, event: {kind: "retire", output: o, x: 0, y: 0}}, o,
                 {...v, live: false, committed: 0})
  }
  action deviceLost = s' = {...clear(s), device: false, forwarded: false, event: {kind: "deviceLost", output: 0, x: 0, y: 0}}
  action backendLost = s' = {...s, backend: false, forwarded: false, event: {kind: "backendLost", output: 0, x: 0, y: 0}}
  action supersede(x: int, y: int): bool = s' = {...clear(s), px: x, py: y, forwarded: false, event: {kind: "supersede", output: 0, x: x, y: y}}
  action layout(o: int, width: int, origin: int): bool = {
    val v = output(s, o)
    val st = replace({...s, forwarded: false, event: {kind: "layout", output: o, x: width, y: origin}}, o, {...v, x: origin, width: width})
    val a = output(st, st.anchor)
    s' = if (st.anchor == 0) st else if (not(usable(st, st.anchor))) clear(st)
         else if (st.appliedX != a.x or st.appliedWidth != a.width) dispatch(st) else st
  }
  action monitorFlag(o: int, mirror: bool, monitorEnabled: bool): bool = {
    val v = output(s, o)
    s' = replace({...s, forwarded: false, event: {kind: "flag", output: o, x: if (mirror) 1 else 0, y: if (monitorEnabled) 1 else 0}}, o,
                 {...v, mirror: mirror, enabled: monitorEnabled})
  }
  action check(ok: bool): bool = all {assert(ok), s' = {...s, forwarded: false, event: blank}}
  action step = {
    nondet o = Set(1, 2).oneOf()
    nondet point = Set(-1, 0, 1, 2, 3, 4, 5).oneOf()
    nondet width = Set(400, 800).oneOf()
    any {motion(o, point, 2), focus(o), focus(0), stage(o), acknowledge(o),
         commit(o, output(s, o).ack), commit(o, output(s, o).ack - 1), retire(o),
         deviceLost, backendLost, supersede(100, 100), layout(o, width, if (o == 1) 0 else 1000),
         monitorFlag(o, true, true), monitorFlag(o, false, false), monitorFlag(o, false, true)}
  }
  val safety = (s.anchor == 0 or s.anchor == 1 or s.anchor == 2) and s.warps >= 0 and
    (s.forwarded implies (s.anchor > 0 and usable(s, s.anchor) and
      s.px == output(s, s.anchor).x + output(s, s.anchor).width * s.nx / 4 and
      s.py == output(s, s.anchor).width * 3 * s.ny / 16)) and
    (s.anchor > 0 implies (s.nx >= 0 and s.nx <= 4 and s.ny >= 0 and s.ny <= 4))

  run stationaryScaleTest = init.then(motion(1, 1, 2)).then(layout(1, 400, 0)).then(check(s.px == 100 and s.py == 150 and s.warps == 2 and safety))
  run restoreScaleTest = init.then(motion(1, 1, 2)).then(layout(1, 400, 0)).then(layout(1, 800, 0)).then(check(s.px == 200 and s.py == 300 and s.warps == 3))
  run outputRelativeTest = init.then(focus(2)).then(motion(2, 1, 2)).then(check(s.px == 1100 and s.py == 150 and safety))
  run outputOriginChangesTest = init.then(focus(2)).then(motion(2, 1, 2)).then(layout(2, 400, 1200)).then(check(s.px == 1300 and s.warps == 2))
  run unfocusedMotionTest = init.then(motion(2, 1, 2)).then(check(s.warps == 0 and s.anchor == 0))
  run focusLeaveBlocksReplayTest = init.then(motion(1, 1, 2)).then(focus(0)).then(layout(1, 400, 0)).then(check(s.warps == 1 and s.anchor == 0))
  run stagedConfigureBlocksTest = init.then(stage(1)).then(motion(1, 1, 2)).then(check(s.warps == 0 and s.anchor == 0))
  run ackAloneBlocksTest = init.then(stage(1)).then(acknowledge(1)).then(motion(1, 1, 2)).then(check(s.warps == 0))
  run staleCommitBlocksTest = init.then(stage(1)).then(acknowledge(1)).then(commit(1, 1)).then(motion(1, 1, 2)).then(check(s.warps == 0))
  run freshCommitAllowsTest = init.then(stage(1)).then(acknowledge(1)).then(commit(1, 2)).then(motion(1, 1, 2)).then(check(s.warps == 1 and safety))
  run deviceRetirementBlocksTest = init.then(motion(1, 1, 2)).then(deviceLost).then(layout(1, 400, 0)).then(check(s.warps == 1 and s.anchor == 0))
  run outputRetirementBlocksTest = init.then(motion(1, 1, 2)).then(retire(1)).then(layout(1, 400, 0)).then(check(s.warps == 1 and s.anchor == 0))
  run backendRetirementBlocksTest = init.then(motion(1, 1, 2)).then(backendLost).then(layout(1, 400, 0)).then(check(s.warps == 1 and s.anchor == 0))
  run supersedingWarpBlocksReplayTest = init.then(motion(1, 1, 2)).then(supersede(100, 100)).then(layout(1, 400, 0)).then(check(s.px == 100 and s.py == 100 and s.warps == 1 and s.anchor == 0))
  run unchangedLayoutNoReplayTest = init.then(motion(1, 1, 2)).then(layout(1, 800, 0)).then(check(s.warps == 1))
  run unrelatedLayoutNoReplayTest = init.then(motion(1, 1, 2)).then(layout(2, 800, 1000)).then(check(s.warps == 1 and s.px == 200))
  run clampedCoordinatesTest = init.then(motion(1, -1, 5)).then(check(s.px == 0 and s.py == 600 and safety))
  run disabledOutputBlocksTest = init.then(monitorFlag(1, false, false)).then(motion(1, 1, 2)).then(check(s.warps == 0))
  run mirroredOutputBlocksTest = init.then(monitorFlag(1, true, true)).then(motion(1, 1, 2)).then(check(s.warps == 0))
}
