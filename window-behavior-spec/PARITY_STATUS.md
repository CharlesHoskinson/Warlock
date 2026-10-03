# Windows 11 window-system parity status

## Current checkpoint — resumed work, 2026-10-03 UTC

Full parity remains incomplete. Candidates remain private; the main desktop is unchanged.

- **Pin campaign A passed:**14 feature checks. Bv4 completed B01–B10, including both MAX pin/unpin paths, two overlapping-window click cases and modal focus. It failed B11 because the QA incorrectly treated `allows_input=false` as an input blocker. A genuine native blocker setup is under review; the non-revival assertion remains mandatory. All18 main preservation checks and normal private closure/module unload passed. B12, remaining full-case predicates and B13–B24 remain unaccepted.
- **Restore remains rejected:** V28 passed444 CPU checks and its original collector passed169 CPU checks. The unprofiled baseline reached19 checks/17 pass: six focus actions and three refreshes completed before metadata at about692 ms; three captures exist, but no renderer seed/uploads before the original two-second deadline. All helpers exited normally and all15 main checks passed. Original baseline38/recovery34 remain mandatory. A pixel-preserving fused capture proposal is being refined before application.
- **Quint coverage corrected:** default name filtering previously executed zero of the declared45 restore transaction scenarios and14 producer scenarios. Both exact source models now passed explicit45 and14 named runs; original invariant traces remain separately retained. The selected35 pin design,20 transfer,24 hit and original205 collector named proofs were independently checked and unaffected. Historical false counts remain preserved and disclosed.
- **Process verifier:** V9 actual Qt-signal fault component and five V10 CPU components are independently accepted. Actual Quickshell/menu and reliability remain open.
- **Popup/input:** source review passed24 Quint cases/2000 traces,28 decoder/controller tests, one receipt-loop test and six QML-as-JavaScript checks. A fresh actual-Quickshell launcher and probe compiled against the owning candidate headers are being prepared. No actual Quickshell/native input/reliability acceptance yet.
- **Remaining:** complete pin/focus/masks/scroll/transfer; restore38/recovery34; original52 dragging/resize/reload; cancellation/reduced motion; actual popup/input/reliability; multiple displays/hardware cadence/accessibility; combined regression and deployment.

The [live status record](overnight-status.json) preserves failures and bounded evidence. This session is working after resume; the saved automatic goal remains marked blocked and automatic continuation has not been reactivated.

## Feature audit

This is the current implementation audit for the local Omarchy desktop. The
[requirements](requirements.md) define the acceptance checklist; the [QA report](QA.md)
records model, fuzz, backend and live checks. “Implemented” below means the
listed local behavior exists. It does not claim every Windows application API
is available to Linux applications.

| Area | Status | Evidence and remaining work |
| --- | --- | --- |
| Focus, raise, minimize, maximize, restore, close and window pin | Partial | Ordinary controls and inactive scrolling pass native checks. The deployed v18 retains the unchanged v14 bridges and the 13 ordinary modal input/family and 11 pinned/nested modal checks established on both Wayland and XWayland, including first-click delivery after reopening a dialog beneath a stationary pointer. Ten native Alt+Tab/Shake/Snap Assist paths also pass on both protocols. V13 now keeps pinned owners and actual modal descendants together across desktop switches: 12 main checks per protocol and 13 isolated checks per protocol, including legacy split-family repair on reload. Other toolkits remain open. |
| Titlebar drag, resize, double-click, right-click system menu | Partial; original full matrix pending | Native virtual-pointer trials cover every edge/corner, drag-to-top maximize, cancellation and a later move without stuck state. Exact drag-start normal rectangle restoration passes. Deployed hyprbars v18 retains synchronous titlebar/Alt/Super lifecycle handling; main-desktop v13 regressions pass held-edge pause, exact restore, Escape, anchoring and release after reload. Nested checks also cover maximize-to-snap and resize exclusion. V13 preserves the original caption press identity/offset on first motion and invalidates pending/active capture on reload; 14 live paths and 10 native Quint traces pass. Physical 240 Hz presentation/geometry sampling now covers caption dragging in Foot, GTK4 and Qt Quick; no >33.4 ms stall was observed in those captures. |
| Snap Layouts, corners, Snap Bar and Snap Assist | Partial | Maximize hover and Win+Z picker, half/quarter/third/asymmetric layouts, precise titlebar release, drag-to-top targets and candidate chooser. Native Snap Bar drop and square snapped/rounded restored corners checked live. The deployed Files Explorer now supports 330×320: 120 copied-app layout cases, 42 native size/Snap/control checks and 20 actual reload checks pass. Original same-process migration preserves public history/preferences and hidden pre-map state; 12 acceptance checks pass. FilesV7 keyboard and AT-SPI guards/routing are now deployed after48 broad actual reader gates,20 copied samePID reload gates and22 original migration/preservation gates; audible/braille/hardware use remains open. |
| Snap Groups and adjacent resize | Implemented | Group recording/recall, workspace/monitor cleanup, custom ratio preservation, four-quarter diagonal separator protection. Quint/backend geometry fuzz and live paired resize checked. |
| Window shortcuts and Alt+Tab | Implemented | Win+arrows, monitor move, minimize, Home, Z, Tab and virtual-desktop binds exist. Native Alt hold/release, Shift reverse and Escape cancel passed with temporary virtual-keyboard input; the original input setting was restored. |
| Task View and virtual desktops | Implemented | Actual pointer moves visible/minimized windows between desktops, reorders/renames desktops and drops on New desktop; keyboard navigation and close/switch tested. Deployed overlay_v13 adds AT-SPI actions, captured identity guards, desktop context menus and fixes stale active-desktop selection/rename Enter propagation. Native assistive creation, move, switch, rename, both reorder directions and close pass. Temporary test desktops and focus were restored. |
| Titlebar Shake | Implemented | Owner-targeted minimize-others toggle, isolated per desktop. Lua reversal/one-trigger, Python state tests, and a real three-reversal titlebar gesture passed; the disposable peer restored. |
| Taskbar launchers, grouping, previews, Jump Lists and keyboard | Partial | Persistent pins/order, combine modes, grouped actions, compositor toplevel thumbnails, desktop actions/recent files and Win+number/T controls are deployed. Dynamic LauncherEntry/DBusmenu app actions now import, update, populate on opening, and send clicks to their publisher. A minimized browser's actual thumbnail passed live taskbar and Task View checks. Current/all taskbar and Alt+Tab scope pass live checks; keyboard menus now support wheel input, row visibility and reliable reopen/dismissal. File-drag navigation is deployed through compositor activity/coordinate relay: single minimized restore, grouped preview selection, actual destination file drop, early leave and Escape cancellation pass native GTK checks. Running app order now survives focus/stack changes. Cross-display native GTK FileList dragging now passes 11 acceptance assertions across eight paths, including exact grouped preview selection, three verified byte copies, Escape and removal of an output during an open chooser; all 11 original-state restoration checks pass. Physical-display visibility and other native app compatibility remain open. Apps must supply app-specific data. |
| Show Desktop and Peek | Implemented | Per-desktop restore sets; live compositor opacity 1→0.03→1 and screenshot verified. Peek state is cleared when the taskbar widget reloads. |
| Multiple monitors and scale | Partial | Native headless second-output transfer, scale reflow, output removal and real QML monitor filtering pass; 2,000 monitor reflows augment geometry fuzz. Minimized home-display ownership, deleted workspace restore, minimized desktop move and removed-output fallback pass a dedicated native fixture. Physical hotplug remains open. |
| Motion and accessibility | Partial | 27 physical-output cases across Foot, GTK4 and Qt Quick pass: caption dragging, snap/maximize/restore, rapid reversal, reduced motion and mid-transition reduction. 3,634 paired hardware presentations show a maximum 16.669 ms display gap and 20.835 ms active geometry-update gap; missed 240 Hz refreshes are reported. Six Quint motion scenarios/2,000 samples check qualitative interruption, stale ticks and reduced submissions independently of measured timing. The V4 Qt extension and persistent keyed controls expose accessible actions; window menus pass 13 native assistive checks and shell controls pass 19 more. Actual Orca passes 16 checks for announcements, focus, navigation and native actions. A focused controls process now exits normally with V4. Eight accessibility scenarios/2,000 samples cover action lifetime/identity. Six physical repaint cases across GTK4, Qt Quick and Brave, with baseline and bounded CPU/browser load, add 4,353 paired presentations and no >33.4 ms observed content gap. Deployed v18/widget65 whole-window snapshots include titlebar/border pixels. Reversal freezes the displayed frame before metadata queries, preserves visible pixels across a third request, and retains cancellation guards for live minimized identities. Four strict native trials (Qt Quick, GTK4, pinned Foot and maximized Foot) each pass six paths including both reversals and reduced motion; the Qt reversal origins are at 28% progress, well before either endpoint. Seventeen native export checks cover occlusion, output edges and identity guards. The reproduced modal-family rapid-reversal race is now fixed in helper 836: fresh member state and all family reservations occur under one callback lock before peer preparation. Six strict native pinned-family paths and a fresh six-path Qt regression pass, including interior reversals and reduced motion, with original clients/focus/cursor restored. Candidate offline QA passes 105 Python checks and 17 actual QML scenarios, plus 12 freeze, eight family-scope and four family-order scenarios with 2,000 samples per model. The completed central installed-source run passes 48 files, 175 named scenarios and 48,000 samples across 24 models, plus backend replay/fuzz and 105 Python/17 actual QML checks; the previous 6add run is retained. Native profiles still show a visible reversal preparation pause; smooth provisional reversal remains open. Cross-screen routes settle directly. Audible/braille use, global reader commands with non-AT-SPI clients and other displays/rates remain open. |
| Reload, stale windows and failure recovery | Partial | Window and thumbnail stable identities, per-desktop batch state, reload hydration and live snap-size/position restore are implemented. Virtual output removal passes. Snap Group persistence now rejects foreign compositor tags, resolves only unique unknown targets, and passes nine Quint scenarios plus 1,010 installed replay states. Attention resolves an explicit or unique compositor before changing cache, reconnects only to that target and clears stale urgency. Six installed selection tests plus reconnect/focus checks pass; its guarded restart preserves main state. An actual nested compositor shutdown/restart passes eight checks, including exact normal geometry through reload and foreign-session group cleanup, while preserving main windows/input/accessibility. Full main compositor restart, physical hotplug and application-specific dialogs remain untested. |
| App attention, progress and numeric badges | Implemented; compatibility QA open | Hyprland urgency reaches a taskbar dot and clears on focus/close. LauncherEntry counts, progress, urgency and dynamic menus are received on D-Bus, support partial updates and clear on publisher disconnect. Independent urgency changes now refresh QML. Actual Brave download signals from the browser PID now pass through the main D-Bus receiver and live QML, with publisher restart/exit cleanup. User-local library/wrapper integration is deployed for future browser launches; the already-running browser was preserved. Other app compatibility depends on protocol support. |

