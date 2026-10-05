# Consensus candidate v1

This is the exact first ballot, not an accepted implementation. All30 candidates are draft refinements except conditional export015. Existing242/417 and current acceptance levels remain unchanged.

Ballot SHA256: ae1d72ea0b44236c40cc9e94db47c3b9e180660b207378097c45c833caf7807e

## Common constraints

- Preserve native authority, exact identities, original clocks/deadlines, ordered retirement, and no automatic replay of Unknown.
- Typed state does not grant linear ownership. Cancel/Release commands do not prove physical retirement.
- Model/CPU/replay/native/hardware/AT evidence remains distinct. No comparator superiority or performance claim from source review.
- Missing budgets require measurement and a frozen policy before qualification; no invented numbers.
- All implementation tasks remain unchecked. No installed/session changes or archive/promote.
- Conditional diagnostic export is deferrable. Research integration must preserve existing delivery priority and scope.

## ELM-ADOPT-001 — Versioned complete replay inputs with effect isolation

WHEN a reducer replay is evaluated, the verifier SHALL reproduce state and ordered effect descriptions from versioned initial state and complete recorded inputs, reject invalid input explicitly, report selected and processed coverage, and execute no native mutations.

Classification: refinement. Priority: P0. Capability: elm-verification.

Mapping: ELM-TEA-002, ELM-TEA-003, ELM-QA-006, ELM-QA-007, ELM-REV-007, ELM-REV-012; W03, W04, W05.

Constraints: Sanitized replay needs an explicit semantics-preserving mapping. Refused dummy events are counted explicitly; a nonempty selected corpus cannot pass by processing zero inputs.

Tradeoffs: Fixture/schema upkeep and log bytes; preserve existing reducer rather than build another. Recorded timer inputs do not qualify native deadlines.

### Scenario: Deterministic history
- GIVEN A valid checkpoint and ordered native observations including deadlines
- WHEN The compiled reducer processes them twice
- THEN All state/effect rows match and no effect endpoint is invoked

### Scenario: Malformed racing clock input
- GIVEN A pending request and envelope missing clock-domain metadata
- WHEN A late receipt is supplied through the envelope
- THEN Validation fails explicitly; valid inputs retain original deadline and recorded order

Source proposals: IMM-01, OPUS01-IMM-2, OPUS01-IMM-4.

## ELM-ADOPT-002 — Proof-safe bounded history retention and compaction

WHEN retained records reach their configured bound, the authority SHALL reclaim only records whose safety obligations are preserved by retained proofs and replay floors, or explicitly refuse new admission while preserving unresolved and cleanup obligations.

Classification: refinement. Priority: P0. Capability: elm-native-bridge.

Mapping: ELM-ARC-014, ELM-ARC-015, ELM-ARC-016, ELM-REV-011; W01, W02, W03, W10.

Constraints: No age-based deletion of Unknown, cleanup, issuance/revocation authority or replay floors. A presentation close/restart is not proof-safe reclamation.

Tradeoffs: Retention ownership table and compaction proof work; persistent sharing cannot make retained roots free; diagnostics may rotate independently.

### Scenario: Expired replay after compaction
- GIVEN A settled reclaimable record and retained replay floor
- WHEN Compaction completes and its old identity returns
- THEN No mutation occurs and defined expired disposition is recorded

### Scenario: Unknown and late cleanup
- GIVEN Capacity pressure, Unknown request and outstanding consumer fence
- WHEN Diagnostics rotate and matching late receipt arrives
- THEN Unresolved/cleanup obligations remain reconciled and charged storage is not freed prematurely

Source proposals: IMM-02, OPUS01-IMM-3.

## ELM-ADOPT-003 — Coherent recovery checkpoints and interrupted migration qualification

WHEN recovery installs a checkpoint, the authority SHALL validate its coherent schema, lifetime, watermark and retained obligations before effect admission, reconcile uncertain outcomes without replay, and preserve each original deadline.

Classification: refinement. Priority: P0. Capability: elm-delivery.

Mapping: ELM-ARC-010, ELM-ARC-014, ELM-REV-008, ELM-REV-012, ELM-QA-007; W01, W02, W09, W10.

Constraints: Use existing durable ledger. Interrupted migration/write/fsync and storage-full are qualifying faults; coherent checkpoint is not proof that a window action completed.

Tradeoffs: Crash-barrier fixture maintenance and synchronous storage cost; a manifest over existing stores may suffice; database replacement is deferred.

### Scenario: Completed checkpoint
- GIVEN Synchronized checkpoint with Unknown and retired-request floors
- WHEN Frontend restarts
- THEN Coherent observation/reconciliation state is restored without old mutation dispatch

### Scenario: Interrupted migration
- GIVEN Visible rename and incomplete synchronization/migration barrier
- WHEN Recovery sees newer scene plus late old-binding receipt
- THEN Validated recovery completes or remains fail-closed without mixed owners, lost Unknown, or reset deadline

Source proposals: IMM-03.

## ELM-ADOPT-004 — Measured revision-bound derived caching

WHERE derived-state caching is enabled, the frontend SHALL return the same projection as uncached derivation for every accepted revision and invalidate cached results before using changed or retired dependencies.

