# opus-02-typed-events: typed events, effect algebra, protocols, ordering, identities, ownership and cancellation

**Reviewer:** opus-02-typed-events (Claude Opus 5.5). This is an independent first-round draft, not consensus. Everything below is a draft proposal. No source, config or GUI action was taken.

**Path convention:** paths are relative to `docs/elm-roadmap/research/20261005-design-adoption/inputs/`. `v509/` stands for `implementation/elm-preview-shared-bridge-v509/`. The v509 Elm `src` is byte-identical to v814 for every module discussed here except `Popup`, `SurfaceRenderer` and the `Preview*` modules (checked against the source-manifest hashes).

**Inventory gap:** `source-manifest.json:1369` lists the component `elm-preview-elm-policy-v470`, but no v470 files exist under `inputs/`. Any v470-only decoders are outside this review.

---

## 1. Current-design findings

Findings are split into implemented behavior (what the frozen source does), obligations already in the baseline, and acceptance gaps.

### Implemented strengths

- **S1. The preview lane already uses a typed effect algebra.**
  - `PreviewLifecycle.Event` and `Command` are closed unions (`v509/src/PreviewLifecycle.elm:28-29`).
  - `Candidate` and `Accepted` are distinct wrappers, so a candidate cannot be used where an accepted frame is required (`:21-23`).
  - Commands are appended to an ordered list (`emit`, `:152-153`) and encoded as one ordered array (`:323-329`). This sidesteps the fact that `Cmd.batch` has no ordering guarantee.
  - Phantom identity domains with private constructors exist (`v509/src/PreviewIdentity.elm:7-24`).
- **S2. The native broker's types mirror those domains.** `Id<Domain>` covers Lifetime, Session, Request, Clock and the other domains (`implementation/elm-preview-producer-refusal-v517/src/preview_broker.hpp:15-21`). Its ownership handling is careful:
  - Buffer transfer is affine: `allocate` takes `std::unique_ptr&` and moves it only on success (`:200-206`).
  - Destruction is gated on `use_count()==1` (`:241, :246`).
  - Physical destruction happens before the cleanup proof (`:249-252`).
  - Acknowledgement must name the final proof (`:255-259`).
  - The v520 check proves that a cancel racing a refusal yields both terminal proofs and retires the ledger on the final sequence (`implementation/elm-preview-producer-refusal-qualification-v520/qa/check.py:23`).
- **S3. Cancellation semantics are already pinned in the frozen spec.** The spec covers cancel-before-commit and commit-before-cancel (`openspec/changes/elm-desktop-pivot/specs/elm-native-bridge/spec.md:151-169`), and Unknown is reconciled rather than retried (`:183-189`).

### Gaps in the window-effect / catalog lane (W04 territory)

- **G1. The boundary is untyped, and JSON is used as an internal reducer API.**
  - `Shell.Msg` carries `Incoming D.Value` (`v509/src/Shell.elm:33`), and `Shell.Effect` is `Send E.Value` (`:34`).
  - `Effects.apply` takes `D.Value` (`v509/src/Effects.elm:62`).
  - Internal callers hand-build JSON just to call that reducer: `Effects.elm:219`, `Shell.elm:64, 141, 186-188, 227, 237, 243`, `ReceiptRouter.elm:153`.
  - At `Shell.elm:143-144` an emitted intent is decoded and wrapped again.
  - This directly contradicts `docs/elm-roadmap/ELM-PRACTICES.md:21` ("do not use hand-built JSON as a child reducer API").
- **G2. One protocol frame has three decoders that disagree on vocabulary.**
  - An `effect-outcome` frame passes the Bool shape gate `NativeOutcome.valid` (`NativeOutcome.elm:49-53`), is partially re-decoded, is re-encoded as a different `"receipt"` schema, and is decoded again in `Effects.apply` (`Shell.elm:240-257`).
  - `NativeOutcome` (`:41-42`) and `ReceiptRouter` (`:133`) accept only Committed, Refused and Unknown.
  - `Effects.statusDecoder` also accepts `Cancelled` (`Effects.elm:44`). It also accepts a legacy receipt frame with no `effectProtocol`, defaulting it to 1 (`:105`).
  - `ReceiptRouter` redefines `Operation`, `Context` and `Intent`, and its `Operation` omits `Activate` (`ReceiptRouter.elm:18-21`).
  - The operation→protocol mapping exists three times: `Effects.elm:166-167`, `ReceiptRouter.elm:73`, `NativeOutcome.elm:31`.
  - There are four outcome vocabularies in total: `Effects.Status`; `Menu.Outcome` (Committed | Refusal String | Cancellation | Uncertain, `Menu.elm:148-152`); `Menu.Status`; and the broker's seven-value `Result::Status`.
  - ELM-ARC-007 requires Cancelled as a distinct state. On the protocol-3 path it is currently unreachable.
