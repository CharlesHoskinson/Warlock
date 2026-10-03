# Staged minimize / restore motion

Candidate only; no live helpers, plugin manifest, compositor configuration, user
windows, installed libraries or native GUI tests were changed by this task.
Reader compatibility agent contributed the ignored keyboard catcher and changed
the candidate's absolute accessibility import to fresh WindowAccessibilityV4.

## Files

- `widget_v62/Windows.qml`: exact icon target lookup across taskbar instances;
  monitor origins, left/right/top/bottom placement, clipped scroll and hidden bar
  checks; passive motion IPC; asynchronous taskbar operations; accepted-intent
  `activate` semantics for rapid clicks. Includes reader agent's AX focus repair.
- `widget_v62/WindowMotion.qml`: transparent, empty-input-region layer overlay,
  one dynamic full-resolution image per address; shrinking/expanding geometry
  route with 190/230 ms ease; reversal starts from sampled rendered rectangle,
  retains old pixels until replacement image loads; independent window frames.
- `widget_v62/TaskbarPopup.qml`: copied current popup source unchanged.
- `hypr-windowctl`: front end for normal operations, lazy service requests.
- `hypr-windowctl-core`: copy of installed backend with only recursive calls
  routed through front end and preview-capture skip for an already-published
  identity-bound snapshot. It performs the established native pin/desktop/focus
  operations. No resize, position tween, alpha override or scratchpad animation.
- `hypr-window-motion`: identity-bound Unix service, monotonic unique tokens,
  full-resolution compositor `grim -T` capture and thumbnail publication,
  readiness-before-minimize / endpoint-before-restore handshake, journal and
  watchdog, close/reuse rejection, family focus reconciliation.
- `minimize_motion.qnt`, `minimize_motion_test.qnt`: qualitative lifecycle
  contract created before backend changes; extended before activate semantics.
- `test_minimize_motion.py`, `test_motion_core.py`, `test_motion_qml.js`: offline
  actual-source tests; never connect to the desktop.

## Guarantees established offline

1. The image travels from the native window rectangle to the taskbar's actual
   19 px Image icon, and back. There is no generic fade substituted for motion.
2. Native geometry is never changed for animation. Actual Bash core tests retain
   exact at/size, saved desktop and pin through minimize and restore.
3. Both stable ID and PID must match before capture acceptance and native commit.
   Address reuse cannot apply stale readiness, completion, image or recovery.
4. Only the latest address token can commit. Reversal samples its current eased
   visual rectangle. Another window's request never destroys this frame.
5. Native minimize waits for image readiness; restore waits for the expansion
   endpoint and retains the snapshot until native restore finishes.
6. Capture failure, missing/hidden/clipped icon or renderer rejection uses the
   established operation, cleans the snapshot and leaves no pending visual.
7. Reduced motion skips snapshots; file monitoring immediately stops an active
   QML tween, with an independent 40 ms service watchdog settling native state.
8. Watchdog expiry after shell loss commits the latest intent; service restart
   replays journaled intent only for matching identities and cancels old images.
9. Modal peers restore independently, then the captured modal focus member wins
   after all peers complete. Newer requests invalidate the old family focus.
10. Existing CLI callers remain synchronous until their token settles, retaining
    group recall / desktop / restore-all ordering. Taskbar requests asynchronous
    acceptance so clicks can supersede ongoing motion. `activate` atomically
    toggles accepted intent while capture/native taskbar snapshots lag.
11. The visual layer has no opaque background, keyboard focus or input region.
    Native geometry, compositor configuration and user opacity are untouched.

## Executed checks

- 9 named Quint scenarios pass; invariant sampling previously passed 2,000
  samples of 100 steps, and is rerun in `check.sh` for the final model.
- 28 actual-controller tests pass: readiness/endpoint, rapid intent toggles,
  capture-time supersession, independent frames, PID / ID reuse, failure,
  reduction, shell watchdog, journal recovery, failed reversal cleanup, foreign
  desktop ordering, permanent native failures and modal completion ordering.