Classification: refinement. Priority: P1. Capability: elm-performance.

Mapping: ELM-TEA-001, ELM-QA-021, ELM-QA-022, ELM-QA-023, ELM-REV-020, ELM-REV-021; W08, W09.

Constraints: Caching/indexing is an implementation option after profiling. Cache keys include native dependency/output/publication revisions; stale cached data grants no authority.

Tradeoffs: Cache/index memory and invalidation bookkeeping may outweigh scan savings; adoption requires frozen-budget evidence, no invented thresholds.

### Scenario: Unchanged dependency
- GIVEN Pointer events with unchanged scene/query/policy revisions
- WHEN Taskbar groups are derived
- THEN Output equals uncached oracle and measured recomputation improves under frozen workload comparison

### Scenario: Identity reuse race
- GIVEN Cached retired family incarnation
- WHEN Same label appears under new lifetime/incarnation during query change
- THEN New identities govern derivation and action eligibility; stale family/preview authority does not survive

Source proposals: IMM-04.

## ELM-ADOPT-005 — Explicit concrete state and command refinement mapping

WHEN coupled replay is reported as conformance evidence, the verifier SHALL compare concrete state and ordered commands through a documented abstraction map and disclose stuttering, equivalence and environmental assumptions without substituting that evidence for native acceptance.

Classification: refinement. Priority: P1. Capability: elm-verification.

Mapping: ELM-QA-004, ELM-QA-005, ELM-QA-006, ELM-TEA-002, ELM-REV-009; W03, W04, W10.

Constraints: Explicit partial-observation/stuttering abstraction; compare actual commands and resources as well as model state. Bounded sampling/trace validation is not an exhaustive proof.

Tradeoffs: Mapping/comparator reviewer upkeep; full mechanized proof deferred; sampled exploration remains bounded evidence.

### Scenario: Backend stuttering
- GIVEN Broker housekeeping without observable frontend change
- WHEN Coupled replay applies declared abstraction map
- THEN Frontend stutters while native accounting and eligible queued receipts remain checked

### Scenario: Equal final state with incorrect effect order
- GIVEN Executions with equal final visible model
- WHEN One reorders Cancel/Ack or retires before consumer completion
- THEN Transition/command/resource comparison fails at first relevant mismatch

Source proposals: IMM-05, OPUS01-IMM-1.

## ELM-ADOPT-006 — Complete typed internal boundaries

WHEN a validated external event enters an internal reducer, the controller SHALL carry domain-specific typed identities and outcomes through its resulting effect descriptions until wire encoding.

Classification: refinement. Priority: P0. Capability: elm-native-bridge.

Mapping: ELM-TEA-001, ELM-TEA-002, ELM-TEA-003, ELM-REV-007; W04, W01, W02.

Constraints: Narrow module-owned typed events, effects and identity domains; native authenticates context. Do not mandate a new language, framework, giant event type or incompatible wire change.

Tradeoffs: Codec and call-site migration; phantom types do not authenticate senders; preserve wire bytes.

### Scenario: Exact receipt
- GIVEN a validated receipt for one request/incarnation
- WHEN the typed outcome is reduced
- THEN only the exact transaction settles and wire encoding remains unchanged

### Scenario: Foreign input
- GIVEN a malformed or foreign-binding payload
- WHEN boundary validation runs
- THEN no admitted event or mutation is produced and correlated refusal is retained

Source proposals: TE-01, OPUS02-TE-01, OPUS02-TE-03.

## ELM-ADOPT-007 — Preserve effects as an auditable dependency algebra

WHEN a native effect depends on another effect's completion, the controller SHALL admit the dependent request only after the matching native committed receipt satisfies the recorded prerequisite.

Classification: refinement. Priority: P0. Capability: elm-native-bridge.

Mapping: ELM-TEA-002, ELM-TEA-003; W04, W01, W02, W09.

Constraints: Register every implied native request; preserve child effects. Cmd.batch does not sequence dependent results. Independent actions need not wait for unrelated dependencies.

Tradeoffs: Explicit dependency metadata and replay oracle costs; retain independence; no new framework necessary.

### Scenario: Pending prerequisite
- GIVEN restore-before-activate dependency for an exact incarnation
- WHEN restore remains Pending then its exact committed receipt arrives
- THEN activation waits then registered activation can proceed

### Scenario: Wrong prerequisite
- GIVEN a refused restore or foreign committed receipt
- WHEN it arrives before activation
- THEN it cannot satisfy the prerequisite and independent controls remain usable

Source proposals: TE-02.

## ELM-ADOPT-008 — Publish one conversation contract with local obligations

WHEN an authenticated protocol event is admitted, each participant SHALL follow the declared actor-specific legal transitions and outcome reachability for that protocol version, preserving exact correlation and stable proof identities.

Classification: refinement. Priority: P1. Capability: elm-native-bridge.

Mapping: ELM-TEA-001, ELM-ARC-012, ELM-ARC-014, ELM-REV-008, ELM-REV-009, ELM-REV-011; W03, W04, W06.

Constraints: Share semantic outcome classes but keep operation/protocol-specific transitions. Window Committed is not preview Released/fenced/presented. Model transitions/typestate are implementation choices, not a claim of static session typing.

