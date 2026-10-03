# Native first-class minimize experiment — acceptance blocked

This derivative implements native process-owned minimized state independent of
`hidden` and workspace/scratchpad membership. A prepared weak-window registry is
swapped for all currently mapped family members. Native renderer predicates,
live render entry, window input eligibility and both full/raw window focus paths
consult that state. Existing owning SDK headers and class layouts are unchanged;
new WindowPolicy functions are exported by the exact newly compiled core.

The effect authority runs on the compositor thread and authenticates SO_PEERCRED,
PID start, lifetime/session/frontend binding and a seven-field intent tuple.
It checks output generation and current native dependency revision before effects,
uses actual parent relations, protects exclusive/locked input and keeps one
bounded request journal per peer. Exact same-byte retry is deduplicated; reused
or older identities refuse. Unsupported/stale effects are refused before state
mutation. A prepared Unknown outcome is retained if post-effect proof fails.
It does not silently present such a transaction as committed.

Native projections enumerate explicit minimized booleans, geometry and fullscreen
mode. The canonicalScene capability remains false: vector positions and sequential
observations do not establish canonical atomic presentation/input revisions.
The experimental protocol enables only minimize/restore. The production/read-only
Elm host remains unchanged until its actual effect and scene gates pass.

## Evidence

Core `build-1791057748334299238/report.json`: six fresh objects and link passed,
ancestor archive/binary preserved. Core SHA256:
`2be14de3fd1cddd12e40919bf7a97d95d2799df2b9df48a632b2b654d015c51e`.
Latest effect build: `qa/build-1791058557036219462/report.json`.
`qa/build-pair-manifest.json` pins the exact tuple and compilation inputs.

`qa/native-1791058639153902245/report.json`: 42 private native checks passed.
`qa/native-1791058947594074854/report.json`: 54 checks passed, preserving those
42 and adding MRU keyboard delivery before pointer activation, last-family no-focus/
no-key-delivery, recovery, modal-family minimize/restore and actual modal keyboard.
Actual captures prove MAX and modal live pixels excluded while minimized and
visible after restore. Direct minimized-window focus refuses. Enumeration remains,
workspace/geometry/mode stay equal in these static fixtures. Both paired clients
and modules close before private compositors; the main desktop is not touched.

Nine explicit named Quint scenarios and 1,000 sampled invariant runs exercise a
fixed owner/modal/peer abstract policy. This does not prove native refinement or
new-window lifecycle behavior. Initial typecheck failure is retained with its
original model and source closure.

## Blocking failure

`qa/native-1791059374174458273/report.json` fails the late-child probe after its
previous bounded cases pass. Native owner incarnation 4 is minimized, but newly
opened modal incarnation 5 is not minimized, accepts input, remains renderable
and becomes focused. The registry covers existing members without ancestor
inheritance for subsequently mapped children. This is P1 and prevents accepting
complete minimize/scene/focus behavior. It is not a main-desktop incident.

Next derivative must consult minimized ancestry before map-time focus/render,
retain inherited state through subsequent owner/window lifetimes, and repeat this
unchanged negative oracle. It must preflight the unique eligible restore recipient
before clearing flags: two sibling modals can otherwise leave the previous peer
focused while the current weak restore postcondition reports Committed. Add
refusal/no-mutation and recovery oracles. Use semantic full-tuple retry comparison
rather than raw payload bytes. Preserve these positive and negative packets.

Remaining: native/Elm effect integration, canonical scene/presentation receipts,
retained previews and original capture deadlines, tiled layout handling, saved
restore state under client reconfiguration, output/workspace changes, popup and
subsurface/seat-focus routes, held-device races, complete resource/performance and
AT/IME checks, and whole desktop/release acceptance. No whole requirement or build
cycle is completed here. This candidate is not deployed.
