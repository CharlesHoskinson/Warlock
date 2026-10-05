# Sol-01: immutable state, replay, bounded history and refinement

Status: independent research draft; not consensus or release acceptance. Retrieved primary sources on 2026-10-05. The frozen manifest is observed at 09:30:58 UTC, repository head `7acf7a790b6e914ac902e75351da4a059155574f`. All local anchors below are relative to this packet's `inputs/`; current-design claims use only those snapshots. No implementation, configuration, GUI or acceptance campaign was changed.

## Current design and evidence limits

The appropriate adoption strategy is to strengthen existing immutable-controller contracts. A wholesale event-sourcing framework would duplicate authority and introduce disk work into interaction paths without demonstrated benefit. Modern TEA already supplies the useful separation: policy consumes explicit messages and returns state plus effect descriptions, while native systems establish whether effects happened.

`docs/elm-roadmap/ARCHITECTURE.md:45–118` and `ELM-PRACTICES.md:3–27` prescribe immutable models, typed messages, pure reducers, one authoritative snapshot, derived projections, narrow transport and native clocks. These are documented obligations, not blanket proofs of their implementation. `implementation/elm-catalog-input-integrated-gui-v814/src/Main.elm:24–64` actually wraps `Outputs.Model`, routes inputs through `Outputs.update`, registers effects, and interprets them as commands. Its `Process.sleep` timers are runtime effects; recording a timer message can reproduce policy but does not qualify the original native deadline. The W05 monotonic-clock qualification remains essential.

`src/OutputController.elm:18–36,75–80,150–193` retains controller state, topology, scoped batch correlation and explicit capacity flags. Its register path bounds pending batches, request count and serialized bytes; admission failure is explicit. Binding changes clear batch correlation. W01 already identifies historical-correlation hazards, so this report does not call that finding new or assert that v814 has solved every crossing. `src/Effects.elm:87–125` separately bounds unresolved operations; `src/Shell.elm:240–250` keeps issued correlation on Unknown and removes matching terminal entries. Immutable state does not imply unlimited history, nor does a bounded list establish safe retirement.

`src/BatchReplay.elm:19–60` is an actual worker reducing input rows through the controller; it also performs registration. Its permissive replay-envelope fallbacks (`[]`, null, empty kind) deserve an explicit distinction between rejected test input and a legitimate no-op. A repeatable output from an accidentally empty replay is weak evidence. The workplan's coupled W03 checkpoint is stronger: real compiled native output feeds Elm, and state plus ordered commands are compared. Separate pure, broker, native and GUI evidence must retain separate labels.

The durable Python boundary intentionally differs from Elm. `adapter/durable_ledger.py:1–15,90–149` calls the store an observation ledger, retains unresolved identities and watermarks, makes duplicates non-resubmittable, and performs file/directory synchronization around replacement. `adapter/recovery_journal.py:1–50,100–140` strictly validates historical schemas and uses a migration plan with source hashes. `adapter/retirement_ledger.py:205–267` coordinates release with admission history. `adapter/delivery_ledger.py:1–18,35–110` separates mutable delivery certificates from immutable release anchors, treats missing initialized files as failures, and explicitly says rename visibility alone is insufficient durability evidence. These are important implemented controls. They are not a proof of every interruption boundary or production storage latency.

`src/Taskbar.elm:14–28` derives groups from projection windows, scans family membership and accumulates ordered groups. This avoids another native truth store, but repeated scans and list appends merit measurement at realistic catalog sizes. No complexity observation alone justifies a new cache, lazy rendering, or a numeric threshold.

The packet preserves original 242 requirements/417 scenarios, S01–S16, the right-click amendment, all 13 native preview scenarios, restore38/recovery34, drag/resize52 and original deadlines. GUI509/native513 do not qualify the unfinished production provider519; native492's root monitor-plane route remains preview-ineligible. Primary GUI814 and toolkit391 are separate ABI lanes. Nothing here transfers acceptance among them or revives removed named-application repairs. C00–C06 remain conditional.

## Verified primary sources

These claims are narrow observations; applicability below is my proposed inference.