Tradeoffs: New verification artifact refining existing behavior; manual table maintenance; no static-session-typing claim.

### Scenario: Unadopted refusal
- GIVEN an admitted reservation without storage
- WHEN the trusted producer refuses
- THEN stable refusal proof preserves already-ordered cancellation proof

### Scenario: Illegal retirement
- GIVEN an adopted buffer or stale actor
- WHEN producer-refused or final-ack is supplied
- THEN it cannot bypass drainage or retire current actor resource

Source proposals: TE-03, OPUS02-TE-02, OPUS02-TE-05.

## ELM-ADOPT-009 — Treat cancellation as a request followed by proved closure

WHILE a resource or reservation is owned, the native broker SHALL account for its admission, transfer and cleanup until matching native completion permits retirement; cancellation or release intent alone SHALL NOT erase ownership, charge or cleanup obligations.

Classification: refinement. Priority: P0. Capability: elm-native-bridge.

Mapping: ELM-ARC-012, ELM-ARC-016, ELM-REV-010; W03, W06, W10.

Constraints: Conservation includes newly admitted resources and ownership transfers. Cancel/Release emission is not physical retirement; producer refusal is valid only after trusted failure before image adoption. Native producer/consumer completion and reader drain remain distinct.

Tradeoffs: Retained records and native callback coordination; release on cancel-send unsafe; generation-scoped drain avoids global waits.

### Scenario: Cancel refusal race
- GIVEN capture cancelled before adoption
- WHEN refusal completes asynchronously
- THEN ordered cancellation/refusal proofs leave no reservation after final ack

### Scenario: Held reader
- GIVEN adopted buffer with held GIO reader
- WHEN cancel and shutdown occur
- THEN fetch revoked immediately and terminal release waits for producer completion and reader drainage

Source proposals: TE-04, OPUS02-TE-06.

## ELM-ADOPT-010 — Separate causal order, epoch identity and deadline time

WHEN queueing, frontend replacement or reconciliation occurs, the authority SHALL preserve the operation's original native clock domain, time origin and deadline while validating ordered control delivery independently of observation revisions.

Classification: refinement. Priority: P1. Capability: elm-native-bridge.

Mapping: ELM-REV-007, ELM-REV-008, ELM-REV-009, ELM-REV-012, ELM-ARC-013, ELM-ARC-014; W01, W02, W05.

Constraints: Original absolute native deadlines/start events survive queue/recovery. Causality/order counters, presentation clock, input clock and epoch are distinct. Late receipts may reconcile knowledge without becoming timely success.

Tradeoffs: Metadata and clock/queue instrumentation; frontend timers feedback only; vector clocks unnecessary.

### Scenario: Restart receipt
- GIVEN pending work and frontend restart
- WHEN exact late receipt arrives
- THEN original request reconciles without deadline renewal or mutation replay

### Scenario: Gap clock
- GIVEN control sequence gap or replaced clock domain
- WHEN later delta/timeout arrives
- THEN new admission withheld until coherent reconciliation and invalid timing cannot authorize work

Source proposals: TE-05, SOL-FLUID-03.

## ELM-ADOPT-011 — preserve uncertainty in a structured reporting contract

WHEN an operation report is presented, the shell SHALL derive its message and available recovery actions from a validated correlated outcome and SHALL distinguish definitive refusal from Unknown without implying completion or authorizing replay.

Classification: refinement. Priority: 1. Capability: elm-shell-experience.

Mapping: ELM-ARC-007, ELM-ARC-008, ELM-ARC-014; W04, W11.

Constraints: Stable bounded outcome/reason catalog and actionable localized text. Unknown remains perceivable. Unknown reason within a validated Refused class may use generic refusal text; unknown schema/outcome cannot fabricate Refused.

Tradeoffs: status-only messages are cheaper but obscure safe recovery; raw native messages reduce mapping work but leak details and blur semantics. Cost: category registry, compatibility review and differential fixtures. Validation: enumerate every existing outcome/recovery reason; every class has reviewed text and enabled-action oracle; corrupt or future reasons fail closed without fabricating a terminal outcome.

### Scenario: ERR-01-01
- GIVEN an admitted restore with lost receipt
- WHEN transport disconnects
- THEN the report states that completion is unconfirmed, preserves Unknown and offers no automatic repeat.

### Scenario: ERR-01-02
- GIVEN an exact unsent certificate and a simultaneous late receipt for a different request
- WHEN reports are reduced
- THEN refusal is attached only to the certified request and the foreign receipt cannot alter its message or actions.

Source proposals: ERR-01, OPUS03-ER-01.

## ELM-ADOPT-012 — one announcement owner and outcome-aware deduplication

WHEN an eligible correlated outcome transition requires attention, the controller SHALL publish one accessible status through the designated announcement owner, retain focus and suppress repeats of that outcome while preserving later distinct outcome transitions.

Classification: duplicate. Priority: 1. Capability: elm-accessibility.

Mapping: ELM-UI-009, ELM-UI-010; W08.

Constraints: One announcement owner; deduplicate repeated outcomes, not distinct later state changes. Native speech/braille/focus transcript required; ARIA alone is insufficient. The semantic owner is the controller; delivery must reach a qualified AT-active document or declared native/fallback route, including when application focus remains outside shell.

