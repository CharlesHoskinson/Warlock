# elm-native-bridge — design adoption draft

## Purpose

Draft refinements for the existing in-flight `elm-native-bridge` capability. This change contains ADDED research contracts only; it does not create or archive a main spec, replace existing pivot/right-click deltas, or establish release acceptance.

Provisional research drafts awaiting ratification and a separate reviewed baseline amendment. These artifacts do not change the canonical 242 requirements/417 scenarios, S01–S16, right-click24, original13 native preview cases, restore38/recovery34/drag-resize52 or original deadlines. Native authority and no automatic replay of Unknown remain mandatory. C00–C06 compositor replacement remains conditional.

No new native, hardware, IME, AT or full-release evidence is supplied by this packet. Frozen component/model/CPU/compiled replay evidence is not production-provider or full GUI ownership/drain/fidelity acceptance. GUI814 and toolkit391 retain separate owning ABI pairs. Implementation and qualification tasks remain unchecked.

## ADDED Requirements

### Requirement: ELM-ADOPT-002 — Proof-safe bounded history retention and compaction

WHEN retained records reach their configured bound, the authority SHALL reclaim only records whose obligations remain protected by proofs and replay floors, or report distinct capacity refusal while preserving unresolved and cleanup obligations until proof-safe reclamation permits admission.

Status: draft-refinement-awaiting-ratification. Classification: draft-refinement; original research classification: refinement. Priority: P0.

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

#### Scenario: Expired replay after compaction

- **GIVEN** A settled reclaimable record and retained replay floor
- **WHEN** Compaction completes and its old identity returns
- **THEN** no mutation occurs; expired or retention disposition is distinct from definitive refusal of the original operation, and retained Unknown remains unchanged

#### Scenario: Unknown and late cleanup

- **GIVEN** Capacity pressure, Unknown request and outstanding consumer fence
- **WHEN** Diagnostics rotate and matching late receipt arrives
- **THEN** Unresolved/cleanup obligations remain reconciled and charged storage is not freed prematurely

### Requirement: ELM-ADOPT-006 — Complete typed internal boundaries

WHEN a validated external event enters an internal reducer, the controller SHALL carry domain-specific typed identities and outcomes through its resulting effect descriptions until wire encoding.

Status: draft-refinement-awaiting-ratification. Classification: draft-refinement; original research classification: refinement. Priority: P0.

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

#### Scenario: Exact receipt

- **GIVEN** a validated receipt for one request/incarnation
- **WHEN** the typed outcome is reduced
- **THEN** only the exact transaction settles and wire encoding remains unchanged

#### Scenario: Foreign input

- **GIVEN** a malformed, untrusted or unauthorized payload that fails boundary admission
- **WHEN** boundary validation runs
- **THEN** no admitted event, native mutation or transaction settlement is produced; only a bounded allowlisted rejection diagnostic is retained, with no fabricated Refused outcome

#### Scenario: authenticated-historical-reconciliation

- **GIVEN** an exact authenticated historical receipt for a retained obligation and its declared reconciliation route
- **WHEN** it arrives after frontend replacement
- **THEN** only the historical obligation may settle; the receipt grants no authority to the replacement binding and renews no deadline

### Requirement: ELM-ADOPT-007 — Preserve effects as an auditable dependency algebra

WHEN a native effect depends on a prerequisite, the controller SHALL admit its request only after matching authenticated evidence satisfies that operation's protocol-specific prerequisite, while native authority revalidates the dependency at commit.

Status: draft-refinement-awaiting-ratification. Classification: draft-refinement; original research classification: refinement. Priority: P0.

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

#### Scenario: Pending prerequisite

- **GIVEN** restore-before-activate dependency for an exact incarnation
- **WHEN** restore remains Pending then its exact committed receipt arrives
- **THEN** activation waits then registered activation can proceed

#### Scenario: Wrong prerequisite

- **GIVEN** a refused restore or foreign committed receipt
- **WHEN** it arrives before activation
- **THEN** it cannot satisfy the prerequisite and independent controls remain usable

### Requirement: ELM-ADOPT-008 — Publish one conversation contract with local obligations

WHEN a protocol event is received, each participant SHALL admit it only under the declared actor-specific transitions, version and outcome reachability with exact correlation; otherwise it SHALL reject it without authority, ownership or settlement effect and retain a bounded rejection diagnostic.

