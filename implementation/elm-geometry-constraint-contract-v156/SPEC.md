# Constraint-aware native geometry contract proposal

This proposal addresses RIGHT-CLICK ELM-RC-006 ordinary resizable Maximize and
exact Restore. The motivating real GTK failure is frozen in V154. It adds a
focused constraint model alongside the pending broader V16 geometry sketch;
it does not replace original native08/09/10 or the full desktop roadmap.

One serialized compositor authority owns window, placement and operation state.
API admission, native mutation, callback readback, client configure/ACK and
presentation remain separate observations. Existing transport/journal models
retain delivery loss, duplicate receipts and fresh frontend recovery. This
single-authority model uses plain Quint with grouped state, rather than a
message protocol. Types only are supplied for approval; no functions, actions
or claimed invariants have been written.

## Bounds and capability semantics

Normalize client and layout/rule hints into the same native logical target size
space before comparison. Preserve both authorities; one cannot widen a bound
supplied by the other. Zero raw XDG maximum means unbounded. Layout sentinel
conversion must follow the owning implementation. Invalid, negative, nonfinite,
missing or unconvertible observations refuse the geometry operation. Resolve
the owning scale/decoration conversion from V155 before implementing this
normalization; direct raw-versus-layout arithmetic is not authorized by this
proposal.

Effective lower bounds are the greater lower bound on each axis. Effective
upper bounds are the smaller finite upper bound, or unbounded when neither
authority limits that axis. Inconsistent intervals are invalid. Equality on
either axis is an operation-blocking fixed-size restriction. A positive lower
bound alone is not grounds for refusing Maximize.

Maximize is feasible only when the exact current workarea target satisfies
every effective bound, all existing nonconstraint native guards hold, and its
ordinary placement can be retained under the original identity/scope/capacity
rules. A finite maximum below the workarea refuses; do not silently choose a
smaller rectangle and call it maximized. Feasible finite maxima are preserved.

RestoreGeometry is independently feasible only when the exact retained logical
and visual placement remains valid under current bounds and coordinate
semantics. If constraints change after capture and forbid that placement,
refuse exact restoration; retain the original record and never replace it with
a newly clamped or fallback rectangle. The visual rectangle may include
decorations: its feasibility must use the verified owning conversion, not a
second arbitrary size comparison.

All existing mapped/floating/Wayland, transient/family, grouping, pinning,
minimized/hidden/workspace, mode consistency, lock/exclusive/grab/drag,
peer/focus, ownership generation and Unknown barriers remain necessary.

## Projection and execution

Use a fresh negotiated geometry observation version with explicit normalized
client/layout bounds and a constraint revision. Preserve geometry effect
protocol2 full-key identities and existing durable schema5 admission. Do not
silently change the meaning of the frozen `constrainedSize` field: existing
version1 clients retain their original strict interpretation. New consumers
validate per-operation feasibility from the explicit new facts and native
capabilities. Negotiation must refuse unsupported versions and avoid enabling
an action while attach/refresh is incomplete.

Changing either bound source changes the geometry fingerprint/revision even
when the old blanket constrained boolean would remain true. Revalidate exact
scope, workarea, bounds and saved placement immediately before mutation and
after callbacks. A changed dependency before dispatch causes refusal without
mutation. A changed dependency after mutation retains Unknown until exact
reconciliation. Duplicate full keys never authorize another mutation.

## Required witnesses and acceptance

After sketch approval, explicitly run named model scenarios and sampled traces
covering minimum-only feasible MAX; too-large minimum; zero/unbounded maximum;
finite maximum below/equal/above the workarea; one-axis fixed bounds; invalid
and inconsistent intervals; conflicting raw/layout limits; changes invalidating
retained originals; changes during callbacks; duplicate/stale/Unknown no replay;
and preservation of peer/focus/ownership state. Typechecking this sketch is not
model or native acceptance.

Implementation then requires a fresh native authority and exact owning ABI
pair, both strict consumers and negotiation, meaningful producer/effect/decoder
tests, and unsafe controls that reject incorrect bound combination. Native
qualification must use real GTK minimum-size, fixed/maximum-size and scaled
fixtures, actual native/client modes, configure/ACK serials, exact geometry,
pixels and unchanged peers under original deadlines. Re-run the failed shared
multi-action route and coherent original08/09/10 on that same tuple.