- **G3. Domain identities are imprecise.**
  - `Effects.Context` and `Intent` use bare `UInt64.Counter` for lifetime, epoch, output, revision, request, generation and incarnation (`Effects.elm:13-15`).
  - `Binding` is three positional Counters (`Binding.elm:7`). `matchesContext life epoch` compares the intent's `epoch` with the binding's `frontend` field by position (`:18-19`).
  - `Shell.request` (the projection request id) and `Effects.request` (the intent request id) are different counters of the same type (`Shell.elm:35`, `Effects.elm:17`).
  - In the preview lane, `PreviewIdentity.positive : D.Decoder (Identity domain)` is domain-polymorphic (`:26-27`). The domain is picked by type inference at the use site, so decoding field `"epoch"` into an `Output` slot would still typecheck.
  - In C++, `deadline` and `now` are raw `uint64_t` (`preview_broker.hpp:33, 37`), while Elm uses a `MonotonicTime` domain.
  - `docs/elm-roadmap/ARCHITECTURE.md:196` already requires distinct opaque types for these identities.
- **G4. Controller protocol state is spread across parallel booleans.**
  - `Shell.Model` has seven Bools and three `Maybe Counter` request slots (`Shell.elm:35`). `available` is a nine-way conjunction (`:67`).
  - Observation kinds are strings (`UnsentObservations (List (String,Counter))` at `:33`; matched at `:316-323`).
  - `ELM-PRACTICES.md:9` already says to use custom types rather than parallel booleans.

### Ordering, causality and ownership (W03/W06/W10)

- **G5. FIFO delivery of receipts is assumed, not established.**
  - The broker numbers proofs with one global counter (`preview_broker.hpp:76, 91-97`). The Elm reducer uses that `sequence` only to choose which proof to acknowledge (`PreviewLifecycle.elm:236-248`). It never checks the sequence for order, gaps or duplicates.
  - A duplicate terminal receipt re-emits `Acknowledge`. This is benign only because the broker rejects it (`preview_broker.hpp:258`).
  - The host says FIFO first delivery "remains an explicit qualification gate" (`v509/native/shared-host.c:132-133`).
  - The workplan records reliable per-frontend FIFO as an unproven transport obligation (`docs/elm-roadmap/delivery/FRP-ELM-WORKPLAN.md:133-135`). It also notes that native397 deliberately separated proof identity from FIFO delivery order (`:181`).
- **G6. Elm-side correctness quietly depends on native emission order.** On `Cancelled job`, the Elm handler drops every retiring packet for that job without a `Released` receipt (`PreviewLifecycle.elm:285-287`). This is safe only because the broker emits `Cancelled` after physical destruction (`preview_broker.hpp:249-252`). Nothing on the Elm side states or checks that dependency.
- **G7. Ownership is emulated without a global check.**
  - Packets move by hand between candidate, accepted and retiring; `heldHandle` checks local membership only (`PreviewLifecycle.elm:196-197`).
  - In C++, `Record` encodes its lifecycle as five independent bools (`preview_broker.hpp:69`). That makes combinations such as `terminal && !cleanup` representable.
  - The v516 Quint model encodes phase as `int` (`implementation/elm-preview-producer-refusal-policy-v516/spec/source.qnt:2, 7-10`), even though Quint supports sum types.

**Bottom line.** The preview lane already reflects what the literature recommends. The catalog/window-effect lane does not yet, and the cross-language contract (FIFO, identity domains, outcome vocabulary) is maintained by convention rather than by types or oracles.

---

## 2. Primary sources (all retrieved 2026-10-05)

