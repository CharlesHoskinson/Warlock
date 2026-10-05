# Design adoption — EARS draft registry

Consensus research drafts ready for internal specification integration and implementation. A reviewed baseline amendment remains a separate integration step. These artifacts do not change the canonical 242 requirements/417 scenarios, S01–S16, right-click24, original13 native preview cases, restore38/recovery34/drag-resize52 or original deadlines. Native authority and no automatic replay of Unknown remain mandatory. C00–C06 compositor replacement remains conditional.

No new native, hardware, IME, AT or full-release evidence is supplied by this packet. Frozen component/model/CPU/compiled replay evidence is not production-provider or full GUI ownership/drain/fidelity acceptance. GUI814 and toolkit391 retain separate owning ABI pairs. Implementation and qualification tasks remain unchecked.

30 requirements /67 scenarios:29 draft refinements and015 deferred conditional export. Normative EARS, scenario names and GIVEN/WHEN/THEN text below are copied exactly from the v3 ballot. Source duplicate classifications remain recorded separately; they do not inflate baseline scope.

Source: [immutable v3 ballot](candidates-v3.json), SHA256 `1f4ab93e1ab93afd94ea58511d8a426dbed8ccdc4e08096e6c80bf72e62aa78f`. [Machine registry](requirements.json) preserves all53 proposal dispositions and10 report provenance entries. The [workplan](WORKPLAN.md) routes work through existing W01–W12; no implementation is completed.

## ELM-ADOPT-001 — Versioned complete replay inputs with effect isolation

WHEN a reducer replay is evaluated, the verifier SHALL reproduce state and ordered effect descriptions from versioned initial state and complete recorded inputs, reject invalid input explicitly, report selected and processed coverage, and execute no native mutations.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P0.

Baseline mapping: ELM-TEA-002, ELM-TEA-003, ELM-QA-006, ELM-QA-007, ELM-REV-007, ELM-REV-012.

Existing work mapping: W03, W04, W05.

Source proposals: IMM-01, OPUS01-IMM-2, OPUS01-IMM-4.

Owner: Verification lead. Verifier: Independent acceptance reviewer.

Guardrails: Sanitized replay needs an explicit semantics-preserving mapping. Refused dummy events are counted explicitly; a nonempty selected corpus cannot pass by processing zero inputs.

Tradeoffs: Fixture/schema upkeep and log bytes; preserve existing reducer rather than build another. Recorded timer inputs do not qualify native deadlines.

Primary sources:

- <https://apalache-mc.org/docs/adr/015adr-trace.html>
- <https://arxiv.org/abs/2006.00915>
- <https://arxiv.org/abs/2104.01146>
- <https://arxiv.org/abs/2404.16075>
- <https://doc.akka.io/libraries/akka-core/current/typed/persistence.html>
- <https://guide.elm-lang.org/architecture/>
- <https://immerjs.github.io/immer/patches/>
- <https://kafka.apache.org/43/design/design/>
- <https://lamport.azurewebsites.net/pubs/abadi-existence.pdf>
- <https://people.seas.harvard.edu/~chong/pubs/pldi13-elm.pdf>
- <https://quint.sh/docs/checking-properties>
- <https://raw.githubusercontent.com/avh4/elm-program-test/main/src/ProgramTest.elm>
- <https://raw.githubusercontent.com/elm/browser/master/src/Debugger/History.elm>
- <https://raw.githubusercontent.com/elm/core/1.0.5/src/Array.elm>
- <https://raw.githubusercontent.com/elm/core/1.0.5/src/Dict.elm>
- <https://redux.js.org/style-guide/>
- <https://redux.js.org/usage/structuring-reducers/prerequisite-concepts>
- <https://www.cs.cmu.edu/~rwh/students/okasaki.pdf>

#### Scenario: ELM-ADOPT-001 Deterministic history

- **GIVEN** A valid checkpoint and ordered native observations including deadlines
- **WHEN** The compiled reducer processes them twice
- **THEN** All state/effect rows match and no effect endpoint is invoked

#### Scenario: ELM-ADOPT-001 Malformed racing clock input

- **GIVEN** A pending request and envelope missing clock-domain metadata
- **WHEN** A late receipt is supplied through the envelope
- **THEN** Validation fails explicitly; valid inputs retain original deadline and recorded order

## ELM-ADOPT-002 — Proof-safe bounded history retention and compaction

WHEN retained records reach their configured bound, the authority SHALL reclaim only records whose obligations remain protected by proofs and replay floors, or report distinct capacity refusal while preserving unresolved and cleanup obligations until proof-safe reclamation permits admission.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P0.

Baseline mapping: ELM-ARC-014, ELM-ARC-015, ELM-ARC-016, ELM-REV-011.

Existing work mapping: W01, W02, W03, W10.

Source proposals: IMM-02, OPUS01-IMM-3.

Owner: Native authority lead. Verifier: Independent acceptance reviewer.

Guardrails: No age-based deletion of Unknown, cleanup, issuance/revocation authority or replay floors. A presentation close/restart is not proof-safe reclamation. Capacity refusal is distinct from the original operation outcome and clears when proof-safe reclamation is possible. Scope replay floors retire only through authority-certified scope retirement or equivalent retained proof.

Tradeoffs: Retention ownership table and compaction proof work; persistent sharing cannot make retained roots free; diagnostics may rotate independently.

Primary sources:

- <https://apalache-mc.org/docs/adr/015adr-trace.html>
- <https://arxiv.org/abs/2006.00915>
- <https://arxiv.org/abs/2104.01146>
- <https://arxiv.org/abs/2404.16075>
- <https://immerjs.github.io/immer/patches/>
- <https://immutable-js.com/>
- <https://kafka.apache.org/43/design/design/>
- <https://lamport.azurewebsites.net/pubs/abadi-existence.pdf>
- <https://people.seas.harvard.edu/~chong/pubs/pldi13-elm.pdf>
- <https://quint.sh/docs/checking-properties>
- <https://raw.githubusercontent.com/avh4/elm-program-test/main/src/ProgramTest.elm>
- <https://raw.githubusercontent.com/elm/browser/master/src/Debugger/History.elm>
- <https://raw.githubusercontent.com/elm/core/1.0.5/src/Array.elm>
- <https://raw.githubusercontent.com/elm/core/1.0.5/src/Dict.elm>
- <https://redux.js.org/style-guide/>
- <https://www.cs.cmu.edu/~rwh/students/okasaki.pdf>
- <https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/abadi-existence.pdf>

#### Scenario: ELM-ADOPT-002 Expired replay after compaction

- **GIVEN** A settled reclaimable record and retained replay floor
- **WHEN** Compaction completes and its old identity returns
- **THEN** no mutation occurs; expired or retention disposition is distinct from definitive refusal of the original operation, and retained Unknown remains unchanged

#### Scenario: ELM-ADOPT-002 Unknown and late cleanup

- **GIVEN** Capacity pressure, Unknown request and outstanding consumer fence
- **WHEN** Diagnostics rotate and matching late receipt arrives
- **THEN** Unresolved/cleanup obligations remain reconciled and charged storage is not freed prematurely

## ELM-ADOPT-003 — Coherent recovery checkpoints and interrupted migration qualification

WHEN recovery installs a checkpoint, the authority SHALL validate its coherent schema, lifetime, watermark and retained obligations before effect admission, reconcile uncertain outcomes without replay, and preserve each original deadline.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P0.

Baseline mapping: ELM-ARC-010, ELM-ARC-014, ELM-REV-008, ELM-REV-012, ELM-QA-007.

Existing work mapping: W01, W02, W09, W10.

Source proposals: IMM-03.

Owner: Release integration lead. Verifier: Independent acceptance reviewer.

Guardrails: Use existing durable ledger. Interrupted migration/write/fsync and storage-full are qualifying faults; coherent checkpoint is not proof that a window action completed.

Tradeoffs: Crash-barrier fixture maintenance and synchronous storage cost; a manifest over existing stores may suffice; database replacement is deferred.

Primary sources:

- <https://sqlite.org/atomiccommit.html>
- <https://doc.akka.io/libraries/akka-core/current/typed/persistence.html>

#### Scenario: ELM-ADOPT-003 Completed checkpoint

- **GIVEN** Synchronized checkpoint with Unknown and retired-request floors
- **WHEN** Frontend restarts
- **THEN** Coherent observation/reconciliation state is restored without old mutation dispatch

#### Scenario: ELM-ADOPT-003 Interrupted migration

- **GIVEN** Visible rename and incomplete synchronization/migration barrier
- **WHEN** Recovery sees newer scene plus late old-binding receipt
- **THEN** Validated recovery completes or remains fail-closed without mixed owners, lost Unknown, or reset deadline

## ELM-ADOPT-004 — Measured revision-bound derived caching

WHERE derived-state caching is enabled, the frontend SHALL return the same projection as uncached derivation for every accepted revision and invalidate cached results before using changed or retired dependencies.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P1.

Baseline mapping: ELM-TEA-001, ELM-QA-021, ELM-QA-022, ELM-QA-023, ELM-REV-020, ELM-REV-021.

Existing work mapping: W08, W09.

Source proposals: IMM-04.

Owner: Performance qualification lead. Verifier: Independent acceptance reviewer.

Guardrails: Caching/indexing is an implementation option after profiling. Cache keys include native dependency/output/publication revisions; stale cached data grants no authority. Enable an optimization only after the frozen workload comparison shows an accepted benefit; equivalence alone does not justify adopting it.

Tradeoffs: Cache/index memory and invalidation bookkeeping may outweigh scan savings; adoption requires frozen-budget evidence, no invented thresholds.

Adoption gate: enable caching only after profiling demonstrates measured benefit within the existing frozen budgets; otherwise preserve uncached derivation. This is a conditional implementation option, not a mandatory cache feature.

Primary sources:

- <https://elm-lang.org/assets/papers/concurrent-frp.pdf>
- <https://redux.js.org/usage/deriving-data-selectors>
- <https://raw.githubusercontent.com/elm/core/1.0.5/src/Array.elm>
- <https://immutable-js.com/>

#### Scenario: ELM-ADOPT-004 Unchanged dependency

- **GIVEN** Pointer events with unchanged scene/query/policy revisions
- **WHEN** Taskbar groups are derived
- **THEN** output equals the uncached oracle under the correct dependency revision; recomputation and whole-process resource results are measured separately for the adoption decision

#### Scenario: ELM-ADOPT-004 Identity reuse race

- **GIVEN** Cached retired family incarnation
- **WHEN** Same label appears under new lifetime/incarnation during query change
- **THEN** New identities govern derivation and action eligibility; stale family/preview authority does not survive

## ELM-ADOPT-005 — Explicit concrete state and command refinement mapping

WHEN coupled replay is reported as conformance evidence, the verifier SHALL compare concrete state and ordered commands through a documented abstraction map and disclose stuttering, equivalence and environmental assumptions without substituting that evidence for native acceptance.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P1.