## Reproduce the bounded QA

Run `./qa.sh` here. It typechecks and explores the Quint models, replays generated
traces against installed backends, fuzzes installed Lua snap/pin logic, and runs
stateful window/taskbar integration tests. The live pointer and visual checks are
documented separately in [QA.md](QA.md).


### Current incremental checkpoint

Guarded idle stop is deployed in helper 6d9. The completed installed-source central
run passes 50 Quint files, 179 named scenarios and 50,000 samples across 25 models,
plus backend replay, Lua fuzz and 112 Python / 17 actual QML checks. Source hashes
are unchanged through the run. The native actor lifecycle passes seven checks and
five preservation gates. Its window controller is byte-identical to helper 836;
the earlier 48-file run remains preserved.

Private global Orca terminal commands pass 15 native checks and 12 restoration
gates for stable US input. The corrected wider policy run
passes 51 native assertions and all 12 preservation gates, including a real denial
transition. The earlier failed reload-based fixture remains retained; those rules
are startup-only. The fresh private v6a lifecycle run passes 35 native checks and
14 preservation gates, including actual startup, owner churn, reader service
restart, irreversible retirement and surviving-device Caps/Num parity. Production
maintenance packaging and PointerLocator integration remain open. No main deployment or
broad keyboard compatibility is claimed. Canonical atlas v15 failed actual pixels
and remains rejected. The staged provisional route also needs observed per-output
reversal origins. Files retained hidden actions, prompt shortcuts, Home peer
identity and reload-focus fixes remain staged pending complete native acceptance.
The final Files focus model passes 21 scenarios and 2,000 samples; actual Qt
deferred restoration preserves newer Sort, Tab and prompt intent. Fresh Files V6
repairs the independent editable-text gap: 90 offscreen gates over 88 mutator
calls, 58 keyboard checks, and 12 formal scenarios / 2,000 samples pass. Its broad
actual Orca run stopped at Rename focus and remains rejected for deployment.
The isolated reader and copied Files exited; 23 of 24 preservation gates pass.
One original terminal title changed; the exact difference remains retained.

Atlas v16's seven scale-dependent caption cache failures remain retained.
Fresh v17 passes 34 feature checks and 12 preservation checks, including all 16
exact scale/transform trials, full-frame equality after both capture paths, and
two controls without capture. Its 33 input hashes remain unchanged. The corrected styled v18 run passes all 59 checks (47 feature and 12 preservation),
including controls and normal rendering. The guarded native-only main replacement
passes 18 deployment/preservation checks; the desktop now uses v18 with v14
retained for rollback. Helpers and widget65 are unchanged. Integrated QA passes
54 files, 190 named scenarios and 54,000 samples across 27 models, plus backend
replay/fuzz, 112 Python / 17 actual QML checks and the actual coordinate/cache
C++ helpers. All 82 frozen source hashes remain unchanged.

PointerLocator passes 11 formal scenarios / 2,000 samples, plus 41 Quint traces
replayed through 3,066 actual C++ transitions. Native integration and reader
pointer recovery are in progress. A private Omarchy Orca compat stage fixes the
official mouse-review active flag and adds a public device refresh method. Root
review reproduced a disable-during-backend-loss intent bug. The fresh mouse-review v2
repair passes12 formal scenarios,2,000 samples and14 actual source-method checks,
including independent disable-intent replays; actual reader outage recovery remains open. Continuous provisional animation is
being implemented with owned Wayland/EGL surfaces. The Qt presentation probe
remains diagnostic evidence only.

### Latest acceptance boundary

FilesV7 now passes its complete broad actual reader run:48 feature gates,359 command acknowledgements and25 original-preservation gates. The exact focused file, full/public selection and F2 payload agree; the real rename preserves115 source bytes. Durable nativeURLreload passes20 feature and21 preservation gates, including a rich prompt/selection/clipboard snapshot. Guarded original-process migration passes7 deployment and15 preservation gates;15 QML files and the accepted V6 native module at a fresh URL are deployed. Original Files667402 remains hidden with exact history/preferences/public/fullUI plus an empty focusIdentity, and unchanged operations/fileops spec. The installed-source central QA run passes58 Quint files,231 named scenarios and58,000 samples across29 models,112 Python/17 QML checks,164 actual Files Qt checks and12 Files source checks; all177 hashes remain unchanged.

The private pointer telemetry run confirms a new obsolete registration notification after release/reclaim. The fresh bounded ownership-fence candidate passes69 reached native gates, including8 real owner churn and4 alias churn cases plus actual Orca GTK child navigation. A later GTK popup hit timeout leaves full native acceptance incomplete; all14 preservation gates,296 frozen hashes and normal unload pass.

The owned EGL V4 producer passes mapped Intel Mesa material verification and23 of24 native gates, including captured window pixels and interior retarget feedback. Actual moving presentation gaps of54 and61ms fail the unchanged cadence bound. That candidate remains rejected for deployment; composite family/service integration and causal timing diagnosis continue separately.

### Current private native acceptance boundary: crash handoff follow-up

All five requested harness safeguards are applied before further nested runs. The current private host enforces mandatory Wayland with actual AQ4ed46 mapping and complete exact-peer IPC readiness; normal scopes inherit core1. Actual rasterV4 transport and primary output presentation are accepted independently. All2736 input hashes/6links and15 main preservation checks pass; producer exits0 and every private PID/runtime is gone. FullRGBA scaled raster remains failed at7pixels/8channels/maxerror2 with unchangedtol1. Cursor suppression removes369 prior cursor errors; actual disabled dithering leaves the same seven member errors, so no dithering-cause claim is made. Precision investigation and native family/taskbar/service/cadence integration remain open.

QtV5 confirms real public Qt6.11.2 same-process independent peer action and native WindowModal metadata, then fails owner-body route-to-child focus. All18 main checks and independent cleanup pass; fixture observation/portal descendants are under fresh diagnosis, without accepting the19-gate campaign. PointerPrivateV1 stopped beforeclients/phases on startup buffered-log observation; null cleanup masked the primaryerror. Its archived transport/all19 preservation and independent316+2913file/121link/process cleanup checks pass, but no pointer/keyboard/reader feature acceptance is added. Frozen historical attempts remain unchanged; fresh contracts/fixtures are being prepared.

These failures leave full Windows11 parity unproven. Installed central Quint/backend acceptance remains58files/231named/58000samples with177 unchanged sources; staged offline serviceV7 is75Python/46named/7models×2000 and is not installed native service proof. See QA.md, overnight-status.json and linked retained reports for exact scope.

## Actual Qt, full raster boundary, and pointer follow-up

Fresh QtV8 passes real owner-button baseline callback, native Qt WindowModal metadata and independent same-process peer callback. Blocked ancestor body still fails deepest child focus; before/after native hitOwner/pointerOwner/modalTarget are null despite correct real float cursor and no grabs/locks/constraints. Main18/source3290+6/normal cleanup passed. Core modal-parent filtering is a concrete source boundary for a fresh press-only candidate; no corrected routing is accepted yet.

RasterV6 now retains all4 complete screenshot comparisons and4 producer readbacks at progress0/.35 across scale1/1.5. Primaryp0 exact and primaryp.35 tolerance1 pass. Scaledp0 fails7pixels/8channels/max2; scaledp.35 fails2pixels/2channels/max2. All4 screenshots exactly match raw producer RGB over opaque black, with identical raw/composed failure vectors. This locates errors before compositor composition, without identifying shader versus sampling/blend/readback/oracle cause. All15 preservation/2881inputs+6links/186producerinputs/normal private cleanup pass. Separate collection Quint7named+2000×100 traces pass bookkeeping/refusal only; the real fullraster result remains FAIL.