| ID | Direct primary source; year/version | Supporting observation | Limitation here |
|---|---|---|---|
| A1 | Evan Czaplicki, [Elm: Concurrent FRP for Functional GUIs](https://elm-lang.org/assets/papers/concurrent-frp.pdf), 2012, introduction and §2.1 | Expensive sequential updates delay following events; unchanged inputs can cause needless recomputation. | Historical Signal-based implementation; use its cost questions, not its runtime or API. |
| A2 | Abadi and Lamport, [The Existence of Refinement Mappings](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/abadi-existence.pdf), SRC report 1991; original LICS publication 1988, §§1,5 | Refinement relates permitted behaviors; auxiliary history may record past information without changing original behavior; internal steps can stutter. | The theorem has hypotheses. Sampled trace agreement is not its proof and supplies no hardware timing guarantee. |
| O1 | Elm authors, [The Elm Architecture](https://guide.elm-lang.org/architecture/), current official guide, undated | Model, update and view define the application architecture. | Educational description, not a distributed consistency protocol. |
| O2 | Redux maintainers, [Prerequisite Reducer Concepts](https://redux.js.org/usage/structuring-reducers/prerequisite-concepts), current docs, undated | Pure reducers avoid mutation, ambient timestamps/randomness and external side effects; time travel must not change the world. | JavaScript discipline is weaker than Elm typing; Redux need not be adopted. |
| O3 | Redux maintainers, [Deriving Data with Selectors](https://redux.js.org/usage/deriving-data-selectors), current docs, undated | Keep state minimal and derive values; memoization can avoid repeated computation when inputs are unchanged. | Cache identity/invalidation must match this shell's revision domains. |
| O4 | Elm core, [Array.elm](https://raw.githubusercontent.com/elm/core/1.0.5/src/Array.elm), pinned 1.0.5 source | Immutable arrays use a branching tree, trading copying per level against traversal depth. | Pinned source, not a new dependency recommendation; JSON serialization does not preserve sharing. |
| O5 | Immutable.js maintainers, [official v5 site](https://immutable-js.com/), current, undated | Persistent collections reuse unchanged parts of prior versions. | Marketing-level performance claims need local measurements; keeping old roots still retains reachable data. |
| O6 | SQLite authors, [Atomic Commit in SQLite](https://sqlite.org/atomiccommit.html), current technical design, undated, §§2,3.7,3.10 | Buffered/reordered writes require explicit synchronization; durable commit has material storage cost and hardware assumptions. | SQLite's algorithm does not prove this JSON ledger correct; replacing it with a database adds migration/maintenance costs. |
| X1 | Akka maintainers, [Event Sourcing](https://doc.akka.io/libraries/akka-core/current/typed/persistence.html), 2.10.23, event-handler/recovery sections | Recovery reconstructs state from persisted events; side effects in event handlers would execute again. | Current edition is BUSL-1.1, so do not count it as permissively licensed OSS adoption. Actor persistence semantics are not compositor receipts. |

O1–O6 supply more than three official OSS project sources, including direct pinned code. The maintained documentation endpoints were accessed directly; these observations do not establish independent release-recency audits of each project. A1/A2 are actual author-hosted academic texts, not search summaries.

## Prioritized draft proposals

### IMM-01 — Make replay inputs complete, versioned and effect-isolated (P0)

**Classification/mapping:** refinement of ELM-TEA-002/003, ELM-QA-006/007 and ELM-REV-007/012; W04 and W05, with W03 command-conformance dependency; S05. Primary support: O1, O2, X1. W03 already compares commands; that existing work is duplicate evidence rather than a new task.

**Requirement:** the replay artifact must identify initial state/checkpoint, ordered accepted messages, decoder rejections, native clock observations, source/tool/schema hashes and resulting ordered effect descriptions. A rejected replay envelope cannot silently count as a successful empty execution. Replay observes would-be commands without dispatching native mutations. Determinism concerns identical complete inputs under a pinned transition implementation, not different asynchronous histories.

**Implementation choice/cost:** extend existing workers and serializers instead of creating a second reducer. Stable canonical encoding and explicit reject rows cost fixture maintenance and log bytes. Injecting synthetic timestamps into reducers or re-running ports is rejected. Test instrumentation must not establish native order that production lacks.

**Validation:** replay frozen corpus twice and compare models and registered effect packets byte-for-byte; retain a malformed-envelope negative and a clock-input mutation; assert zero native mutation calls from the replay harness.

**EARS:** WHEN a reducer replay is evaluated, the verifier SHALL reproduce state and ordered effect descriptions from the same versioned initial state and complete sanitized message history, while rejecting invalid replay input explicitly and executing no native mutations.

- **Deterministic history:** GIVEN a valid checkpoint and ordered native observations including deadlines, WHEN the compiled reducer processes them twice, THEN every state and effect-description row is identical and no effect endpoint is invoked.
- **Malformed/racing clock input:** GIVEN a pending request and a replay envelope missing its clock-domain metadata, WHEN a late receipt is supplied through that envelope, THEN the fixture fails validation rather than becoming an empty success; with valid metadata the recorded event order decides the outcome without resetting the original deadline.

### IMM-02 — Bound retained history without deleting safety knowledge (P0)

**Classification/mapping:** refinement of ELM-ARC-014/015/016 and ELM-REV-011; W01/W02/W03/W10; S05/S09/S15. Primary support: A2, O4/O5. Existing runtime ledger bounds are duplicates; the incremental obligation is a complete retention/retirement argument across correlation, floors and unresolved records.

**Requirement:** distinguish live unresolved state, terminal deduplication results, replay floors, release proof, delivery acknowledgment and diagnostic history. Reclaim a record only when remaining authority metadata still refuses its expired identity and preserves outstanding Unknown/cleanup obligations. Retention pressure causes explicit admission refusal rather than inferred terminal outcomes. Diagnostic truncation must not alter authority records.

**Implementation choice/cost:** create a ownership/retention table and derive proof-safe compaction criteria for existing ledgers. A ring buffer is suitable for diagnostics, not unresolved requests. A single ever-growing history is rejected. Persistent sharing reduces copying but cannot make reachable old snapshots free; disk JSON copies are independent of Elm sharing.

**Validation:** extend the workplan's more-than-200-effects/restart fixture across configured capacities, retain Unknown and delayed cleanup, and submit identities below each preserved floor. Record live/retained items and bytes against the frozen contract, not invented limits.

**EARS:** WHEN retained records reach their configured bound, the authority SHALL reclaim only records whose safety obligations are preserved by retained proofs and replay floors, or explicitly refuse new admission while preserving unresolved and cleanup obligations.

- **Expired replay after compaction:** GIVEN a settled record with a validated reclaim criterion and retained replay floor, WHEN compaction completes and its original identity returns, THEN no mutation occurs and the identity receives its defined expired disposition.
- **Unknown plus late cleanup:** GIVEN capacity pressure, an Unknown request and a consumer fence still outstanding, WHEN diagnostics rotate and a matching late receipt arrives, THEN the authority retains/reconciles those obligations and does not free charged storage or invent Refused merely to create capacity.

### IMM-03 — Qualify coherent checkpoints and interrupted migration (P0)

**Classification/mapping:** refinement of ELM-ARC-010/014, ELM-REV-008/012 and ELM-QA-007; W01/W02/W09/W10; S05/S15. Primary support: O6 and X1. The existing atomic writes/migration plan are implemented duplicate mechanisms; their composition needs falsifiable qualification.

**Requirement:** a recovered checkpoint must bind its schema, authenticated lifetime, contiguous observation watermark, unresolved identities, floors and original deadline references coherently. It restores observation/reconciliation state, never an executable retry queue. A fresh scene snapshot cannot erase missing ordered control outcomes or turn uncertainty into commitment.

**Implementation choice/cost:** extend current migration and synchronization fixtures at each file-write, sync, rename and admission-removal boundary. The checkpoint can be a validated manifest over existing stores rather than one enormous file. Additional synchronous writes increase latency and failure modes; group commit or a database may be evaluated only after profiling and a separately reviewed durability contract.

**Validation:** inject interruption at named barriers, recover in a new process, and compare accepted checkpoint/floors with an independent pre/post-state oracle. Reject mixed versions/lifetimes and unfinished migrations. Preserve original recovery34 deadlines.

**EARS:** WHEN recovery installs a checkpoint, the authority SHALL validate its coherent schema, lifetime, watermark and retained obligations before effect admission, reconcile uncertain outcomes without replay, and preserve each original deadline.

- **Completed checkpoint:** GIVEN a synchronized checkpoint with Unknown and retired-request floors, WHEN the frontend restarts, THEN it receives coherent observation/reconciliation state and dispatches no old window mutation.
- **Interrupted migration:** GIVEN rename visibility but an unfinished synchronization/migration barrier, WHEN recovery observes a newer scene and a late old-binding receipt, THEN it completes the defined validated recovery or stays fail-closed; it does not mix owners, discard Unknown, or refresh the deadline.

### IMM-04 — Profile and constrain revision-bound derived caching (P1)

**Classification/mapping:** refinement of ELM-TEA-001, ELM-QA-021/022/023 and ELM-REV-020/021; W08/W09; S02/S05/S07/S14. Primary support: A1, O3/O4/O5. Minimal state and profiling before lazy rendering already exist; new draft specificity is cache dependency and retirement evidence.

**Requirement:** any adopted cache must derive exclusively from explicit source/query/policy revisions, invalidate on all relevant dependency changes, and retain no input/pixel authority after retirement. Optimize measured hotspots; do not turn a cache into another mutable taskbar model.

**Implementation choice/cost:** first instrument Taskbar.groups and projection/encoding separately; compare an identity-indexed family derivation with existing scans. Reuse unchanged immutable values where useful. Index memory and revision bookkeeping may outweigh savings at normal catalog sizes. Cache keys must include lifetime/incarnation, not application label or reused display position.

**Validation:** freeze workload/device/absolute/regression budgets under S02, compare uncached/cached outputs over the same replay corpus, and measure whole-tree memory, CPU, wakeups and latency with observer overhead recorded. Adoption is conditional on measured benefit within those budgets.

**EARS:** WHERE derived-state caching is enabled, the frontend SHALL return the same projection as uncached derivation for every accepted revision and invalidate cached results before using changed or retired dependencies.

- **Unchanged dependency:** GIVEN repeated pointer events and unchanged scene/query/policy revisions, WHEN the view derives taskbar groups, THEN output equals the uncached oracle and measured recomputation falls under the frozen workload comparison.
- **Identity reuse race:** GIVEN cached family state for a retired incarnation, WHEN an identical label appears under a new lifetime/incarnation during query change, THEN derivation and action eligibility use the new identities and no stale family or preview authority survives.

### IMM-05 — Publish an explicit state/command refinement map (P1)

**Classification/mapping:** refinement of ELM-QA-004/005/006, ELM-TEA-002 and ELM-REV-009; W03/W04/W10; S05/S09/S15/S16. Primary support: A2 and O2. Existing coupled W03 replay is substantial duplicate evidence; the draft adds a reviewable map and coverage boundaries rather than claiming a new proof.

**Requirement:** map concrete native/Elm state and externally significant commands to abstract model variables; mark internal stuttering, nonce equivalence, control order, clock assumptions and ghost-only history explicitly. Compare each transition, not just the final state. Do not quotient observable authentication identity or deadline differences away.

**Implementation choice/cost:** attach a small mapping specification and executable comparator to current replay. Mutation controls must change an observable obligation; observationally equivalent mutants need an explanation, not artificial expected failures. Full mechanized proof is deferred because maintaining the mapping and environmental assumptions already costs reviewer time.

**Validation:** retain exact named cases, seeds, concrete inputs/outputs and first mismatching transitions; include backend-only steps, reordered effects and resource-retirement races. Repeat current precise compiled mutants. Bounded exploration remains bounded evidence.

**EARS:** WHEN coupled replay is reported as conformance evidence, the verifier SHALL compare concrete state and ordered commands through a documented abstraction map and disclose stuttering, equivalence and environmental assumptions without substituting that evidence for native acceptance.

- **Backend stuttering:** GIVEN a broker-only housekeeping transition without an observable frontend change, WHEN coupled replay applies the declared map, THEN frontend state stutters while native resource accounting and eligible queued receipts remain checked.
- **Same final state, wrong effects:** GIVEN two executions ending in identical visible models, WHEN one reorders Cancel/Ack or retires storage before consumer completion, THEN transition/command/resource comparison fails at the first relevant step even though final-state equality passes.

## Deferred alternatives and remaining research

Defer frontend event sourcing, automatic undo of native actions, full-model time-travel UI, perpetual snapshot retention, cross-output controller replicas and global history deletion. They add privacy/storage/coordination costs and can replay irreversible window actions or confuse stale authority with historical display. Preserve a bounded sanitized diagnostic history separately from native durability. No credentials, private text or pixel payloads belong in it.

Defer framework replacement with Redux, Immutable.js or Akka: these sources explain patterns, not a need to import another state owner. Historical Elm Signals and JavaScript safety controllers are rejected. SQLite is a possible storage alternative only after measured need, schema/migration design and fault qualification; it is not an automatic correctness upgrade.

Unknowns requiring owner evidence are production catalog/event distributions, actual storage synchronization tails, the frozen numeric budget sheet, complete floor/archive retirement coverage, and which revisions invalidate every derived family field. The supplied snapshots cannot settle full GUI provider ownership, physical retirement, multi-output hardware, AT or IME behavior. All proposed implementation work remains unchecked. Independent initial review does not establish agreement; a later shared candidate matrix must record votes and dissent.