Baseline mapping: ELM-QA-004, ELM-QA-005, ELM-QA-006, ELM-TEA-002, ELM-REV-009.

Existing work mapping: W03, W04, W10.

Source proposals: IMM-05, OPUS01-IMM-1.

Owner: Verification lead. Verifier: Independent acceptance reviewer.

Guardrails: Explicit partial-observation/stuttering abstraction; compare actual commands and resources as well as model state. Bounded sampling/trace validation is not an exhaustive proof. Every concrete state and command field is listed as mapped or explicitly reviewed quotient/stutter/ghost-only; an unlisted field fails coverage. Quotients preserve authentication/binding identity, clock/deadline and outcome meaning; reviewed opaque-nonce renaming is allowed without erasing those relations.

Tradeoffs: Mapping/comparator reviewer upkeep; full mechanized proof deferred; sampled exploration remains bounded evidence.

Primary sources:

- <https://apalache-mc.org/docs/adr/015adr-trace.html>
- <https://arxiv.org/abs/2006.00915>
- <https://arxiv.org/abs/2104.01146>
- <https://arxiv.org/abs/2404.16075>
- <https://immerjs.github.io/immer/patches/>
- <https://kafka.apache.org/43/design/design/>
- <https://lamport.azurewebsites.net/pubs/abadi-existence.pdf>
- <https://people.seas.harvard.edu/~chong/pubs/pldi13-elm.pdf>
- <https://quint.sh/docs/checking-properties>
- <https://raw.githubusercontent.com/avh4/elm-program-test/main/src/ProgramTest.elm>
- <https://raw.githubusercontent.com/elm/browser/master/src/Debugger/History.elm>
- <https://raw.githubusercontent.com/elm/core/1.0.5/src/Array.elm>
- <https://raw.githubusercontent.com/elm/core/1.0.5/src/Dict.elm>
- <https://redux.js.org/style-guide/>
- <https://redux.js.org/usage/structuring-reducers/prerequisite-concepts>
- <https://www.cs.cmu.edu/~rwh/students/okasaki.pdf>
- <https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/abadi-existence.pdf>

#### Scenario: ELM-ADOPT-005 Backend stuttering

- **GIVEN** Broker housekeeping without observable frontend change
- **WHEN** Coupled replay applies declared abstraction map
- **THEN** Frontend stutters while native accounting and eligible queued receipts remain checked

#### Scenario: ELM-ADOPT-005 Equal final state with incorrect effect order

- **GIVEN** Executions with equal final visible model
- **WHEN** One reorders Cancel/Ack or retires before consumer completion
- **THEN** Transition/command/resource comparison fails at first relevant mismatch

#### Scenario: ELM-ADOPT-005 unlisted-field-mutation

- **GIVEN** a runtime mutant drops an Unknown reservation or changes an undeclared field
- **WHEN** abstraction coverage and coupled replay run
- **THEN** verification fails at that field rather than silently observing only the visible model

## ELM-ADOPT-006 — Complete typed internal boundaries

WHEN a validated external event enters an internal reducer, the controller SHALL carry domain-specific typed identities and outcomes through its resulting effect descriptions until wire encoding.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P0.

Baseline mapping: ELM-TEA-001, ELM-TEA-002, ELM-TEA-003, ELM-REV-007.

Existing work mapping: W04, W01, W02.

Source proposals: TE-01, OPUS02-TE-01, OPUS02-TE-03.

Owner: Native authority lead. Verifier: Independent acceptance reviewer.

Guardrails: Narrow module-owned typed events, effects and identity domains; native authenticates context. Do not mandate a new language, framework, giant event type or incompatible wire change. Terminal Refused requires exact authenticated native evidence or a validated definitive unsent certificate. Historical proof admission follows its explicit recovery contract.

Tradeoffs: Codec and call-site migration; phantom types do not authenticate senders; preserve wire bytes.

Primary sources:

- <https://arxiv.org/abs/1910.11108>
- <https://arxiv.org/pdf/1910.11108>
- <https://dl.acm.org/doi/10.1145/3290341>
- <https://docs.rs/tokio/latest/tokio/macro.select.html>
- <https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ECOOP.2020.14>
- <https://grpc.io/docs/guides/cancellation/>
- <https://grpc.io/docs/guides/deadlines/>
- <https://guide.elm-lang.org/interop/ports.html>
- <https://jgbm.github.io/pubs/fowler-popl2019-sessions-extended.pdf>
- <https://lamport.azurewebsites.net/pubs/time-clocks.pdf>
- <https://lmcs.episciences.org/4973>
- <https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/>
- <https://quint.sh/docs/lang>
- <https://raw.githubusercontent.com/elm/core/1.0.5/src/Platform/Cmd.elm>
- <https://raw.githubusercontent.com/elm/core/master/src/Platform/Cmd.elm>
- <https://wayland.freedesktop.org/docs/book/Protocol.html>
- <https://wayland.freedesktop.org/docs/html/apa.html>

#### Scenario: ELM-ADOPT-006 Exact receipt

- **GIVEN** a validated receipt for one request/incarnation
- **WHEN** the typed outcome is reduced
- **THEN** only the exact transaction settles and wire encoding remains unchanged

#### Scenario: ELM-ADOPT-006 Foreign input

- **GIVEN** a malformed, untrusted or unauthorized payload that fails boundary admission
- **WHEN** boundary validation runs
- **THEN** no admitted event, native mutation or transaction settlement is produced; only a bounded allowlisted rejection diagnostic is retained, with no fabricated Refused outcome

#### Scenario: ELM-ADOPT-006 authenticated-historical-reconciliation

- **GIVEN** an exact authenticated historical receipt for a retained obligation and its declared reconciliation route
- **WHEN** it arrives after frontend replacement
- **THEN** only the historical obligation may settle; the receipt grants no authority to the replacement binding and renews no deadline

## ELM-ADOPT-007 — Preserve effects as an auditable dependency algebra

WHEN a native effect depends on a prerequisite, the controller SHALL admit its request only after matching authenticated evidence satisfies that operation's protocol-specific prerequisite, while native authority revalidates the dependency at commit.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P0.

Baseline mapping: ELM-ARC-008, ELM-ARC-012, ELM-TEA-002, ELM-TEA-003.

Existing work mapping: W04, W01, W02, W09.

Source proposals: TE-02.

Owner: Native authority lead. Verifier: Independent acceptance reviewer.

Guardrails: Register every implied native request; preserve child effects. Cmd.batch does not sequence dependent results. Independent actions need not wait for unrelated dependencies. Native revalidates prerequisite incarnation, generation and dependency revision. Preview drain/release/presentation require their own evidence; a window Committed receipt cannot substitute.

Tradeoffs: Explicit dependency metadata and replay oracle costs; retain independence; no new framework necessary.

Primary sources:

- <https://arxiv.org/abs/1910.11108>
- <https://dl.acm.org/doi/10.1145/3290341>
- <https://docs.rs/tokio/latest/tokio/macro.select.html>
- <https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ECOOP.2020.14>
- <https://grpc.io/docs/guides/cancellation/>
- <https://grpc.io/docs/guides/deadlines/>
- <https://guide.elm-lang.org/interop/ports.html>
- <https://jgbm.github.io/pubs/fowler-popl2019-sessions-extended.pdf>
- <https://lamport.azurewebsites.net/pubs/time-clocks.pdf>
- <https://lmcs.episciences.org/4973>
- <https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/>
- <https://quint.sh/docs/lang>
- <https://raw.githubusercontent.com/elm/core/1.0.5/src/Platform/Cmd.elm>
- <https://raw.githubusercontent.com/elm/core/master/src/Platform/Cmd.elm>
- <https://wayland.freedesktop.org/docs/book/Protocol.html>
- <https://wayland.freedesktop.org/docs/html/apa.html>
- <https://www.doc.ic.ac.uk/~yoshida/multiparty/multiparty.pdf>
- <https://www.microsoft.com/en-us/research/wp-content/uploads/2016/12/Time-Clocks-and-the-Ordering-of-Events-in-a-Distributed-System.pdf>

#### Scenario: ELM-ADOPT-007 Pending prerequisite

- **GIVEN** restore-before-activate dependency for an exact incarnation
- **WHEN** restore remains Pending then its exact committed receipt arrives
- **THEN** activation waits then registered activation can proceed

#### Scenario: ELM-ADOPT-007 Wrong prerequisite

- **GIVEN** a refused restore or foreign committed receipt
- **WHEN** it arrives before activation
- **THEN** it cannot satisfy the prerequisite and independent controls remain usable

## ELM-ADOPT-008 — Publish one conversation contract with local obligations

WHEN a protocol event is received, each participant SHALL admit it only under the declared actor-specific transitions, version and outcome reachability with exact correlation; otherwise it SHALL reject it without authority, ownership or settlement effect and retain a bounded rejection diagnostic.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P1.

Baseline mapping: ELM-ARC-004, ELM-ARC-007, ELM-ARC-012, ELM-ARC-014, ELM-REV-008, ELM-REV-009, ELM-REV-011, ELM-TEA-001.

Existing work mapping: W03, W04, W06.

Source proposals: TE-03, OPUS02-TE-02, OPUS02-TE-05.

Owner: Native authority lead. Verifier: Independent acceptance reviewer.

Guardrails: Share semantic outcome classes but keep operation/protocol-specific transitions. Window Committed is not preview Released/fenced/presented. Model transitions/typestate are implementation choices, not a claim of static session typing.

Tradeoffs: New verification artifact refining existing behavior; manual table maintenance; no static-session-typing claim.

Primary sources:

- <https://arxiv.org/abs/1910.11108>
- <https://arxiv.org/pdf/1910.11108>
- <https://dl.acm.org/doi/10.1145/3290341>
- <https://docs.rs/tokio/latest/tokio/macro.select.html>
- <https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ECOOP.2020.14>
- <https://grpc.io/docs/guides/cancellation/>
- <https://grpc.io/docs/guides/deadlines/>
- <https://guide.elm-lang.org/interop/ports.html>
- <https://jgbm.github.io/pubs/fowler-popl2019-sessions-extended.pdf>
- <https://lamport.azurewebsites.net/pubs/time-clocks.pdf>
- <https://lmcs.episciences.org/4973>
- <https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/>
- <https://quint.sh/docs/lang>
- <https://raw.githubusercontent.com/elm/core/1.0.5/src/Platform/Cmd.elm>
- <https://wayland.freedesktop.org/docs/book/Protocol.html>
- <https://wayland.freedesktop.org/docs/html/apa.html>
- <https://www.doc.ic.ac.uk/~yoshida/multiparty/multiparty.pdf>

#### Scenario: ELM-ADOPT-008 Unadopted refusal

- **GIVEN** an admitted reservation without storage
- **WHEN** the trusted producer refuses
- **THEN** stable refusal proof preserves already-ordered cancellation proof

