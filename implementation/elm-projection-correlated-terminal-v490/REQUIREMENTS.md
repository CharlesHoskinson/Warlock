# EARS/OpenSpec projection-read terminal contract

When a projection request cannot obtain a coherent bracketed scene, the backend
shall emit exactly one unavailable terminal containing the admitted binding and
requestId and a fixed scene-changed reason. It shall not publish incoherent scene
facts or substitute an uncorrelated refresh notice for that request's terminal.
When the typed Elm model admits a matching terminal, it shall retire only that
projection read, preserve independently pending geometry/effect state, and queue
one projection retry. While an effect, disposition handoff or transport refusal
blocks reads, it shall defer the retry. When the blocker clears, it shall issue
one fresh projection request with a strictly new ID without replaying effects.
When a terminal has a stale/foreign binding/request or malformed fields/reason,
it shall leave model/read/effect state unchanged. When the backend disconnects or
the binding is replaced, it shall revoke the queued retry. Existing dirty-notice
coalescing shall preserve a subsequent coherent geometry/projection refresh.

OpenSpec ADDED: projection-unavailable terminal, protocol3. Exact fields:
protocolVersion3, kindprojection-unavailable, binding(valid current lifetime/
session/frontend), requestId(canonical positive UInt64), reason(scene-changed).
This is a read terminal, not an operation refusal/commit. It grants no window
capability, native scene authority, action readiness or effect-retry permission.
One typed projectionRetryQueued flag belongs to the existing Shell model. Reply
admission requires current bound model and exact pending projection ID. Geometry
read slots are neither cleared nor considered replies by this message. A retry
remains under native read/effect/transport/session and queue-capacity fences;
read exhaustion remains explicit. Native original deadlines never change.

Model scope: discrete read-slot/binding/blocker/retry abstraction; no backend
callback, full typedElm/host serialization/refinement or native repair acceptance.
Original handler/compiledShell liveness witness486 and failednative478 preserved.
