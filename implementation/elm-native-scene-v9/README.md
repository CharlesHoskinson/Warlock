# Native scene and modal experiment

This slice exercises a privately launched, exact source/ABI tuple. It makes no
main-desktop changes and does not complete S06 or any entire product requirement.

V8 failed the genuine blocked-parent click: the independent peer retained focus.
See `qa/native-1791054684986443860/report.json`. The earlier placement/preflight
failures and their inputs remain preserved. The V10 core derivative rebuilds
FocusState, ViewHitTester and InputManager on the V8 renderer-fixed archive.
It resolves native modal ancestry before a full focus transaction, queries blocked
parent hits only for activation, redirects focus to the unique deepest modal,
and consumes that press and matching same-device release. Cyclic/ambiguous
constraints refuse. It clears the parent's surface when redirecting keyboard focus.
No PID/app-id grouping or synthetic click is used.

V10 exact core: `75548c72f43554a0c351f3a43b4d928238571282b975b7c3c11802a2779cd546`.
Its own `qa/slice-manifest.json` freezes compilation, exact SDK headers, source
inputs, the read-only authority plugin, Elm/Quint replay and 33 private native
observer/predicate checks. The modal-specific implementation has not received
complete Quint/fuzz/security/performance qualification; observer model success
is not a proof of the new modal algorithm.

`qa/native-1791056049919900659/report.json` passed the original pixel/pointer
suite on V10. The stronger keyboard run at
`qa/native-1791056238592548761/report.json` failed independent-peer key delivery:
native active-window metadata selected the peer, while GTK's default shared
modal group redirected its key to the modal. The fixture now gives independent
roots explicit GTK WindowGroups, keeping each real transient family together.
This follows the installed GTK GIR contract that groups limit grabs/modality;
it changes the fixture's independent-document premise, not product authority.
The failure remains evidence of the toolkit/metadata distinction.

`qa/native-1791056292999426300/report.json` passes 19 actual checks, including
MAX/peer raise/lower, pin/unpin, MAX mode preservation, inactive special-workspace
pixel/hit/focus exclusion, native modal ownership, independent same-process
peer identity, parent-click redirection with no delivered press/release, actual
modal keyboard delivery and actual independent-peer keyboard delivery. All
pointer/keyboard helpers use only the private Wayland endpoint. The fixture
exits normally and clients/modules retire before compositors.

These are single-output quiescent observations. They do not establish canonical
atomic presentation/input revision, first-class minimization, all nested/ambiguous
families, all focus routes, exclusive-layer and device/session transitions,
resource bounds, multi-output hardware or release acceptance. The special-workspace
case is inherited exclusion input, not an implementation of minimize.

Next: add hold/release across modal retirement, device incarnation and exclusive
surface cases; address transaction/refusal and bounded-resource concerns; model
and fuzz the actual modal algorithm. Then implement first-class minimized state
and complete canonical scene observations for the Elm projection.
