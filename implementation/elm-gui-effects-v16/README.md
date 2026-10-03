# Elm GUI effect integration

An isolated GTK/WebKit host now presents keyed Elm minimize/restore controls.
Typed decimal uint64 identities, generations and native dependency context remain
lossless. Elm owns transaction state; native receipts never optimistically change
window state. Pending commands disable controls. An authenticated fresh native
projection follows receipts and event notifications, with no periodic state polling.
Unknown outcomes remain distinct and terminal; reconnect preserves uncertainty.

ActionProjection is a window action enumeration, not a canonical paint/input scene.
Native canonicalScene capability stays false. The backend checks facts before and
after window enumeration, identity/minimized agreement, peer credentials and binding.
The host queues requests instead of overwriting pending effects and refuses overflow.

The private native runner measures actual DOM button bounds and clicks them with an
owned Wayland pointer. It verifies native minimized/render/input state, restore focus,
and receipt-to-observation-to-control transitions. This does not qualify full scene
ordering, all modal/seat/device routes, accessibility/IME, GPU performance or release.
Earlier hardware acceleration evidence belongs to V4; V16 makes no WebGPU claim.

Preserved first native packet native-1791062751797227892 contains a reporting defect:
its passed field is true despite a private-host cleanup exception and unexpected
inner descendants. Treat that packet as FAILED. The corrected runner sets passed
false on exceptions, checks unexpected descendants and retires owned auxiliary
processes before the compositor. Later clean runs supersede it within this scope.

No desktop configuration or session activation changed.

Build-1791062868223382968 also exited successfully without the second replay
publication/report: nested worker initialization needed a deferred send. Treat its
replay claim as unaccepted. The corrected build requires the durable report and all
20 executed assertions, and its Node harness has a completion deadline. Failed
compiler attempts and these incomplete proof packets remain preserved.
