# FRP and Elm review workplan

The user requested five independent Claude Opus 5.5 reviewers at high effort.
All five finished successfully on a frozen 127-file snapshot. Session logs
confirm `claude-opus-5-5`; every launch requested `--effort high`. Tools were
Read, Glob, Grep, WebFetch and WebSearch. The reviewers did not change source,
compile, test or activate the desktop.

[The review packet](../reviews/frp-elm-opus55-20261005T005653Z/request.json)
contains exact prompts, reports, source hashes and execution provenance.
[The finding ledger](FRP-ELM-WORKPLAN.json) assigns all 44 findings to work.
Advice identifies source concerns; it cannot establish native acceptance.

## Preserve the architecture

Keep modern Elm Architecture: immutable models, typed messages, pure reducers
and derived views. Keep one controller and read-only bar/popup projections.
Native owns window effects, input eligibility, pixels, clocks and retirement.
Keep receipt-driven sequencing, bounded queues, exact generations and lossless
uint64 strings. Never automatically replay Unknown operations.

The official [command source](https://raw.githubusercontent.com/elm/core/1.0.5/src/Platform/Cmd.elm)
does not guarantee batch-result ordering. The [Process kernel](https://raw.githubusercontent.com/elm/core/1.0.5/src/Elm/Kernel/Process.js)
uses a JavaScript timer for sleep. The [ports guide](https://guide.elm-lang.org/interop/ports.html)
supports a small message boundary with explicit state ownership. These support
the design; native atomicity, deadlines and displayed pixels remain explicit.

## Immediate implementation order

1. **W07: input identity and focus.** Candidate690 uses unkeyed interactive
   lists, and `context.js` refocuses the selected menu row on any mutation and
   omits Space. Use keyed controls, a press-time identity/publication/lease guard,
   explicit focus identity/revision, and Enter/Space routing. Validate publication
   between press/release, Tab to Close then unrelated updates, retired focused
   rows, IME composition, actual native recipients and AT events. The existing
   integration lane owns a fresh GUI derivative and its qualification.
2. **W01/W02: transport and durable liveness.** Reproduce a commit crossing a
   topology change: native early refusal logs only, Elm clears batch correlation,
   and Pending can be stranded. Retain historical correlation and narrowly
   authenticated unsent certificates; reconcile uncertain dispositions. A valid
   full catalog can also trigger sticky whole-packet byte refusal. Separate byte
   budgets while preserving atomic projection/effect dependencies. Integrate
   existing670/675 receipt work under the updated693 gates to address cumulative
   64-history/128-scope exhaustion. Preserve Unknown reservations and anti-replay
   floors. Qualify more than 200 effects and repeated restarts in one lifetime.
3. **W03: preview ownership, observations and effects.** Freeze native ownership
   transfer, session/actor binding, source revision rules, observation ordering,
   reset/exhaustion and cleanup receipts. Extend Quint with asynchronous channels,
   independent issued/revoked history, cancellation, retirement, deadlines, lease
   expiry and global capacity. Then implement typed Elm lifecycles/fidelity/handle
   domains. Replay must compare commands as well as states. Native resources and
   all 13 original S09 scenarios remain required.

W07 and W01 share paths and integrate serially in the existing GUI lane. The
preview lane can advance W03 independently. Native campaigns remain serialized
through the unchanged protected launcher with the exact owning ABI.

## Remaining tasks and acceptance

| Task | Implementation/dependency | Evidence required |
|---|---|---|
| W04 | Typed internal outgoing messages, reducer inputs, decoded outcomes and admission results; preserve child effects; opaque identity domains. Coordinate with W01/W02. | Byte-identical differential replay; foreign-binding controls; every expected request linked to an emitted/registered request; native requalification of changed assets. |
| W05 | Native monotonic deadlines from original input through queues/recovery; late exact outcomes reconcile Unknown. Depends on W01/W02 protocol decisions. | Original durations/start events unchanged; queue delay, frontend stall, restart, late receipt and case-34 negative evidence. Measure hidden-page timers before claiming throttling. |
| W06 | Native opaque preview/icon routes, bounded ownership, no handle reuse, revoke refusal, fences, cache discipline and keyed image identity. Depends on W03. | Source-stop/family pixels, after-revoke fetch refusal and output samples; image load distinct from physical presentation; all original S09 identities. |
| W08 | One announcement owner/outcome identity; inert preview imagery with state on its control; text scaling/content height and measured performance. Depends on W07/W06. | Multi-output AT transcript; repeat-outcome controls; S02 budgets; CPU/idle/latency distributions without QA observers; native presentation timing. Profile before lazy rendering. |
| W09 | Revision-driven invalidation and coherent scene/geometry admission. | Inspect owning plugin event/revision coverage first; bracketed reads and stale-menu native rejection. |
| W10 | Ordered shared-host broker drain and resource closure within original operation budgets. | Inspect existing recovery evidence; held-effect restart receipts/journal, normal exits and empty process census. |
| W11 | Explicit fail-closed malformed attachment/presentation policy. | Strict fuzz cases, diagnostics/reconciliation; retained display metadata grants no input or revoked-pixel authority. |
| W12 | Native motion intents, last-presented geometry/velocity, reversal and reduced motion. Depends on W05/W06 and S10 prerequisites. | Quint reversal/dependencies plus original native restore, fault, deadline and presentation campaigns; no browser animation-clock substitute. |

## Reconcile advice with newer evidence

Reviewers saw preview366 and its failed held-cache verification. Fresh367 now
compiles optimized policy and Html view in an isolated working cache. Actual
compiled replay matches 45 Quint365 traces and 1,347 states; six compiled guard
mutants are detected and 20 adversarial controls pass. This partially addresses
04-6. The newer W03 checkpoint below adds command conformance; observation channels and native lifetime remain open.
Failed364/366 remain preserved; no source/native acceptance transfers to367.

Actual Quint365 mutant stdout has the named `QNT508: Assertion failed`
diagnostics, rather than parser/typecheck errors. Harden the next runner to
validate these diagnostics instead of exit codes alone (04-4);372 now does so. Random invariant
sampling remains bounded simulation.

Some advice requires narrower authority rules before implementation:

- Stale revocation must follow the authenticated authority/tombstone contract;
  an obsolete/foreign scope must not operate on a new lifetime. Native lock and
  URI revocation must work while Elm stalls.
- Release unadopted offers through their validated native ownership record.
  An `owned` JSON flag alone grants no authority. Establish offer/ack transfer
  semantics before classifying ignored offers as confirmed native leaks.
- Duplicate/expired operations may have committed. Never fabricate Refused:
  use definitive evidence, a genuine unsent certificate or durable Unknown.
- Keyed images and load events help webview identity/labels; actual output pixel
  disappearance and native presentation still need independent evidence.
- Separating presentation/request budgets must preserve admission dependencies.

## W03 implementation checkpoint

Fresh372 preserves all original21 policy cases and adds25 lifecycle cases. All46
named cases and1,000 bounded50-step invariant samples pass; seven separately
typechecked mutants fail their exact named QNT508 assertions. Fresh373 compiles
the typed reducer and keyed Html view. Actual compiled replay matches state and
ordered commands across70 retained traces/1,509 steps. All46 named cases decode
without rejection. The random traces include557 events referencing inactive
Quint dummy slots; strict decoding rejects them with unchanged state/no effects.
Seven real compiled regressions are caught;22 wire/domain controls pass.

The frontend records pending cancellation and retiring leases until exact native
cleanup receipts, carries session/frontend identity through request reset, checks
native clock/deadlines/lease expiry, and reconciles incoherent source revisions.
This qualifies the frontend policy boundary. Native issuance history, asynchronous
control delivery, global resource budgets, source-stop/family pixel capture,
authenticated enrollment, URI serving and physical presentation remain open.
Continue W03 with the independent broker ledger/channel model before W06 native
integration. No baseline requirement or original S09 scenario is completed here.

## W03 broker model checkpoint

Fresh383 composes two entries with the exact372 pure reducer and independently
owned native admission, issuance, revocation and fence histories.26 named races,
1,000 bounded50-step samples and10 separately typechecked named QNT508 mutants
pass. Fresh384 replays the actual compiled373 frontend against50 real broker
traces/two entries:100 cases,461 state/ordered-command steps and
1529 underlying broker states checked, with zero typed rejections. Backend-only
steps preserve frontend state; observations come directly from eligible queued
input, never expected next state.

Cancel-before-Acquire tombstones prevent late allocation. All revoked resources
stay charged through independent producer and consumer completion. Fetch checks
trusted entry/binding identity and native policy even while Elm stalls. Receipts
must be reliable FIFO per frontend so Fence cannot overtake Offer or successive
attachments. These are explicit transport obligations, not proven properties of
a current native channel. Permanent loss and missing fences do not imply liveness.

The exploration capacities are abstract units; production limits remain original.
All historical sets are verification ghosts, not a bounded production design.
Next implement cleanup acknowledgements/admission floors and bounded authoritative
records, then compile/refine the real native broker and integrate owned pixels,
URI callbacks and native fences. The original13 S09 native scenarios, physical
presentation, resource/performance gates and full release remain open.

## W03 bounded runtime implementation checkpoint

Model388 adds bounded authoritative records, acknowledgement and per-binding
request floors while retaining separate verification ghosts.30 named cases,
1,000 bounded50-step samples and10 specific typechecked QNT508 mutants pass.
The earlier386200-cycle Quint exploration exhausted Node heap; it remains failed.
The separately named corrected exploration uses12 cycles. Actual C++394 retains
200 cancellation jobs and200 complete owned-buffer cycles without record growth.

Fresh394 implements typed native C++ reservation, ownership, revocation, native
callbacks, reader references, acknowledgement and request floors.43 controls,
seven separately compiled precise assertion mutants and address/undefined-behavior
sanitizers pass.390's consumer-fence mutant initially escaped;391 added the real
missing consumer-only case, and all seven mutants are now detected. No parser,
compiler failure or crash substitutes for a guard detection.

This is a compiled RAM ownership prototype. It has not been loaded into the
native GUI, and separate model/runtime passes do not establish refinement. Next
run the coupled native/Elm state-and-command oracle, reconcile full-record
Backpressure/refusal and cancellation-first/receipt identities, add typed frontend
cleanup Ack, then integrate the native channel, URI ownership, real producer and
GPU fences. Bounded reliable FIFO, native supervision/drain and all13 original
S09 scenarios remain mandatory. Family output, physical revocation while stalled,
production resource budgets and full coherent release remain open.

## W03 coupled protocol checkpoint

Fresh403 preserves the original30 broker scenario identities and adds six
protocol witnesses: refusal followed by cancellation, recorded old-actor cleanup,
record-capacity backpressure, source revision at buffer adoption, release before
cancellation, and stale terminal acknowledgement.36 named cases and1,00050-step
samples pass;14 specific typechecked mutants fail their named QNT508 assertions.
401 preserved an escaped candidate mutation: ignoring a duplicate Acquire while
its request floor already denies reallocation was observationally equivalent in
that witness.403 instead tests the unsafe creation of a refusal for an active job.

Native397 fixes a real refused-job cleanup bug and separates stable native proof
identity from FIFO delivery order.399 adds typed Receipt identities, rejects bare
or nested terminal wire events, and emits Ack only after all frontend references
are gone.402 couples real compiled C++397 and compiled Elm399 across60 actual ITF
traces:1,775 states and433 frontend events. It compares physical resources,
charge/items, authenticated commands, exact records/certificates/floors, native
counters, fetch authorization and queued receipts/Acks. Actual C++ output feeds
Elm; expected next state does not construct native receipts. Opaque token nonces
remain intact in both programs and are quotiented only for comparisons.

The original70 pure frontend traces retain1,509 state/ordered-command comparisons
under the new receipt envelope. Their terminal proof IDs are explicit fixtures;
real native proof provenance is established separately by402.34 compiled strict
wire/domain controls, three compiled Elm regressions and nine compiled native
regressions pass. The first old-actor mutant escaped406 because native observation
had already cancelled that unallocated record.407 adds the allocated-buffer case;
409 catches the exact cancellation failure.52 native controls,200 cancellation
jobs and200 complete owned RAM capture cycles pass, including ASan/UBSan.
Failed mutation compilation404 and escaped controls401/406 remain preserved.

This qualifies a bounded RAM protocol prototype, with trusted coherent observer
fixtures. It does not qualify production transport authentication/FIFO bounds,
malformed native scope recovery, native supervisory drain, GPU/URI/pixel behavior
or a GUI release. Next implement the native bridge and authorized URI resource
lifetime with real producer/consumer fences on the owning ABI tuple, then run all
13 original S09 scenarios. Full original deadlines, production budgets,
hardware/accessibility/IME, integrated journeys and reversible release remain.

## W06 native image-stream checkpoint

418 adds11 explicitly executed URI-reader scenarios over byte-identical403
broker/lifecycle policies,1,00050-step samples and three precise typed mutants.
412 implements real GInputStream ownership and native authorization. It binds
reads to a registered view, actor and permitted entry, rechecks native authority
and a separate fresh native clock on every read, and assigns a new view epoch
when the native address is reused. A live reader retains the broker's buffer;
closing that reader does not grant a producer/consumer fence or cleanup Ack.
31 actual native stream controls, three compiled regressions and ASan/UBSan pass.
The fixture contains owned RAM bytes with a PNG signature; decoded pixels and
valid image encoding are deliberately not claimed from those byte-level checks.

Fresh421 links the actual349-derived GTK/WebKit C host with the C++ broker/stream
callback and passes all11 inherited host self-tests. The callback derives its
view identity from WebKit's request object, accepts only exact opaque native
routes, returns image/png, and declares no-store/nosniff response headers. Header
ownership follows the installed WebKit GIR's transfer-full contract. The native
producer/supervisor must install the endpoint on the GTK owner thread, enroll
views and clear that pointer before teardown; no web message can install it.
The endpoint remains null until that producer is connected. No WebKit preview
request has been executed, no windows captured, and no pixel presentation accepted.

Failed411 namespace/keyword parsing,413 record/effect typing,414 selector assertion,
and416 obsolete Map spelling on the invariant runner are preserved. Every named
418 scenario really ran; nominal counts do not substitute for explicit selection.
Next connect the owning native capture/PNG producer and authenticated scope/view
bridge, implement resource drain, and replay actual stream/model interleavings.
Then run the original13 S09 native scenarios on one reviewed source/ABI tuple.
None of this closes the GPU, output/hardware, AT/IME, original timing or release gates.

## W06 native producer checkpoint

434 compiles the real owning205 window snapshot API, synchronous framebuffer SHM
readback and an independently owned complete PNG encoder.436 passes19 bounded
private native checks: capture completed in24.55ms under the original two-second
absolute deadline; expired, nonexistent-incarnation and foreign-binding requests
refuse. Actual minimize and normal source process exit leave the owned PNG size
and checksum unchanged. Explicit retirement removes it, then empty clients,
plugin unload and private host teardown complete. These metadata checks do not
independently verify the compositor's encoded pixels, family coverage or color.

430 independently decodes the actual encoder's PNG through libpng and the real
GIO reader, with26 checks including destruction of the original source raster.
428 catches four separately compiled orientation, alpha and allocation-bound
regressions, and passes the earlier25 controls under ASan/UBSan. The production
encoder is byte-identical; the new26th assertion was run separately. The ledger
reserves nominal framebuffer, CPU raster and complete PNG storage before GPU
allocation. Its128MiB/two-item cap is a prototype bound, not a release budget;
GPU driver/compositor intermediates and real resource/presentation costs remain.

The first432 native attempt crashed in the internal buffer's inherited client
release callback. The saved stack and failed fixture normal exit are preserved.
Required core suppression worked, and the private runtime was cleaned up.434
provides an internal readback release override without emitting a fake Wayland
release or conferring a consumer fence;438/439 review and436 rerun support this
bounded correction. Earlier423–425 compilation failures are also retained.

Fresh441 reruns all19 controls and adds recorded exitCode0 assertions for the
source client,205 compositor, private Weston and private D-Bus:20 checks pass,
with capture at22.72ms.436 remains a separate earlier metadata/cleanup result;
its runner did not record normal parent/compositor exits.

Next deliver sealed native image buffers through an authenticated FD bridge into
412/421, enroll actual host views and scope, and verify native decoded/presented
pixels. Family/modal composition, crop/output transform/color, native lock/device
and replacement revocation, production broker/receipts and supervised drain,
stream/model interleavings, and all13 original S09 scenarios remain open. No
baseline requirement, full GUI acceptance or release gate is closed here.

## W06 descriptor and actual WebKit pixel checkpoint

446 adds a compositor-owned Unix descriptor socket with kernel peer PID/UID,
process-start and grant checks. It exports a sealed immutable PNG memfd once per
capture, reserves backing storage before allocation, and retains its reservation
until authenticated transfer release. Native lock/output/config invalidation
revokes availability while preserving outstanding resource ownership. This is a
bounded prototype; device loss, trusted launcher policy and full production
observer enrollment remain unqualified.

450 passes ten protected private native checks on the exact205/446/AQ155 tuple.
The actual448 host independently authenticates the compositor, imports the sealed
buffer through the412 broker/GIO and unchanged421 WebKit callback, then libpng
and an actual browser canvas both verify a red source pixel in the800x600 image.
The registered view loads it twice, including after committed minimization;
an unregistered actual WebView is denied. These are decoded canvas pixels,
not an independently measured compositor presentation fence or display sample.
Outstanding export blocks producer retirement; local reader drain and physical
mapping destruction precede transfer release, raw producer retirement and unload.
All five owned processes exit0 and private runtime cleanup passes.

447 passes29 Linux descriptor checks, but453 preserves a survived seal-query
mutant: its ordinary-file fixture lived on tmpfs and did not exercise a failed
query. Fresh454 adds an actual unlinked btrfs file and asserts the kernel query
fails:30 controls pass.455 passes those30 under ASan/UBSan and detects three
precise compiled seal-query, foreign-actor and pre-map reservation regressions.
The corrected receiver header remains byte-identical to the native448 host.
Failed445 compile,451 stale review label and all qualification failures remain.
458 passes seven explicitly selected Quint ownership scenarios and1,000 sampled
50-step traces, retaining24 traces. Three typed actor/transfer/reader-drain
mutants fail their precise assertions. Failed456 annotations and457 reserved
name parsing are preserved. This abstraction has no actual FD trace refinement
or native consumer fence claim; release authentication and host drain remain
separate obligations.

Next integrate the bounded bridge into the current production Elm host, couple
actual transfer/read/revoke/drain traces with the model, and qualify native lock,
replacement, expiry and source destruction interleavings. Full family/modal
composition, physical crop/transforms/color, supervised crash drain, hardware
budgets and every original S09/S10 acceptance gate remain open. The ten native
checks close no frozen requirement and do not accept a full release.

## W06 current Elm picker integration checkpoint

470 derives from the current814 catalog/input GUI. It connects the399 typed
preview lifecycle to picker controls, matching publication, lease, enabled
control and native incarnation. Images use a keyed inline view with bounded
responsive sizing. The control's existing action identity remains intact. Popup
closure hides imagery and cancels capture demand while retaining cached ownership,
request counters and pending cleanup receipts. Native expiry retires cached
acceptance; late typed receipts can acknowledge after ownership is released.
Binding replacement, sticky2051-entry history exhaustion and production recovery
still require native reconciliation rather than discarding retained owners.

A compiled negative control in467 exposed a real retarget bug: standalone lifecycle
Observe could change its subject while the presenter retained the original control
identity.468/470 reject cross-incarnation Observe/Attach and follow the successful
lifecycle's binding.469 passes27 actual optimized state/effect controls.476 passes
28 controls on470 and detects three separately compiled stale-publication,
subject-retarget and owner-forgetting regressions.481 passes seven explicitly
selected Quint admission/ownership guards,1,000 sampled50-step traces and three
precise typed mutants. This finite two-entry abstraction has no actual Elm trace
refinement and does not replace the existing full lifecycle/broker models.

The current C host links the native URI callback and provides native owner-thread
endpoint/command installation and access to its actual popup view. Preview commands
are limited to the popup manager and a single4096-byte envelope before reaching
an installed native handler, which must independently validate binding, job and
budgets. Default endpoint and handler remain null. No production capture provider,
main-host native view enrollment or supervised drain is installed yet.

486 passes ten protected native checks on exact205/446/AQ155. It loads the actual
470 optimized Popup, adapter and styles in a private WebKit view. Independent
libpng verifies the captured source pixel; native WebKit snapshots verify the
rendered image in live and historical Elm states, with actual120px image bounds.
The actual Elm ports emit one acquire, one release and two typed cleanup
acknowledgements. Native mapping destruction precedes the receipts and final
ledger acknowledgement. A foreign WebView is denied access; all five owned
processes exit0, clients empty before unload and private runtime cleanup passes.

This driver captures before frontend demand and supplies a bounded root-plane
packet; it does not establish production acquire scheduling, client/family fidelity,
GPU presentation fencing or an independently sampled physical display. The whole
current C host was compiled and its inherited CPU checks passed, but486 exercises
its Elm picker assets rather than the complete shared controller/native host.
Original S09/S10, lock/device/replacement/source-destruction, multi-output,
accessibility, hardware, performance/resource and release gates remain open.
Failed460/461 Elm shadowing/tuple builds,462 test linkage,464–466 fixture premises,
467 retarget witness,471 C++ arity,473/479 strict effect-schema refusals and475
Quint Map typing are retained. Unexecuted483/484 preparations are not native proof.

## W06 native source scope and demand checkpoint

492 observes the actual root wl_surface commit and destruction signals for each
native incarnation. A checked positive source counter advances on commits and
becomes permanently unavailable on exhaustion. Authenticated pre-capture scope
contains the native seven-field context, observation identity, original clock and
bounded transfer plan. Scoped capture compares the entire requested context before
allocation, through capture and before publication. Content now names actual root
surface commits, rather than the number of captures. Subsurface/popup/family
versions and production device-loss epoch handling remain open.

491 passes seven explicitly selected Quint scope/deadline/exhaustion scenarios,
1,000 sampled50-step runs,24 retained traces and three precise typed mutations.
493 checks the byte-identical actual SourceEpoch under ASan/UBSan with six boundary
controls and a separately compiled wrap regression. These are bounded component
checks, without native driver/model trace refinement.

504 passes26 protected private native checks on exact205/492/AQ155. Real source
recolor commits advance content without any capture. Each of the seven mutated
context fields refuses capture; no completed probe is published. The pre-allocation
guard is source-reviewed; those absence checks do not measure GPU allocation peaks.
Actual470 compiled Elm emits Acquire before broker reservation and scoped capture.
The sealed image preserves the original context and two-second deadline. libpng
and native WebKit snapshots verify live and minimized historical red source pixels.
Physical imported mapping destruction precedes typed terminal receipts and their
actual Elm acknowledgements. The foreign view is denied; all five owned processes
exit0, clients empty before plugin unload, and private runtime cleanup passes.

The private502 driver carries the source-scope change; the full470 shared C host
still has no installed production provider/supervisor. Root monitor-plane capture
remains previewEligible false. Native frame fences, client/family crop and color,
trusted launcher/view enrollment, native async clock and receipt replay, retained
historical capture, lock/device/expiry/replacement/source destruction and supervised
crashed-host drain remain open. Package the actual current compiled Elm assets and
close the full native C++ dependency inventory before release. Scope/refusal handling
must retire broker reservations and preserve frontend ownership through recovery.

497 preserves a mistaken source-review spelling assertion.496 preserves the test
runner's incorrect error-field lookup despite a correct native refusal.499 preserves
a failed demanded capture; its original native refusal reason was not recorded,
so its cause is unqualified.502 adds raw refusal diagnostics and504 passes without
weakening context, pixel or deadline checks. No claim follows that the earlier
refusal race has been resolved. Original13 S09 cases, S10 baseline38/recovery34,
full S01–S16, hardware, accessibility/IME, resource and release gates remain open.

## W06 full shared host route and native coexistence checkpoint

509 corrects two actual470 integration gaps. Shared-host input now uses the same
popup-only preview-command router as the older host entry point. Previously its
separate dispatcher bypassed that router. Malformed/foreign preview envelopes
are consumed without becoming desktop actions. The provider remains responsible
for exact authenticated jobs, source scope, bounds and retained ownership.

The backend's strict effect handshake now accepts the optional native descriptor
field only when it exactly names the authenticated compositor PID and binding
lifetime. Legacy hello remains valid and other unknown fields/capability changes
still refuse.510 passes25 actual parser controls, including replacement refusal
without modifying the retained binding. These controlled responses alone do not
prove transport authentication.514 exercises the actual shared C dispatcher with
ten controls and detects four separately compiled bypass, manager, protocol and
size regressions with precise normal exit1 assertions rather than crashes.

All25 build commands pass, including optimized Main/Bar/Popup/Replay, both native
C++ objects, inherited carriers and12 host self-tests. The compiler dependency
inventory now covers all three compilation units:1,209 unique files including187
C++ system headers, with compiler tools and linked library hashes. The build
records the exact compiled asset package; its inherited source assets still
contain earlier precompiled JS, so native runs use the held build package.

513 passes15 protected native checks on205/492/AQ155 using the complete509 shared
controller/bar/popup and actual production backend. Native descriptor hello is
accepted and the main model reaches Coherent. Physical pointer input opens a
grouped picker with both native incarnation labels, then closes the current lease.
The backend and all five owned processes exit0; clients empty before plugin unload
and private runtime cleanup passes. This is full-host coexistence and fallback
input evidence. It does not exercise a preview provider, image stream, native
capture scheduling, typed cleanup receipts or supervised recovery in that host.

508 retains its failed Werror build from a misleadingly indented test assertion;
509 fixes that fixture in a fresh derivative. Next install the authenticated native
provider and supervisor in509, bind view scope to actual popup publication/lease,
handle stale/refused demand without leaking reservations or losing retained owners,
and qualify actual Elm ports, native clock, images and physical drain together.
492 still reports previewEligible false for root monitor-plane pixels. Client and
full family/subsurface/modal/popup versions, crop/transform/color and physical
renderer fences must be qualified before production image acceptance. Original
13 S09 cases, S10 baseline38/recovery34 and full release gates remain open.

## Build-loop obligations

Consume this plan with the original roadmap and current checkpoints. Select an
owned ready task, model its interleavings in Quint, implement a fresh derivative,
and run compiled state/effect oracles plus required native campaigns. Record
artifact pointers and findings resolved; never close a gate from counts alone.

All S01–S16, baseline242 requirements/417 scenarios, right-click additions,
applicable C00–C06, hardware/IME/accessibility, budgets, journeys and reversible
release remain in scope. Reviews and preview367 complete no requirement or
sprint. The overall finishing goal remains active.
