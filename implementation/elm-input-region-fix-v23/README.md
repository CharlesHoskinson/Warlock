# V23: respect main-surface input holes during window selection

V23 changes the pinned, floating and tiled bounding-box selection branches in
`ViewHitTester::windowAt`. For Wayland client content, a candidate must have an
input-eligible surface at the point. Existing X11 selection and compositor
decoration/border eligibility outside the client geometry are preserved.

The candidate is copied from the exact frozen V14 owning source inherited by
the V20 archive. It replaces that object in a fresh V20-derived compositor;
it does not change the owning upstream tree, earlier candidates, installed
compositor, or retained failed evidence.

The private native packet
[`qa/native-1791066870280313454/report.json`](qa/native-1791066870280313454/report.json)
reports **97 passing checks** (84 original checks and 13 region checks) and
`cleanupPassed=true`, with `mainDesktopActions=false`. The opaque green peer's
input hole passes actual pointer events and resulting keyboard focus to the
underlying maximized window. The outside point and restored full input region
deliver pointer/keyboard events to the peer. Retained input facts remain
unchanged, and the original pixel/pointer/MAX/modal regression is retained.

This is bounded single-output native evidence using scale 1, transform 0 and
disabled animations. The hole fixture independently qualifies the pinned route;
the changed unpinned floating and tiled routes have not received independent
hole-fixture qualification. Draw dispatch is not presentation evidence; the trace
protocol continues to advertise `canonicalScene=false`. Final source closure,
combined release regression, deployment and full parity remain separate.

See [HANDOFF.md](HANDOFF.md) for provenance, the failure mechanism and remaining
acceptance gates.