- 9 actual Bash backend tests pass using a fake compositor: exact geometry/pin,
  stale identity/PID rejection, invalid PID and stale saved-state rejection.
- 3 actual daemon/socket subprocess tests pass in a private fake desktop:
  first startup with SINGLE/ASYNC flags, a later full family, sanitized daemon
  environment; stale socket plus old-journal recovery before opposite new intent
  exactly once; permanent core failure returns error and clears pending state.
  Every test daemon is gracefully stopped and its socket/runtime is cleaned.
- Existing 19 stateful windowctl/desktop scenarios and 165 desktop fuzz operations
  pass with candidate front end/core and explicit motion opt-out.
- Node executes actual candidate QML function bodies for visual continuity,
  previous-pixel retention, stale tokens, independent frames and reduced motion.
- Bash/Python syntax and qmlformat parser checks pass. qmllint reports only its
  standard Quickshell PanelWindow uncreatable-type tooling warning for the new
  motion component; runtime load still needs native validation.

## Integration and remaining acceptance

Root owns live installation and QA.md / requirements.md / PARITY_STATUS.md /
qa.sh. Install all three helpers together under ~/.local/bin and copy the whole
candidate widget directory to a fresh plugin path; then change the manifest and
rescan. This candidate uses WindowAccessibilityV4 from reader agent. Do not
activate Windows.qml against the previous helper (new activate operation).

Root's deployed v62 native trial has one in-flight client-only frame; blocking grim readback reduced observation cadence. It does not yet establish whole decorated-window motion. Coordinate one GUI slot to
check visible trajectory/capture frame/decorations, real timer pacing, rapid
min/restore/toggle, close, reduced mid-flight, shell reload while pending,
minimized thumbnails, pinned and modal family ownership, and exact geometry.
Also check workspace-switch and multi-display restore. In the final candidate: destination desktop/display metadata is validated against both PID
and stable ID, the desktop is selected while the native window stays minimized,
and taskbar snapshots are refreshed before expansion. Native validation remains
required. Cross-screen or spanning routes use immediate native fallback; a
snapshot is never animated clipped across an unrelated output. Such fallback
cases remain a visual parity gap. Transparent snapshots naturally overlap
other visible windows along the animation route; input still reaches them.

## Service / backend integration details

Production motion defaults on. `HYPR_WINDOWCTL_MOTION=0` delegates synchronously
to the core without starting a daemon, contacting the shell or changing backend
semantic tests. Export this only for isolated replay/semantic QA.
`HYPR_WINDOWCTL_ASYNC=1` requests acceptance instead of completion and is used
by the taskbar. `HYPR_WINDOWCTL_FAMILY_SINGLE=1` is carried per request; the lazy
daemon strips request-scoped flags from its environment. The daemon retries
actual socket connection until bounded startup/journal recovery completes; a
submitted request is never retried through a duplicate core fallback. Native
failure clears pending state and reports an error to synchronous callers.

`hypr-window-motion stop` gracefully settles current intents and exits its own
compositor-session service. Runtime/socket paths use a bounded SHA-256 prefix of
the compositor signature, avoiding Unix socket path-length problems.

The exact fixture change is staged in `windowctl-fixture.patch`: copy
`hypr-windowctl-core` beside the copied frontend inside Environment's fake home
and set `HYPR_WINDOWCTL_MOTION=0` in Environment.env. Root should apply those two
changes to ~/window-integration-qa/test_windowctl.py and export the opt-out in
qa.sh for its isolated backend replay subprocesses. Models are now frozen.

Reproduce all scoped checks: `./check.sh`. Candidate backend fixture commands:
`python3 test_windowctl.py` and `python3 fuzz_desktops.py`. Production defaults
must stay enabled for separate native motion tests.

## Final opt-out and native observer additions

The motion opt-out also supports `activate`: it captures the requested address,
stable ID and PID, then maps active visible windows to minimize and inactive or
minimized windows to restore. Both supplied ID and PID are preserved for core
validation. Four actual Bash tests cover these cases plus reused identity/PID.

