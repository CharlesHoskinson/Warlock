# Private nested selection and xdg lifecycle contract

Preserve aquamarine-version-guard-v1 and every historical attempt. The raster
attempt proved the parent disconnected with xdg_surface error3 before producer
input. Initial output announcement allowed a modeset buffer before initial
configure ACK; toplevel configure also emitted a frame before surface configure.
The inherited AQ_BACKENDS variable was ignored and DRM attempted first.

For AQ_BACKENDS=wayland in the private library, choose Wayland mandatory before
optional explicitly requested headless auxiliary outputs. Never construct DRM,
open libseat, or create a DRM backend on later GPU notification. Reject unknown
explicit selection before creating a backend; an unset selection preserves
ordinary upstream behavior. An auxiliary headless output cannot replace a
failed mandatory live parent. Parent socket verification stays in qa_launch.

A Wayland output starts unacknowledged and unannounced. Toplevel configure stages
size only; it cannot signal a consumer state or frame. Surface configure first
sends ACK then marks acknowledged and queues a weak-lifetime callback. That
callback announces the output exactly once, publishes the staged size, and kicks
the frame. Buffer commit and idle-frame emission refuse until ACK and announcement.
A destroyed output invalidates state and queued weak callbacks cannot revive it.
Keep public headers byte-identical; private per-output state is internal to the
translation unit. Repeated configure ACK updates remain usable after publication.

C++ tests exercise the actual internal lifecycle/selection helpers and source
wiring checks cover the protocol callbacks. Quint covers ACK, publication,
frame/buffer requests and destruction plus mandatory selection/refusal. Retain
old 72 global-version checks and 2000 version-model traces. New native proof must
also require actual parent delivery of nested output frames, no protocol errors,
no DRM/libseat attempt, exact mappings, original15 desktop checks and cleanup.
No pixel, window-transaction or physical cadence acceptance follows from this.

A detected wl_display transport error invalidates every output lifecycle, pending
callback and frame scheduler. Startup dispatch failure rejects the mandatory
parent. Returning a live IPC process does not establish healthy parent transport.

For explicit mandatory Wayland only, transport failure also clears actual
CBackend::ready. Auxiliary frame events cannot replace required parent feedback;
optional unset/upstream backends keep their independent readiness semantics.