| # | Source | Kind | Supporting claim used | Limitations |
|---|---|---|---|---|
| A1 | Fowler, *Model-View-Update-Communicate: Session Types meet the Elm Architecture*, ECOOP 2020 ([arXiv 1910.11108v3](https://arxiv.org/abs/1910.11108); [LIPIcs DOI](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ECOOP.2020.14)) | Academic | Session types need linearity. Embedding a linear endpoint in a GUI is unsound because a button can be pressed twice (§1, p.3). Encoding protocol states as one sum-typed model forces handlers for impossible states, and the handlers then cancel resources "to satisfy a code path that must exist, but should never be used" (§3.2, Fig. 7, p.14-15). *Model transitions* swap model/view/update per state (§3.3). Views take the unrestricted model via `extract`. `cancel` is "crucial… as all unprocessed messages (which may contain linear resources) must be safely discarded when a transition occurs" (§3.4, p.17). | Requires a linear type system (implemented in Links). Elm has neither linearity nor transitions, so the ideas can only be emulated with types plus runtime oracles. |
| A2 | Fowler, Lindley, Morris, Decova, *Exceptional Asynchronous Session Types*, PACMPL 3 (POPL 2019), [DOI 10.1145/3290341](https://dl.acm.org/doi/10.1145/3290341) ([author-hosted extended PDF](https://jgbm.github.io/pubs/fowler-popl2019-sessions-extended.pdf)) | Academic | Affine (silent-discard) endpoints mean "a developer receives no feedback if they accidentally forget to finish a protocol" and a peer "may be left waiting forever" (§1.3-1.4). Explicit `cancel` plus exceptions on cancelled peers keeps preservation, progress, the diamond property and termination under asynchronous communication. | Proof is for a core calculus. Native compositor resources, GPU fences and crash-stop failure are out of scope. |
| A3 | Mostrous and Vasconcelos, *Affine Sessions*, LMCS 14(4), 2018 ([lmcs 4973](https://lmcs.episciences.org/4973)) | Academic | Explicit cancellation gives error handling without losing progress ("sessions never get stuck"). | Synchronous process calculus (noted by A2). Read the abstract only. |
| A4 | Lamport, *Time, Clocks, and the Ordering of Events in a Distributed System*, CACM 21(7), 1978 ([PDF](https://lamport.azurewebsites.net/pubs/time-clocks.pdf)) | Academic | Happened-before is a partial order. "Messages may be received out of order" (fn. 2, p.559). The mutual-exclusion algorithm assumes per-pair FIFO and eventual delivery: "These assumptions can be avoided by introducing message numbers and message acknowledgment protocols" (p.561). | Logical clocks only. This design has one serialization point, so only per-channel order is needed, not a global total order. |
| O1 | elm/core 1.0.5 [`Platform/Cmd.elm`](https://raw.githubusercontent.com/elm/core/1.0.5/src/Platform/Cmd.elm); [Elm guide: ports](https://guide.elm-lang.org/interop/ports.html) | OSS code/docs | `batch`: "there are no ordering guarantees about the results." Ports are "about creating strong boundaries"; use "one or two ports to send messages back and forth." | The guide does not specify how port delivery is ordered against native callbacks. |
| O2 | Wayland protocol, [Appendix A](https://wayland.freedesktop.org/docs/html/apa.html) and [Protocol chapter](https://wayland.freedesktop.org/docs/book/Protocol.html) (freedesktop.org) | OSS official docs | `wl_display.sync` works as a barrier only because requests and events are handled in order. `delete_id` tells the client that the server no longer references an object, so the ID can be reused. `wl_buffer.release` returns storage ownership. Typed `enum` arguments and a per-object version inherited from its parent. | The GitLab raw XML was behind an access wall, so I used the official rendered appendix. Wayland's ordering comes from one socket per client. Here the path goes native → WebKit → JS → Elm. |
| O3 | Tokio 1.53.2, [`select!` cancellation safety](https://docs.rs/tokio/latest/tokio/macro.select.html) | OSS official docs | "If you have a future that has not yet completed, then it must be a no-op to drop that future and recreate it." Futures that are not cancel-safe lose progress when dropped. | Rust runtime semantics. Used here as a classification criterion, not a mechanism. |
| O4 | gRPC guides: [Deadlines](https://grpc.io/docs/guides/deadlines/), [Cancellation](https://grpc.io/docs/guides/cancellation/) | OSS official docs | Deadlines are converted to timeouts minus elapsed time, to avoid clock skew. The server auto-cancels and must stop work it spawned. Cancellation propagates forward; it does not roll back. | Cross-host design. This shell uses one native monotonic domain (ELM-REV-012), so the timeout conversion is a rejected alternative. |
| O5 | [LSP 3.17 specification](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/) | OSS official spec | "A request that got canceled still needs to return from the server and send a response back. It can not be left open / hanging." Cancellation has distinct error codes. Responses may be reordered only where correctness is unaffected. | Editor protocol with no resource ownership. |
| O6 | [Quint language manual](https://quint.sh/docs/lang) (page updated 2026-06-02) | OSS official docs | Sum types and `match` are supported. | The manual does not say whether `match` is checked for exhaustiveness. |

---

## 3. Prioritized adoption proposals

Each proposal states the requirement first, then non-normative implementation options. Performance effects are referred to the frozen budget contract: ELM-QA-021 and ELM-REV-020/021 (`specs/elm-performance/spec.md:5-83`). No numeric budget is proposed here. The measurement task for every proposal is: the performance owner measures the catalog refresh, switcher, minimized-preview and first-capture rows before and after the change, with QA observers disabled, and freezes any delta against the existing matrix.

### OPUS02-TE-04 (P0): explicit delivery order for control receipts, separate from proof identity

**Classification:** new obligation that refines an existing one. It extends ELM-ARC-010 and ELM-REV-008/009/010 from observation deltas to cleanup and effect receipts, and turns the FIFO gate (`shared-host.c:133`; workplan W03/W10) into a measurable check.

- **Sources:** A4 (message numbers plus acks replace a FIFO assumption), O2 (`sync` relies on in-order delivery), A2.
- **Why:** G5 and G6. Today the frontend cannot tell reordering, loss or duplication apart from ordinary interleaving, because proof sequences are global across entries. A frontend-visible gap therefore does not mean a lost receipt.
- **Requirement (EARS):** WHEN a control receipt arrives on an authenticated (binding, channel) stream, the frontend SHALL admit it only if its delivery ordinal is exactly one greater than the last admitted ordinal for that stream. IF a gap, duplicate or regression is detected, THEN the frontend SHALL withhold new acquisition and effect admission, emit no acknowledgement for unseen proofs, and request native reconciliation without replaying any operation.
- **Implementation options (non-normative):**
  - (a) The native adapter stamps a per-binding ordinal in the envelope. The proof `sequence` is kept unchanged for Ack.
  - (b) Prove FIFO end-to-end through the WebKit evaluate path and keep the current envelope.
  - Recommendation: (a). Option (b) has no ordinal to make a violation observable.
  - Rejected: vector clocks (there is one authority), and JS-side reordering (keeps native safety out of JS).
- **Costs:** an envelope field, schema version bump, Quint channel model, wire-compatibility replay. Bytes and latency are measured per the measurement task.
- **Fit:** layer it under W03/W10 before the production provider is installed in v509.
- **Validation:**
  - A Quint model with a lossy, reordering, duplicating channel. Named mutants: ignore a gap; ack a duplicate.
  - Compiled Elm replay comparing state and ordered commands.
  - Native adapter fault injection that drops or swaps one receipt, which must yield `NeedsReconciliation` plus `Reconcile`, no `Acquire`, and no `Acknowledge` naming an unseen proof.
  - The original 13 S09 scenarios rerun unchanged.

**Scenarios:**

- **Scenario: OPUS02-TE-04 reordered-cleanup**
  - GIVEN a retiring packet whose native record will emit Released (ordinal n) then Cancelled (ordinal n+1)
  - WHEN Cancelled arrives before Released
  - THEN the frontend withholds Cancelled, emits no Acknowledge and no Acquire, and requests reconciliation; the retiring packet stays recorded
- **Scenario: OPUS02-TE-04 duplicate-terminal (negative)**
  - GIVEN Refused for job J was admitted and acknowledged
  - WHEN the same Refused frame is delivered again
  - THEN state is unchanged, no second Acknowledge is emitted, and the duplicate is recorded as a transport diagnostic
- **Scenario: OPUS02-TE-04 cross-entry gap is not loss (race)**
  - GIVEN two popup entries sharing one broker
  - WHEN entry B's stream sees global proof sequences 7 and 9 because 8 belonged to entry A
  - THEN entry B's delivery ordinals are contiguous and no reconciliation is triggered

### OPUS02-TE-06 (P0): ownership conservation oracle (linearity emulated in Elm and native)

**Classification:** refines W03/W06 (01-02, 04-2), ELM-ARC-012, ELM-ARC-019 and task `P4-ELM-ARC-019`. New in that it adds a whole-system conservation check and an explicit C++ record state.

- **Sources:** A1 §3.4, A2 §1.3-1.4, A3, O3, O2 (`wl_buffer.release`, `delete_id`).
- **Why:** G7. Elm cannot enforce "exactly once". A1 and A2 show that silent discard is the failure mode, and explicit cancel is the fix. The frontend already emits explicit Cancel and Release, but no check covers every transition.
- **Requirement (EARS):** For every reducer step, the frontend SHALL preserve the invariant `held(before) = held(after) ⊎ released(step) ⊎ cancelled(step) ⊎ terminallyProven(step)` over lease handles and jobs. Here `terminallyProven` covers only the jobs named by an admitted native terminal receipt. WHERE a native record changes ownership state, the native broker SHALL use only legal transitions of a declared state set.
- **Implementation options (non-normative):**
  - Replay oracle: compute the multiset equation from the encoded model and the command list per step.
  - C++: replace the five bools at `preview_broker.hpp:69` with an enum or `std::variant` plus a transition table.
  - Quint: convert the v516 `phase:int` into a sum type (O6).
  - Rejected: porting the frontend to a linear-typed language (A1's Links). It breaks the pinned Elm release tuple.
- **Costs:** oracle code, C++ refactor needing sanitizer reruns and mutant requalification. Runtime effect is expected to be negligible but must be measured per the measurement task.
- **Fit:** extends the existing 402-style coupled oracle.
- **Validation:**
  - The oracle runs on all retained traces (70 + 60).
  - Mutants that delete one `emit (Release …)` or `emit (Cancel …)`, or drop retiring packets without a matching terminal, must be detected.
  - C++ compile-time or `static_assert` coverage of illegal states, plus sanitizer reruns.

**Scenarios:**

- **Scenario: OPUS02-TE-06 binding-replacement**
  - GIVEN capture, candidate and accepted resources under binding B1
  - WHEN Attach replaces B1 with B2
  - THEN every B1 resource is either Cancel/Release-emitted or still held, and no handle disappears without a command
- **Scenario: OPUS02-TE-06 offer-after-cancel race**
  - GIVEN Cancel(J) was emitted and the capture is Idle
  - WHEN an owned Offer for J arrives before Cancelled(J)
  - THEN Release is emitted for that packet and J stays known until its final receipt
- **Scenario: OPUS02-TE-06 illegal native state (negative)**
  - GIVEN a record with `terminal` set
  - WHEN a transition would clear `cleanup` or re-adopt a buffer
  - THEN the transition is rejected and charge is unchanged

### OPUS02-TE-01 (P1): decode once at the boundary; typed reducer inputs and typed outgoing intents

**Classification:** duplicate/refinement of W04 (02-02, 02-03), ELM-ARC-003/004, ELM-REV-034 and `ELM-PRACTICES.md:21`. It adds falsifiable structural checks; it adds no new behavior.

- **Sources:** A1 (typed `Msg`, commands as data), O1 (strong port boundaries).
- **Why:** G1 and G2. Re-encoding JSON inside the controller widens the accepted language (the legacy receipt frame), duplicates validation, and lets the two schemas drift apart.
- **Requirement (EARS):** The controller SHALL decode each inbound native frame exactly once into a closed typed frame union, and SHALL pass only typed values to child reducers. The interpreter SHALL be the only module that encodes outbound intents.
- **Implementation options (non-normative):**
  - `type NativeFrame = EffectOutcome … | ActionProjection … | HostUncertain …`.
  - `Effects.apply` takes typed inputs; `Shell.Effect` becomes a typed union and `Send E.Value` is removed.
  - The legacy receipt branch is retired only through a versioned change.
  - Rejected: generating Elm from a session-protocol language (§4).
- **Costs:** refactor along the W01/W02 paths; byte-identical wire replay is the gate.
- **Fit:** after W01/W02, as W04 already sequences it.
- **Validation:**
  - Differential wire replay is byte-identical.
  - Grep/AST check: zero `E.object` or `D.decodeValue` outside boundary modules.
  - Each frame fixture decodes once.
  - Foreign-binding and legacy-shape controls.

**Scenarios:**

- **Scenario: OPUS02-TE-01 legacy receipt shape (negative)**
  - GIVEN a protocol-3 controller
  - WHEN a receipt without `effectProtocol` arrives
  - THEN it is refused with a recorded reason, with no model change or effect
- **Scenario: OPUS02-TE-01 wire equivalence**
  - GIVEN the retained trace corpus
  - WHEN replayed through the typed boundary
  - THEN every emitted wire frame is byte-identical to the prior build's

### OPUS02-TE-02 (P1): one canonical outcome algebra and legal-transition relation

**Classification:** refines ELM-ARC-007, 008, 012 and 014, tasks P2-ELM-ARC-007/008, and W02/W04. New in that it requires a single vocabulary and declared per-protocol reachability.

- **Sources:** O5 (cancelled requests still return a terminal response with a distinct code), O4 (cancellation is forward-only), A2.
- **Why:** G2: four vocabularies, Cancelled unreachable on protocol 3, the protocol mapping in three places, and a duplicate `Operation` type that lacks `Activate`.
- **Requirement (EARS):**
  - The bridge SHALL define one outcome type with the legal transitions Pending→{Committed, Refused, Cancelled, Unknown} and Unknown→{Committed, Refused, Cancelled} only via an authenticated native outcome or reconciliation.
  - Committed, Refused and Cancelled SHALL be absorbing.
  - Each effect protocol version SHALL declare which outcomes it can emit.
  - IF a frame names an outcome its protocol does not declare, THEN it SHALL be refused.
- **Implementation options (non-normative):** one `Outcome` module consumed by Effects, ReceiptRouter and Menu, with UI wording derived from it. One `protocolOf : Operation -> EffectProtocol`.
- **Costs:** small; touches shared GUI paths.
- **Fit:** with TE-01.
- **Validation:**
  - Transition-table property tests.
  - Mutants: allow Committed→Cancelled; allow local Unknown→Pending.
  - Per-protocol reachability report for Cancelled.

**Scenarios:**

- **Scenario: OPUS02-TE-02 commit-before-cancel**
  - GIVEN restore Committed for (I, G)
  - WHEN a late Cancelled for (I, G) arrives
  - THEN state stays Committed and no rollback is claimed
- **Scenario: OPUS02-TE-02 undeclared outcome (negative)**
  - GIVEN protocol 1 does not declare Cancelled
  - WHEN a protocol-1 Cancelled frame arrives
  - THEN it is refused and the request stays Pending or Unknown

### OPUS02-TE-03 (P1): precise identity domains fixed at the decoder, across Elm and C++

**Classification:** duplicate/refinement of `ARCHITECTURE.md:196`, ELM-ARC-005, ELM-REV-007/012 and W04's "opaque identity domains". New in three ways: domain-fixed decoders, a compile-failure corpus, and a C++ clock domain.

- **Sources:** O2 (typed ids and per-object version inheritance), A4 (clocks are only comparable within their defined relation), A1.
- **Why:** G3. Swapped positional Counters typecheck today, and so do two `request` counters in different domains.
- **Requirement (EARS):** The bridge SHALL represent each authority identity as a distinct opaque type whose decoder fixes the domain. Native deadlines SHALL carry their clock identity. Comparisons across domains or clocks SHALL fail to compile.
- **Implementation options (non-normative):**
  - Monomorphic decoders such as `lifetimeDecoder : Decoder (Identity Lifetime)`.
  - A record-typed `Binding`.
  - C++ `Deadline{Id<Clock>, Id<MonotonicTime>}`.
- **Costs:** mechanical refactor. Whether `--optimize` unboxes single-constructor wrappers is a research unknown; measure it per the measurement task.
- **Fit:** with TE-01.
- **Validation:**
  - An expected-compile-failure corpus covering swapped Binding fields, an epoch compared with an output, and deadlines from two clocks compared with each other.
  - Byte-identical wire replay.
  - The above-2^53 fixtures from ELM-REV-007.

**Scenarios:**

- **Scenario: OPUS02-TE-03 swapped fields (negative)**
  - GIVEN a source edit passing `frontend` where `epoch` is expected
  - WHEN it is compiled
  - THEN compilation fails
- **Scenario: OPUS02-TE-03 cross-clock deadline (race)**
  - GIVEN a restart produces a fresh clock C2
  - WHEN a C1 deadline is evaluated against C2 time
  - THEN the work is invalidated rather than reinterpreted

### OPUS02-TE-05 (P2): typestate for the controller's observation/attach session

**Classification:** refines `ELM-PRACTICES.md:9` and ELM-ARC-017. New structural obligation for `Shell`.

- **Sources:** A1 §3.2-3.3 (sum-typed model states, transitions, `extract` → read-only projection).
- **Why:** G4. Nine-way conjunctions and string-keyed slots make impossible combinations representable, which is the "code path that must exist" problem A1 describes.
- **Requirement (EARS):** The controller SHALL represent each observation channel's protocol position as a closed union (for example `Idle | Awaiting (Identity Request) | Refused`), with typed channel kinds. Read-only projections SHALL be derived through a single extract function.
- **Implementation options (non-normative):** per-channel union types; enumerate and diff the reachable states of the current corpus first.
- **Costs:** moderate; it overlaps W01/W07 paths.
- **Fit:** deferred until W01/W07 integrate.
- **Validation:**
  - Reachable-versus-representable report.
  - Byte-identical replay.
  - A Quint session model with named illegal-state mutants.

**Scenarios:**

- **Scenario: OPUS02-TE-05 stale response**
  - GIVEN the projection channel is Awaiting R2
  - WHEN a response for R1 arrives
  - THEN state and effects are unchanged
- **Scenario: OPUS02-TE-05 unsent while attach pending (race)**
  - GIVEN geometry attach is Awaiting R5
  - WHEN an unsent certificate for R5 arrives alongside a projection response
  - THEN the attach returns to Idle with a pending re-request, and the projection is admitted only if it matches its own slot

---

## 4. Rejected or deferred alternatives

- **Rejected: Elm Signals, automatic replay of Unknown, and moving FIFO or ownership checks into JS.** These are excluded by scope.
- **Rejected: rewriting the frontend in Links or Rust to get static session typing (A1, A2).** It breaks the pinned Elm tuple and the release identity.
- **Rejected: relative-timeout deadline propagation as in gRPC (O4).** Absolute native monotonic deadlines with a clock identity keep the original deadlines intact.
- **Rejected: vector or Lamport total-order clocks.** With one serialization point, per-channel ordinals are enough.
- **Deferred: generating Elm decoders from a session or multiparty protocol language.** I did not verify that any maintained toolchain has an Elm backend.
- **Deferred: algebraic effect handlers.** Elm has none. Commands as data plus a small interpreter (`ELM-PRACTICES.md:15`) is the applicable form of an effect algebra.

## 5. Research unknowns

- Whether WebKit's evaluate-script path (`surface_eval`, `shared-host.c:145`) keeps native → Elm ordering under load. This has not been measured.
- Whether the absent v470 sources or the W01/W02 lanes (670/675/693) make `Cancelled` reachable for protocol 1/2.
- What single-constructor wrappers cost at runtime in Elm `--optimize`.
- Whether Quint `match` checks exhaustiveness (O6 is silent on this).
- How much ordinal stamping adds in bytes and latency. To be measured per the measurement task, not assumed.

**Status:** independent draft with no reviewer agreement implied. I'm ready to vote on the combined candidate matrix in round 2. Baseline 242/417, S01–S16, the 13 S09 scenarios, restore38/recovery34, the original deadlines and all implementation tasks remain open and unchanged.
