# sol-02: Typed events, effects, causality and ownership

Independent research draft, retrieved 2026-10-05. This is neither implementation authorization nor release acceptance. Reviewed `INVENTORY.md`, the hash/byte inventory in `source-manifest.json`, and frozen `inputs/` sources. All paths below are relative to that frozen directory. Preserve original 242 requirements/417 scenarios, S01–S16, the right-click amendment, 13 native preview scenarios, restore38/recovery34/drag-resize52, and original deadlines. Conditional C00–C06 remain conditional. Generic application compatibility remains; removed named application repair targets are not reinstated.

## Current design findings

The strongest existing design is the preview subsystem, not a missing session-typing framework. `implementation/elm-preview-shared-bridge-v509/src/PreviewIdentity.elm:7–42` gives private phantom-domain wrappers for lifetime, session, frontend, incarnation, output, revisions, observation, receipt, clock, request, origin and monotonic time. Canonical lossless uint64 strings remain the wire representation. `PreviewLifecycle.elm:11–30` separates demand, connection, capture, accepted ownership, cancelling jobs and retiring packets; its typed `Command` algebra distinguishes Acquire, Cancel, Release, Reconcile and Acknowledge. `eventDecoder` at lines 112–123 restricts receipt bodies to terminal cleanup events and rejects bare terminal events. Crucially, the provenance comment explicitly says JSON does not grant native retirement authority.

This is partial adoption of the desired discipline. `Main.elm:18–30` still transports six raw `D.Value` message variants; `Desktop.elm:46–63` includes raw Incoming/OwnerScope and `Send E.Value`; `SurfaceController.elm:18–19` and `OutputController.elm:33` retain raw renderer/topology/disposition payloads. `Effects.elm:10–17` defines custom operations/statuses but gives request, generation, incarnation, output, epoch and revision the same `UInt64.Counter` type. Its `apply` function also decodes JSON internally. Therefore “typed ports” and “typed generic effects” should not be counted complete merely because Elm compiles. Runtime malformed-input checks exist; domain interchange and internal construction errors remain a separate concern.

`Main.commit:32–41` batches an atomic commit with Elm Process.sleep feedback timers. That does not prove a dependent-effect ordering defect: the native packet may express its own atomic dependencies. It does prove that reviewers must inspect the packet/register protocol rather than infer ordering from a list or `Cmd.batch`. Those frontend delays also must not become authoritative operation clocks. Existing `Effects.apply:107–127` performs exact intent/protocol matching and turns uncertain pending work into Unknown on disconnect; `blocked:170` blocks Pending/Unknown per lifetime/incarnation. Preserve this reconciliation policy.

Native ownership is unusually explicit in `implementation/elm-preview-producer-refusal-v517/src/preview_broker.hpp:210–264`: producer refusal applies only before buffer adoption, racing cancellation preserves its proof, consumer completion requires drainage, physical destruction precedes cleanup proof, and acknowledgement requires the final receipt sequence. These are runtime obligations, not linear guarantees supplied by Elm. Source-level and bounded-model evidence supports this component design; inventory explicitly withholds acceptance of production provider integration, real family/decor/modal/subsurface fidelity and full GUI drain. Native513 fallback/coexistence is not production image ownership qualification. GUI814/toolkit391 are separate ABI lanes and must never be cross-loaded.

## Verified primary sources

Each linked source was opened directly, not inferred from a search summary. Versions below describe retrieved documents, not locally installed dependencies. Source claims are deliberately narrow; adoption is this reviewer's inference.