PointerV3 actual keyboard and pointer sync readiness passed;78 reached gates passed, including actual official Orca pointer/frame/child behavior and fractional/negative/native geometry cases. Popup toolkit hit succeeds, but Orca current-item fails: correct negative y=-14 wraps to GObject unsigned4294967282 and overflows signed WINDOW component query. Fresh formal signed-boundary correction is being prepared; full popup/policy/lifecycle acceptance remains open. All19 preservation/source356+2915/121links/normal quiescent native unload/final exactPID/runtime cleanup pass. Seven unexpected portal/helper descendants were present before cleanup; abnormal fixture lifecycle is retained as failure even though all are gone.

ServiceV10 explicit native composition is frozen with112 candidate Python/61named/10models×2000 offline checks. It has not been run natively. Root review found zero-request IPC credential checks can reproduce retained IPC BrokenPipe; V11 must consume a bounded actual read-only version reply before its first native run. Actual taskbar/native family runtime/frontend/recovery, fullcadence and broad physical parity are still required. No main desktop input or restoration, installed module replacement, or relaxed gate occurred in these runs.

## Corrected private Qt modal candidate accepted; full goal remains open

The fresh modal-ancestor discoveryV2 avoids the rejectedV1 X11-only assertion by selecting protocol-specific region authority; both source/model branches were checked before loading. Actual private QtV9 now passes all19 unchanged public Qt6.11.2 toolkit gates and10 host gates. The reproduced blocked-owner body route, caption route, nested/deepest modal input, independent same-process peer action, exact family minimize/restore, actionable restored dialogs and normal destruction all pass. Report SHAe7f0a07338e1e84b8db468206f9bf1d1295ee8d55aea1757eac3ff72811467c5.

All18 original desktop preservation fields,3644 frozen files/6 links, normal fixture/pointer/daemon exit, native unload, exact ownedPID/start disappearance, runtime removal and archived parent transport pass independent audits. Candidate SO412c0fee was loaded only privately; installedv18 remains unchanged. Native X11/cross-toolkit/pinned family coverage and production deployment remain open. RetainedV1 review rejection and QtV8 failure remain unchanged.

Full PointerPrivateV4 is running in root's exclusive private slot, with all original pointer/policy/lifecycle cases and actual signedAX/speech/no-helper gates. No success is inferred before its terminal result. ServiceV11 has121 candidatePython/65named/11×2000 offline checks; its actual taskbar/native service/recovery proof remains pending. RasterV6 attribution preserves scaled pixel and cadence failures, excludes only proved CPU/ideal-math boundaries, and proposes further controlled GPU evidence. Full Windows11 parity remains incomplete.

Evidence: [QtV9 report](../window-integration-qa/qt-modal-private-v9/attempt-1/report.json), [independent cleanup](../window-integration-qa/qt-modal-private-v9/attempt-1/root-completion.json), [motion lifetime audit](../window-integration-qa/qt-modal-private-v9/attempt-1/root-motion-completion.json), [handoff53 guards](../window-integration-qa/crash-handoff-v5/review.json).

### PointerPrivateV4 terminal outcome

The97 reached native gates include96PASS, including the full negative-origin popup raw signal→signed original AX query→exact actual child→real Orca speech, plus public disable/toggle and actual pointer service absence/restart/current-item recovery. The full campaign is FAIL: normalGTK A exits0 without the requested exit acknowledgement, and strictterminal cleanup retains an actual org.gtk.vfs.Daemon activation/two unexpected helpers. Policy/lifecycle phases were not reached. Fullpointer/keyboard acceptance is not claimed.

All19 originaldesktop preservation fields,561 local/copy+3110external sources/121links, normalquiescent nativeunload, exactPID/start disappearance, runtime removal and archivedtransport pass independentroot audit. Normalfixture lifecycle remainsFAIL despite final ownedcleanup. Fresh causalV5 preparation is assigned;V4 remains immutable. [Report](../window-integration-qa/recovery-audit/keyboard-monitor/pointer-private-host-v4/native-pointer-attempt-4/native-pointer-report.json), [independent audit](../window-integration-qa/recovery-audit/keyboard-monitor/pointer-private-host-v4/native-pointer-attempt-4/root-completion.json).

## Resumed acceptance update

- PointerPrivateV5 passed all 185 actual pointer, policy and lifecycle checks. All 19 main desktop preservation checks and independent frozen-input/process/runtime/transport verification passed. Normal client acknowledgements and exits, no unexpected helper activation, and native unload are required and passed. This remains a private candidate; production deployment and physical hardware acceptance remain open.
- Family/taskbar V3 is retained as FAIL. Actual production icons, family minimize/restore, independent peer preservation and minimized previews passed. Its restore source evidence archive lacks the freshly composed epoch images; normal shell close selection returned 108 and forced cleanup was needed. Private portal activation caused unexpected helpers. All 15 original desktop preservation checks, 4119 inputs/8 links, recorded PID/start disappearance and mandatory parent transport independently passed. These failures are not waived.
- Root reviewed the separate X11 authentication/authority/cleanup packet and launched its first private Qt campaign. Native acceptance is pending.

## XWayland and GPU causal acceptance update

- QtX11V2 passed 19 toolkit/10 host gates with seven actual command acknowledgements. Real private no-cookie refusal/cookie acceptance and XCB mappings were verified. All 18 main preservation checks and independent 3823 files/176 links, normal fixture/pointer/motion/X server/host cleanup, display artifacts gone, runtime gone and archived parent transport passed. Modal candidate remains private and uninstalled. X11V1 launcher-permission failure remains retained.
- GPU causal V7 retained all eight final images and eighteen prefix/control read pairs. 92 gates reached, 82 passed. The original scaled 7+2 pixel failures remain; constant controls passed exactly and both read formats matched for all full images. Scaled progress0 first fails after member3; scaled progress0.35 first fails after member2 and gains a second failed coordinate after member3. This narrows attribution but does not uniquely identify filtering versus blend/attachment quantization. All 15 main preservation, 2983 inputs/6 links, normal producer wait zero, no helpers, owned process/runtime disappearance and archived mandatory parent transport independently passed. No raster or cadence acceptance.
- New collection model: seven named Quint scenarios plus 2000 samples at 100 steps passed. Collection and bindings establish bookkeeping; actual pixel failures remain failures.

## Actual taskbar/native family baseline accepted

Fresh familyV4 passed all19 native baseline gates, report eab144c1cdc4334f2487d8ee09f6b55a144cae07e79274356342dc4fd90f1539. The unmodified production taskbar supplied actual icon endpoints. Three-member owner/modal/nested minimize and restore used six retained actual epoch PNGs, matched actual uploads and complete accepted presentation/successful swaps before native commits. Minimized windows retained previews; independent same-PID peer and restored geometry/pin/deepest-modal focus were preserved. Service/producer/Qt/shell exited normally with no unexpected helper activation before native unload.

Independent root audit passed4345 inputs/8 links,203 exact production copies,15 main desktop preservation checks, every recorded PID/start disappearance, ownedruntimegone, no cleanup errors and archived mandatory parent transport. V3 failure remains immutable. This accepts only the private baseline: family draw-order, rapid reversals, membership changes, resource retirement/native recovery, full raster/cadence and deployment remain open.


## Resumed QA: manual sampler V8 and concrete interruption gaps

The explicit four-center highp bilinear diagnostic completed privately through
`family-raster-sampler-v8/attempt-1/report.json` (SHA
`0a3ed7ea819401a97e48e2fa0acaf32ad80a3411df8b1d136298552359976374`).
The run retained all44 full-image comparisons and eighteen causal read pairs.
It FAILED: scaled progress0 has10 bad pixels and progress0.35 has1, with maximum
channel error2 against the unchanged limit1. Raw producer and composed failures
match. Constant controls and complete paired read-format equality pass; actual
sampler state/digests/extents/shader match the reviewed candidate. Manual
sampling did not establish a repair or uniquely identify the failing GPU stage.

Root independently replayed every comparison from retained immutable pixels and
scene/presentation bindings, with the same failures. All3157 frozen inputs,6
links,15 main preservation checks, normal producer exit0, recorded host process
lifetimes, owned runtime deletion and archived mandatory parent transport pass.
The source/model collector passed37 Python tests,7 named Quint tests and2000
samples at100steps. Models validate bookkeeping and refusal; actual pixels remain
failed. No cadence, deployment, or full parity acceptance follows.

The feature audit found move-only cancellation tracking: held resize rollback
and ending the exact native controller during reload/unload need fresh fixes.
Minimize during a held gesture also needs separate current-geometry retirement
before capture, avoiding accidental rollback. Fresh native/SnapLua and ServiceV12
integration are staged; actual GTK/Qt Wayland/X11 interruption proof is pending.
The original Brave drafting/Files focus scenario is assigned a private local
compose-like fixture with an isolated browser profile and copied real Files.

Production accessibility maintenanceV2 is frozen with8 named/2000 Quint
samples,24 Lua/runtime scenarios,19 source/filesystem tests and7 signatures;
actual wrapper acceptance remains false. Review found installer mode stripping
and explicit-instance reader launcher routing gaps. Fresh V3 corrections and
actual private proof are underway; frozen V2 stays unchanged. Main desktop and
installed code/config were untouched during this resumed run.


### Further source corrections this resumed pass