Tradeoffs: per-view live regions are simple locally but duplicate output on multiple surfaces; one modal per failure interferes with focus and ordinary work. Cost: semantic routing, native AT integration and multi-output transcript qualification. Validation: count announcements against distinct eligible transitions, observe focus and speech/braille, include duplicate receipts and surface recreation. Preserve existing policy thresholds; freeze any missing quantitative oracle through S02/P0 rather than inventing one.

### Scenario: ERR-02-01
- GIVEN bar and popup projections on two outputs with stable focus
- WHEN the same refusal receipt is delivered repeatedly and a popup recreates
- THEN one eligible announcement occurs and recovery detail remains reachable.

### Scenario: ERR-02-02
- GIVEN Unknown was announced and the original deadline has elapsed
- WHEN a valid late correlated receipt settles knowledge
- THEN a distinct policy-eligible update is exposed without restarting the effect or changing its deadline; foreign-epoch receipts produce no such update.

Source proposals: ERR-02, OPUS03-ER-02, UXA-04.

## ELM-ADOPT-013 — bounded allowlisted diagnostics independent of authority

WHILE ordinary diagnostics are enabled, the diagnostics subsystem SHALL admit only allowlisted bounded records and SHALL report record loss without collecting excluded content or altering native authority, operation outcomes or deadlines.

Classification: refinement. Priority: 2. Capability: elm-delivery.

Mapping: ELM-DEL-017; W04, W11.

Constraints: Allowlist excludes secrets, draft content, pixels, raw port bodies, titles/arguments/paths by default. Bounded lost-record counters. Diagnostics saturation cannot block native control/cleanup or compact durable authority.

Tradeoffs: unrestricted verbose logs simplify one incident at privacy/resource cost; aggregate-only metrics lose sequence context. Cost: event schema, producer audits and saturation tests. A ring buffer and separate counters are possible implementations, not mandated architecture. Validation: sensitive canaries across nested values and error strings; resource saturation, failure to write and malformed events preserve controller decisions. Measure log-rate, whole-process CPU/wakeups/memory, export cost and retention against `elm-performance/spec.md` ELM-PER obligations; the performance owner freezes numeric limits from P0 workloads before acceptance.

### Scenario: ERR-03-01
- GIVEN a decoder failure containing a secret canary and window title
- WHEN a diagnostic record is produced
- THEN only allowed category/context fields appear and neither canary nor title is retained.

### Scenario: ERR-03-02
- GIVEN diagnostic capacity is exhausted during a pending effect
- WHEN further records arrive and a terminal receipt races
- THEN loss is observable, memory stays within the frozen budget and receipt settlement is identical to diagnostics-disabled execution.

Source proposals: ERR-03, OPUS03-ER-03, OPUS01-IMM-5.

## ELM-ADOPT-014 — recovery evidence distinguishes restored availability from past success

WHEN a failed frontend or authority recovers, the shell SHALL report verified current availability separately from unresolved historical outcomes and SHALL admit new effects only after native reconciliation under the original deadline and identity contracts.

Classification: refinement. Priority: 1. Capability: elm-delivery.

Mapping: ELM-ARC-014, ELM-ARC-026, ELM-QA-002, ELM-QA-003; W05, W10, W11.

Constraints: Recovery action must preserve durable Unknown, replay floors, held resources and original clocks. Generic restart guidance is not acceptance. Compositor replacement is not an incidental recovery action.

Tradeoffs: automatic retries may appear faster but are prohibited here; generic “recovered” banners omit the critical uncertainty. Cost: recovery phase/report integration and protected fault campaign evidence. Validation: original restore38/recovery34 with unchanged identity/oracle/deadline, held effects, missing/corrupt journal, unavailable storage, frontend/authority epoch replacement and stale proof. Component replay supplements rather than replaces native acceptance.

### Scenario: ERR-04-01
- GIVEN an admitted effect and crash before durable settlement
- WHEN a fresh epoch receives a coherent snapshot
- THEN availability may recover while the previous effect remains unconfirmed and is never replayed.

### Scenario: ERR-04-02
- GIVEN a storage-full recovery failure and matching-looking geometry from a replacement incarnation
- WHEN reconciliation is attempted
- THEN geometry alone cannot clear the historical reservation, no new dependent effect is admitted and the original recovery deadline remains enforced.

Source proposals: ERR-04, OPUS03-ER-05.

## ELM-ADOPT-015 — explicit diagnostics export boundary

WHERE local diagnostic export is selected, WHEN the user requests an export, the shell SHALL produce an inspectable local bundle of validated export-allowed evidence and declared omissions, preserving recovery authority and sending nothing externally.

Classification: conditional-new. Priority: deferred. Capability: elm-delivery.

Mapping: ELM-DEL-017; W11.

Constraints: Conditional/deferrable feature; not a new mandatory release blocker. No default cores, screenshots, environment, unrestricted journals or uploads. Explicit local user request; cancellation/disk-full has truthful partial-artifact outcome.

