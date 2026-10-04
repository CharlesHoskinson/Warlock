# Shared Elm controller boundary

V145 implements one `OutputController` containing exactly one existing
`SurfaceController`/Desktop model. Additional display programs (`Bar.elm`) contain
only Presentation state and dispatch enabled controls from the current frame.
They do not attach a second native session or run a Desktop reducer. Main renders
no controls; all visible bar views use the read-only presenter.

The host supplies a complete `view-topology` snapshot with a monotonic revision
and at most64 unique positive uint64 view IDs/generations. New IDs exceed the
highest issued ID; retired IDs cannot reappear, and live generations cannot go
backward. These are native presenter incarnations, not compositor monitor IDs or
the authority protocol's output configuration generation.

A `view-action` envelope contains the host-bound scope and the existing
publication/lease/control action. Membership and popup ownership are checked
before the existing Surface resolver. Unknown/retired scopes, stale publications,
wrong surface roles and arbitrary controls cannot emit effects. A valid bar
interaction selects its originating display. Relocation of an open popup advances
the logical lease so a retired native wrapper cannot be reused. Scoped native
reflow/dismiss messages also require the current owner and lease.

Topology removal/replacement closes an owned popup through the existing reducer;
it preserves the shared authority model and selects a surviving focus scope.
An empty topology suspends view presentation without creating another authority.
The projection explicitly carries both popupOwner and focusOwner: closed popup
focus belongs to a surviving bar rather than an unscoped DOM ID.

## Wire contract for the next native host

- Host to Main: `receiveTopology({viewProtocol:1,kind:"view-topology",revision,
  views:[{id,generation}]})` through the nativeViews port.
- Bound view to Main: `receiveAction({viewProtocol:1,kind:"view-action",scope,
  action})`. Native code supplies scope from the manager/widget identity; it must
  reject renderer-supplied outer scope/kind and arbitrary direct native requests.
- Native popup events: `receiveReflow({scope,lease})` and
  `receiveDismiss({scope,lease})`; source callbacks must remain widget/lease scoped.
- Main to host: `{viewProtocol:1,kind:"view-commit",projection,requests,focus}`.
  The projection is `{viewProtocol:1,kind:"view-frame",revision,views,popupOwner,
  focusOwner,frame}`. Publish the same frame into each presentation-only Bar;
  configure the popup beneath popupOwner. Route DOM focus only to focusOwner.
- One authority client/backend stays attached even across view changes. Ordered
  shutdown, bounded queues, private surfaces and exact source/ABI closure persist.

The inherited C host in this directory is comparison material. It understands
surface-commit rather than view-commit and is not the new shared-host implementation.
Do not launch/deploy this directory as an accepted GUI. Native manager binding,
multiple bar creation, popup anchoring, monitor addition/removal and zero-output
recovery are the next implementation slice. Its original native oracles must pass
before this component supersedes the accepted V132/V140 GUI tuple.

## Evidence and limitations

37 compiled shared-controller cases pass, including one attach path for two
views, correct ownership/relocation, duplicate launch rejection, removal,
generation replacement/rollback, zero outputs/replug, malformed capabilities and
scoped focus fallback. Actual optimized Main and Bar programs compile. Inherited
58 controller and12 presenter cases are separately retained on the changed
SurfaceController. Ten explicit named Quint scenarios and1,000 sampled traces of
40 steps check abstract lifetime/ownership invariants. No automatic Elm/C
refinement, native multiple-view host, hardware, accessibility or release claim.

V141 preserves a failed Elm compile due to shadowing. V142 compiles the first
boundary. V144 preserves the earlier projection evidence before adding explicit
focus scope; V145 supplies the final coherent current source/test closure. Failed
and superseded evidence stays intact. No baseline requirement or sprint is closed.
