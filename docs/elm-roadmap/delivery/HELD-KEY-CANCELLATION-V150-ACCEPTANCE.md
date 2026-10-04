# Parent held-key cancellation

Frozen AQ138 fixes the reproduced AQ120 held-key loss: it cancels only recorded
key presses before retiring the keyboard and clears modifiers after releases.
Private state is cleared before callbacks; a strong snapshot protects reentry.
Only Wayland.cpp changes; all prior public headers and exported symbols remain.

Actual key C++ checks2735/7 mutation controls, pointer152/5 and transport63/7
pass. Quint10 selected two-key scenarios,1000x40 traces and7 typechecked controls
pass as a separate abstraction. Native467 check executions pass with exact
Core89/plugin90/AQ138 mapping, real GTK releases, cleared input/shortcut/modifier
ledgers, device/output/poll retirement, original6s deadlines and ordered cleanup.
A/Shift/both masks plus original input/geometry/unheld/pointer regressions pass.
Failures and scheduling conflicts remain archived; no full release is accepted.

[Acceptance inventory](../../../implementation/elm-held-key-cancellation-acceptance-v150/acceptance-manifest.json)
binds2907 source/build/evidence files and links; manifest SHA256
`f9d9cb6ad81dbdea941de4586473442d0115c910c64dac52fe35452f50203ba2`.
[Detailed scope and remaining work](../../../implementation/elm-held-key-cancellation-acceptance-v150/HANDOFF.md)
records held-key capability/focus/multiple-device gates and remaining roadmap.
Library SHA256: `aa65d4bc1e7a14771614d1a9013d5eb07d2e758538c3d892df4b97db2c218c5f`.

Hosted goal remained paused during this implementation turn. To enable later
automatic turns, use `/goal resume` or Resume in the goal progress row. The
repository coordinator records checkpoints and serializes native QA; it cannot
resume a hosted goal or launch an AI daemon. Nothing was installed or activated.