Tradeoffs: copying a journal manually is cheaper but produces unreviewable privacy and scope surprises; automated cloud uploads introduce unsupported product scope. Cost: bundle builder, accessible review and export fault testing. Validation: unpack and schema-check artifacts; canary and content scans; stale-epoch snapshot race, cancellation, disk-full and symlink/path defenses; measured export overhead must meet frozen performance budgets.

### Scenario: ERR-05-01
- GIVEN diagnostics and an available core dump containing private memory
- WHEN the user requests the ordinary bundle
- THEN the bundle includes allowed metadata and states that core/pixels/content are omitted.

### Scenario: ERR-05-02
- GIVEN export is assembling records while frontend epoch changes
- WHEN cancellation or disk-full occurs
- THEN no success is reported, partial-artifact disposition is explicit, and neither old nor fresh recovery reservation is changed.

Source proposals: ERR-05, OPUS03-ER-04.

## ELM-ADOPT-016 — Preserve control identity across publication and focus changes

WHEN a presentation publication changes while a shell scope retains focus, the host SHALL preserve the focused surviving control identity, reject activation captured for retired or changed-scope identities, and apply the frozen eligible fallback only when that control is no longer eligible.

Classification: refinement. Priority: P0. Capability: elm-shell-experience.

Mapping: ELM-UI-011, ELM-UX-023, ELM-UX-024; W07.

Constraints: Publication/lease/incarnation captured at press remains authoritative at release. Preserve a surviving focus identity across unrelated changes; explicit eligible fallback only on removal. Keyed DOM is an implementation choice. Admitted keyboard activation must equal the native AT-exposed focused identity, not merely a selected row.

Tradeoffs: Identity propagation and native focus evidence; preserve identity rather than index or automatic selected-row refocus.

### Scenario: SOL04-01-scenario-1
- GIVEN Close is focused while another row is selected
- WHEN an unrelated catalog publication arrives
- THEN Close keeps focus and the next activation invokes only Close

### Scenario: SOL04-01-scenario-2
- GIVEN an activation press belongs to a window incarnation and lease
- WHEN that incarnation retires and the row position is reused before release
- THEN release dispatches no replacement action and eligible fallback remains reachable

Source proposals: SOL04-01, UXA-01.

## ELM-ADOPT-017 — Treat native semantics and announcements as a coherent projection

WHEN a shell projection changes, the shell SHALL expose coherent native names, roles, states, relationships and actions for the current control identities, keeping preview imagery inert and keyboard focus distinct from selection.

Classification: refinement. Priority: P0. Capability: elm-accessibility.

Mapping: ELM-UI-009, ELM-UI-010, ELM-UX-025, ELM-UX-026; W08, W07, W06.

Constraints: Control semantics plus actual native bridge required. Announcement ownership is separately ELM-ADOPT-012; multiple read-only status regions do not establish a single AT announcement. Keep the visible stable control label as the accessible name; expose transient state and action descriptions separately, within the frozen per-control naming policy.

Tradeoffs: One outcome owner requires lifecycle correlation and native speech/braille inspection; API availability differs by ABI.

### Scenario: SOL04-02-scenario-1
- GIVEN bar and popup show the same pending operation
- WHEN the matching refusal arrives twice
- THEN one relevant refusal is announced, both projections show the same outcome, and focus remains on the user's control

### Scenario: SOL04-02-scenario-2
- GIVEN a preview image has retired while its restore control survives
- WHEN AT explores the control
- THEN source state and supported action are available without an actionable image object or stale-incarnation activation

Source proposals: SOL04-02, UXA-03.

## ELM-ADOPT-018 — Qualify composition as native field ownership

WHILE an input method owns a shell field composition, the host SHALL preserve native preedit and candidate interaction, suppress shell handling of consumed keys, and accept commits only for the current field identity and composition generation.

Classification: duplicate. Priority: P0. Capability: elm-accessibility.

Mapping: ELM-UI-012, ELM-UX-028; W07.

Constraints: Native field/composition epoch binds commits; consumed keys cannot trigger shell shortcuts. Native candidate/preedit and actual input target evidence required.

Tradeoffs: Native IME campaigns are costly; toolkit API examples cannot be transplanted across host lanes.

### Scenario: SOL04-03-scenario-1
- GIVEN a launcher field has active preedit
- WHEN the input method consumes Enter to commit text
- THEN the query receives the commit once and no launch occurs from that consumed key

### Scenario: SOL04-03-scenario-2
- GIVEN composition belongs to a retired field generation
- WHEN its delayed commit arrives after a new field takes focus
- THEN neither field nor shell action receives the stale commit

Source proposals: SOL04-03, UXA-06.

## ELM-ADOPT-019 — Preserve hierarchy and reachability under constrained geometry

WHEN output geometry, text scale or label length changes, the shell SHALL preserve readable control names, visible focus, non-color state cues and keyboard-reachable actions using the frozen contrast, geometry and reflow policy.

Classification: refinement. Priority: P1. Capability: elm-accessibility.

Mapping: ELM-UI-013, ELM-UX-027, ELM-UI-019; W08.

Constraints: Freeze measurable contrast/target/text/reflow budgets and test constrained outputs, long labels, scaling and non-color cues. Do not assume CSS tokens or screenshots establish native reachability.

Tradeoffs: Layout choices need measured geometry and AT bounds; freeze thresholds before qualification.

