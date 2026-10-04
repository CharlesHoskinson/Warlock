# Parent-pointer model and capability lifecycle V37/V39/V40

V37 adds the previously missing Quint contract for the V30/V31 parent-coordinate
adapter. V39 checks selected model witnesses against extracted production
routing bodies. V40 additionally passes actual pointer-capability removal and
restoration in the protected private parent host. Native parent-focus/layout
qualification is still failed. No installed compositor or desktop was changed.

## Formal contract and implementation comparison

The model represents two owning outputs, normalized quarter-unit coordinates,
logical boxes and origins, parent focus, device/backend lifetime, and staged,
ACKed and committed mapping generations. Its actor is the serialized adapter;
it adds no second desktop authority or transport actor. It starts from committed
mapping state and does not model startup, numeric overflow, GPU pixels, physical
devices, general pointer clamping, or queued backend idle work.

The explicit selector executes all 19 named scenarios. A separate seeded run
checks the safety invariant in 1,000 samples of up to 40 steps. Three typechecked
model mutations fail: bypassing output focus, dropping the output origin, and
retaining an anchor after a superseding warp. This is sampled bounded evidence,
not an exhaustive proof.

V39 converts the 19 named ITF witnesses into typed C++ fixtures and compares 86
states against actual extracted V30 readiness-query and V31 routing fragments.
Those fragments include private state, warpTo, the parent output projection,
layout handler, detach handler and parent warp listener body. The fixture does
not reimplement their decisions. It compares anchor/output identity, normalized
point, routed warp count and forwarded/superseding logical coordinates. Three
independent production-fragment mutations are rejected.

The environment mocks ownership and monitor lists and routes InputManager back
into the extracted projection. Renderer/idle/DPMS effects and general
closestValid clamping are stubbed. The comparison therefore supports only the
documented adapter behavior; it does not prove full compositor refinement or
native focus/configure acceptance. V36's initial reserved-identifier parsing
failure and V38's missing JSON-header build failure are preserved. V39 uses
generated typed trace data and requires no added JSON library.

## Actual private capability loss

V40's fresh parent helper extends the private protocol to version 2. Its
same-UID exclusive controller may disable the sole fake-seat pointer capability
only when the owning seat has exactly one pointer reference. It balances held
buttons, then invokes the owning libweston's weston_seat_release_pointer.
Restoration requires zero references and invokes weston_seat_init_pointer.
Duplicate transitions are rejected. The module includes the owning internal
header and captures compiler/header/library dependencies; it reproduces no ABI
declarations. No physical or installed seat is touched.

The original held-button campaign and two additional capability cycles pass
135 native checks on the unchanged V31 core/V30 AQ binaries from V35. One cycle
removes an idle pointer, and one removes it with a physical button held. Checks
observe actual child device retirement, exactly one paired GTK release for the
held case, rejection of duplicate disable and absent-pointer motion, no button
events after a logical scale change while the device is absent, restoration of
one nested pointer, actual subsequent GTK input, and duplicate-enable refusal.
All controllers and the private GUI host exit with normal ordered cleanup.
Reused memory addresses are recorded and never treated as lifetime identities.

The accepted native report is
implementation/elm-parent-capability-v40/qa/native-1791099701423667415/report.json.
V45's protected freezer binds the model, comparison and native reports, unchanged
V35 owning tuple, private helper build/dependencies, seven failed attempts and
483 archived files. It explicitly records nativeFocusAcceptance=false and
releaseAcceptance=false.

## Open native parent-focus/layout failure

V41–V43 retain fixture synchronization failures: allocation alone did not prove
parent pointer ownership, an already focused view received motion rather than
a new enter, and the leave observation interval began after the cover mapped.
Fresh derivatives retain the original six-second deadlines and correct those
observation prerequisites.

V44 reaches actual parent GTK press/release receipts and a child wl_pointer.leave
on the wire. Cover buttons do not reach the child, and its pointer device stays
present. The logical scale request returns ok, but the monitor predicate does
not reach the requested scale within the original six seconds. Normal cleanup
passes. The child wire log contains repeated commits before the cover, a gap
while covered, and renewed activity after the cover exits during cleanup.
Frame-callback suspension is a hypothesis to investigate, not a proved cause.

V46 uses an RGBA cover with a 240×160 input/opaque region and reaches the same
141 checks before the same monitor-change deadline failure. It does not prove
that the parent shell keeps the child visible or that this hint survived every
GTK commit. Neither failed campaign certifies focus replay after a layout
change or stationary input after re-entry. The failures remain first-class
evidence; partial model/capability passes do not replace these obligations.

Next: inspect nested frame scheduling and owning monitor-rule application, fix
progress while parent focus/visibility changes in a fresh owning tuple, and
rerun the full original focus/layout oracle without widening deadlines. Native
configure-generation fencing, queued work retirement, multiple outputs/rotation,
physical devices, shared-shell integration on a coherent core, AT/IME, measured
budgets and complete roadmap/reversible deployment gates remain open.