Status: draft-refinement-awaiting-ratification. Classification: draft-refinement; original research classification: refinement. Priority: P1.

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

#### Scenario: Unadopted refusal

- **GIVEN** an admitted reservation without storage
- **WHEN** the trusted producer refuses
- **THEN** stable refusal proof preserves already-ordered cancellation proof

#### Scenario: Illegal retirement

- **GIVEN** an adopted buffer or stale actor
- **WHEN** producer-refused or final-ack is supplied
- **THEN** it cannot bypass drainage or retire current actor resource

### Requirement: ELM-ADOPT-009 — Treat cancellation as a request followed by proved closure

WHILE a resource or reservation is owned, the native broker SHALL account for its admission, transfer and cleanup until matching native completion permits retirement; cancellation or release intent alone SHALL NOT erase ownership, charge or cleanup obligations.

Status: draft-refinement-awaiting-ratification. Classification: draft-refinement; original research classification: refinement. Priority: P0.

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

#### Scenario: Cancel refusal race

- **GIVEN** capture cancelled before adoption
- **WHEN** refusal completes asynchronously
- **THEN** ordered cancellation/refusal proofs leave no reservation after final ack

#### Scenario: Held reader

- **GIVEN** adopted buffer with held GIO reader
- **WHEN** cancel and shutdown occur
- **THEN** fetch revoked immediately and terminal release waits for producer completion and reader drainage

### Requirement: ELM-ADOPT-010 — Separate causal order, epoch identity and deadline time

WHEN queueing, frontend replacement or reconciliation occurs, the authority SHALL preserve the operation's original native clock domain, time origin and deadline while validating ordered control delivery independently of observation revisions.

Status: draft-refinement-awaiting-ratification. Classification: draft-refinement; original research classification: refinement. Priority: P1.

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

#### Scenario: Restart receipt

- **GIVEN** pending work and frontend restart
- **WHEN** exact late receipt arrives
- **THEN** original request reconciles without deadline renewal or mutation replay

#### Scenario: Gap clock

- **GIVEN** control sequence gap or replaced clock domain
- **WHEN** later delta/timeout arrives
- **THEN** new admission withheld until coherent reconciliation and invalid timing cannot authorize work

### Requirement: ELM-ADOPT-022 — Demand scheduling with bounded control liveness

WHILE preview or observation demand exceeds admitted capacity, the bridge SHALL coalesce only replaceable observations within their identity domain, refuse unadmitted effects explicitly and preserve ordered cancellation, receipts and retirement capacity.

Status: draft-refinement-awaiting-ratification. Classification: draft-refinement; original research classification: refinement. Priority: P0.

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

#### Scenario: Observation storm with cancellation

- **GIVEN** preview queues are saturated within frozen byte and item bounds
- **WHEN** new observations and a cancellation arrive
- **THEN** only semantically replaceable observations coalesce; cancellation and all retirement receipts remain deliverable in order

#### Scenario: Close during producer reservation

- **GIVEN** a producer owns a reservation and the picker closes
- **WHEN** a late producer result arrives
- **THEN** the closed demand remains cancelled and its existing owner/cleanup stays recorded; another authorized demand may use only independently available eligible capacity, never the held reservation before matching release

### Requirement: ELM-ADOPT-025 — Control delivery continuity distinct from proof identity

WHEN authenticated control receipts are delivered, the bridge SHALL preserve their required per-channel causal order, detect gaps or regressions under the declared transport contract, reconcile uncertainty and keep repeated proofs idempotent without acknowledging unseen cleanup.

Status: draft-refinement-awaiting-ratification. Classification: draft-refinement; original research classification: refinement. Priority: P0.

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

#### Scenario: reordered-cleanup

- **GIVEN** Released and racing Cancelled proofs for a still-held job
- **WHEN** the later control event overtakes its prerequisite
- **THEN** no unseen proof is acknowledged and no ownership is forgotten; the declared gap/reconciliation policy preserves cleanup

#### Scenario: cross-entry-proof-and-retry

- **GIVEN** global proof IDs interleave across entries and a valid final Ack is lost
- **WHEN** a stable proof repeats on the authenticated delivery stream
- **THEN** it does not create a false gap or duplicate physical cleanup; the declared idempotent acknowledgement/reconciliation policy can finish retirement
