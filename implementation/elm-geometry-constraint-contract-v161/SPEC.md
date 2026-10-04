# Revised constraint-aware geometry contract

This replaces V156 and V160 drafts, following V155 coordinate research and
independent type review. Output ownership is separate from workspace-owned
workareas: multiple live workspaces on one output retain independent revisions. It retains V156's requirement scope, refusal/Unknown semantics, fresh
negotiated projection, named witnesses, original deadlines and final native
acceptance duties. V156's types and typecheck remain historical draft evidence.
No transition or functional logic has been written in either draft.

## Actor and state shape

One serialized native authority owns windows, outputs, placements and full-key
transactions. Separate admission, mutation, callback/readback, client ACK and
presentation observations permit dependency changes between stages. Transport
and schema5 journal recovery remain their existing independently qualified
models. Plain Quint is appropriate for this single-authority state machine;
this is not a multi-process message protocol.

## Size spaces and prospective operations

Keep raw client hints, effective layout hints and optional rule hints distinctly
typed. Known absence of an optional rule and an unbounded maximum are valid;
unavailable or invalid observations refuse execution. Zero raw XDG maximum is
unbounded. Positive maxima, including values1–4 that the owning layout helper
can normalize away, remain real client restrictions. Nonfinite/negative and
inconsistent intervals refuse. Fixed equality on either axis blocks MAX.

Never intersect sizes from different box conventions. Project each operation
into its prospective logical target, visual target, real client box and integer
configure size using the owning core's actual conversion and rounding.
Represent fractional box values as rationals in the model; executable native
floating-point and rounding equivalence requires separate implementation tests.
Record ordinary and maximized conversions separately, including XDG geometry
origin, decoration reserved extents and conversion revision. Monitor scale is
an explicit diagnostic input; no scale multiplication is assumed for Wayland
configure sizes. Unsupported conversions refuse rather than guessing.

MAX uses the exact current floating workarea and the owning maximize conversion.
Raw client limits are checked against actual prospective configure dimensions;
layout/rule limits are checked in their corresponding verified target box
convention. Greater lower bounds and smaller upper bounds are combined only
within a common convention. Positive minimum sizes that fit do not block MAX.
Finite upper bounds below the exact required size refuse; a smaller clamped box
does not qualify as maximized. Because core89 bypasses normal size clamps during
MAX, authority-side feasibility checks are mandatory before native mutation.

RestoreGeometry independently projects the exact retained ordinary logical and
visual placement through the ordinary restoration path. Preserve the recorded
client box, configure size and coordinate revision for compatibility checks.
Changed constraints/decorations/origin can invalidate exact restoration. Refuse
without recapture or invented fallback, retain the original, and do not subtract
MAX decoration reservations again during ordinary restoration.

## Authority, negotiation and recovery

Retain complete native lifetime/incarnation and workspace/output ownership
scope, including generation and workarea revision. Every existing nonconstraint
eligibility guard remains required: mapped floating Wayland singleton, no
transient/group/pin/hidden/minimized/special workspace, matching native/client
modes, no fullscreen/layout-managed mode, lock/exclusive/grab/drag exclusion,
compatible peers/focus and no unresolved operation barrier.

A fresh negotiated geometry observation version carries explicit bound spaces,
coordinate/conversion revisions and per-operation capabilities. Frozen version1
clients retain their strict `constrainedSize` interpretation. Preserve effect
protocol2 keys and durable schema5 admission. Unsupported versions refuse;
incomplete attach or observation recovery cannot enable a geometry action.
Any bounds/conversion change contributes to the geometry revision even when
the old blanket boolean would not change.

Revalidate scope, live bounds, conversion and retained placement immediately
before mutation. Dependency mismatch then refuses without mutation. Revalidate
after callbacks and compare actual native/client mode, exact prospective sizes,
peers and focus; post-mutation mismatch remains Unknown for exact reconciliation.
Duplicate full keys never authorize a second mutation. Native Committed receipts
and independently observed client ACK/presentation remain distinct evidence.

## Required qualification

After explicit sketch approval, model witnesses cover feasible minimum-only
MAX, minimum above workarea, unbounded and finite upper bounds, tiny maxima,
one-axis fixed/inconsistent intervals, conflicting same-space limits,
unavailable versus valid absent hints, nonzero/negative geometry origin,
decoration reserves, fractional rounding, scale1/2, changed bounds/conversion,
incompatible saved restore, callback races, duplicate/stale/Unknown no mutation,
and exact peer/focus/scope preservation. Typechecking declarations proves none
of these properties; sampled model results will remain distinct from native QA.

Before release, build a fresh specification/source/owning ABI tuple and strict
producer/consumer/negotiation tests, with controls detecting wrong coordinate
combination and replay. Exercise real GTK minimum-size, decorated/scaled and
fixed/maximum-size fixtures with actual configure/ACK, native/client modes,
exact rectangles, pixels and unchanged peers. Re-run V152's failed multi-action
route and original08/09/10 on the same coherent tuple and unchanged deadlines.
All broader S01–S16/UIUX/release/deployment/rollback duties remain open.
