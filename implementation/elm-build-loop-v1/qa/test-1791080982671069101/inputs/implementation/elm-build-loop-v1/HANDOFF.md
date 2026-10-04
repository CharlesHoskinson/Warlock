# Build-loop handoff

The hosted goal is active for the complete mandatory replacement Elm desktop.
Original S01–S16 and conditional C00–C06 gates, frozen baseline 242/417,
additive right-click 24/48, and the comprehensive UI/UX strategy remain explicit.
The repository coordinator supplies durable per-thread checkpoints and shared
native serialization; it does not create another model process or timed daemon.

The integration lane is developing the shared Elm bar/presentation-only popup
controller. Our independent next lane is `../elm-menu-lifecycle-v2`, addressing
resource bounds and receipt reconciliation. Its [scope](../elm-menu-lifecycle-v2/SCOPE.md)
contains behavioral oracles. Preserve both workers' source/evidence and use fresh
derivatives. The mutable primary integration loop state is read-only to this lane.

Native campaigns now have a shared lock wrapper, invoked by the updated repository
`AGENTS.md`. Existing sessions must adopt it to prevent future direct-launch races;
the conservative process preflight alone cannot guarantee that adoption. No GUI
campaign was launched to test this administrative coordinator. The original
protected launcher and all five crash-noise corrections were left unchanged.

`goal-receipt.json` records active hosted-goal state at observation time. It is a
checkpoint, not a live goal API. Inspect the hosted goal to determine whether
automatic continuation is currently enabled. A closed client, explicit pause,
approval-dependent gate or unavailable device may prevent further execution;
do not manufacture acceptance to bypass such a gate.

Synthetic QA packets preserve failure and success history separately. Their
results establish orchestration behavior, not native UI, full roadmap completion,
resource/performance qualification or release acceptance.