### Scenario: SOL04-04-scenario-1
- GIVEN enlarged text and long localized labels on a small output
- WHEN the picker opens
- THEN every action remains reachable and focused labels are legible according to the frozen oracle

### Scenario: SOL04-04-scenario-2
- GIVEN a popup owns focus on a removed output
- WHEN surviving-output recovery runs
- THEN its declared fallback or rehosted scope is reachable and removed-generation input cannot activate controls

Source proposals: SOL04-04.

## ELM-ADOPT-020 — Make action discovery agree with acknowledged outcomes

WHEN a shell action is unavailable or its outcome is unresolved, the shell SHALL expose the correlated reason and safe next step, retain eligible focus and independent controls, and avoid queuing or automatically replaying a rejected or Unknown action.

Classification: refinement. Priority: P1. Capability: elm-shell-experience.

Mapping: ELM-UI-005, ELM-UI-007, ELM-UI-015, ELM-UI-020; W07, W08, W01, W02.

Constraints: Unrelated refresh must not collapse a valid picker or disable unrelated actions. Repeated clicks during pending have truthful outcome under the interruption policy; no announcement storm.

Tradeoffs: Shared vocabulary must follow native outcomes; no optimistic success or Unknown replay.

### Scenario: SOL04-05-scenario-1
- GIVEN a minimized generic application family is selected
- WHEN activation is refused natively
- THEN it is not shown as restored, the reason and next action are reachable, and its preserved identity remains selected

### Scenario: SOL04-05-scenario-2
- GIVEN an operation has Unknown disposition and guidance was dismissed
- WHEN the user opens help or recovery with the keyboard
- THEN guidance is available without resetting the desktop and reconciliation creates no automatic repeated mutation

Source proposals: SOL04-05, FI-03.

## ELM-ADOPT-021 — Stage-qualified feedback and physical presentation evidence

WHEN an interaction stage is observed, the native authority and read-only projection SHALL label feedback, effect commitment, renderer submission, presentation and retirement separately, accepting physical completion only from identity-matched native evidence.

Classification: refinement. Priority: P0. Capability: elm-performance.

Mapping: ELM-ARC-020, ELM-REN-005, ELM-REN-022; W06, W08, P4-ELM-ARC-020, P4-ELM-REN-005, P6-ELM-REN-022.

Constraints: Input, commit, rendering, presentation and retirement are separate stages. Record clock mappings, feedback flags and missing/discarded events. Frame callback/image-load/screenshot request is not hardware presentation.

Tradeoffs: ['Extra trace stages and correlation storage', 'Native feedback can approximate light output; independent hardware evidence is still needed']

### Scenario: Queued is not presented
- GIVEN a matching image was decoded and a renderer queued a frame
- WHEN only image load or frameSwapped arrives
- THEN presentation remains unproven and no physical-completion verdict is recorded

### Scenario: Stale output presentation
- GIVEN a transaction targets one output generation
- WHEN a presentation receipt arrives after hotplug changed that generation
- THEN the receipt is retained diagnostically but cannot complete the replacement transaction

Source proposals: SOL-FLUID-01, FI-01.

## ELM-ADOPT-022 — Demand scheduling with bounded control liveness

WHILE preview or observation demand exceeds admitted capacity, the bridge SHALL coalesce only replaceable observations within their identity domain, refuse unadmitted effects explicitly and preserve ordered cancellation, receipts and retirement capacity.

Classification: refinement. Priority: P0. Capability: elm-native-bridge.

Mapping: ELM-ARC-015, ELM-ARC-016, ELM-REN-012; W01, W03, W06, W10.

Constraints: Coalesce only explicitly replaceable observations in the exact identity/dependency domain. Preserve reliable ordered effect/cleanup/control events, original deadlines and reserved progress capacity; no universal lossy stream.

Tradeoffs: ['Fairness and reserving control bytes reduce peak preview throughput', 'Coalescing requires explicit event taxonomy and atomic dependency preservation']

### Scenario: Observation storm with cancellation
- GIVEN preview queues are saturated within frozen byte and item bounds
- WHEN new observations and a cancellation arrive
- THEN only semantically replaceable observations coalesce; cancellation and all retirement receipts remain deliverable in order

### Scenario: Close during producer reservation
- GIVEN a producer owns a reservation and the picker closes
- WHEN a late producer result arrives
- THEN demand remains cancelled and the existing owner receives cleanup; no new capture is admitted until capacity is legitimately released

Source proposals: SOL-FLUID-02.

## ELM-ADOPT-023 — Reversal and live reduced motion share native semantics

WHEN motion is interrupted or the reduced-motion preference changes, the native renderer SHALL derive the successor from the last-presented geometry and preserve the same identity, cancellation, commitment and retirement rules under the approved motion profile.

Classification: refinement. Priority: P1. Capability: elm-capture-motion.

Mapping: ELM-REN-010, ELM-REN-011, ELM-UI-014, ELM-UX-022; W12, P4-ELM-REN-010, P4-ELM-REN-011, P4-ELM-UI-014.

Constraints: Native last-presented geometry/velocity and approved reversal profile. Reduced motion is a live native preference, with no velocity continuation/decorative motion under the selected reduced profile. Presentation timestamps, original38/34/52 cases remain required.