| ID | Primary source, title/year and direct link | Supporting claim and precise locus | Limits |
|---|---|---|---|
| A1 | Simon Fowler, *Model-View-Update-Communicate: Session Types meet the Elm Architecture*, 2019/2020, [extended paper](https://arxiv.org/pdf/1910.11108) | §§1, 3.3–3.4: GUI callbacks can duplicate endpoint use; commands, linearity, model transitions and unrestricted view extraction enable a formal session-typed MVU integration; transitions address stale messages. | Implemented in Links with a linear system. Its soundness theorem does not transfer to Elm, native C++, JSON or this shell. |
| A2 | Honda, Yoshida, Carbone, *Multiparty Asynchronous Session Types*, POPL 2008, [author-hosted paper](https://www.doc.ic.ac.uk/~yoshida/multiparty/multiparty.pdf) | §§1–3: global conversations project to participant protocols; per-channel order does not establish order between distinct senders; causal dependencies matter. | Calculus assumptions and well-typed participants are not automatically satisfied by transport adapters or crash recovery. |
| A3 | Leslie Lamport, *Time, Clocks, and the Ordering of Events in a Distributed System*, 1978, [primary paper](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/12/Time-Clocks-and-the-Ordering-of-Events-in-a-Distributed-System.pdf) | Definition of happens-before and logical-clock condition: causal order is partial; scalar order alone does not establish physical timing or reverse causation. | Does not define this project's admission/retirement protocol; monotonic deadline clocks remain native. |
| O1 | Elm core, *Platform.Cmd*, current maintained source, [official code](https://raw.githubusercontent.com/elm/core/master/src/Platform/Cmd.elm) | Lines 30–36, 52–55: commands describe effects and result message types; batched command results have no ordering guarantee. | A Cmd type alone does not preserve child effect descriptions or authenticate receipts. No recommendation to use Signals. |
| O2 | Wayland, *Protocol Specification: wl_buffer*, maintained official specification, [buffer section](https://wayland.freedesktop.org/docs/html/apa.html#protocol-spec-wl_buffer) | wl_buffer.destroy/release distinguish destroying a protocol object, factory-defined backing storage and compositor no-longer-use notification. | A wl_buffer release does not by itself prove this broker's producer fence, GIO reader drain or actual physical presentation. |
| O3 | GLib/GIO, *Cancellable.cancel*, API 2.0/library 2.90.0 documentation, [official docs](https://docs.gtk.org/gio/method.Cancellable.cancel.html) | Cancellation is thread-safe; asynchronous cancellation completion returns through the main loop, rather than necessarily during cancel(). | Cancellation intent is not stream closure or producer drain; locally installed GLib version must be pinned later. |
| O4 | GLib/GIO, *InputStream.close_async*, same retrieved documentation, [official docs](https://docs.gtk.org/gio/method.InputStream.close_async.html) | Callback reports asynchronous completion; close_finish obtains its result. | Stream close can be only one ownership edge, not proof that GPU/native producer stopped. |
| O5 | Tokio 1.53.2, *JoinHandle*, maintained library documentation, [official API](https://docs.rs/tokio/latest/tokio/task/struct.JoinHandle.html) | Dropping a handle detaches work; abort may race completion, and task termination must be observed; started spawn_blocking work cannot generally be aborted. | Comparative protocol evidence only; no proposal to migrate this Python/C++ host to Rust/Tokio. |

## Prioritized adoption drafts

### TE-01 — Complete typed internal boundaries (P0)

**Mapping/classification:** refinement of ELM-TEA-001/002/003, ELM-REV-007, and W04, coordinated with W01/W02. Already largely implemented for preview; not a new user-visible feature. **Sources:** O1, A1. **Requirement:** once external input is validated, internal reducers and outgoing descriptions must preserve its domain meaning without unvalidated JSON reconstruction. **Implementation choice:** decode at the boundary into private event/admission/outcome custom types, retain JSON only for wire codecs and inspections, and extend the existing identity wrapper technique to generic effects. Phantom types prevent accidental interchange after decode but cannot detect a malicious sender putting a valid string in the wrong field; native binding/context validation remains mandatory.

This gives compiler assistance where generic Counters currently permit swaps and makes invalid construction easier to localize. Keeping raw JSON everywhere with exhaustive decoder tests is cheaper initially but leaves internal errors runtime-only. A universal giant event type would centralize everything at the cost of coupling independent domains; prefer narrow module-owned types. Incremental cost is codec/replay churn and call-site migration. Preserve wire bytes first, migrate one module at a time, and requalify affected native assets.

**Measurable validation:** compile-negative fixtures for request/output, clock/deadline and lifetime/incarnation interchange; unchanged canonical encodings at uint64 boundaries; byte-identical state/effect differential replay; malformed/extra/missing/numeric-field and foreign-binding controls produce unchanged authoritative state and no mutation commands. Counter-domain errors should fail construction, not merely later decoder tests.

**EARS:** WHEN a validated external event enters an internal reducer, the controller SHALL carry domain-specific typed identities and outcomes through its resulting effect descriptions until wire encoding.

**OpenSpec scenarios:**

- GIVEN a validated activation receipt for one request and incarnation, WHEN its typed outcome is reduced, THEN only its exact transaction settles and its original wire encoding remains unchanged.
- GIVEN a malformed or foreign-binding payload, WHEN boundary validation runs, THEN no internal admitted event or native mutation is produced and a correlated refusal/diagnostic is retained.

### TE-02 — Preserve effects as an auditable dependency algebra (P0)

**Mapping/classification:** refinement of ELM-TEA-002/003 and W04; dependencies on W01/W02/W09. **Sources:** O1, A2, A3. **Requirement:** every native request implied by a transition must remain linked to an emitted/registered request, and dependent work must await its actual prerequisite acknowledgement. **Implementation choice:** retain data-level child effects through controller composition, encode explicit prerequisite identities for dependent work, and interpret only at the narrow outer boundary. This need not introduce a free-monad package or a new framework; existing lists/custom constructors are sufficient if their semantics are explicit.

The benefit is detecting lost effects during nesting, filtering or batching. “Order the list” is an inadequate alternative; serialized native packets are acceptable if they enforce the same dependency relation and give receipts. A total order of all effects would simplify some tests but block unrelated controls unnecessarily. Costs are explicit dependency metadata, replay-oracle updates and a small number of native admission controls, not wholesale UI rewriting.

**Measurable validation:** compare expected reducer request identities to registered/emitted identities; inject omission, duplication and swapped prerequisite mutants. Delayed, refused and foreign committed receipts must never unlock the dependent command. Independent operations must still progress. Measure interpreter/metadata overhead under the existing frozen performance/resource contract; do not invent a new latency allowance.

**EARS:** WHEN a native effect depends on another effect's completion, the controller SHALL admit the dependent request only after the matching native committed receipt satisfies the recorded prerequisite.

**OpenSpec scenarios:**

- GIVEN restore-before-activate dependency for an exact incarnation, WHEN restore remains Pending, THEN activation is not dispatched; WHEN its exact committed receipt arrives, THEN the registered activation can proceed.
- GIVEN a refused restore or a committed receipt from another frontend/request, WHEN it arrives before activation, THEN it cannot satisfy the prerequisite and independent controls remain usable.

### TE-03 — Publish one conversation contract with local obligations (P1)

**Mapping/classification:** refinement of W03/W04/W06 and ELM-TEA-001, ELM-ARC-012/014, ELM-REV-008/009/011. The cross-language conformance artifact is a new verification deliverable, not new accepted behavior. **Sources:** A1/A2. **Requirement:** controller, transport, producer, consumer and authority must agree on legal state/event/outcome transitions, including which actor may emit each proof. **Implementation choice:** a reviewed transition table/global protocol plus projections into module obligations; maintain manual codecs initially. State plainly that these are session-type-inspired contracts, not static session typing in Elm.

The preview protocol already provides the difficult branches: admission, refusal before adoption, offer/fence, cancellation, revocation, drain, release and final acknowledgement. The missing review aid is a coherent map across these implementations and recovery. Independent binary interface documents obscure multiparty drainage dependencies. Full generated session-typed code is deferred because the toolchain and linearity assumptions do not match current Elm. Costs include maintaining the table and conformant fixtures; start with preview then generic effects.

**Measurable validation:** each legal transition has an actual compiled Elm/native witness; each forbidden actor/message/state combination has a negative fixture. Include receipt duplication, final-ack-before-release, actor replacement and refusal-after-adoption. Bind table version, source hashes and ABI pair to reports. Bounded Quint checks remain model evidence; full native integration remains a separate gate.

**EARS:** WHEN a protocol participant receives a control message, the system SHALL validate its actor, exact conversation identity and permitted transition before producing authority or ownership effects.

**OpenSpec scenarios:**

- GIVEN an admitted reservation without adopted storage, WHEN the trusted producer refuses, THEN the conversation emits its stable refusal proof and preserves any already-ordered cancellation proof.
- GIVEN an adopted buffer or a stale actor, WHEN a producer-refused or final-ack message is supplied, THEN it cannot bypass consumer drainage or retire the current actor's resource.

### TE-04 — Treat cancellation as a request followed by proved closure (P0)

**Mapping/classification:** refinement of ELM-ARC-012/016, ELM-REV-010 and W03/W06/W10. **Sources:** O2–O5. **Requirement:** invalidate publication/admission immediately where required, retain ownership accounting until physical producer/consumer closure is proved, and distinguish cancel-before-commit from commit-before-cancel. **Implementation choice:** keep cancellation requested, authority decision, drainage and terminal receipt as separate protocol stages; continue using the existing native ownership ledger and exact receipts. Never move this safety policy to JavaScript or equate img.onload with presentation/closure.

Existing broker517 implements important parts; the adoption work is production-provider integration and shutdown/recovery conformance. Releasing records when cancellation is sent is cheaper but unsafe with asynchronous callbacks. Waiting for every unrelated task globally is unnecessarily restrictive; drain the owned generation. Costs are retained records, native callback coordination and reserved control transport. Backpressure must not consume cancellation capacity.

**Measurable validation:** actual production-path race controls for close/offer, cancel/producer refusal, lock/fetch and restart/drain; producer and reader holds prevent final receipt, drained ownership permits it, duplicate receipts are idempotent, and final ack frees only the exact record. Verify native allocations/FDs/readers/process census under original operation deadlines and frozen budget contract. The unfinished provider519 cannot supply passing evidence.

**EARS:** WHEN cancellation invalidates an owned operation, the native authority SHALL reject subsequent unauthorized publication and retain its ownership record until matching physical retirement proof permits final acknowledgement.

**OpenSpec scenarios:**

- GIVEN a capture cancelled before producer adoption, WHEN refusal completes asynchronously, THEN cancellation/refusal proofs preserve that ordering and no buffer or reservation remains after final acknowledgement.
- GIVEN an adopted buffer with a held GIO reader, WHEN cancellation and frontend shutdown occur, THEN fetch is revoked immediately but terminal release is withheld until native producer completion and reader drainage are proved.

### TE-05 — Separate causal order, epoch identity and deadline time (P1)

**Mapping/classification:** refinement of ELM-REV-007/008/009/012, ELM-ARC-013/014 and W01/W02/W05. **Sources:** A3, O1. **Requirement:** receipt/control sequence order, source revisions, binding epochs and native monotonic deadline values must never be substituted for one another. **Implementation choice:** explicit clock-domain/epoch wrappers, contiguous control watermark and deadline origin carried from original input; frontend timers provide feedback only. Existing sequence-gap and Unknown rules remain unchanged.

No vector-clock system is needed for the single native authority. A blanket global scene freshness requirement can also starve valid target actions; preserve the existing target-dependency revalidation requirement. Costs are boundary metadata and clock/queue instrumentation. Native clock pinning and actual source ordering need measurement, not academic assumptions.

**Measurable validation:** queue delay, stalled frontend, reconnect, sequence gap and stale-clock tests; original deadline and time origin remain byte-identical; late exact receipt reconciles Unknown without automatic replay. Freeze observed installed clock/API behavior and budget measurement method before implementation acceptance, preserving recovery case34's independent oracle.

**EARS:** WHEN queueing, frontend replacement or reconciliation occurs, the authority SHALL preserve the operation's original native clock domain, time origin and deadline while validating ordered control delivery independently of observation revisions.

**OpenSpec scenarios:**

- GIVEN pending work and a frontend restart, WHEN the exact late receipt arrives, THEN it reconciles the original request without renewing its deadline or replaying its mutation.
- GIVEN a control sequence gap or a clock from a replaced domain, WHEN a later delta/timeout is received, THEN new effect admission is withheld until coherent reconciliation, and the invalid timing value cannot authorize work.

## Deferred alternatives and research unknowns

Reject historical Elm Signals, automatic replay of Unknown, JavaScript resource authority, treating phantom domains as cryptographic provenance, and treating a model's “Released” label as physical retirement. Defer Links migration, Rust rewrite, generated multiparty endpoint libraries and pervasive type-level typestate: none is justified by incremental benefit over the established controller/native split. Keep desired UI state and read-only projections free of owned endpoints; native runtime single-ownership enforcement complements ordinary Elm types.

Unknowns needing implementation evidence are production-provider callback ordering, installed GIO/WebKit semantics, reader drainage across actor replacement, clock-domain reset policy, and transport behavior when reserved receipt capacity exhausts. Academic progress proofs assume semantics this host has not demonstrated. Budget values and original deadlines must come from the frozen contract and original scenario ledger; measure queue bytes/items, record high-water marks, callback/retirement latency, allocation/FD/process closure and native timing with pinned artifacts. No prototype bound becomes a release budget by repetition. These five drafts leave all implementation tasks unchecked and await the shared candidate matrix, explicit reviewer votes and dissent; independent initial agreement is not unanimous consensus.