`native_motion_trial.py --window ADDRESS [--window FAMILY_MEMBER ...] --output
DIR [--capture-frames] [--reduced-motion-trial]` targets explicitly supplied
disposable identities. It rejects unspecified transient-family members and
hidden/minimized starting fixtures. Its oracles are actual QML visual geometry,
image readiness, service loading/running acknowledgements, native minimize state,
exact native at/size/desktop/pin and identity-bound minimized thumbnail metadata.
It records layers separately and never treats focus as a motion pass/fail oracle,
so external exclusive sudo layers are documented without invalidating unrelated
geometry observations. Normal minimize/restore and rapid min/restore/min are
covered. Optional mid-flight reduction restores the original global setting.
Optional monitor screenshots provide reviewable rendered frames. Cleanup
supersedes pending requests with a synchronous restore of surviving fixtures.
Root ran the earlier driver; current separated observer and active-interruption driver are staged for the next native trial.

Read-only `motionVisualState` IPC returns actual dynamic-image rectangles and
progress across taskbar screens for that observer; `motionState` stays available
for full request snapshots.


## Whole-window capture candidate and observer correction

`whole-window/whole_snapshot.qnt` specifies the decorated snapshot contract before
candidate native capture changes; the original frozen motion models are unchanged.
`whole-window/native/` is an isolated copy of root's current caption/drag/modal
plugin source; those original files match root source hashes. Only a new native
snapshot entry and build dependency are added. The compositor/header ABI hash
check remains before hook registration. Its built `.so` is staged, never loaded
in the main compositor.

The native entry checks address/stable ID/PID, noScreenShare, monitor transform,
private runtime output path, and framebuffer dimensions. The compositor's public
`makeSnapshotFB` renders the requested window plus server caption/border into a
transparent framebuffer, independent of other windows. PNG readback preserves
premultiplied alpha and native geometry. EGL context, read/draw framebuffer and
pack alignment are restored around readback; safe JSON failure covers unavailable
windows, unsupported displays and exceptions.

`whole-window/hypr-window-motion` caches the full native frame by stable ID/PID;
restore requires matching identity and native client size, and composites the
latest client buffer inside the cached caption/border without losing rounded
alpha. Thirteen actual ImageMagick PNG/cache tests pass, including drift rejection, visible capture without grim, concurrent capture/cache consistency and bounded janitor ownership. `whole-window/widget_v64` is
the newest fresh widget candidate: V4 accessibility and all keyed models, correct
`bar.shell.bar` hidden-bar cancellation, and recovery agent's additive read-only
stateAll/stateForMonitor diagnostics. Both QML parser checks pass. Earlier v63
remains the source before those diagnostics.

Cross-screen, transformed and spanning rectangles currently fall back immediately.
A changed title while minimized retains the last captured server caption until
native reveal. Complex transparency/color-managed rendering and whole decorated
motion still require rendered acceptance; client-only v62 is explicitly insufficient.

`native_motion_trial.py` now separates no-screenshot route assertions from optional
instrumented screenshot replays. Rapid reversals and reduction wait for a matching
running journal token and actual visible Image.Ready animation with progress in
(0,1); fixed delays are removed. Reversal requires same ID/PID/pixel SHA256 and
bounded continuity on the prior eased route, rejecting full/native resets and
endpoint arrival. Six offline observer-contract tests pass. Same-ID/unchanged
native rectangle requests reuse the current captured bytes, avoiding grim latency
between active reversals; its actual controller test passes.

