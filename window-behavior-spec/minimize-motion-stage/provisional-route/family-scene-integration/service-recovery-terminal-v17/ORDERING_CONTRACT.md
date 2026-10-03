# Exact family draw ordering V12

Specified before changing the candidate family ordering. Immutable V11 retains
its native baseline evidence and the owner/nested/child counterexample.

## Invariants

Every exact transient ancestor must precede every descendant in the immutable
snapshot/source/draw vector. Ordering is independent of the deepest modal
endpoint focus and of source capture timing. A focus-history index cannot be a
paint-order witness. Ancestor ordering applies to an entire family even when
native pin planes would otherwise put an owner over its modal descendants.

For independent siblings, retain genuine native paint order: tiled content
before ordinary floating content before pinned floating content. Within each
plane use the current compositor WindowState vector order, with the currently
active tiled member drawn last in its tiled pass. The native window_families
array exports mapped WindowState windows in exactly that vector order. The
planner's complete client/native identity coverage and parent stable IDs remain
mandatory; no workspace or shared-PID relation inference is introduced.

Apply a stable topological selection: among eligible members whose exact parent
has already been emitted, choose the lowest native plane/vector paint key. This
preserves native sibling order while guaranteeing every ancestor precedes all
of its descendants. The owner is the sole root. A missing/mismatched exact
record, duplicate, missing selected parent, stale parent stable ID, selected
cycle, unsupported pass state or incomplete active-tiled witness refuses the
whole visual order. Malformed unrelated parent edges are not traversed.

Independent fullscreen siblings require compositor-specific over-fullscreen
pass evidence absent from the existing export, and therefore refuse rather
than invent their order. Fullscreen ancestors do not defeat the explicit
ancestor rule. Cross-workspace visual route/destination authority remains the
existing family/context contract. This is not a claim to cover all native
fullscreen rendering states or translucent backdrop equivalence.

Once a complete immutable scene vector is seeded, reversals retain that vector
and its exact original pixels. Fresh callbacks validate the same exact members
and geometry without replacing source order mid-scene. A new independent scene
recomputes the fresh order. Endpoint native commits and final deepest-modal
focus remain separate from draw order and use the existing guarded core policy.

## Genuine native source witnesses

The pinned Hyprland commit efb50993780079460b0cbed1363e2166a2de1d9f matches the
installed 0.56.2 version header. WindowState.cpp: moveToTop rotates the raised
window to the vector end. Renderer.cpp: renderWorkspaceWindows draws nonactive
tiled windows in vector order then the active tiled window, ordinary floating
windows in vector order; renderWindows draws pinned floating windows in its
later pass. Its separate fullscreen logic is the reason ambiguous independent
fullscreen siblings cannot be authorized from a simple vector alone.

Native V18 familyBridge.cpp: luaWindowFamilies iterates WindowState::windows()
without sorting; hookedRaise raises the ancestor chain toward the deepest
modal child. Exact source bytes/hashes are retained in native-order-primary.
The service changes its adapter ordering, never these native source bytes.

## Observer lifetime

Product resources must not retain retired actors for QA. The existing exact
creation seam is transport.bind_controller(controller), invoked once by
SceneManager after factory(number) returns. An external read-only observer can
chain the original binding and record that actor/controller reference, copy
actual returned capture PNG bytes, and drain actual transport events before
cleanup. On successful normal controller/transport close and actor-file disposal,
NativeFactory.retired(number, desktop) removes its desktop from the product
registry. The observer may chain that method to record retirement completion;
its independent evidence storage is outside product resources/authority.

Before a first seed, the post-capture native draw vector must still equal the
exact captured vector in order, not merely contain the same members. Equal
client rectangles cannot substitute for identity/order agreement. A changed
independent sibling paint order during capture rejects that visual seed and
releases every owned epoch source; accepted native intent retains only its
existing fresh guarded settlement authority.