#### Scenario: ELM-ADOPT-008 Illegal retirement

- **GIVEN** an adopted buffer or stale actor
- **WHEN** producer-refused or final-ack is supplied
- **THEN** it cannot bypass drainage or retire current actor resource

## ELM-ADOPT-009 — Treat cancellation as a request followed by proved closure

WHILE a resource or reservation is owned, the native broker SHALL account for its admission, transfer and cleanup until matching native completion permits retirement; cancellation or release intent alone SHALL NOT erase ownership, charge or cleanup obligations.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P0.

Baseline mapping: ELM-ARC-012, ELM-ARC-016, ELM-REV-010.

Existing work mapping: W03, W06, W10.

Source proposals: TE-04, OPUS02-TE-06.

Owner: Native authority lead. Verifier: Independent acceptance reviewer.

Guardrails: Conservation includes newly admitted resources and ownership transfers. Cancel/Release emission is not physical retirement; producer refusal is valid only after trusted failure before image adoption. Native producer/consumer completion and reader drain remain distinct.

Tradeoffs: Retained records and native callback coordination; release on cancel-send unsafe; generation-scoped drain avoids global waits.

Primary sources:

- <https://arxiv.org/abs/1910.11108>
- <https://dl.acm.org/doi/10.1145/3290341>
- <https://docs.gtk.org/gio/method.Cancellable.cancel.html>
- <https://docs.gtk.org/gio/method.InputStream.close_async.html>
- <https://docs.rs/tokio/latest/tokio/macro.select.html>
- <https://docs.rs/tokio/latest/tokio/task/struct.JoinHandle.html>
- <https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ECOOP.2020.14>
- <https://grpc.io/docs/guides/cancellation/>
- <https://grpc.io/docs/guides/deadlines/>
- <https://guide.elm-lang.org/interop/ports.html>
- <https://jgbm.github.io/pubs/fowler-popl2019-sessions-extended.pdf>
- <https://lamport.azurewebsites.net/pubs/time-clocks.pdf>
- <https://lmcs.episciences.org/4973>
- <https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/>
- <https://quint.sh/docs/lang>
- <https://raw.githubusercontent.com/elm/core/1.0.5/src/Platform/Cmd.elm>
- <https://wayland.freedesktop.org/docs/book/Protocol.html>
- <https://wayland.freedesktop.org/docs/html/apa.html>
- <https://wayland.freedesktop.org/docs/html/apa.html#protocol-spec-wl_buffer>

#### Scenario: ELM-ADOPT-009 Cancel refusal race

- **GIVEN** capture cancelled before adoption
- **WHEN** refusal completes asynchronously
- **THEN** ordered cancellation/refusal proofs leave no reservation after final ack

#### Scenario: ELM-ADOPT-009 Held reader

- **GIVEN** adopted buffer with held GIO reader
- **WHEN** cancel and shutdown occur
- **THEN** fetch revoked immediately and terminal release waits for producer completion and reader drainage

## ELM-ADOPT-010 — Separate causal order, epoch identity and deadline time

WHEN queueing, frontend replacement or reconciliation occurs, the authority SHALL preserve the operation's original native clock domain, time origin and deadline while validating ordered control delivery independently of observation revisions.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P1.

Baseline mapping: ELM-REV-007, ELM-REV-008, ELM-REV-009, ELM-REV-012, ELM-ARC-013, ELM-ARC-014.

Existing work mapping: W01, W02, W05.

Source proposals: TE-05, SOL-FLUID-03.

Owner: Native authority lead. Verifier: Independent acceptance reviewer.

Guardrails: Original absolute native deadlines/start events survive queue/recovery. Causality/order counters, presentation clock, input clock and epoch are distinct. Late receipts may reconcile knowledge without becoming timely success.

Tradeoffs: Metadata and clock/queue instrumentation; frontend timers may provide feedback or fail-closed withdrawal of unsent local intent, but cannot authorize, extend, settle or time native work or substitute for native original deadlines. Vector clocks are unnecessary.

Primary sources:

- <https://arxiv.org/abs/1910.11108>
- <https://dl.acm.org/doi/10.1145/3290341>
- <https://docs.rs/tokio/latest/tokio/macro.select.html>
- <https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ECOOP.2020.14>
- <https://grpc.io/docs/guides/cancellation/>
- <https://grpc.io/docs/guides/deadlines/>
- <https://guide.elm-lang.org/interop/ports.html>
- <https://jgbm.github.io/pubs/fowler-popl2019-sessions-extended.pdf>
- <https://lamport.azurewebsites.net/pubs/time-clocks.pdf>
- <https://lmcs.episciences.org/4973>
- <https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/>
- <https://quint.sh/docs/lang>
- <https://raw.githubusercontent.com/elm/core/1.0.5/src/Platform/Cmd.elm>
- <https://raw.githubusercontent.com/elm/core/master/src/Platform/Cmd.elm>
- <https://wayland.freedesktop.org/docs/book/Protocol.html>
- <https://wayland.freedesktop.org/docs/html/apa.html>
- <https://www.microsoft.com/en-us/research/wp-content/uploads/2016/12/Time-Clocks-and-the-Ordering-of-Events-in-a-Distributed-System.pdf>

#### Scenario: ELM-ADOPT-010 Restart receipt

- **GIVEN** pending work and frontend restart
- **WHEN** exact late receipt arrives
- **THEN** original request reconciles without deadline renewal or mutation replay

#### Scenario: ELM-ADOPT-010 Gap clock

- **GIVEN** control sequence gap or replaced clock domain
- **WHEN** later delta/timeout arrives
- **THEN** new admission withheld until coherent reconciliation and invalid timing cannot authorize work

## ELM-ADOPT-011 — preserve uncertainty in a structured reporting contract

WHEN an operation report is presented, the shell SHALL derive its message and available recovery actions from a validated correlated outcome and SHALL distinguish definitive refusal from Unknown without implying completion or authorizing replay.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: 1.

Baseline mapping: ELM-ARC-007, ELM-ARC-008, ELM-ARC-014.

Existing work mapping: W04, W11.

Source proposals: ERR-01, OPUS03-ER-01.

Owner: Desktop experience lead. Verifier: Independent acceptance reviewer.

Guardrails: Stable bounded outcome/reason catalog and actionable, reviewed text from a catalog that supports localization. Unknown remains perceivable. Unknown reason within a validated Refused class may use generic refusal text; unknown schema/outcome cannot fabricate Refused. Supporting localization does not add a translation release gate.

Tradeoffs: status-only messages are cheaper but obscure safe recovery; raw native messages reduce mapping work but leak details and blur semantics. Cost: category registry, compatibility review and differential fixtures. Validation: enumerate every existing outcome/recovery reason; every class has reviewed text and enabled-action oracle; corrupt or future reasons fail closed without fabricating a terminal outcome.

Primary sources:

- <http://www.bitsavers.org/pdf/xerox/parc/techReports/CSL-83-7_Implementing_Remote_Procedure_Calls.pdf>
- <https://docs.gtk.org/glib/logging.html>
- <https://docs.rs/thiserror/latest/thiserror/>
- <https://docs.sentry.io/platforms/python/data-management/sensitive-data/>
- <https://google.aip.dev/193>
- <https://opentelemetry.io/docs/specs/semconv/attributes-registry/error/>
- <https://raw.githubusercontent.com/grpc/grpc/master/doc/statuscodes.md>
- <https://raw.githubusercontent.com/mozilla/gecko-dev/master/toolkit/crashreporter/CrashAnnotations.yaml>
- <https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.journal-fields.xml>
- <https://systemd.io/CATALOG/>
- <https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/sosp153-glerum-web.pdf>
- <https://www.microsoft.com/en-us/research/wp-content/uploads/2019/01/Guidelines-for-Human-AI-Interaction-camera-ready.pdf>
- <https://www.nngroup.com/articles/ten-usability-heuristics/>
- <https://www.usenix.org/events/hotos03/tech/full_papers/candea/candea.pdf>
- <https://www.w3.org/TR/wai-aria-1.2/>
- <https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html>

#### Scenario: ELM-ADOPT-011 ERR-01-01

- **GIVEN** an admitted restore with lost receipt
- **WHEN** transport disconnects
- **THEN** the report states that completion is unconfirmed, preserves Unknown and offers no automatic repeat.

#### Scenario: ELM-ADOPT-011 ERR-01-02

- **GIVEN** an exact unsent certificate and a simultaneous late receipt for a different request
- **WHEN** reports are reduced
- **THEN** refusal is attached only to the certified request and the foreign receipt cannot alter its message or actions.

## ELM-ADOPT-012 — one announcement owner and outcome-aware deduplication

WHEN an eligible correlated outcome transition requires attention, the controller SHALL publish one accessible status through the designated announcement owner, retain focus and suppress repeats of that outcome while preserving later distinct outcome transitions.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: duplicate. Priority: 1.

Baseline mapping: ELM-UI-009, ELM-UI-010.

Existing work mapping: W08.

Source proposals: ERR-02, OPUS03-ER-02, UXA-04.

Owner: Accessibility lead. Verifier: Independent acceptance reviewer.

Guardrails: One announcement owner; deduplicate repeated outcomes, not distinct later state changes. Native speech/braille/focus transcript required; ARIA alone is insufficient. The semantic owner is the controller; delivery must reach a qualified AT-active document or declared native/fallback route, including when application focus remains outside shell.

Tradeoffs: per-view live regions are simple locally but duplicate output on multiple surfaces; one modal per failure interferes with focus and ordinary work. Cost: semantic routing, native AT integration and multi-output transcript qualification. Validation: count announcements against distinct eligible transitions, observe focus and speech/braille, include duplicate receipts and surface recreation. Preserve existing policy thresholds; freeze any missing quantitative oracle through S02/P0 rather than inventing one.

Primary sources:

- <http://www.bitsavers.org/pdf/xerox/parc/techReports/CSL-83-7_Implementing_Remote_Procedure_Calls.pdf>
- <https://arxiv.org/html/2609.17959>
- <https://developer.gnome.org/hig/guidelines/keyboard.html>
- <https://doc.qt.io/qt-6/qstyle.html>
- <https://docs.gtk.org/glib/logging.html>
- <https://docs.gtk.org/gtk4/method.Accessible.announce.html>
- <https://docs.sentry.io/platforms/python/data-management/sensitive-data/>
- <https://google.aip.dev/193>
- <https://grouplab.cpsc.ucalgary.ca/grouplab/uploads/Publications/Publications/2007-PredictiveModelMenus.CHI.pdf>
- <https://help.gnome.org/users/gnome-help/stable/keyboard-nav.html.en>
- <https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-automation-element-propids>
- <https://opentelemetry.io/docs/specs/semconv/attributes-registry/error/>
- <https://raw.githubusercontent.com/GNOME/gnome-shell/main/js/ui/ctrlAltTab.js>
- <https://raw.githubusercontent.com/GNOME/gtk/gtk-3-24/gtk/gtkmenuitem.c>
- <https://raw.githubusercontent.com/GNOME/orca/main/src/orca/live_region_presenter.py>
- <https://raw.githubusercontent.com/KDE/plasma-desktop/master/applets/taskmanager/qml/Task.qml>
- <https://raw.githubusercontent.com/grpc/grpc/master/doc/statuscodes.md>
- <https://raw.githubusercontent.com/mozilla/gecko-dev/master/toolkit/crashreporter/CrashAnnotations.yaml>
- <https://raw.githubusercontent.com/qt/qtbase/dev/src/widgets/styles/qwindowsstyle.cpp>
- <https://raw.githubusercontent.com/swaywm/wlr-protocols/master/unstable/wlr-layer-shell-unstable-v1.xml>
- <https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.journal-fields.xml>
- <https://raw.githubusercontent.com/wmww/gtk-layer-shell/master/include/gtk-layer-shell.h>
- <https://sre.google/sre-book/monitoring-distributed-systems/>
- <https://support.microsoft.com/en-us/windows/keyboard-shortcuts-in-windows-dcc61a57-8ff0-cffe-9796-cb9706c75eec>
- <https://systemd.io/CATALOG/>
- <https://wayland.app/protocols/text-input-unstable-v3>
- <https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/sosp153-glerum-web.pdf>
- <https://www.nngroup.com/articles/ten-usability-heuristics/>
- <https://www.usenix.org/events/hotos03/tech/full_papers/candea/candea.pdf>
- <https://www.w3.org/TR/uievents/>
- <https://www.w3.org/TR/wai-aria-1.2/>
- <https://www.w3.org/WAI/ARIA/apg/patterns/menubar/>
- <https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/>
- <https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html>

#### Scenario: ELM-ADOPT-012 ERR-02-01

- **GIVEN** bar and popup projections on two outputs with stable focus
- **WHEN** the same refusal receipt is delivered repeatedly and a popup recreates
- **THEN** one eligible announcement occurs and recovery detail remains reachable.

#### Scenario: ELM-ADOPT-012 ERR-02-02

- **GIVEN** Unknown was announced and the original deadline has elapsed
- **WHEN** a valid late correlated receipt settles knowledge
- **THEN** a distinct policy-eligible update is exposed without restarting the effect or changing its deadline; unauthenticated, unrelated or unauthorized receipts cause no update, while exact authenticated historical evidence may reconcile retained Unknown through the declared recovery route

## ELM-ADOPT-013 — bounded allowlisted diagnostics independent of authority

WHILE ordinary diagnostics are enabled, the diagnostics subsystem SHALL admit only allowlisted bounded records and SHALL report record loss without collecting excluded content or altering native authority, operation outcomes or deadlines.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: 2.

Baseline mapping: ELM-DEL-017, ELM-QA-021, ELM-QA-023, ELM-REV-020, ELM-REV-021.

Existing work mapping: W04, W11.

Source proposals: ERR-03, OPUS03-ER-03, OPUS01-IMM-5.

Owner: Release integration lead. Verifier: Independent acceptance reviewer.

Guardrails: Secrets, credentials, draft contents and captured pixels are always excluded from ordinary diagnostics under ELM-DEL-017. Raw port bodies, titles, arguments and paths are also excluded by this ordinary allowlist. A different scoped mode requires a separate reviewed contract and is outside this draft. Retention/loss counters remain bounded. Saturation cannot block native control/cleanup or compact durable authority.

Tradeoffs: unrestricted verbose logs simplify one incident at privacy/resource cost; aggregate-only metrics lose sequence context. Cost: event schema, producer audits and saturation tests. A ring buffer and separate counters are possible implementations, not mandated architecture. Validation: sensitive canaries across nested values and error strings; resource saturation, failure to write and malformed events preserve controller decisions. Measure log-rate, whole-process CPU/wakeups/memory, export cost and retention against `elm-performance/spec.md` ELM-QA-021/023 and ELM-REV-020/021; the performance owner freezes numeric limits from P0 workloads before acceptance. Measure under the actual ELM-QA-021/023 and ELM-REV-020/021 budget contract.

Primary sources:

- <http://www.bitsavers.org/pdf/xerox/parc/techReports/CSL-83-7_Implementing_Remote_Procedure_Calls.pdf>
- <https://apalache-mc.org/docs/adr/015adr-trace.html>
- <https://arxiv.org/abs/2006.00915>
- <https://arxiv.org/abs/2104.01146>
- <https://arxiv.org/abs/2404.16075>
- <https://docs.gtk.org/glib/logging.html>
- <https://docs.sentry.io/platforms/python/data-management/sensitive-data/>
- <https://google.aip.dev/193>
- <https://immerjs.github.io/immer/patches/>
- <https://kafka.apache.org/43/design/design/>
- <https://lamport.azurewebsites.net/pubs/abadi-existence.pdf>
- <https://opentelemetry.io/docs/security/handling-sensitive-data/>
- <https://opentelemetry.io/docs/specs/otel/logs/data-model/>
- <https://opentelemetry.io/docs/specs/semconv/attributes-registry/error/>
- <https://people.seas.harvard.edu/~chong/pubs/pldi13-elm.pdf>
- <https://quint.sh/docs/checking-properties>
- <https://raw.githubusercontent.com/avh4/elm-program-test/main/src/ProgramTest.elm>
- <https://raw.githubusercontent.com/elm/browser/master/src/Debugger/History.elm>
- <https://raw.githubusercontent.com/elm/core/1.0.5/src/Array.elm>
- <https://raw.githubusercontent.com/elm/core/1.0.5/src/Dict.elm>
- <https://raw.githubusercontent.com/grpc/grpc/master/doc/statuscodes.md>
- <https://raw.githubusercontent.com/mozilla/gecko-dev/master/toolkit/crashreporter/CrashAnnotations.yaml>
- <https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.journal-fields.xml>
- <https://redux.js.org/style-guide/>
- <https://systemd.io/CATALOG/>
- <https://www.cs.cmu.edu/~rwh/students/okasaki.pdf>
- <https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/sosp153-glerum-web.pdf>
- <https://www.nngroup.com/articles/ten-usability-heuristics/>
- <https://www.usenix.org/events/hotos03/tech/full_papers/candea/candea.pdf>
- <https://www.w3.org/TR/wai-aria-1.2/>
- <https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html>

#### Scenario: ELM-ADOPT-013 ERR-03-01

- **GIVEN** a decoder failure containing a secret canary and window title
- **WHEN** a diagnostic record is produced
- **THEN** only allowed category/context fields appear and neither canary nor title is retained.

#### Scenario: ELM-ADOPT-013 ERR-03-02

- **GIVEN** diagnostic capacity is exhausted during a pending effect
- **WHEN** further records arrive and a terminal receipt races
- **THEN** loss is observable, memory stays within the frozen budget and receipt settlement is identical to diagnostics-disabled execution.

## ELM-ADOPT-014 — recovery evidence distinguishes restored availability from past success

WHEN a failed frontend or authority recovers, the shell SHALL report verified current availability separately from unresolved historical outcomes and SHALL admit new effects only after native reconciliation under the original deadline and identity contracts.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: 1.

Baseline mapping: ELM-ARC-014, ELM-ARC-026, ELM-QA-002, ELM-QA-003.

Existing work mapping: W05, W10, W11.

Source proposals: ERR-04, OPUS03-ER-05.

Owner: Release integration lead. Verifier: Independent acceptance reviewer.

Guardrails: Recovery action must preserve durable Unknown, replay floors, held resources and original clocks. Generic restart guidance is not acceptance. Compositor replacement is not an incidental recovery action.

Tradeoffs: automatic retries may appear faster but are prohibited here; generic “recovered” banners omit the critical uncertainty. Cost: recovery phase/report integration and protected fault campaign evidence. Validation: original restore38/recovery34 with unchanged identity/oracle/deadline, held effects, missing/corrupt journal, unavailable storage, frontend/authority epoch replacement and stale proof. Component replay supplements rather than replaces native acceptance.

Primary sources:

- <http://www.bitsavers.org/pdf/xerox/parc/techReports/CSL-83-7_Implementing_Remote_Procedure_Calls.pdf>
- <https://docs.gtk.org/glib/logging.html>
- <https://docs.sentry.io/platforms/python/data-management/sensitive-data/>
- <https://google.aip.dev/193>
- <https://opentelemetry.io/docs/specs/semconv/attributes-registry/error/>
- <https://raw.githubusercontent.com/grpc/grpc/master/doc/statuscodes.md>
- <https://raw.githubusercontent.com/mozilla/gecko-dev/master/toolkit/crashreporter/CrashAnnotations.yaml>
- <https://raw.githubusercontent.com/systemd/systemd/main/man/systemd-coredump.xml>
- <https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.journal-fields.xml>
- <https://systemd.io/CATALOG/>
- <https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/sosp153-glerum-web.pdf>
- <https://www.nngroup.com/articles/ten-usability-heuristics/>
- <https://www.usenix.org/events/hotos03/tech/full_papers/candea/candea.pdf>
- <https://www.w3.org/TR/wai-aria-1.2/>
- <https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html>
- <https://www2.eecs.berkeley.edu/Pubs/TechRpts/2002/Archive/CSD-02-1175.pdf>

#### Scenario: ELM-ADOPT-014 ERR-04-01

- **GIVEN** an admitted effect and crash before durable settlement
- **WHEN** a fresh epoch receives a coherent snapshot
- **THEN** availability may recover while the previous effect remains unconfirmed and is never replayed.

#### Scenario: ELM-ADOPT-014 ERR-04-02

- **GIVEN** a storage-full recovery failure and matching-looking geometry from a replacement incarnation
- **WHEN** reconciliation is attempted
- **THEN** geometry alone cannot clear the historical reservation, no new dependent effect is admitted and each affected operation's original deadline is unchanged and is not renewed by recovery.

## ELM-ADOPT-015 — explicit diagnostics export boundary

WHERE local diagnostic export is selected, WHEN the user requests an export, the shell SHALL produce an inspectable local bundle of validated export-allowed evidence and declared omissions, preserving recovery authority and sending nothing externally.

Status: deferred-conditional-draft. Classification: deferred-conditional-export; original research classification: conditional-new. Priority: deferred.

Baseline mapping: ELM-DEL-017.

Existing work mapping: W11.

Source proposals: ERR-05, OPUS03-ER-04.

Owner: Release integration lead. Verifier: Independent acceptance reviewer.

Guardrails: Conditional/deferrable feature; not a new mandatory release blocker. No default cores, screenshots, environment, unrestricted journals or uploads. Explicit local user request; cancellation/disk-full has truthful partial-artifact outcome.