Fresh production maintenanceV3 preserves byte+mode closure for2392 payload files
including38 executable helpers. It restores previous launcher modes during guarded
rollback and routes explicit reader --instance arguments correctly. Six mode
model cases and2000 samples plus26 source/filesystem tests pass. Root independently
verified2436 local,846 external,89 links and local modes; frozenV2 remains unchanged.
Actual production wrapper/reader acceptance remains false.

Fresh gestureV3 has19 named Quint cases/2000samples,16 source gates and33
source-derived extracted-function assertions. Root verified all835 frozen files
and reviewed exact weak target/lifetime capture, separate current-geometry
retirement, resize rollback and cancellation hooks that suppress unintended
nonrelease decoration/group drops and focus theft. Real input proof remains open.
A further source-backed delayed close bug was found: address-only asynchronous
unsnap can remove a newer lifetime's snap state. An exact native old-lifetime
notification and guarded helper correction are being staged formally. Touch
classification is unverified and is explicitly retained as required device work.

Fresh family-taskbarV5 preparation keeps product actors disposable and retains
QA histories externally through delegated bind/retirement seams. Its16 offline
checks pass; planned27 native order/retirement/cache/restore gates remain unrun
and unfrozen pending the reviewed native/SnapLua/service pair.


### Resumed native integration: 2026-10-01 21:05 UTC

Frozen ServiceV12 adds bounded live/retiring actors, monotonic actor numbers,
normal worker/renderer shutdown before exact directory disposal, cache pruning
without losing minimized previews, ancestor/native paint ordering and gesture
retirement before fresh capture. Its165 Python/90 named/14 models×2000 samples
pass; root verified all1148 inputs. Native gestureV4 adds a public Lua native
identity getter and exact old-lifetime close helper, preserving reviewed V3
cancellation guards. Root verified all936 inputs. Neither is main-deployed.

Fresh familyV5 actual full-Snap/helper run failed before Qt/service startup.
Copied HOME/.local mode0755 violates the observer's required0700. An actual
frozen-function sandbox reproduces this before any IPC. Two early gates pass;
29-gate integration remains unaccepted. All4899 frozen inputs/8 links, all15
main preservation checks, recorded processes and owned runtime cleanup pass
independent root audit. Normal explicit plugin unload and helper lifetimes are
not accepted. Fresh V6 corrects runtime-only directory modes, explicit private
OMARCHY_PATH and genuine inactive fileDrag relay supervision; full Snap bytes
and production taskbar remain unchanged.

Production proofV1 stopped before host creation: copied import-preflight.json
collided with the fresh runtime output. V2 corrected this with actual attempt
materialization testing (21 checks), then ran a real private host. Ten reached
gates pass, including disabled reader refusal before Orca imports and unchanged
owned profile. Actual Control.load loaded the candidate but its device guard
rejected the correct Btrfs mapping: statdevice58 versus procmapdevice30 with
the same exact path/inode. A read-only self mmap independently reproduces the
mismatch without executing native code. Normal explicit unload also refused
the guard; full maintenance/reader proof remains false. Root independently
verified2449 local+6347 external source bytes/modes and162 links, all19 main
preservation checks, no private helpers, processes gone/runtime removed and
archived healthy parent transport. A fresh formal-first calibrated kernel
mapping identity guard is required; do not remove device/inode checking.

The full Windows parity goal remains active. Required native held gestures,
group/focus positive-negative controls, original Brave draft/copied Files,
continuous family reversal/recovery, strict scaled GPU pixels/cadence, physical
displays/input/audio/braille and final integrated deployment are still open.

