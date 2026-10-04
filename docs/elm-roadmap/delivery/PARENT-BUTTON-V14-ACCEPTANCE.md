# Bounded parent-button lifecycle V14

The complete S01–S16/right-click desktop and release gates remain open.
V14 retains V12's original twelve parent-to-GTK coordinate probes and adds
persistent parent controller/button lifecycle campaigns on the same reviewed
core/AQ tuple, with a fresh private input-probe module.

Manifest: `implementation/elm-parent-button-lifecycle-v14/qa/implementation-manifest.json`,
SHA256 `5c39d644a9254043f7262ffa2b509e761abe4a6198662ad49872a54b44d3274b`.
All 134 recorded inventory entries were independently rehashed. Native report:
`implementation/elm-parent-button-lifecycle-v14/qa/native-1791095144943565889/report.json`,
SHA256 `d05beaf21ad004f4694fe9cfbad265e3f1f653344df83097a4bd7b3f5ed764a4`.
All 105 checks pass, including complete cleanup.

## Actual native behavior

- A real physical GTK press precedes each held shrink/scale/restore transition.
  The exact recipient resizes while held, then receives exactly one release.
- Controller quit and EOF balance the held button through the parent module.
- A duplicate parent press is refused. The controller exits6 and its resource
  teardown produces exactly one balancing release. An unmatched parent release
  is refused without creating a physical pair.
- Three simultaneously held buttons each receive their matching release on EOF.
- Eight subsequent clean clicks prove usable input after the tested transitions,
  rather than inferring absence of a stuck grab from controller exit alone.

The seventeen added physical pairs include those recovery clicks. Sixteen
persistent controller processes have exact expected exit status (fourteen0,
two6); owned logs, exact PID/start/socket guards and source hashes are preserved.
GDK double/triple-click signals remain recorded and counted by the original
fixture. Physical pair assertions additionally distinguish actual event types4/7.
The original twelve coordinate probes/raw-count assertions stay unchanged.

## Source correction and CPU evidence

Owning Weston destroys its pointer before emitting seat.destroy_signal. The old
probe seat-destroy callback could notify through that retired pointer. Fresh V14
clears its borrowed seat and held records without notifying at that boundary.
Normal controller teardown still balances while the seat is live. The actual
extracted callback passes all eight held-record combinations; the previous
unsafe body fails the same independent retirement oracle. This is CPU-only
callback proof, not real native seat hot-unplug acceptance.

Protected CPU reports separately pass inspection60, real GDK event-kind14,
retirement/mutant2 and actual persistent-helper parser16 checks. The helper checks
include partial/malformed/multiple/out-of-order packets and bounded logs/deadlines;
they do not launch a parent connection. Initial fixture test failure remains in
its report. The initial freeze utility assumed an `inputs` field where the helper
report uses `sources`; its source is retained as `qa/freeze-attempt1.py`. The
corrected utility verifies either nonempty source inventory and final evidence.

## Remaining qualification

A fixed parent800x600 with child-mode changes does not exercise a staged parent
configure/ACK generation fence. Weston retains pointer focus under a held-button
grab, so these tests do not prove independent focus-leave routing. Negative
requests are rejected by the parent probe before reaching AQ; they do not prove
AQ's denial branches. Parent-configure fences, capability loss/hot-unplug,
output-identity/multi-output routing, cursor fallback, actual pixel presentation,
rotation, full window operations, AT/IME, performance and release/deployment
remain open. No main desktop configuration or activation changed.