Tradeoffs: copying a journal manually is cheaper but produces unreviewable privacy and scope surprises; automated cloud uploads introduce unsupported product scope. Cost: bundle builder, accessible review and export fault testing. Validation: unpack and schema-check artifacts; canary and content scans; stale-epoch snapshot race, cancellation, disk-full and symlink/path defenses; measured export overhead must meet frozen performance budgets.

Disposition: deferred conditional export. This adds no mandatory release blocker. Product selection, destination/privacy policy and measured budgets require separate review before implementation.

Primary sources:

- <http://www.bitsavers.org/pdf/xerox/parc/techReports/CSL-83-7_Implementing_Remote_Procedure_Calls.pdf>
- <https://docs.gtk.org/glib/logging.html>
- <https://docs.sentry.io/platforms/python/data-management/sensitive-data/>
- <https://google.aip.dev/193>
- <https://opentelemetry.io/docs/security/handling-sensitive-data/>
- <https://opentelemetry.io/docs/specs/semconv/attributes-registry/error/>
- <https://raw.githubusercontent.com/grpc/grpc/master/doc/statuscodes.md>
- <https://raw.githubusercontent.com/mozilla/gecko-dev/master/toolkit/crashreporter/CrashAnnotations.yaml>
- <https://raw.githubusercontent.com/systemd/systemd/main/man/systemd-coredump.xml>
- <https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.journal-fields.xml>
- <https://systemd.io/CATALOG/>
- <https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/sosp153-glerum-web.pdf>
- <https://www.nngroup.com/articles/ten-usability-heuristics/>
- <https://www.usenix.org/events/hotos03/tech/full_papers/candea/candea.pdf>
- <https://www.w3.org/TR/wai-aria-1.2/>
- <https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html>

#### Scenario: ELM-ADOPT-015 ERR-05-01

- **GIVEN** diagnostics and an available core dump containing private memory
- **WHEN** the user requests the ordinary bundle
- **THEN** the bundle includes allowed metadata and states that core/pixels/content are omitted.

#### Scenario: ELM-ADOPT-015 ERR-05-02

- **GIVEN** export is assembling records while frontend epoch changes
- **WHEN** cancellation or disk-full occurs
- **THEN** no success is reported, partial-artifact disposition is explicit, and neither old nor fresh recovery reservation is changed.

## ELM-ADOPT-016 — Preserve control identity across publication and focus changes

WHILE a shell focus scope is open, the host SHALL preserve an eligible focused control through unrelated publications and dispatch admitted keyboard or assistive activation only to that native AT-exposed identity, rejecting retired or changed-scope targets and applying the frozen fallback when focus becomes ineligible.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P0.

Baseline mapping: ELM-UI-011, ELM-UX-023, ELM-UX-024.

Existing work mapping: W07.

Source proposals: SOL04-01, UXA-01.

Owner: Desktop experience lead. Verifier: Independent acceptance reviewer.

Guardrails: Publication, lease and incarnation captured at press remain authoritative at release. Preserve the surviving focused identity while eligible under the frozen per-surface policy; disabled-but-focusable controls remain focused when030 allows it, otherwise apply the declared fallback. Selection is distinct from focus. Keyed DOM is an implementation choice.

Tradeoffs: Identity propagation and native focus evidence; preserve identity rather than index or automatic selected-row refocus.

Primary sources:

- <https://arxiv.org/html/2609.17959>
- <https://developer.gnome.org/hig/guidelines/keyboard.html>
- <https://doc.qt.io/qt-6/qstyle.html>
- <https://docs.gtk.org/gtk4/method.Accessible.announce.html>
- <https://grouplab.cpsc.ucalgary.ca/grouplab/uploads/Publications/Publications/2007-PredictiveModelMenus.CHI.pdf>
- <https://help.gnome.org/users/gnome-help/stable/keyboard-nav.html.en>
- <https://learn.microsoft.com/en-us/windows/apps/develop/input/keyboard-interactions>
- <https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-automation-element-propids>
- <https://raw.githubusercontent.com/GNOME/gnome-shell/main/js/ui/ctrlAltTab.js>
- <https://raw.githubusercontent.com/GNOME/gtk/gtk-3-24/gtk/gtkmenuitem.c>
- <https://raw.githubusercontent.com/GNOME/orca/main/src/orca/live_region_presenter.py>
- <https://raw.githubusercontent.com/KDE/plasma-desktop/master/applets/taskmanager/qml/Task.qml>
- <https://raw.githubusercontent.com/qt/qtbase/dev/src/widgets/styles/qwindowsstyle.cpp>
- <https://raw.githubusercontent.com/swaywm/wlr-protocols/master/unstable/wlr-layer-shell-unstable-v1.xml>
- <https://raw.githubusercontent.com/wmww/gtk-layer-shell/master/include/gtk-layer-shell.h>
- <https://support.microsoft.com/en-us/windows/keyboard-shortcuts-in-windows-dcc61a57-8ff0-cffe-9796-cb9706c75eec>
- <https://wayland.app/protocols/text-input-unstable-v3>
- <https://www.w3.org/TR/uievents/>
- <https://www.w3.org/WAI/ARIA/apg/patterns/menubar/>
- <https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/>

#### Scenario: ELM-ADOPT-016 SOL04-01-scenario-1

- **GIVEN** Close is focused while another row is selected
- **WHEN** an unrelated catalog publication arrives
- **THEN** Close keeps focus and the next activation invokes only Close

#### Scenario: ELM-ADOPT-016 SOL04-01-scenario-2

- **GIVEN** an activation press belongs to a window incarnation and lease
- **WHEN** that incarnation retires and the row position is reused before release
- **THEN** release dispatches no replacement action and eligible fallback remains reachable

#### Scenario: ELM-ADOPT-016 focus-without-publication

- **GIVEN** Close has keyboard/native AT focus while another row is selected
- **WHEN** Enter or Space is admitted without an intervening publication
- **THEN** only Close is invoked, no window intent is dispatched and selection cannot override focused identity

## ELM-ADOPT-017 — Treat native semantics and announcements as a coherent projection

WHEN a shell projection changes, the shell SHALL expose coherent native names, roles, states, relationships and actions for the current control identities, keeping preview imagery inert and keyboard focus distinct from selection.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P0.

Baseline mapping: ELM-UI-009, ELM-UI-010, ELM-UX-025, ELM-UX-026.

Existing work mapping: W08, W07, W06.

Source proposals: SOL04-02, UXA-03.

Owner: Accessibility lead. Verifier: Independent acceptance reviewer.

Guardrails: Control semantics plus actual native bridge required. Announcement ownership is separately ELM-ADOPT-012; multiple read-only status regions do not establish a single AT announcement. Keep the visible stable control label as the accessible name; expose transient state and action descriptions separately, within the frozen per-control naming policy. Verify cross-surface relationships in the native AT tree; DOM-local relationships do not automatically cross WebView documents.

Tradeoffs: One outcome owner requires lifecycle correlation and native speech/braille inspection; API availability differs by ABI.

Primary sources:

- <https://arxiv.org/html/2609.17959>
- <https://developer.gnome.org/hig/guidelines/keyboard.html>
- <https://doc.qt.io/qt-6/qstyle.html>
- <https://docs.gtk.org/gtk4/method.Accessible.announce.html>
- <https://gnome.pages.gitlab.gnome.org/orca/help/howto_forms.html>
- <https://grouplab.cpsc.ucalgary.ca/grouplab/uploads/Publications/Publications/2007-PredictiveModelMenus.CHI.pdf>
- <https://help.gnome.org/users/gnome-help/stable/keyboard-nav.html.en>
- <https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-automation-element-propids>
- <https://raw.githubusercontent.com/GNOME/gnome-shell/main/js/ui/ctrlAltTab.js>
- <https://raw.githubusercontent.com/GNOME/gtk/gtk-3-24/gtk/gtkmenuitem.c>
- <https://raw.githubusercontent.com/GNOME/orca/main/src/orca/live_region_presenter.py>
- <https://raw.githubusercontent.com/KDE/plasma-desktop/master/applets/taskmanager/qml/Task.qml>
- <https://raw.githubusercontent.com/qt/qtbase/dev/src/widgets/styles/qwindowsstyle.cpp>
- <https://raw.githubusercontent.com/swaywm/wlr-protocols/master/unstable/wlr-layer-shell-unstable-v1.xml>
- <https://raw.githubusercontent.com/wmww/gtk-layer-shell/master/include/gtk-layer-shell.h>
- <https://support.microsoft.com/en-us/windows/keyboard-shortcuts-in-windows-dcc61a57-8ff0-cffe-9796-cb9706c75eec>
- <https://wayland.app/protocols/text-input-unstable-v3>
- <https://www.w3.org/TR/uievents/>
- <https://www.w3.org/WAI/ARIA/apg/patterns/menubar/>
- <https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/>

#### Scenario: ELM-ADOPT-017 SOL04-02-scenario-1

- **GIVEN** bar and popup show the same pending operation
- **WHEN** the matching refusal arrives twice
- **THEN** both projections expose the same refusal state for the same control identity and focus remains on the user's control; announcement count follows ELM-ADOPT-012

#### Scenario: ELM-ADOPT-017 SOL04-02-scenario-2

- **GIVEN** a preview image has retired while its restore control survives
- **WHEN** AT explores the control
- **THEN** source state and supported action are available without an actionable image object or stale-incarnation activation

#### Scenario: ELM-ADOPT-017 stable-name-state-change

- **GIVEN** a single-window group whose visible identity label is unchanged becomes active or pending
- **WHEN** native AT re-reads the control
- **THEN** the accessible name remains aligned with the same visible label while state/description changes under the frozen naming policy

## ELM-ADOPT-018 — Qualify composition as native field ownership

WHILE an input method owns a shell field composition, the host SHALL preserve native preedit and candidate interaction, suppress shell handling of consumed keys, and accept commits only for the current field identity and composition generation.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: duplicate. Priority: P0.

Baseline mapping: ELM-UI-012, ELM-UX-028.

Existing work mapping: W07.

Source proposals: SOL04-03, UXA-06.

Owner: Accessibility lead. Verifier: Independent acceptance reviewer.

Guardrails: Native field/composition epoch binds commits; consumed keys cannot trigger shell shortcuts. Native candidate/preedit and actual input target evidence required.

Tradeoffs: Native IME campaigns are costly; toolkit API examples cannot be transplanted across host lanes.

Primary sources:

- <https://arxiv.org/html/2609.17959>
- <https://developer.gnome.org/hig/guidelines/keyboard.html>
- <https://doc.qt.io/qt-6/qstyle.html>
- <https://docs.gtk.org/gtk4/method.Accessible.announce.html>
- <https://docs.gtk.org/gtk4/method.IMContext.filter_keypress.html>
- <https://gnome.pages.gitlab.gnome.org/orca/help/howto_forms.html>
- <https://grouplab.cpsc.ucalgary.ca/grouplab/uploads/Publications/Publications/2007-PredictiveModelMenus.CHI.pdf>
- <https://help.gnome.org/users/gnome-help/stable/keyboard-nav.html.en>
- <https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-automation-element-propids>
- <https://raw.githubusercontent.com/GNOME/gnome-shell/main/js/ui/ctrlAltTab.js>
- <https://raw.githubusercontent.com/GNOME/gtk/gtk-3-24/gtk/gtkmenuitem.c>
- <https://raw.githubusercontent.com/GNOME/gtk/main/gtk/gtkimcontext.h>
- <https://raw.githubusercontent.com/GNOME/orca/main/src/orca/live_region_presenter.py>
- <https://raw.githubusercontent.com/KDE/plasma-desktop/master/applets/taskmanager/qml/Task.qml>
- <https://raw.githubusercontent.com/qt/qtbase/dev/src/widgets/styles/qwindowsstyle.cpp>
- <https://raw.githubusercontent.com/swaywm/wlr-protocols/master/unstable/wlr-layer-shell-unstable-v1.xml>
- <https://raw.githubusercontent.com/wmww/gtk-layer-shell/master/include/gtk-layer-shell.h>
- <https://support.microsoft.com/en-us/windows/keyboard-shortcuts-in-windows-dcc61a57-8ff0-cffe-9796-cb9706c75eec>
- <https://wayland.app/protocols/text-input-unstable-v3>
- <https://www.w3.org/TR/uievents/>
- <https://www.w3.org/WAI/ARIA/apg/patterns/menubar/>
- <https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/>

#### Scenario: ELM-ADOPT-018 SOL04-03-scenario-1

- **GIVEN** a launcher field has active preedit
- **WHEN** the input method consumes Enter to commit text
- **THEN** the query receives the commit once and no launch occurs from that consumed key

#### Scenario: ELM-ADOPT-018 SOL04-03-scenario-2

- **GIVEN** composition belongs to a retired field generation
- **WHEN** its delayed commit arrives after a new field takes focus
- **THEN** neither field nor shell action receives the stale commit

## ELM-ADOPT-019 — Preserve hierarchy and reachability under constrained geometry

WHEN output geometry, text scale or label length changes, the shell SHALL preserve readable control names, visible focus, non-color state cues and keyboard-reachable actions using the frozen contrast, geometry and reflow policy.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P1.

Baseline mapping: ELM-UI-013, ELM-UX-027, ELM-UI-019.

Existing work mapping: W08.

Source proposals: SOL04-04.

Owner: Accessibility lead. Verifier: Independent acceptance reviewer.

Guardrails: Freeze measurable contrast/target/text/reflow budgets and test constrained outputs, long labels, scaling and non-color cues. Do not assume CSS tokens or screenshots establish native reachability.

Tradeoffs: Layout choices need measured geometry and AT bounds; freeze thresholds before qualification.

Primary sources:

- <https://faculty.washington.edu/wobbrock/pubs/taccess-11.pdf>
- <https://raw.githubusercontent.com/KDE/kirigami/master/src/controls/Action.qml>
- <https://learn.microsoft.com/en-us/windows/apps/develop/input/keyboard-interactions>

#### Scenario: ELM-ADOPT-019 SOL04-04-scenario-1

- **GIVEN** enlarged text and long localized labels on a small output
- **WHEN** the picker opens
- **THEN** every action remains reachable and focused labels are legible according to the frozen oracle

#### Scenario: ELM-ADOPT-019 SOL04-04-scenario-2

- **GIVEN** a popup owns focus on a removed output
- **WHEN** surviving-output recovery runs
- **THEN** its declared fallback or rehosted scope is reachable and removed-generation input cannot activate controls

## ELM-ADOPT-020 — Make action discovery agree with acknowledged outcomes

WHEN a shell action is unavailable or unresolved, the shell SHALL expose the correlated reason and safe next step, retain eligible focus and controls outside its dependency domain, and never queue, defer or automatically replay input not accepted in that state or a rejected or Unknown action.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P1.

Baseline mapping: ELM-UI-005, ELM-UI-007, ELM-UI-015, ELM-UI-020.

Existing work mapping: W07, W08, W01, W02.

Source proposals: SOL04-05, FI-03.

Owner: Desktop experience lead. Verifier: Independent acceptance reviewer.

Guardrails: Unrelated refresh means an unchanged declared family/target dependency domain and must preserve a valid picker/focus. Do not require concurrent native transactions. Repeated input during Pending follows INTERACTION.md feedback policy and ELM-UI-015; no second intent or announcement storm.

Tradeoffs: Shared vocabulary must follow native outcomes; no optimistic success or Unknown replay.

Primary sources:

- <http://direction.bordeaux.inria.fr/~roussel/publications/2015-UIST-mouse-based-lagmeter.pdf>
- <https://docs.gtk.org/gdk3/class.FrameClock.html>
- <https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html>
- <https://gitlab.freedesktop.org/wayland/wayland-protocols/-/blob/main/stable/presentation-time/presentation-time.xml>
- <https://idl.cs.washington.edu/files/2007-AnimatedTransitions-InfoVis.pdf>
- <https://raw.githubusercontent.com/KDE/kirigami/master/src/controls/Action.qml>
- <https://raw.githubusercontent.com/hyprwm/hyprutils/main/include/hyprutils/animation/AnimatedVariable.hpp>
- <https://webkitgtk.org/2026/09/16/webkitgtk-2.54-highlights.html>
- <https://www.cs.umd.edu/users/ben/papers/Shneiderman1983Direct.pdf>
- <https://www.cs.umd.edu/~ben/papers/Shneiderman1983Direct.pdf>

#### Scenario: ELM-ADOPT-020 SOL04-05-scenario-1

- **GIVEN** a minimized generic application family is selected
- **WHEN** activation is refused natively
- **THEN** it is not shown as restored, the reason and next action are reachable, and its preserved identity remains selected

#### Scenario: ELM-ADOPT-020 SOL04-05-scenario-2

- **GIVEN** an operation has Unknown disposition and guidance was dismissed
- **WHEN** the user opens help or recovery with the keyboard
- **THEN** guidance is available without resetting the desktop and reconciliation creates no automatic repeated mutation

#### Scenario: ELM-ADOPT-020 unrelated-observation-refresh

- **GIVEN** a picker is open for a family
- **WHEN** an unrelated observation refresh completes with that family's dependency revision unchanged
- **THEN** picker identity and focus persist and no new intent is emitted

#### Scenario: ELM-ADOPT-020 same-control-during-pending

- **GIVEN** a native operation is Pending for a control
- **WHEN** the same control is activated again
- **THEN** no second intent is emitted; one truthful not-accepted result is exposed under the frozen feedback policy without repeated announcement or later replay

## ELM-ADOPT-021 — Stage-qualified feedback and physical presentation evidence

WHEN an interaction stage is observed, the native authority and read-only projection SHALL label feedback, effect commitment, renderer submission, presentation and retirement separately, accepting physical completion only from identity-matched native evidence.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P0.

Baseline mapping: ELM-ARC-020, ELM-REN-005, ELM-REN-022.

Existing work mapping: W06, W08, P4-ELM-ARC-020, P4-ELM-REN-005, P6-ELM-REN-022.

Source proposals: SOL-FLUID-01, FI-01.

Owner: Performance qualification lead. Verifier: Independent acceptance reviewer.

Guardrails: Input, commit, rendering, presentation and retirement are separate stages. Record clock mappings, feedback flags and missing/discarded events. Frame callback/image-load/screenshot request is not hardware presentation.

Tradeoffs: ['Extra trace stages and correlation storage', 'Native feedback can approximate light output; independent hardware evidence is still needed']

Primary sources:

- <http://direction.bordeaux.inria.fr/~roussel/publications/2015-UIST-mouse-based-lagmeter.pdf>
- <https://doc.qt.io/qt-6/qquickwindow.html>
- <https://docs.gtk.org/gdk3/class.FrameClock.html>
- <https://docs.kernel.org/gpu/drm-uapi.html>
- <https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html>
- <https://gitlab.freedesktop.org/wayland/wayland-protocols/-/blob/main/stable/presentation-time/presentation-time.xml>
- <https://idl.cs.washington.edu/files/2007-AnimatedTransitions-InfoVis.pdf>
- <https://raw.githubusercontent.com/hyprwm/hyprutils/main/include/hyprutils/animation/AnimatedVariable.hpp>
- <https://raw.githubusercontent.com/wayland-mirror/wayland-protocols/main/stable/presentation-time/presentation-time.xml>
- <https://webkitgtk.org/2026/09/16/webkitgtk-2.54-highlights.html>
- <https://www.cs.umd.edu/users/ben/papers/Shneiderman1983Direct.pdf>

#### Scenario: ELM-ADOPT-021 Queued is not presented

- **GIVEN** a matching image was decoded and a renderer queued a frame
- **WHEN** only image load or frameSwapped arrives
- **THEN** presentation remains unproven and no physical-completion verdict is recorded

#### Scenario: ELM-ADOPT-021 Stale output presentation

- **GIVEN** a transaction targets one output generation
- **WHEN** a presentation receipt arrives after hotplug changed that generation
- **THEN** the receipt is retained diagnostically but cannot complete the replacement transaction

## ELM-ADOPT-022 — Demand scheduling with bounded control liveness

WHILE preview or observation demand exceeds admitted capacity, the bridge SHALL coalesce only replaceable observations within their identity domain, refuse unadmitted effects explicitly and preserve ordered cancellation, receipts and retirement capacity.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P0.

Baseline mapping: ELM-ARC-015, ELM-ARC-016, ELM-REN-012.

Existing work mapping: W01, W03, W06, W10.

Source proposals: SOL-FLUID-02.

Owner: Native authority lead. Verifier: Independent acceptance reviewer.

Guardrails: Coalesce only explicitly replaceable observations in the exact identity/dependency domain. Preserve reliable ordered effect/cleanup/control events, original deadlines and reserved progress capacity; no universal lossy stream.

Tradeoffs: ['Fairness and reserving control bytes reduce peak preview throughput', 'Coalescing requires explicit event taxonomy and atomic dependency preservation']

Primary sources:

- <https://wayland.freedesktop.org/docs/html/apa.html#protocol-spec-wl_surface>
- <https://docs.gtk.org/gdk4/class.FrameClock.html>
- <https://doc.qt.io/qt-6/qquickwindow.html>

#### Scenario: ELM-ADOPT-022 Observation storm with cancellation

- **GIVEN** preview queues are saturated within frozen byte and item bounds
- **WHEN** new observations and a cancellation arrive
- **THEN** only semantically replaceable observations coalesce; cancellation and all retirement receipts remain deliverable in order

#### Scenario: ELM-ADOPT-022 Close during producer reservation