Tradeoffs: ['Geometry and velocity continuity need native samples, not model time', 'The exact preference-switch policy must be frozen before qualification']

### Scenario: Reverse after an unpresented sample
- GIVEN a restore has a queued sample newer than its last native presentation
- WHEN a minimize intent reverses it
- THEN the successor starts from last-presented geometry under the native continuity rule and retires only the superseded generation

### Scenario: Preference changes during capture
- GIVEN a restore is awaiting a retained frame
- WHEN reduced motion becomes enabled before its matching frame arrives
- THEN the approved reduced-motion route uses identical commit and cancellation obligations without replaying the effect or resetting its deadline

Source proposals: SOL-FLUID-04, FI-06.

## ELM-ADOPT-024 — Separate feedback latency and useful completion measurement

WHEN host selection or release evaluation is prepared, the performance owner SHALL freeze same-machine workload budgets that separately measure input feedback, useful native presentation, whole-process resource closure and observer overhead, declaring missing stages.

Classification: refinement. Priority: P0. Capability: elm-performance.

Mapping: ELM-QA-021, ELM-QA-023, ELM-REV-020, ELM-REV-021, ELM-REN-021, ELM-REN-022; W08, W12, P6-ELM-QA-023, P6-ELM-REN-021, P6-ELM-REN-022.

Constraints: No numeric limit invented from papers. Record latency distributions, missed frames, hardware/refresh/output metadata, CPU/memory/wakeups/idle-power and resource soak; QA observers disabled for product measurements.

Tradeoffs: ['Hardware and minimally observed measurements cost time', 'Academic thresholds do not substitute for the frozen local budget contract']

### Scenario: Missing presentation instrument
- GIVEN a benchmark records CPU submission and feedback but lacks a presentation span
- WHEN the host comparison is evaluated
- THEN unsupported spans are explicit and physical latency acceptance remains blocked rather than treating submission as presentation

### Scenario: Observer hides tail failure
- GIVEN a debug observer improves or perturbs scheduling
- WHEN the final benchmark packet is prepared
- THEN paired observed and minimally observed runs expose overhead and all frozen workload thresholds are evaluated without discarding misses

Source proposals: SOL-FLUID-05.

## ELM-ADOPT-025 — Control delivery continuity distinct from proof identity

WHEN authenticated control receipts are delivered, the bridge SHALL preserve their required per-channel causal order, detect gaps or regressions under the declared transport contract, reconcile uncertainty and keep repeated proofs idempotent without acknowledging unseen cleanup.

Classification: refinement. Priority: P0. Capability: elm-native-bridge.

Mapping: ELM-ARC-010, ELM-REV-008, ELM-REV-009, ELM-REV-010; W03, W10.

Constraints: Use a separate delivery ordinal or independently qualified continuity mechanism. Proof IDs are not stream ordinals. Duplicate Acks may be retried idempotently when required; do not mandate withholding known-safe Ack retries. No global total order.

Tradeoffs: Additional protocol/evidence complexity must meet the frozen workload/resource budget. Reuse current modules and incrementally qualify changed paths.

### Scenario: reordered-cleanup
- GIVEN Released and racing Cancelled proofs for a still-held job
- WHEN the later control event overtakes its prerequisite
- THEN no unseen proof is acknowledged and no ownership is forgotten; the declared gap/reconciliation policy preserves cleanup

### Scenario: cross-entry-proof-and-retry
- GIVEN global proof IDs interleave across entries and a valid final Ack is lost
- WHEN a stable proof repeats on the authenticated delivery stream
- THEN it does not create a false gap or duplicate physical cleanup; the declared idempotent acknowledgement/reconciliation policy can finish retirement

Source proposals: OPUS02-TE-04.

## ELM-ADOPT-026 — Capture must not starve native presentation

IF a preview capture or export route exceeds its frozen presentation-impact budget on an active output, THEN the release verifier SHALL reject that route and retain a qualified alternative or explicit unavailable-preview state.

Classification: refinement. Priority: P0. Capability: elm-performance.

Mapping: ELM-REV-022, ELM-REN-012, ELM-QA-023, ELM-UI-017; W06, W08.

Constraints: Synchronous compositor readback/encode is a concern, not a measured regression. Async readback/cropping/off-thread encoding need their own safety, fence, eligibility and ABI qualification. Unavailable fallback does not close mandatory source-stop/family gates.

Tradeoffs: Additional protocol/evidence complexity must meet the frozen workload/resource budget. Reuse current modules and incrementally qualify changed paths.

### Scenario: cross-output-capture-impact
- GIVEN restore motion on one output and capture demand on another
- WHEN the capture route runs on the measured hardware tuple
- THEN presentation gaps and latency are measured on every active output against the same workload without capture

### Scenario: over-budget-route
- GIVEN measured route impact exceeds the frozen budget
- WHEN release admission evaluates it
- THEN the route is rejected and the documented unavailable fallback is truthful; no stale or unqualified route substitutes for required capture acceptance

Source proposals: FI-02.

## ELM-ADOPT-027 — Persistent demand converges to latest authorized source content