Kernel source confirms the mapping identity distinction used in the diagnostic:
[proc mapping display](https://github.com/torvalds/linux/blob/master/fs/proc/task_mmu.c)
uses the backing inode superblock device, while
[Btrfs getattr](https://github.com/torvalds/linux/blob/master/fs/btrfs/inode.c)
reports the subvolume anonymous device. The actual local read-only mmap
counterexample is the acceptance-relevant runtime witness; these upstream
sources are explanatory and do not assert identical local kernel source.


## Resume evidence — 2026-10-01T21:39:40.858464+00:00

Root ran three actual owned private campaigns, each in its own QA scope/Core1.

- Family/taskbarV6: full paired Snap hydration and actual QS taskbar query complete normally; five early gates pass. Idle exact `retire_gesture_current` aborts V20 at `WeakPtr.hpp:180`: uniquely owned CHyprBar weak references cannot be promoted with `.lock()`. Actual plugin offset0x294e8 and frozen source symbolization identify the call. No service or motion gates reached. All4912 frozen inputs/8links,15main preservation checks, recorded PID/start identities and runtime cleanup independently verified. Normal client lifecycle/native unload and full helper terminals unaccepted. Fresh V21 repair and V7 complete early JSONL archival are underway; old failures unchanged.
- Quantized rasterV9: actual primary raw and composed images match exactly; real shader/program/frame/attachment configuration passes. First causal binding fails because intermediate RGBA read pair6408 differs from required actual default BGRA pair32993. Original pair guard,44image oracle and tolerance remain unchanged. Two reached comparisons independently replayed; all3649 inputs/1286producer modes/55links,15main checks, producer exit0 and normal private transport/cleanup verified. Full raster acceptance false; fresh producerV8 must capture each causal prefix on the required owned target.
- Production proofV3/V4 mapping: actual calibrated Btrfs device30/inode guard now accepts exact loaded module despite statdevice58. Real load/reload/fresh incarnation and normal exact quiescent retirement/unload pass.43checks reached/42pass;19main preservation/source bytes+modes/links/processes/runtime/healthy transport independently verified. Stale incarnation specificity gate fails because the QA transport reports `IPC failed: ` without native Lua error text; the full proof remains false and later reader/pointer phases were not reached. Fresh proofV4 must preserve genuine error and unchanged policy evidence.

Browser draft/Files packet is frozen and preflight passes; its native run and52held Qt/GTK Wayland/authenticated-X11 scenarios wait for corrected gesture candidate review. Remaining full scope includes strict scaled raster, continuous motion reversal/recovery/cadence, physical display/input/audio/braille and final integrated acceptance/deployment. Main installed GUI and reader state remain unchanged.


## Resume evidence — 2026-10-01T22:04:25.820705+00:00

- V21 idle retirement now succeeds on the actual private compositor. FamilyV7 reaches19 gates/17pass and shuts down normally. Service `motionTarget` is rejected with exit125 before capture, so minimized fallback occurs and no cache publication is attempted; this establishes a harness registration defect, not a V12 cache defect. Source, helper identities and private cleanup are verified. Main preservation is12/15: a client workspace/focus/cursor changed during the run, origin unestablished. The failure remains retained; no main restoration writes. FreshV8 stages exact ServicePID/start/argv/source/environment registration.
- BrowserV2 reaches the isolated local draft page on a fresh profile and network namespace with only loopback. Renderer sandbox identification times out before Files/input tests. Ten actual private-bus helper activations are unexpected. Full focus/Files acceptance remains false. Browser exits normally, V21 unloads normally and18main preservation checks pass. FreshV3 retains raw renderer process evidence and corrects private helper startup.
- Default-target rasterV10 completes and independently replays all44 original full-image comparisons. All18 causal target/prefix/read-format bindings pass. Secondary output at progress.35 fails83pixels; the child top boundary lands on pixel center y157.5 and the failed top row retains the preceding prefix. Fresh explicit coverage diagnostic is being staged; oracle/tolerance remain unchanged. All3813 frozen bytes+modes/55links,15main checks, producer exit0, host/runtime/process/transport cleanup independently pass. Raster/cadence/production acceptance remains false.
- ProductionproofV4 passes61/61 actual maintenance/reader checks and19main preservation checks. Real enabled private reader uses Manager, pointer capability reaches actual GTK child, selected global command consumes client bytes, normal reload restores learn configuration and exact balanced H packets, stale native incarnation is specifically refused without changing new capture policy. Root verifies2461local/13703external bytes+modes/162links and normal helper/process/runtime/transport cleanup. Original root-completion conservatively lacks its finally-only unload field because proof_cases already unloaded normally. Additive root-retirement-completion independently replays3exact identity→prepare ready→same identity→artifact unload ok→module absent sequences. Private maintenance acceptance passes; main deployment/audio/braille/physical input remain open.

Remaining: fresh service/taskbar and browser campaigns, real minimized-preview frontend routing,52held move/resize interruption cases, scaled raster repair, continuous reversal/recovery/cadence, physical display/input/audio/braille, and final integrated production acceptance/deployment. Full Windows parity is incomplete; the continuation goal remains active.


## Accepted familyV8 private baseline — 2026-10-01T22:11:28.314333+00:00

Fresh source-reviewed V8 passes29/29actual native gates and15/15main preservation checks. Exact service PID/start/PGID/source/argv/environment registration permits the real six motionTargets and three motionRefresh calls through unchanged production helpers, with all query/helper processes completing normally. Root independently verifies5612frozen inputs,1354declared modes and137links, normal Qt/QS/service/two renderer exits, clients/helpers before normal V21 unload, complete raw helper archive and healthy parent/runtime/process cleanup.

Causal supplement independently validates six real returned capture sources, two matching renderer seeds/uploads, and three immutable cache PNG/pointer pairs unchanged at capture, minimized actor disposal, restore actor disposal and final archive. Minimized previews remain available; restore preserves geometry, per-member pin state and deepest modal focus. The prior missing-cache failure was caused by harness service-query rejection; ServiceV12 remains unchanged.

This accepts the private full-Snap/taskbar/directServiceAPI baseline. Genuine preview pointer/keyboard callbacks,52held input interruption cases, continuous reversal/recovery, strict scaled raster/cadence, physical device/display/audio/braille and integrated production deployment remain open. Full Windows parity is not accepted.


## BrowserV3 retained failure — 2026-10-01T22:17:48.056494+00:00

Fresh40036file/mode+13758link packet passes source review/preflight and runs on an explicit activation-free owned private bus. Actual readonly ListActivatableNames contains only builtin org.freedesktop.DBus and exact socket peer is the owned bus process. No unexpected private helpers remain; browser/native module/host shutdown is normal. All18main preservation checks and frozen closure/process/runtime/transport checks independently pass.

The flow stops before renderer attach/Files/input on its added actual /proc-environ selector check. Exact pre-exec bus selectors passed, but the failing checker did not retain actual parsed/raw selector bytes. Retained browser cmdline shows actual flattened process title. Upstream Chromium process-title code copies libc environment and clears the original argument/environment memory range; a representation mismatch is a source-backed hypothesis, not yet actual selector proof. Fresh diagnostic must retain raw evidence and establish meaningful exact private bus authority before input. No browser focus acceptance or full parity claim.


## Resume checkpoint — 2026-10-01T22:54:07.915919+00:00

- [x] Re-read crash handoff: all five previously applied protections remain mandatory for these private runs.
- [x] Half-open coverage candidate: actual 114 checks; independently replayed all original 44 images, 18 default-target bindings and four configuration records.
- [x] Default renderer: actual 115 checks without experiment flag; independently replayed the same 44 images and verified exact default role. Original tolerance and oracle unchanged.
- [x] Browser V5: actual private-bus PID binding, renderer seccomp/network isolation, local DOM/native identity and real copied Files launch reached. All18main/normal cleanup independently verified. Full flow **failed** on unlisted libnss_resolve disk mapping before input.
- [x] Continuous campaign preparation: 72 Python checks/two parser probes, six Quint scenarios/2,000×100 traces and 23 adversarial evidence tests.
- [ ] Continuous native acceptance: V1 **failed**. An API request began while the restore frame was interior, but acceptance took **334.778 ms**; actual renderer receipt took333.816ms, after the previous endpoint. Second origin was progress1. Strict oracle retained unchanged. Main15/source/mode/link/process/runtime checks passed; explicit native unload gate remains unmet after failed workload/helper count. FreshV2 stages guaranteed clients-first unload on failure.
- [ ] Fix request responsiveness with receipt-safe locking/queue semantics, then replay both interior reversals and ordinary default-renderer retirement.
- [ ] Complete BrowserV6 NSS closure/raw-mapping diagnostics, then real draft→Files focus and dragging.
- [ ] Run all52 held gesture cases and genuine minimized-preview→CLI→service input.
- [ ] Complete durable recovery, mixed-output animation, physical cadence/device QA and final guarded deployment.

Default raster is accepted in the isolated diagnostic route. Full Windows parity remains incomplete and these candidates are not installed on the main desktop.

Evidence: [default raster](../window-integration-qa/family-raster-production-default-v12/attempt-1/root-completion.json), [browser failure](../window-integration-qa/browser-files-flow-v5/attempt-1/root-completion.json), [actual reversal latency](../window-integration-qa/family-continuous-reversal-v1/attempt-1/root-latency-attribution.json).


### Follow-up to resume checkpoint

BrowserV6 also retains a failed full-flow result: all18main/privatebus/process/runtime gates independently pass, while raw maps expose33 unlisted stable disk inputs andtwo deleted data mappings before real focus input. A fresh dependency/provenance candidate is being prepared; the strict V6 failure remains unchanged. Held52V2 is source ready (47 tests,24 formal scenarios,4,000 traces;20,363 inputs/modes and320 links), awaiting root review and actual execution. The reversal stall is source-confirmed: a shared reservation lock encloses slow native observations and shell refresh; a fresh responsive service fix is in preparation.


## 2026-10-01T23:17:41.687649+00:00 — responsive animation integration accepted; full parity remains open

- Frozen responsive service V13: 187 Python regressions, 98 named Quint scenarios, 15 models × 2,000 traces pass. Root separately reviewed exact 3,126 inputs/modes and 138 links. Slow preparation observations no longer hold the reservation lock; atomic native effects retain ownership checks.
- Fresh continuous V3 actual campaign: **38/38 pass**, independently replayed. Both reversals originate from actual displayed interior frames (progress 0.167293 and 0.074576), reuse three immutable uploads, and bind the latest exact three-member commits to real presentations. Four actors and 12 retained source images validate independently. Requests took 3.174, 1.627, 1.393 and 3.452 ms. The prior 334.778 ms stall and all failed V1/V2 evidence remain immutable.
- All 7,939 frozen file bytes/modes and 146 links, all 15 main observations, normal explicit native unload, client/renderer/helper retirement, private runtime disposal and mandatory parent transport passed. No main GUI or restoration writes.
- V2's full campaign failure was a harness representation error: three exact PNG/JSON pairs produce a six-entry dictionary. V3 checks six entries with three of each after the unchanged three-pair identity/hash validator. Original strict reversal oracle remains byte-identical.
- Held52 V2 stopped before its first case on taskbar readiness/shutdown schema. All 18 main checks and 20,364 files/modes + 320 links stayed exact; forced private shell shutdown means normal unload is unaccepted. A fresh V3 harness correction is in progress; no actual dragging/preview claim follows from this failure.
- Browser V7 is preparing all **32** observed missing stable inputs (prior 33 count was a typo) and exact owned read-only tmpfs data provenance with temporal replacement refusal. The real draft-to-Files focus/input scenario is still unaccepted.

Evidence: [continuous terminal audit](../window-integration-qa/family-continuous-reversal-v3/attempt-1/root-completion.json), [independent causal replay](../window-integration-qa/family-continuous-reversal-v3/attempt-1/root-causal-completion.json), [held failure audit](../window-integration-qa/toolkit-held-matrix-v2/attempt-1/root-held-terminal-audit-v1.json).

Remaining: genuine taskbar hover/preview restoration and all 52 toolkit drag interruptions; real browser draft/focus/drag; pin/legacy lifetime coverage; durable recovery/resource fault interleavings; full mixed-output/default animation and velocity/cadence; physical monitor/input/audio/braille/reader routing; final guarded deployment and regression. Full Windows parity and production readiness remain **unaccepted**. The active loop retains the complete requirements scope.


## 2026-10-01T23:28:47.078072+00:00 — remaining velocity defect isolated and primitive implemented

Independent source-to-native replay of continuous V3 confirms every displayed
member rectangle follows the frozen V10 linear interpolation. Its two reversal
boundaries reset derivative by up to 2,414.17 and 2,093.98 logical pixels/second.
The existing 38 position/lifecycle checks remain accepted; they do not establish
velocity continuity. [Retained audit](../window-integration-qa/family-continuous-reversal-v3/attempt-1/root-velocity-audit.json).

A fresh isolated cubic Hermite family primitive carries the origin derivative,
uses one common duration, preserves positive dimensions, and reaches the exact
endpoint at zero velocity. Five named Quint scenarios, 2,000 × 100 model traces,
and 2,000 randomized numeric families / 2,012,018 checks pass. The initial Quint
test-action preparation failure is retained. [Contract and implementation](minimize-motion-stage/provisional-route/family-scene-integration/producer-trajectory-dev-v11/CONTRACT.md).

Renderer integration must bind derivatives to the same immutable accepted
per-output frame as positions and preserve static diagnostic geometry, source
order, cache/native authority and all original raster/reversal/retirement gates.
No renderer, native velocity, physical cadence or deployment acceptance follows
from these primitive checks. Browser V7 and Held52 V3 source work continues.


## 2026-10-01T23:46:50.444806+00:00 — resume: bounded primitive passes; live setup failures retained

- Held52 V3: exact Quickshell readiness and normal shutdown passed. First child fixture failed native mapping readiness before any held gesture. Early helper lifetime registration and transportchecker import also need correction; fresh V4 is preparing them. All18 main observations and frozen20,680 bytes/modes +320 links remain exact. Full held/preview and complete helper/transport acceptance remain false. [Retained actual audit](../window-integration-qa/toolkit-held-matrix-v3/attempt-1/root-held-terminal-audit-v2.json).
- Browser V7: original focus/input flow stopped before input on strict producer FD metadata. One exact compositor FD matched the Files read-only deleted UUID mapping, but raw stat was not retained, so the failed conjunct is unknown. All18 main observations,40,164 bytes/modes +13,770 links, normal clients/unload and private runtime/transport pass independently. V8 records raw metadata before the unchanged predicate. [Retained actual audit](../window-integration-qa/browser-files-flow-v7/attempt-1/root-completion.json).
- Independent V11 numeric review found trajectories exceeding its own admitted geometry/velocity bounds. Prior passing tests and both concrete counterexamples remain retained. V12 constrains geometry and derivative Bezier control hulls with a common duration intersection, refusing impossible intersections before submission. Five named Quint scenarios,2,000×100 model traces and2,012,523 numeric checks over2,000 random families pass. [Isolated checkpoint](minimize-motion-stage/provisional-route/family-scene-integration/producer-trajectory-dev-v12/offline-checkpoint.json).

Remaining: all52 live held input cases/genuine minimized previews; original browser draft-to-Files focus/drag; legacy pin correctness; renderer integration of accepted position and velocity together; durable recovery/resource faults; mixed-output/cadence; physical display/input/audio/braille/reader routing; guarded deployment and final full regression. Main GUI/restoration writes are absent in these runs. Full Windows parity remains incomplete.


## 2026-10-01T23:54:33.310610+00:00 — exact shared-data mismatch isolated; mapped fixture correction verified

Browser V8's retained failed diagnostic establishes the exact mismatch: the producer FD is a regular, owned, unlinked, read-only tmpfs object with mode0000 and size2960. Only the old fullMode600 conjunct fails; raw fdinfo/mount hashes and inode/device identity independently replay. Installed Hyprland explicitly fchmods this shared allocation to zero. V9 must specify exact0000 first and retain all other authority checks; prior failures remain unchanged. All18main,40,172 byte/mode inputs +13,770 links and normal cleanup/transport/privatebus pass. [Cause](../window-integration-qa/browser-files-flow-v8/attempt-1/root-shared-data-attribution.json), [terminal audit](../window-integration-qa/browser-files-flow-v8/attempt-1/root-completion.json).

Held V4 verifies four mapped fixture lifetimes and early close registrations, normal public/QS/input EOF and ordered unload. Actual mandatory parent transport now passes. Before any held gesture it fails strict toolkit backend module closure; raw candidate paths were not retained. Partial cleanup also asks for serviceMembers before that workload is registered. V5 must retain raw mapping evidence and correct partial-failure accounting without accepting missing full workload. All18main,21,004 byte/mode inputs +320 links remain exact. [Retained full failure](../window-integration-qa/toolkit-held-matrix-v4/attempt-1/root-held-terminal-audit-v2.json).

V12 trajectory primitive now independently passes the copied2,012,523-check suite and an additional64-member40-reversal campaign (2,560 exact origin pairs;258,560 bounded samples). [Review and integration design](../window-integration-qa/velocity-primitive-review-v12/INTEGRATION_REVIEW.md). Renderer/native C1 acceptance remains open. Full Windows parity is incomplete.


### 2026-10-01T23:58:38.186387+00:00 — Browser V9 progress and retained full-flow failure

Fresh exact mode0000 contract/model precedes runtime change; root verifies the helper differs only in that exact permission predicate and diagnostic label. 114 Python tests,69 named cases,7 models×2,000 traces pass. Actual V9 accepts owned Files/compositor before/after read-only UUID FD provenance. Full input flow still stops before input because root Brave retains a4MiB rw-s deleted BrowserMetrics profile allocation despite the fixture prevention flag. Raw maps identify the allocation; its FD metadata and source attribution are not established. No exception or altered prior result was added. All18main,40,179 byte/mode inputs +13,770 links, normal clients/unload/runtime/transport/privatebus independently pass. [Terminal audit](../window-integration-qa/browser-files-flow-v9/attempt-1/root-completion.json), [mapping follow-up](../window-integration-qa/browser-files-flow-v9/attempt-1/root-mapping-followup.json).

Active source work: HeldV5 backend closure/evidence and partial failure accounting; fresh C1 renderer V13 integration; durable recovery V13. All52 actual gestures/genuine previews, original browser focus/drag, legacy pin correctness, mixed-output/cadence, physical accessibility/device QA and guarded final deployment remain outstanding. Full Windows parity is incomplete.

## 2026-10-02T00:34:04.007712+00:00 — retained drag failure isolated; fresh source fixes reviewed

- BrowserV10 LocalMemory fixture still failed before input. BrowserV11 read-only actual diagnostic binds root PID/start/scope/UID/source and exact FD7: owned mode0600 regular unlinked4194304-byte file on runtime tmpfs, exact rw-s offset0 mapping under owned0700 browser profile. Strict old deleted-mapping failure remains. Both terminal packets independently preserve all18main and complete byte/mode/link closure with normal cleanup. BrowserV12 formal-first bounded owned data contract exists; independent review requires concrete replacement identity tokens before implementation. Original browser15 focus/draft/Files gates remain unaccepted.
- Genuine HeldV5 reached the actual gesture and failed independent-focus oracle. Retained trace proves pointer movement reactivated captured source before Escape. No complete after-retirement sample was persisted; Escape-specific theft cannot be concluded. Two exact gone host descendants remain unattributed, so full host/full52 acceptance is false. Fresh V22 preserves independent native focus only against FFM back to exact live captured source. Root independently reconstructed every inherited implementation body, reviewed exact3native deltas and output-only Makefile change, froze/verified21595files+modes327links. Original strict HeldV6 actions/intervention/oracle remain; full52/genuine previews pending.
- C1V13 renderer source ready: root verified2019files+modes49links and37successfulofflinecommands, byte-exact V12primitive and inherited raster native sources. Immutable sample supplies drawing/submission and accepted presentation position+analyticvelocity; all-output duration plan precedes token advance and duplicate start is idempotent. Native original44raster/38reversal/kinematics/mixed-output/reduced/cadence remain pending.
- RecoveryV14 frozen source proof259Python141named20models×2000: journaled gated sources/authenticated retained keeper/restart guards. Actual restart/new latency not accepted. Explicit cancellation discharge remains unimplemented.
- Crash handofffive safeguards remain required. No main desktop/config/deployment writes in these runs. Full parity remains incomplete and goal active; classification: progress.

### 2026-10-02T00:37:38.067154+00:00 — first actual V22 drag regressions pass; full matrix retained failed

HeldV6 root93842 exited1 in uniqueqa-harness-ad1484709b8d4c79bd0dd746dd10d37d scope. Actual QtWayland move-Escape and move-reload passed the unchanged strict original oracles. Independent terminal replay accepts both native cases and public quits; additive retirement replay binds both exact O_EXCL observations and proves independent native focus before/after, core retirement, groups and rawhold preserved. Third move-unload-reload stopped on an actual refused helper before next load generation/retirement observation. Original whole campaign remains failed. Terminal replay16/22 checks pass; all18main/full21804bytes+modes327links/normal inputEOF/explicitQSquit/nativeorderedunload/allrecordedidentitiesgone accepted. Fullhost/helper acceptance false: one exact unexpected gone host lifetime is unattributed and refused event invalidates helperbudget. Full52/genuine previews/remainingbackends/deployment unaccepted. Root is tracing exact helper ownership/argv/generation before a fresh derivative.

### 2026-10-02T00:51:02.717789+00:00 — browser witness reaches exact deleted-data state; parent assumption fails

BrowserV12 root7504 terminal exit1, scopeqa-harness-7cced63944e843f6a134a3f06d170737. Formal refinement50named/2000traces precedes runtime; offline152Python119named8models×2000 and independent31actualkernel tests passed. Root proves all7oldmodels and completeRunSessionAST outside approved mapping/anchor insertions unchanged. Frozen40477files+modes13770links/preflight accepted. Actual run passes4original gates and stops beforeinput because BrowserMetrics parent is absent bothbefore/after samples while actualrootFD7 retains exact owned0600 regular unlinked4194304bytes/O_RDWR/noO_PATH flags32770/mount346/device84/inode330537 and fullrw-s offset0VMA. The strict proof remains rejected. Root terminal audit all12independent safety/source/cleanup gates and18main preservation pass; allrecordedlifetimesgone, normalbrowser/Files/input/plugin/probe/host/runtime/transport/bus accepted. Original15/browserfocus/drag unaccepted. Fresh actual parent-state semantics/fixture review precedes any new authority.

HeldV6 source/log attribution now explains three refusedhydrations: nativeplugin unload schedulesone actualconfigreload and load schedulestwo (core+unchangedpluginAPI request). The original harness reserved only explicitloadgeneration. Late probe-unload also queueshydrate, explaining the exact unexpectedgone hostPID. This attribution does not accept existingfullhost/helperbudget or original52campaign. FreshHeldV7 must bind every exact actualevaluation with per-occurrence/root/lifetime/argv authority and retain duplicate/unrelated refusal, originalexplicitreload and allstrictfeatureoracles.

Full parity remains incomplete; current goal active, classification progress. C1V13 source independently reviewed; fresh44raster/38reversal/kinematics packets in preparation. RecoveryV14 native/restart/cancellation/mixedoutputs/cadence/physicalcompatibility/finaldeployment remain required. No main GUI/config/deployment writes.


## 2026-10-02T01:11:47.428398+00:00 — C1 renderer passes private integration and mixed-output QA

- Fresh C1V13 default raster:115 native gates and independent44 original image comparisons pass, retaining18 causal targets/4quantized bindings/defaultrole and full4519byte-mode/55link closure/all15main/normalcleanup.
- ContinuousC1V4: all39 actual gates pass, preserving the original38 and adding exact accepted presentation position/analyticvelocity replay.29 accepted samples include both nonzero-velocity interior origins; independent root8433byte-mode/146link closure/all15main/clients-before-unload/normalprivate lifecycle passes. Complete independent native causal replay is pending; physical cadence and deployment are not accepted.
- Mixed-scale C1 software:11 actual gates plus13 independent preservation/replay checks pass.49 actual samples and4 exact displayed-origin pairs span scale1/1.5 outputs; duplicate start keeps its epoch clock. Exact cancellation delegate clears readiness/pending/active state and commits transparent layers. Sources8478/modes/146links, all15main and normalparent/runtime cleanup pass. Generated software fixtures do not accept a native window family or the end-user reduced-motion setting.
- BrowserV13 formal70named/2000x100 precedes narrow runtime parent-state refinement;162Python/139named/8modelsx2000 and41kernel fixtures pass. Independent runtime review, rootfreeze/preflight and original15 actual focus/draft/drag flow remain pending.
- HeldV7 evaluation-ticket model15named/2000x100 passes before implementation; original52 actual held gestures/genuine previews remain open. Recovery/cancellation, pinlegacy completeness, physical cadence/devices/accessibility and guarded deployment remain required.

All five crash-handoff safeguards remain applied. No main GUI/config/deployment changes in these runs. Full Windows parity remains incomplete; goal active and this continuation made progress.


### 2026-10-02T01:13:43.657651+00:00 — continuous C1 independent replay accepted

All39 gates and original38 names/oracles survive independent replay. Across4actual renderer actors,88accepted frames match2,112 independent Hermite position/derivative component checks. Both nonzero displayed origins match retained exact position+velocity samples,12source PNGs and immutablepairs remain exact, and4native commit triples bind to current successfulswap/ready/endpoint. Full8433byte-mode/146links/all15main/normalprivate lifecycle pass. [Root completion](../window-integration-qa/family-continuous-c1-v4/attempt-1/root-causal-completion.json). Genuinewidget preview routing, native mixedfamily/reducedsetting/physical cadence and production deployment remain open.


## 2026-10-02T01:28:23.960479+00:00 — browser data witness accepted; original flow stops at geometry

BrowserV13 fresh actual4original gatesPASS after rootfreeze40780bytes/modes13770links. StrictFiles and BrowserMetrics witnesses now accepted, including before/after/postdisk detached-parent state anchored to exactprofileFD and oneFD7/full0600/O_RDWR32770/unlinked4MiB/tmpfs/fullrw-s VMA. Independent4snapshot raw/hash/metadata/parent-state replay passes. Full original15 remainsfailed before input:105identical layoutpairs have native/DOMouter930×700, DOMinner890×563, ratio1, while old readiness assumes zero horizontal viewport inset. Widthdifference does not establish viewportorigin. Rootall12safety/source/cleanup/all18main passes, normalclients/unload/host/runtime/transport/privatebus preserved. [Data/layout replay](../window-integration-qa/browser-files-flow-v13/attempt-1/root-data-and-layout-replay.json). FreshV14 exacttrustedpointer coordinate witness/integer point selection is formal-first; no guessedoffset/tolerance.

HeldV7 source/rootCPU/freeze/preflight passes22167modes327links, original52actions/oracles unchanged. Late independent review finds actual extraevaluation ordinal3 while model kept2 and allowed unreachablecleanup. NoV7native run was launched; freshV8 will model permanentviolatedboundary/quarantine without changing actualguard/budget. PriorfrozenV7 and failures remain. Pinread-onlyaudit finds address-only asynchronous/timer and legacytwofieldstate provenance gaps; concrete fix/nativecoverage remains queued. RecoveryV15 cancellationformal22named/2000 passesbeforeimplementation; usercancel/interruption/reducedmotion ingress remains open.

Fullparity remains incomplete. C1raster/continuous/mixedsoftware private acceptance retained. No main GUI/config/deployment changes; goal active, progress.


## 2026-10-02T02:02:17.775522+00:00 — drag unload/reload passes; preview and browser calibration failures retained

- HeldV8: original Qt Wayland move–Escape, move–reload and move–unload/reload pass. Fourth move–minimize–preview fails entering the native preview layer. Four independent native retirements pass; whole52 remains failed. Terminal replay19/24 preserves all18main/full22476bytes+modes327links/normal lifecycle. All112 helper events are normal. The new evaluation auditor also rejects a separate root invocation mistake (bare `python3` instead of reviewed absolute `/usr/bin/python3`); auditor stays strict and failure is retained.
- BrowserV14: source198Python/184named/11models×2000; root36focused tests/preflight pass. Actual flow stops before first click at button-free coordinate calibration. Independent48snapshots show exact Browser geometric hit/cursor but pointer and keyboard focus remain Files under actualfollow_mouse0, with no DOM pointermove. Full original15 remains open. All12independent safety/all18main/full41111bytes+modes13770links and normal cleanup pass. FreshV15 explicitly establishes Browser focus as fixture setup before the same strict witness; setup is not feature evidence.
- Pin: new14named/2000×100 lifetime/ordering model precedes compiled V23 synchronous captured-owner native action. It is a source prototype; feedback, external helper lifetime, legacy records, maximized policy and real UI/native checks remain open. Installed files are unchanged.
- RecoveryV15 source proof288Python/170named/21models×2000 supports definite stale/incompatible-family cancellation and durable non-settlement acknowledgment before source disposal. Independent review/freeze/native restart tests remain pending. User/current-receipt cancel and interruption/reduced-motion ingress remain separate work.

All five crash-handoff safeguards remain applied. No native handle remains live; no main GUI/configuration/deployment writes. Full Windows parity remains incomplete; active goal made progress.


### 2026-10-02T02:07:06.370037+00:00 — recovery source closure accepted

Root independently verified the corrected RecoveryV15-frozen-v2 packet:11963bytes/modes and158links, all eight reviewed candidate hashes exact. Source288Python/170named/21models×2000 and independent15checks/55kernel tests remain accepted. The earlier stdout self-capture freeze failure remains retained. This accepts the source closure only; real restart/fault/cancellation and current-receipt live ingress remain open. No main changes or native run live.


## Resumed private QA — 2026-10-02T02:23:31.979913+00:00

BrowserV15 passed exact fixture focus setup, two trusted nonzero pointer calibration
moves, and real browser draft editing with an interior caret. The exposed Files
click focused Files and changed its view. The original feature check still failed:
the QA listener read the reactive button identity after its real handler changed
Show list to Show grid. No feature check was relaxed. A fresh immutable press
receipt correction is being modeled. All12 independent safety/source/cleanup
checks, all18 main preservation checks, 41,458 byte/mode inputs and13,770 links
passed. Full15 acceptance remains false. Root's static-count bookkeeping mistake
and launch-before-review-record-write are retained explicitly in the root review.

HeldV9 passed the first3 unchanged QtWayland drag cases and failed fourth preview
entry. Its102 durable diagnostic records include95 native arrival samples. The
selected global point170,637.5 was outside the actual clipped viewport and popup
hover mask. This proves a QA navigation gap; real wheel navigation and preview
restore remain unaccepted. All18 main preservation checks,22,902 frozen inputs,
332 links and4 independently replayed native retirements pass. Whole52/service
workload/evaluation acceptance remain false. A fresh genuine wheel route preserves
the existing click/family/frontend oracles and fixed helper expectations.

RecoveryV15's accepted legacy renderer route has a CPU counterexample: an exited
unreaped Z lifetime passes inherited retirement but is rejected by a new
process_start-only cancellation refresh. Its retired journal and captures remain
retained with zero native writes. Modern authenticated Keeper group closure
correctly refused the separate probe. A fresh formal terminal-state source repair
is required before native recovery collection. PinV2 partial-action/reentrant and
feedback modeling continues; full Windows parity and deployment remain open.

Evidence: [browser actual](../window-integration-qa/browser-files-flow-v15/attempt-1/report.json),
[browser independent](../window-integration-qa/browser-files-flow-v15/attempt-1/root-completion.json),
[preview geometry](../window-integration-qa/toolkit-held-matrix-v9/attempt-1/root-preview-geometry-replay-v1.json),
[held retirements](../window-integration-qa/toolkit-held-matrix-v9/attempt-1/root-held-retirement-audit-v1.json).


## Resumed private QA — 2026-10-02T02:57:14.003628+00:00

- BrowserV16 passes the first eight original checks, including real exposed Files
  click/focus, unchanged draft/caret, and returning to Browser. Typing continuation
  still times out. B17 will retain failed DOM observations and actual Seat keyboard
  focus; the cause is unproved. All12 safety and all18 main checks pass.
- HeldV10 passes all13 QtWayland cases, including move and resize followed by
  minimized preview restore. Each preview uses six genuine wheel receipts and
  preserves the original exact native/frontend/family/cache/focus checks. Root
  independently replays12 receipts and both actual visible source allocations.
  The whole52 campaign remains failed: one Snap query delegate exits120 among
  142 started/terminal helpers, with no refusals; other39 cases remain unrun.
  All18 main, normal unload and process closure pass. Independent retirement
  replay12/12 passes. Original terminal/evaluation failures remain retained;
  fresh wheel-aware audit and actual helper-exit attribution are pending.
- RecoveryV17 fixes the reproduced legacy zombie refusal through exact pidfd
  terminal evidence. Root11 CPU/kernel tests and independent66 tests pass, with
  modern group-closure and uncertainty/ack/disposal guards retained. Full frozen
  12742 byte/mode inputs and158 links independently pass. Native fault/restart
  collection and current-receipt cancellation remain pending.
- A separate unchanged-controller CPU counterexample reproduces loss of an
  accepted request during reduced-motion validation. A16-scenario/2000×100 Quint
  repair model passes before runtime changes. Fresh scene/token, exact visual
  retirement ACK, current context and latest receipt handling require the full
  source repair and real setting-command/native QA.

Evidence: [actual previews](../window-integration-qa/toolkit-held-matrix-v10/attempt-1/root-wheel-causal-replay-v1.json),
[browser safety](../window-integration-qa/browser-files-flow-v16/attempt-1/root-completion.json),
[recovery closure](../window-integration-qa/service-recovery-v17-root-frozen-preflight.json),
[reduction counterexample](../window-integration-qa/reduced-validation-counterexample-v1/result.json).

No main desktop changes or deployment. Goal remains active; full parity remains incomplete.


## Private acceptance checkpoint — 2026-10-02T03:44:06.826593+00:00

- Recovery collector V2 fixes the missing nested manifest and preserves ancestral
  permissions. Root 17 CPU/kernel tests, 13,507 byte/mode inputs and 158 links pass.
  The actual original baseline reaches 11 passing checks, then stalls waiting for
  minimize visual cleanup. Service shutdown requires TERM/KILL; baseline and fault
  acceptance remain false. All 15 main checks and 12 independent preservation
  gates pass, including native unload and actual private process/runtime closure.
- Actual source replay independently reproduces an endpoint/watchdog lock deadlock.
  The endpoint holds the family-query lock while waiting for the manager lock; the
  deadline watchdog holds the manager lock while waiting for the family-query lock.
  Native thread stacks were not archived, so the live cause remains unproved.
  Fresh V19 repair is modeled before source changes; deadlines/oracles stay intact.
- Browser V17 retains the exact first-character omission: `continued0` arrives at
  the original caret, while the leading hyphen does not. Seat focus remains on
  Browser and wtype exits normally. B18 adds read-only capture/bubble key and
  beforeinput metadata with the original 15 checks/runtime unchanged. Root 10
  focused tests, 21 actual CPU JavaScript cases, 11 Quint scenarios and 2,000
  randomized traces pass. Its actual private run is in progress.
- The fresh wheel-aware HeldV10 auditor passes 40/42 checks. Remaining failures are
  incomplete four-toolkit coverage and the actual query delegate exit 120. V11
  adds bounded attribution without redirecting streams or increasing budgets.
- Current-receipt cancellation, reduced-validation request preservation, pin
  lifetime/feedback/legacy/max policy, real mixed outputs, physical cadence and
  accessibility, final integrated regression and deployment remain open.

Evidence: [recovery failure](../window-integration-qa/family-recovery-cancel-v2/attempt-baseline-1/report.json),
[terminal preservation](../window-integration-qa/family-recovery-cancel-v2/attempt-baseline-1/root-terminal-preservation-v1.json),
[independent deadlock replay](../window-integration-qa/recovery-baseline-v2-lock-counterexample-v1/root-independent-replay-v1.json),
[browser Quint replay](../window-integration-qa/browser-v18-root-quint-replay-v1.json).

No main desktop changes or deployment. Full Windows parity remains incomplete.

## QA checkpoint 2026-10-02T04:21:36.255811+00:00

- BrowserB19 actual startup succeeds; original first8 checks pass, continuation remains failed. New real DOM evidence shows leading hyphen key `-` with physical code `Escape` and keyCode27, no canceled handler and no beforeinput; next10 characters insert at original caret. Driver mapping investigation required; full15 not accepted. Original independent auditor all preservation/source/normal cleanup checks pass, all18main intact.
- HeldV11 actual diagnostic run ends before cases on `/proc` ESRCH selected-lifetime observation; strict auditor retains failure. Actual selected delegate is normal0/stdout[] here, so exit120 cause remains unproved. FreshV12 narrow checker fix formal15named/2000 and10actualCPU/kernel tests pass; fullproof pending.
- RecoveryV19 source correction: original family body/TLS/atomicguards/deadlines retained;304CPU/191named/23modelsx2000 source proof plus root35focused pass. Frozen13074/158. Fresh collectorV3 pairs this exactservice, ToolkitV21 anddefaultV10; original38baseline andfault ASTs exact, root15observer/restart pass, frozen14192/158. Actual new baseline/recovery acceptance pending.
- PinV2 freshV24 compiles;53lifecycle Quint cases/2000traces +48transaction/37lifetime-codec CPU tests pass. Actual UI/helper/native/legacy/max acceptance remains open.
- FullWindows parity, physical cadence/device/a11y, integratedC1/reduction/cancel and deployment remain unaccepted.

### Native outcome correction 2026-10-02T04:30:07.007372+00:00

Recovery collector V3 is terminal failed: normal service/renderer/actor retirement now completes, but deadline fallback occurs after only two actual family captures. The original three-capture requirement and four-actor/default-selection checks remain failed. The unchanged-oracle independent auditor passes all 11 preservation gates, including all 15 main checks. No fault campaign was launched. Fresh V20 preparation performance work retains the original deadline and capture requirements.

Held V12 is now frozen (24,338 byte/mode records,332links, exact V11 ancestry) and passes root20actualCPU/kernel/fixture tests, root15named/2000Quint traces, fullsourceproof andpreflight. The actual52-case private campaign is running under root ownership; result pending.

### Held startup result 2026-10-02T04:32:56.871421+00:00

Held V12 is terminal failed before loading plugins or launching feature clients: the original private-output gate ran before any parent configure was observed. The strict transport gate also fails. All 18 main checks and actual process/runtime closure pass; root independent startup replay passes seven preservation/source gates. This grants no feature acceptance. Fresh V13 will use the reviewed B19 actual empty-only output readiness within the same original startup deadline, preserving original52 checks and X11 variants. No blind retry or original budget increase is authorized.

## 2026-10-02: private startup and pin boundary review

- Held V13: frozen 24,771 input/mode rows and 332 links. Root 28 focused tests pass. Actual run fails before any of the original 52 cases: 137 exact-peer, full-EOF empty output replies exhaust the unchanged 15-second startup budget. Normal process/runtime cleanup passes. Strict audit remains failed (6/16); main preservation is 15/18, with cursor, layers and clipboard/primary changes unclassified. No main configuration or restoration writes.
- Bootstrap investigation: initial Aquamarine surface commit lacks an explicit flush. An actual owned libwayland socket test observes 92 queued bytes reaching its peer only after flush. This supports a source hypothesis; native failed-run causality is not established. A fresh formal-first private bootstrap repair is in progress.
- Browser B20: corrected physical keyboard source is frozen. Final 353 Python checks and 298 named cases across 19 models pass. Root independently verifies all 44,182 input/mode rows, 13,774 links, B19 ancestry and 472 ready sources; 33 focused CPU/kernel tests and 35 named/three-model randomized checks pass. Original 15 feature checks still require a native run.
- Pin helper: retained actual malformed-token and typed-projection counterexamples, then refined models before guard changes. Final 32 CPU/kernel checks, 1,000 malformed-projection mutations and 26 named cases/two models × 2,000 traces pass. Real direct-launch/socket tests use an inert mapped fixture and synthetic receipts, proving no native pin effect. Final source handed off for complete UI/native integration.
- Full Windows parity, recovery/cancellation/reduced-motion integration, hardware/accessibility and final deployment remain unaccepted.

### Browser B20 native acceptance closed

The actual private run passes all original 15 Browser/Files features, 10 host
gates, 18 main-session preservation checks and 43 command acknowledgements.
The unchanged independent terminal auditor passes all 12 source, process, bus,
transport and normal-cleanup checks. A separate 22-check replay verifies both
continuations insert exactly at retained carets 29→40→51: trusted DOM Minus
(keyCode 189), genuine beforeinput/input, native wire 12/symbol 45, and 11
balanced native key pairs per continuation with the exact observed Browser
Seat/core owner. No retries, refocus or extra characters were used.

This closes the bounded private Browser/Files scenario. Its source packet
remains 44,182 byte/mode rows and 13,774 exact links. Production deployment,
physical hardware, other toolkit cases and full Windows parity remain pending.
Evidence: browser-files-flow-v20/attempt-1/root-completion.json and
root-physical-keyboard-causal-replay-v1.json.


## 2026-10-02: startup repair verified; reload and shutdown defects retained

- Root independently verified/froze AQ bootstrap and both hosts (1,562 input/mode rows, 214 links); 12 named Quint cases, 2,000 traces, exact source inverses and original guards pass. Held V14 freezes 25,720 inputs/modes and 342 links with all V13 ancestry; original runner, deadlines and 52-case matrix preserved.
- Actual V14 starts with one exact output query, confirms the selected private AQ mapping and configure/transport, and passes all nine move/Escape gates. The second case fails while arming reload. The strict independent auditor remains failed (14/20); one of 52 cases passes in this attempt. Main preservation is 16/18; cursor and clipboard/primary changes remain unclassified. No main configuration or restoration writes.
- Actual retained syscall evidence proves one taskbar query offers `[]` after normal shell quit, receives EPIPE with no delivered bytes and exits 120. All processes/runtime are gone and native unload is normal; helper normal-completion acceptance remains false. Fresh bounded reload-arm and teardown repair is required.
- Recovery V3 observer/runner select V17/V19 respectively; runtime V19 pairing is unverified. V20 now frozen: 14,618 inputs/modes, 158 links; full 328 Python/244 named/27 models proof, root 24 CPU/kernel and 34 named/two-model checks pass. Actual original 38-case baseline, faults, cancellation and reduction integration remain pending. Its 512-query history bound requires durable reclamation before steady-state production parity.
- Persistent pin stacking/menu/max policy, hardware/accessibility, final merged regression and deployment remain open. Full Windows parity remains incomplete.
