# Experimental geometry effect source

Derived from frozen V35 native observation authority and V16 private placement
store. No native qualification, effect advertisement, menu enablement, installation
or formal geometry model approval follows from this source.

Effect 2 uses the existing exact five-field window-effect envelope and the exact
five-field intent (request, generation, incarnation, operation, context). Binding
is lifetime/session/frontend. All counters are canonical positive decimal strings.
Context is lifetime/epoch/output/revision: epoch is current frontend, output is
native output dependency generation, revision is geometry facts revision. It is
not legacy scene-facts revision. Operations are maximize and restore-geometry.
Legacy restore retains unminimize semantics. Outcomes carry effectProtocol 2,
original binding and intent, status/reason and geometry revision/output generation.
No caller-provided position, original rectangle, workspace or monitor is accepted.

Geometry attach remains explicit geometryProtocol 1 negotiation after hello.
Capabilities remain effects:false, operations:[] and both geometry capability
booleans false until a qualified native mutation/readback path authorizes changing
that separate contract. The experimental wire handler is present for qualification;
production adapters must respect unavailable capabilities.

Both effect versions share one per-peer request/generation stream. Canonical
fingerprints include version, operation and every intent/context counter. Exact
retry returns cached reply; lower order or changed same request refuses. The
original transport deadline is owned by the endpoint; this synchronous native
handler has no expiry field and does not implement an approval deadline.

Placement keys are native lifetime/incarnation, independent of transport sessions.
Immutable first originals contain logical and visual rectangles. Scope requires
native workspace ID/ownership generation, monitor ID/ownership generation and
workarea ownership revision; monitor zero is valid, negative sentinels refuse.
A compatible duplicate read is required; duplicate capture alone grants nothing.
Changed scope cannot reuse an original. Externally maximized windows without one
refuse. Completed exact restoration retires it. Ordinary moved origins retained
by an external transition refuse recapture rather than overwriting evidence.

Native barriers reserve all members for a legacy family effect, or the exact root
for geometry, before callbacks. Pending/Unknown occupies a bounded 256-entry
native ledger with no eviction. Hello and peer replacement do not clear barriers.
All legacy family effects check it before mutation. Committed readback or native
identity retirement clears entries. Unknown is not resolved from projections,
retries, new epochs or observation; no automatic recovery operation exists here.

Initial geometry scope is mapped resizable floating singleton Wayland root on a
visible nonspecial workspace, without pin/group/child/fullscreen/minimization,
layout-managed fullscreen, constrained size, competing fullscreen peer, drag,
lock/exclusive layer or grab. Raw committed XDG positive max constraints, including
1..4 values otherwise normalized by Window::maxSize, refuse. V40's finalized
zero-default owning-header tuple is required; no V40 build has been assumed.

The actual fullscreen controller receives explicit MAX/MAX or NONE/NONE once.
After callbacks the source reacquires exact incarnation and owners, reads modes,
logical/visual restoration, focus/keyboard/pointer, input/eligibility and unaffected
peer identity/modes/placement. A maximize requires the exact logical workarea.
Failed readback or exception after the setter retains Unknown and its barrier and
original. No rollback, retargeting, forced focus, client ACK or presentation proof
is fabricated. Native Committed means synchronous state readback only.

Owning ABI compilation, full constraints/rules audit, real configure/buffer/pixel
oracles, legacy maximize/minimize composition, capacity/fault campaigns and future
strict Elm shared allocator/projection/receipt integration remain acceptance gates.
Public owning core headers and Quint logic are untouched.