WHILE preview demand remains authorized, WHEN a newer content revision arrives during outstanding capture, the provider SHALL retain bounded latest-content demand and service it after eligible capacity returns, without admitting work after demand closes or authority revokes.

Classification: refinement. Priority: P1. Capability: elm-capture-motion.

Mapping: ELM-ARC-015, ELM-REN-012, ELM-UI-017, ELM-TEA-004; W03, W06.

Constraints: No forced allocation while backpressured/exhausted. Follow-up is a genuine new native-scoped request with its own original issued clock, not renewal of expired work. Control/retirement events are lossless.

Tradeoffs: Additional protocol/evidence complexity must meet the frozen workload/resource budget. Reuse current modules and incrementally qualify changed paths.

### Scenario: final-content-while-busy
- GIVEN one admitted capture and multiple newer same-source revisions while visible demand persists
- WHEN the first job terminates and capacity returns
- THEN bounded demand selects the latest valid revision without losing the final update or extending the first job deadline

### Scenario: close-or-lock-before-followup
- GIVEN a pending latest-content update
- WHEN demand closes, lock/revocation occurs or source identity changes before admission
- THEN no unauthorized follow-up capture is admitted; existing jobs and cleanup obligations remain accounted

Source proposals: FI-04.

## ELM-ADOPT-028 — Source liveness and frame freshness are separate facts

WHEN an authorized preview is displayed, the shell SHALL distinguish source liveness, captured content revision and frame age, and SHALL NOT describe historical or stale pixels as current content.

Classification: refinement. Priority: P1. Capability: elm-capture-motion.

Mapping: ELM-REN-004, ELM-REN-014, ELM-UI-016, ELM-UX-006, ELM-UX-007; W03, W06.

Constraints: Refine labels only after reviewing the frozen historical/live/unavailable policy; do not relabel stale pixels as current-live or alter original13 S09 assertions.

Tradeoffs: Additional protocol/evidence complexity must meet the frozen workload/resource budget. Reuse current modules and incrementally qualify changed paths.

### Scenario: live-source-with-old-frame
- GIVEN a live source advances after its authorized frame was captured
- WHEN the old frame remains valid while a replacement is pending
- THEN source liveness and frame age/freshness are distinguished; no false current-content claim or target substitution is made

### Scenario: revocation-or-minimize
- GIVEN a displayed frame and native source-state/lease update
- WHEN the source minimizes or lease revokes
- THEN the existing historical/unavailable policy and native revocation govern display before replacement; no revoked pixels remain eligible

Source proposals: FI-05.

## ELM-ADOPT-029 — Native keyboard entry and exit for the taskbar

WHEN the declared taskbar-focus binding is admitted, the native host SHALL enter a bounded keyboard scope on the current output and retain the prior eligible application identity for the frozen exit/fallback policy, keeping the binding inert while locked.

Classification: refinement. Priority: P0. Capability: elm-shell-experience.

Mapping: ELM-UX-023, ELM-UX-024, ELM-UI-011, ELM-UI-019; W07.

Constraints: This is native keyboard scope qualification, not a mandated permanent EXCLUSIVE mode or a new default shortcut. Declare which history changes are focus-only versus real accepted activation; do not override existing MRU policy.

Tradeoffs: Additional protocol/evidence complexity must meet the frozen workload/resource budget. Reuse current modules and incrementally qualify changed paths.

### Scenario: enter-and-escape
- GIVEN an eligible application has focus and the taskbar is idle
- WHEN the declared conflict-resolved taskbar focus binding is invoked and then Escape ends the scope
- THEN native keyboard and AT focus enter the bar and return under the frozen policy, with no unintended activation-history change

### Scenario: retired-source-output-or-lock
- GIVEN a bar keyboard scope whose prior application or output retires
- WHEN the scope exits or the session locks
- THEN no replacement incarnation or removed output receives stale focus; the frozen eligible fallback/lock policy applies and idle bar does not intercept application input

Source proposals: UXA-02.

## ELM-ADOPT-030 — Versioned disabled-action navigation policy

WHEN a supported shell action becomes disabled, the shell SHALL retain its declared position, expose its reason and disabled state, and follow the frozen per-surface navigation policy without dispatching it through pointer, keyboard or accessibility activation.

Classification: refinement. Priority: P1. Capability: elm-shell-experience.

Mapping: ELM-UI-011, ELM-UX-024, ELM-UX-025; W07, W08.

Constraints: GTK and Windows/APG differ. Freeze the chosen per-surface policy; no universal requirement to focus every disabled control. Preserve existing right-click24 amendment and unsupported-action semantics.

Tradeoffs: Additional protocol/evidence complexity must meet the frozen workload/resource budget. Reuse current modules and incrementally qualify changed paths.

### Scenario: supported-disabled-action
- GIVEN a state change disables a supported menu action
- WHEN the user navigates with the declared per-surface policy
- THEN the action position remains stable, native AT exposes unavailable state and reason, and attempted activation dispatches no effect

### Scenario: all-disabled-and-focus-retirement
- GIVEN all menu actions are disabled or the focused action becomes disabled
- WHEN navigation, Enter/Space or Escape occurs
- THEN the frozen policy keeps focus and dismissal reachable without invoking a disabled action or trapping focus

Source proposals: UXA-05.