- **GIVEN** a producer owns a reservation and the picker closes
- **WHEN** a late producer result arrives
- **THEN** the closed demand remains cancelled and its existing owner/cleanup stays recorded; another authorized demand may use only independently available eligible capacity, never the held reservation before matching release

## ELM-ADOPT-023 — Reversal and live reduced motion share native semantics

WHEN motion is interrupted or the reduced-motion preference changes, the native renderer SHALL derive the successor from the last-presented geometry and preserve the same identity, cancellation, commitment and retirement rules under the approved motion profile.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P1.

Baseline mapping: ELM-REN-010, ELM-REN-011, ELM-UI-014, ELM-UX-022.

Existing work mapping: W12, P4-ELM-REN-010, P4-ELM-REN-011, P4-ELM-UI-014.

Source proposals: SOL-FLUID-04, FI-06.

Owner: Graphics lead. Verifier: Independent acceptance reviewer.

Guardrails: Native last-presented geometry/velocity and approved reversal profile. Reduced motion is a live native preference, with no velocity continuation/decorative motion under the selected reduced profile. Presentation timestamps, original38/34/52 cases remain required.

Tradeoffs: ['Geometry and velocity continuity need native samples, not model time', 'The exact preference-switch policy must be frozen before qualification']

Primary sources:

- <http://direction.bordeaux.inria.fr/~roussel/publications/2015-UIST-mouse-based-lagmeter.pdf>
- <https://docs.gtk.org/gdk3/class.FrameClock.html>
- <https://docs.gtk.org/gdk4/class.FrameClock.html>
- <https://docs.gtk.org/gtk4/property.Settings.gtk-enable-animations.html>
- <https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html>
- <https://gitlab.freedesktop.org/wayland/wayland-protocols/-/blob/main/stable/presentation-time/presentation-time.xml>
- <https://idl.cs.washington.edu/files/2007-AnimatedTransitions-InfoVis.pdf>
- <https://raw.githubusercontent.com/hyprwm/hyprutils/main/include/hyprutils/animation/AnimatedVariable.hpp>
- <https://raw.githubusercontent.com/wayland-mirror/wayland-protocols/main/stable/presentation-time/presentation-time.xml>
- <https://webkitgtk.org/2026/09/16/webkitgtk-2.54-highlights.html>
- <https://www.cs.umd.edu/users/ben/papers/Shneiderman1983Direct.pdf>
- <https://www.tactuallabs.com/papers/designingLowLatencyDirectTouchInputUIST12.pdf>
- <https://www.yorku.ca/mack/p488-mackenzie.pdf>

#### Scenario: ELM-ADOPT-023 Reverse after an unpresented sample

- **GIVEN** a restore has a queued sample newer than its last native presentation
- **WHEN** a minimize intent reverses it
- **THEN** the successor starts from last-presented geometry under the native continuity rule and retires only the superseded generation

#### Scenario: ELM-ADOPT-023 Preference changes during capture

- **GIVEN** a restore is awaiting a retained frame
- **WHEN** reduced motion becomes enabled before its matching frame arrives
- **THEN** the approved reduced-motion route uses identical commit and cancellation obligations without replaying the effect or resetting its deadline

## ELM-ADOPT-024 — Separate feedback latency and useful completion measurement

WHEN host selection or release evaluation is prepared, the performance owner SHALL freeze same-machine workload budgets that separately measure input feedback, useful native presentation, whole-process resource closure and observer overhead, declaring missing stages.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P0.

Baseline mapping: ELM-QA-021, ELM-QA-023, ELM-REV-020, ELM-REV-021, ELM-REN-021, ELM-REN-022.

Existing work mapping: W08, W12, P6-ELM-QA-023, P6-ELM-REN-021, P6-ELM-REN-022.

Source proposals: SOL-FLUID-05.

Owner: Performance qualification lead. Verifier: Independent acceptance reviewer.

Guardrails: No numeric limit invented from papers. Record latency distributions, missed frames, hardware/refresh/output metadata, CPU/memory/wakeups/idle-power and resource soak; QA observers disabled for product measurements.

Tradeoffs: ['Hardware and minimally observed measurements cost time', 'Academic thresholds do not substitute for the frozen local budget contract']

Primary sources:

- <https://www.yorku.ca/mack/p488-mackenzie.pdf>
- <https://www.tactuallabs.com/papers/designingLowLatencyDirectTouchInputUIST12.pdf>
- <https://raw.githubusercontent.com/wayland-mirror/wayland-protocols/main/stable/presentation-time/presentation-time.xml>
- <https://docs.gtk.org/gdk4/class.FrameClock.html>
- <https://doc.qt.io/qt-6/qquickwindow.html>
- <https://docs.kernel.org/gpu/drm-uapi.html>

#### Scenario: ELM-ADOPT-024 Missing presentation instrument

- **GIVEN** a benchmark records CPU submission and feedback but lacks a presentation span
- **WHEN** the host comparison is evaluated
- **THEN** unsupported spans are explicit and physical latency acceptance remains blocked rather than treating submission as presentation

#### Scenario: ELM-ADOPT-024 Observer hides tail failure

- **GIVEN** a debug observer improves or perturbs scheduling
- **WHEN** the final benchmark packet is prepared
- **THEN** paired observed and minimally observed runs expose overhead and all frozen workload thresholds are evaluated without discarding misses

## ELM-ADOPT-025 — Control delivery continuity distinct from proof identity

WHEN authenticated control receipts are delivered, the bridge SHALL preserve their required per-channel causal order, detect gaps or regressions under the declared transport contract, reconcile uncertainty and keep repeated proofs idempotent without acknowledging unseen cleanup.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P0.

Baseline mapping: ELM-ARC-010, ELM-REV-008, ELM-REV-009, ELM-REV-010.

Existing work mapping: W03, W10.

Source proposals: OPUS02-TE-04.

Owner: Native authority lead. Verifier: Independent acceptance reviewer.

Guardrails: Use a separate delivery ordinal or independently qualified continuity mechanism. Proof IDs are not stream ordinals. Duplicate Acks may be retried idempotently when required; do not mandate withholding known-safe Ack retries. No global total order.

Tradeoffs: Additional protocol/evidence complexity must meet the frozen workload/resource budget. Reuse current modules and incrementally qualify changed paths.

Primary sources:

- <https://arxiv.org/abs/1910.11108>
- <https://dl.acm.org/doi/10.1145/3290341>
- <https://docs.rs/tokio/latest/tokio/macro.select.html>
- <https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ECOOP.2020.14>
- <https://grpc.io/docs/guides/cancellation/>
- <https://grpc.io/docs/guides/deadlines/>
- <https://guide.elm-lang.org/interop/ports.html>
- <https://jgbm.github.io/pubs/fowler-popl2019-sessions-extended.pdf>
- <https://lamport.azurewebsites.net/pubs/time-clocks.pdf>
- <https://lmcs.episciences.org/4973>
- <https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/>
- <https://quint.sh/docs/lang>
- <https://raw.githubusercontent.com/elm/core/1.0.5/src/Platform/Cmd.elm>
- <https://wayland.freedesktop.org/docs/book/Protocol.html>
- <https://wayland.freedesktop.org/docs/html/apa.html>

#### Scenario: ELM-ADOPT-025 reordered-cleanup

- **GIVEN** Released and racing Cancelled proofs for a still-held job
- **WHEN** the later control event overtakes its prerequisite
- **THEN** no unseen proof is acknowledged and no ownership is forgotten; the declared gap/reconciliation policy preserves cleanup

#### Scenario: ELM-ADOPT-025 cross-entry-proof-and-retry

- **GIVEN** global proof IDs interleave across entries and a valid final Ack is lost
- **WHEN** a stable proof repeats on the authenticated delivery stream
- **THEN** it does not create a false gap or duplicate physical cleanup; the declared idempotent acknowledgement/reconciliation policy can finish retirement

## ELM-ADOPT-026 — Capture must not starve native presentation

IF a preview capture or export route exceeds its frozen presentation-impact budget on an active output, THEN the release verifier SHALL reject that route and retain a qualified alternative or explicit unavailable-preview state.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P0.

Baseline mapping: ELM-REV-022, ELM-REN-012, ELM-QA-023, ELM-UI-017.

Existing work mapping: W06, W08.

Source proposals: FI-02.

Owner: Performance qualification lead. Verifier: Independent acceptance reviewer.

Guardrails: Synchronous compositor readback/encode is a concern, not a measured regression. Async readback/cropping/off-thread encoding need their own safety, fence, eligibility and ABI qualification. Unavailable fallback does not close mandatory source-stop/family gates.

Tradeoffs: Additional protocol/evidence complexity must meet the frozen workload/resource budget. Reuse current modules and incrementally qualify changed paths.

Primary sources:

- <http://direction.bordeaux.inria.fr/~roussel/publications/2015-UIST-mouse-based-lagmeter.pdf>
- <https://docs.gtk.org/gdk3/class.FrameClock.html>
- <https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html>
- <https://gitlab.freedesktop.org/wayland/wayland-protocols/-/blob/main/stable/presentation-time/presentation-time.xml>
- <https://idl.cs.washington.edu/files/2007-AnimatedTransitions-InfoVis.pdf>
- <https://raw.githubusercontent.com/hyprwm/hyprutils/main/include/hyprutils/animation/AnimatedVariable.hpp>
- <https://webkitgtk.org/2026/09/16/webkitgtk-2.54-highlights.html>
- <https://www.cs.umd.edu/users/ben/papers/Shneiderman1983Direct.pdf>

#### Scenario: ELM-ADOPT-026 cross-output-capture-impact

- **GIVEN** restore motion on one output and capture demand on another
- **WHEN** the capture route runs on the measured hardware tuple
- **THEN** presentation gaps and latency are measured on every active output against the same workload without capture

#### Scenario: ELM-ADOPT-026 over-budget-route

- **GIVEN** measured route impact exceeds the frozen budget
- **WHEN** release admission evaluates it
- **THEN** the route is rejected and the documented unavailable fallback is truthful; no stale or unqualified route substitutes for required capture acceptance

## ELM-ADOPT-027 — Persistent demand converges to latest authorized source content

WHILE authorized preview demand persists, WHEN tracked source content advances during outstanding capture, the provider SHALL retain bounded latest-revision demand and service it under the frozen pacing policy after eligible capacity returns, admitting none after closure or revocation.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P1.

Baseline mapping: ELM-ARC-015, ELM-REN-012, ELM-UI-017, ELM-TEA-004.

Existing work mapping: W03, W06.

Source proposals: FI-04.

Owner: Graphics lead. Verifier: Independent acceptance reviewer.

Guardrails: No forced allocation while backpressured/exhausted. Follow-up is a genuine new native-scoped request with its own original issued clock, not renewal of expired work. Control/retirement events are lossless. Pacing/refresh is frozen in the existing budget matrix before qualification; continuous change cannot create unbounded back-to-back capture. Latest revision is limited to native-tracked coverage, currently root-surface commits only; no subsurface/family fidelity expansion.

