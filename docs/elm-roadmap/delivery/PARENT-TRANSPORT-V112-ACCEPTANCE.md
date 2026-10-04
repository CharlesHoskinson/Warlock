# Parent transport retirement V98–V112

The new AQ105 source retires a failed nested Wayland transport once, withdraws
its poll source on the next core idle, and fences copied and late frame work.
It uses the existing core89/authority90 ABI tuple and preserves every AQ79 public
header and export. Qualification covers an unheld private child connection loss
and the original six normal campaigns. It does not establish full transport
recovery, held-loss, physical-device or full-roadmap release acceptance.

## Preserved failure and fixture

V100 uses core89/AQ79 with an actual GTK physical press/release, then asks the
private Weston fixture to destroy exactly the focused child's Wayland connection.
The module verifies the child PID, Linux process start time, same UID, unique
client peer and actual pointer focus. It refuses held buttons, another process
incarnation and the parent PID. There is no process signal or parent termination.
The parent, its socket and the child process remain live; parent admission alone
does not establish child delivery. All runs retain the original six-second
observation deadline and protected lifecycle.

The old backend keeps both devices listed after loss and continues polling the
failed connection. Its private log contains millions of repeated transport
messages. The failed evidence remains, including normal ordered cleanup. V98's
initial warnings-as-errors compilation fails on two misleading-indentation lines;
V99 fixes only those lines and builds the real module/client against the owning
Weston source and headers. Protocol4 is limited to the gated private QA module.

## Implementation and proof

Only `candidate/src/backend/Wayland.cpp` differs from AQ79. Private event-loop
state records failure before callbacks can reenter. The backend drops focus and
serial, discards local publication tasks, destroys output policy/frame state,
removes queued frame idles, clears device vectors, and retires outputs from a
retained copy. Explicit Wayland selection becomes unready. A failed backend offers
no poll FD or new output, and late seat capability callbacks cannot recreate input.

Core idle notification removes the consumer's poll source after its current
`onSignal` function has returned. Output destruction keeps a local strong
reference, sends one retirement signal, and avoids parent attach/commit on the
failed connection. Destruction suppresses a duplicate retirement signal. The
frame idle checks retained lifecycle policy before dereferencing its captured
pointer; a copy already owned by an idle dispatch remains safe after destruction.
Late `scheduleFrame` refuses retired policy before queuing work. Transport is
checked immediately after reading, before dispatching pending protocol events.
Protocol wrappers retain their display until ordinary teardown.

The actual dispatch, poll, output destroy/destructor, frame-idle and schedule
bodies pass 63 typed replay checks with real Hyprutils shared/weak ownership.
Seven compiled mutations fail the corresponding oracles. The old actual bodies
reproduce the retained-device failure. The bounded Quint transport model executes
all 10 named cases, 1,000 seeded samples of up to 40 steps and eight typechecked
negative controls. It abstracts transport and idle interleavings; it is not a
complete compositor or renderer refinement proof.

V101's first replay mutation selector matches two queue-clear sites and is
rejected; replay2 selects the transport site explicitly. V102's late-frame mutant
leaves an unused iterator and fails compilation; replay3 removes the complete
guard and demonstrates the behavioral failure. These failed attempts remain.
V102 and V103 full library builds compile but their unchanged strict export audit
finds one optimized-away weak libstdc++ lifecycle-table support symbol. Constructor
no-inline does not preserve it. AQ105 excludes that experiment and explicitly
instantiates the exact support symbol under `__GLIBCXX__`, with no runtime side
effect. Its complete build and original dimension/presentation checks pass;
every predecessor export and public header remains. Future toolchain changes
still require fresh build/ABI qualification.

## Native qualification

The selected runtime library is AQ105
`build-1791109958106009410/cmake/libaquamarine.so.0.15.0`, SHA-256
`b7431f7036d28ed1f87a1aec9374a7700a2ebb9e819a707f0e8368a87cfcff97`.
Core89 remains SHA-256
`3e02556699f1e1667a88ace26f656ee380fce8a39b20d405a3f0d2757c65cd73`;
authority90 remains SHA-256
`c0bf07547a943e48d5493bc2df490a27c91c2e8def6060150fb59237ade5e20c`.
The AQ component manifest is SHA-256
`12b8c5ad32e64c8cd78fefa072877ba68244d5f6023997094edb07a7b582c089`.
Exact runtime mappings and owning compile/header closures are verified.

V111 passes 26 native check executions. Real pointer and keyboard disappear,
nested outputs retire, the corresponding socket registration leaves actual
kernel epoll state, the same child process and IPC remain live, and the parent
remains alive with the same socket identity. A subsequent balanced physical pair
through that parent produces no stale GTK buttons; the live recipient confirms
this independently. Failure is logged once and devices stay absent. Core's
headless fallback is distinct from DRM backend fallback. V104 already observes
device/output/poll retirement but its informational readlink fails because the
removed event-source descriptor is closed. V111 records that closure, preserving
every behavioral assertion. Both attempts clean up normally.

The six original normal campaigns pass 604 additional check executions:

* V106 input159: held buttons, capability retirement/restoration, parent cover,
  scaled layout and stationary reentry.
* V107 two-output51: logical origins, mode/scale/layout changes, background input
  isolation and focused-output removal with survivor input.
* V108 geometry96: actual configure/ACK/buffer state and seven RGB pixel stages,
  MAX desired-state idempotence, minimize/unminimize and exact restore geometry.
* V109 menu68: actual parent input, receipts, reflow, restored window state/focus
  with the mapped authority90.
* V109 cursor195: actual parent framebuffer extent/hotspot, blank/movement and
  stationary recipient assertions.
* V110 burst35: atomic capability bursts publish only current devices and real
  GTK physical pairs arrive at unchanged coordinates after replacement.

These total 630 native executions, not 630 distinct roadmap scenarios. Original
assertions, identities and deadlines remain. All campaigns use the shared native
lock and unchanged protected launcher, core limit1, private owned runtime/socket/
bus and exact process identity, explicit Wayland selection, disabled Xwayland and
normal ordered client/plugin/core/parent/bus cleanup. No installed desktop or
main-session window changed.

## Integration and open gates

Adopt AQ105 with qualified core89/authority90 or a newer reviewed owning pair
whose public AQ ABI is verified. Preserve the shared host's newer allocator,
admission, journal, recovery and staged-menu logic. The legacy menu regressions
here do not replace its current production transport or journal.

Held-button transport cancellation, early/unannounced and multi-output loss,
full native configure-generation fault coverage and reconnection remain separate
obligations. Zero-input/headless fallback focus behavior needs broader native
journey qualification. Physical rotation/hotplug/zero-output, hardware GPU,
AT/IME, original restore timing, whole-process budgets/soak, user journeys,
S01–S16/right-click/C00–C06 audit, reversible deployment and required activation
authorization remain open. The project goal stays active; there is no remote
publication.