`whole-window/nested_smoke.py --output DIR` is a coordinated native test in a short
/tmp/ws-* runtime and isolated DBus compositor. It checks actual server caption
pixels, exact baseline/occluded image bytes, stale ID/PID rejection, geometry,
rounded alpha, plugin unload, and original main focus/cursor/window geometries
and AT-SPI preservation. First smoke safely rejected readback; cleanup and all
main-preservation checks passed. Missing EGL-current/READ binding and inverted crop coordinates were identified
from the exact compositor readPixels source and corrected. v14e nested smoke
passes all 13 checks. Client red pixels occupy rows30..269 matching metadata
inset30 + native height240; 6,428 gold caption pixels and title text are visible.
Occluded image bytes equal the baseline while the monitor screenshot shows the
blue occluder covering the target. Exact geometry, alpha edges, stale ID/PID,
unload and original main focus/cursor/geometries/AT-SPI all pass. Native artifact:
`~/.cache/window-whole-snapshot-smoke-v14e/snapshot-smoke.json` plus baseline.png,
occluded.png and monitor-occluded.png. Built candidate SHA256:
`175e32005669d32a61b1b3c2250a757014524d3abbec0c450c1ecca1312dcace`.
No main deployment occurred. Full decorated animation needs paired acceptance.


## Predeploy cache and edge hardening

The whole-window service now uses the native decorated PNG directly for visible
minimize and publishes its cropped client thumbnail; no second grim capture or
recomposition delays visible motion readiness. Hidden restore still refreshes
client pixels. Exported full rect/insets must recover the original client rect,
and the live mapped ID/PID/geometry must remain unchanged before publication;
drift rejects the snapshot and uses the established native fallback.

A snapshot lock serializes active capture/cache PNG+JSON pairs and collection;
staging filenames include each token. A nonblocking janitor is invoked at most
once/second even when no request is pending. It retains current exact-identity
minimized caches and removes closed/reused own full-ID-PID caches plus own
abandoned frame/composed/token staging files. It never deletes ordinary token
images or unrelated files. Prune was specified before these changes. The newest
whole service passes the same 28 controller tests and 13 actual PNG/cache tests.

Only decoration extents outside the output are now clipped when the entire
native client lies inside that output. Client spanning still rejects capture.
ClipDecoration was specified before this change. Updated native nested smoke
passes all 17 checks, including left edge x0, right edge x620 and top client y28
with actual caption gold/title pixels and exact client rows/geometry; client
x=-4 is rejected. All original occlusion, stale identity, alpha, unload and main
preservation checks still pass. Artifact:
`~/.cache/window-whole-snapshot-smoke-v14-edge/snapshot-smoke.json` plus edge PNGs.
Latest built candidate SHA256:
`6c9c346e9b7acb0951ee454ecfcf7dba295dfd0e4778d5dbdd883d96ca9c6274`.
The previous v14e hash applies to the source before this edge clipping change.

Scoped whole checks: `python3 whole-window/test_controller.py`,
`python3 whole-window/test_whole_snapshot.py`, and Quint invariant replay of
`whole-window/whole_snapshot.qnt`. Native smoke requires the coordinated GUI slot;
GUI slot is now released and no main candidate deployment was performed by me.

## Paired native integration observer follow-up

Root deployed the paired native snapshot/helpers/widget_v64 and ran unpinned and
pinned native trials. Current driver additionally requires a reversal start
strictly inside the preceding visual route (.001 < progress < .999), and more
than .5px max-field distance from both endpoints. These conditions apply even
when observer latency saturates the cubic velocity bound at1. Reports explicitly
record interior evidence and endpoint distances. Eight observer-contract tests
pass, including saturated-bound endpoint reset rejection. Production timing and
animation code are unchanged by this follow-up.

The driver now compares restored native fullscreen/fullscreenClient/handler
alongside geometry, pin and desktop. Instrumented screenshot replay also copies
the matching token's whole source PNG and native/full rectangles for review;
actual monitor screenshots remain separate from cadence assertions.

`native_motion_fixture.py --toolkit qt|gtk|family|foot --output DIR [--pin]
[--maximize] [--capture-frames] [--reduced-motion-trial]` stages broader native
coverage using disposable Qt/GTK fixtures or the existing native modal-family
fixture. It requires an allocated GUI slot and checks exact original desktop
window states plus focus/cursor cleanup. QML/Python parse checks pass; this agent
has not run those main-desktop wrappers. Root owns their native acceptance slot.