Tradeoffs: Additional protocol/evidence complexity must meet the frozen workload/resource budget. Reuse current modules and incrementally qualify changed paths.

Primary sources:

- <http://direction.bordeaux.inria.fr/~roussel/publications/2015-UIST-mouse-based-lagmeter.pdf>
- <https://docs.gtk.org/gdk3/class.FrameClock.html>
- <https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html>
- <https://gitlab.freedesktop.org/wayland/wayland-protocols/-/blob/main/stable/presentation-time/presentation-time.xml>
- <https://idl.cs.washington.edu/files/2007-AnimatedTransitions-InfoVis.pdf>
- <https://raw.githubusercontent.com/hyprwm/hyprutils/main/include/hyprutils/animation/AnimatedVariable.hpp>
- <https://webkitgtk.org/2026/09/16/webkitgtk-2.54-highlights.html>
- <https://www.cs.umd.edu/users/ben/papers/Shneiderman1983Direct.pdf>

#### Scenario: ELM-ADOPT-027 final-content-while-busy

- **GIVEN** one admitted capture and multiple newer same-source revisions while visible demand persists
- **WHEN** the first job terminates and capacity returns
- **THEN** bounded demand selects the latest valid revision without losing the final update or extending the first job deadline

#### Scenario: ELM-ADOPT-027 close-or-lock-before-followup

- **GIVEN** a pending latest-content update
- **WHEN** demand closes, lock/revocation occurs or source identity changes before admission
- **THEN** no unauthorized follow-up capture is admitted; existing jobs and cleanup obligations remain accounted

#### Scenario: ELM-ADOPT-027 continuous-change-and-final-revision

- **GIVEN** authorized visible demand, continuously changing tracked content and eventually available eligible capacity
- **WHEN** the provider runs and then content change stops
- **THEN** capture follows the frozen pacing policy, the final tracked revision is serviced when eligible, and presentation impact is measured under026 with no original deadline renewal

## ELM-ADOPT-028 — Source liveness and frame freshness are separate facts

WHEN an authorized preview is displayed, the shell SHALL distinguish source liveness, captured content revision and frame age, and SHALL NOT describe historical or stale pixels as current content.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P1.

Baseline mapping: ELM-REN-004, ELM-REN-014, ELM-UI-016, ELM-UX-006, ELM-UX-007.

Existing work mapping: W03, W06.

Source proposals: FI-05.

Owner: Graphics lead. Verifier: Independent acceptance reviewer.

Guardrails: Refine labels only after reviewing the frozen historical/live/unavailable policy; do not relabel stale pixels as current-live or alter original13 S09 assertions.

Tradeoffs: Additional protocol/evidence complexity must meet the frozen workload/resource budget. Reuse current modules and incrementally qualify changed paths.

Primary sources:

- <http://direction.bordeaux.inria.fr/~roussel/publications/2015-UIST-mouse-based-lagmeter.pdf>
- <https://docs.gtk.org/gdk3/class.FrameClock.html>
- <https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html>
- <https://gitlab.freedesktop.org/wayland/wayland-protocols/-/blob/main/stable/presentation-time/presentation-time.xml>
- <https://idl.cs.washington.edu/files/2007-AnimatedTransitions-InfoVis.pdf>
- <https://raw.githubusercontent.com/hyprwm/hyprutils/main/include/hyprutils/animation/AnimatedVariable.hpp>
- <https://webkitgtk.org/2026/09/16/webkitgtk-2.54-highlights.html>
- <https://www.cs.umd.edu/users/ben/papers/Shneiderman1983Direct.pdf>

#### Scenario: ELM-ADOPT-028 live-source-with-old-frame

- **GIVEN** a live source advances after its authorized frame was captured
- **WHEN** the old frame remains valid while a replacement is pending
- **THEN** source liveness and frame age/freshness are distinguished; no false current-content claim or target substitution is made

#### Scenario: ELM-ADOPT-028 revocation-or-minimize

- **GIVEN** a displayed frame and native source-state/lease update
- **WHEN** the source minimizes or lease revokes
- **THEN** the existing historical/unavailable policy and native revocation govern display before replacement; no revoked pixels remain eligible

## ELM-ADOPT-029 — Native keyboard entry and exit for the taskbar

WHEN the declared taskbar-focus binding is admitted, the native host SHALL enter a bounded keyboard scope on the current output and retain the prior eligible application identity for the frozen exit/fallback policy, keeping the binding inert while locked.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: existing-phase-P5; early-feasibility-only.

Baseline mapping: ELM-UX-023, ELM-UX-024, ELM-UI-011, ELM-UI-019.

Existing work mapping: W07.

Source proposals: UXA-02.

Owner: Desktop experience lead. Verifier: Independent acceptance reviewer.

Guardrails: This is native keyboard scope qualification, not a mandated permanent EXCLUSIVE mode or a new default shortcut. Declare which history changes are focus-only versus real accepted activation; do not override existing MRU policy.

Tradeoffs: Additional protocol/evidence complexity must meet the frozen workload/resource budget. Reuse current modules and incrementally qualify changed paths.

Ordering gate: preserve existing P5 keyboard qualification. Earlier feasibility investigation does not promote implementation into the immediate W07/P0 lane.

Primary sources:

- <https://arxiv.org/html/2609.17959>
- <https://developer.gnome.org/hig/guidelines/keyboard.html>
- <https://doc.qt.io/qt-6/qstyle.html>
- <https://docs.gtk.org/gtk4/method.Accessible.announce.html>
- <https://grouplab.cpsc.ucalgary.ca/grouplab/uploads/Publications/Publications/2007-PredictiveModelMenus.CHI.pdf>
- <https://help.gnome.org/users/gnome-help/stable/keyboard-nav.html.en>
- <https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-automation-element-propids>
- <https://raw.githubusercontent.com/GNOME/gnome-shell/main/js/ui/ctrlAltTab.js>
- <https://raw.githubusercontent.com/GNOME/gtk/gtk-3-24/gtk/gtkmenuitem.c>
- <https://raw.githubusercontent.com/GNOME/orca/main/src/orca/live_region_presenter.py>
- <https://raw.githubusercontent.com/KDE/plasma-desktop/master/applets/taskmanager/qml/Task.qml>
- <https://raw.githubusercontent.com/qt/qtbase/dev/src/widgets/styles/qwindowsstyle.cpp>
- <https://raw.githubusercontent.com/swaywm/wlr-protocols/master/unstable/wlr-layer-shell-unstable-v1.xml>
- <https://raw.githubusercontent.com/wmww/gtk-layer-shell/master/include/gtk-layer-shell.h>
- <https://support.microsoft.com/en-us/windows/keyboard-shortcuts-in-windows-dcc61a57-8ff0-cffe-9796-cb9706c75eec>
- <https://wayland.app/protocols/text-input-unstable-v3>
- <https://www.w3.org/TR/uievents/>
- <https://www.w3.org/WAI/ARIA/apg/patterns/menubar/>
- <https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/>

#### Scenario: ELM-ADOPT-029 enter-and-escape

- **GIVEN** an eligible application has focus and the taskbar is idle
- **WHEN** the declared conflict-resolved taskbar focus binding is invoked and then Escape ends the scope
- **THEN** native keyboard and AT focus enter the bar and return under the frozen policy, with no unintended activation-history change

#### Scenario: ELM-ADOPT-029 retired-source-output-or-lock

- **GIVEN** a bar keyboard scope whose prior application or output retires
- **WHEN** the scope exits or the session locks
- **THEN** no replacement incarnation or removed output receives stale focus; the frozen eligible fallback/lock policy applies and idle bar does not intercept application input

## ELM-ADOPT-030 — Versioned disabled-action navigation policy

WHEN a supported shell action becomes disabled, the shell SHALL retain its declared position, expose disabled state and any reason required by the frozen per-surface policy, and follow that navigation policy without dispatching it through pointer, keyboard or accessibility activation.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P1.

Baseline mapping: ELM-UI-011, ELM-UX-024, ELM-UX-025.

Existing work mapping: W07, W08.

Source proposals: UXA-05.

Owner: Desktop experience lead. Verifier: Independent acceptance reviewer.

Guardrails: GTK and Windows/APG differ. Freeze the chosen per-surface policy; no universal requirement to focus every disabled control. Preserve existing right-click24 amendment and unsupported-action semantics.

Tradeoffs: Additional protocol/evidence complexity must meet the frozen workload/resource budget. Reuse current modules and incrementally qualify changed paths.

Primary sources:

- <https://arxiv.org/html/2609.17959>
- <https://developer.gnome.org/hig/guidelines/keyboard.html>
- <https://doc.qt.io/qt-6/qstyle.html>
- <https://docs.gtk.org/gtk4/method.Accessible.announce.html>
- <https://grouplab.cpsc.ucalgary.ca/grouplab/uploads/Publications/Publications/2007-PredictiveModelMenus.CHI.pdf>
- <https://help.gnome.org/users/gnome-help/stable/keyboard-nav.html.en>
- <https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-automation-element-propids>
- <https://raw.githubusercontent.com/GNOME/gnome-shell/main/js/ui/ctrlAltTab.js>
- <https://raw.githubusercontent.com/GNOME/gtk/gtk-3-24/gtk/gtkmenuitem.c>
- <https://raw.githubusercontent.com/GNOME/orca/main/src/orca/live_region_presenter.py>
- <https://raw.githubusercontent.com/KDE/plasma-desktop/master/applets/taskmanager/qml/Task.qml>
- <https://raw.githubusercontent.com/qt/qtbase/dev/src/widgets/styles/qwindowsstyle.cpp>
- <https://raw.githubusercontent.com/swaywm/wlr-protocols/master/unstable/wlr-layer-shell-unstable-v1.xml>
- <https://raw.githubusercontent.com/wmww/gtk-layer-shell/master/include/gtk-layer-shell.h>
- <https://support.microsoft.com/en-us/windows/keyboard-shortcuts-in-windows-dcc61a57-8ff0-cffe-9796-cb9706c75eec>
- <https://wayland.app/protocols/text-input-unstable-v3>
- <https://www.w3.org/TR/uievents/>
- <https://www.w3.org/WAI/ARIA/apg/patterns/menubar/>
- <https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/>

#### Scenario: ELM-ADOPT-030 supported-disabled-action

- **GIVEN** a state change disables a supported menu action
- **WHEN** the user navigates with the declared per-surface policy
- **THEN** the action position remains stable, native AT exposes unavailable state and any reason required by the frozen per-surface policy, and attempted activation dispatches no effect

#### Scenario: ELM-ADOPT-030 all-disabled-and-focus-retirement

- **GIVEN** all menu actions are disabled or the focused action becomes disabled
- **WHEN** navigation, Enter/Space or Escape occurs
- **THEN** the frozen policy keeps focus and dismissal reachable without invoking a disabled action or trapping focus
