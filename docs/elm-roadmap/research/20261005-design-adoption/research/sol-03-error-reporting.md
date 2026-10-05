# sol-03-error-reporting: failure, uncertainty, recovery and diagnostics

Status: independent research draft; not adopted requirements, release acceptance or consensus. Retrieved sources on 2026-10-05. Scope is the frozen manifest at head `7acf7a790b6e914ac902e75351da4a059155574f`, not a claim about subsequently changed working files. No implementation, configuration, GUI campaign or live crash inspection was performed.

## Current design findings

The most important distinction already exists: a failed request and an unconfirmed request are different facts. In `inputs/implementation/elm-preview-shared-bridge-v509/src/Effects.elm:11`, `Status` includes Pending, Committed, Refused, Cancelled and Unknown. The disconnect branch at line127 converts pending transactions to Unknown. The blocked predicate at line170 excludes further effects on the affected lifetime/incarnation while Pending or Unknown is unresolved. The local unsent certificate path at lines190-205 is materially different from inferring refusal from a transport failure. Preserve this distinction in visible text, telemetry and exported evidence.

`src/Shell.elm:68-86` already renders different notices for uncertainty, refusal, exhausted recovery history and unavailable transport; releasing a reconciled reservation explicitly says the previous request remains unconfirmed and invites a new action. This is better than silently retrying. However, plain notice strings and decoder error strings appear in reducers; examining these files does not establish a uniform structured reporting taxonomy, content review, bounded diagnostic schema or accessible announcement coverage. These are acceptance gaps or candidate refinements, not evidence that the native effect protocol is unsound.

`src/ReconciliationTracking.elm`, functions `unknown`, `announce`, `observed` and `release`, stores historical reservations and requires both accepted action and geometry observations plus a matching proof. It rejects released history, uncorrelated proofs and unsupported legacy origins. These checks make “current state looks plausible” insufficient evidence for replay. A UI may describe recovered availability without claiming the historical effect committed. A diagnostics exporter must preserve that epistemic distinction too.

`adapter/recovery_journal.py:1` describes its record as a durable uncertain intent rather than an executable retry queue. `guarded` maps operating-system errors to busy/full/unavailable and validation failure to unverified or legacy-owner. `Journal.atomic` uses bounded bytes, fsync and replacement; directory/file ownership, no-follow access and migration ownership checks are explicit. `uncertain` correlates admitted and settled records and emits an informational frame. This is substantial implemented source evidence, but not qualification of every original crash or storage fault. In particular, the durable recovery record contains authority metadata; it must not become an ordinary logging template.

The frozen OpenSpec already obligates distinct correlated outcomes (ELM-ARC-007), dependency withholding (ELM-ARC-008), reconciliation before retry (ELM-ARC-014), fresh epochs/snapshots after restart (ELM-ARC-026), accessible deduplicated status (ELM-UI-010) and diagnostic content exclusion (ELM-DEL-017). The workplan's W04/W05/W08/W10/W11 directly cover typed outcomes, native deadlines, announcement ownership, drain and fail-closed diagnostics. Advice duplicating these obligations should sharpen their oracles instead of growing a parallel roadmap.

All recommendations preserve original242 requirements/417 scenarios, S01-S16, the right-click amendment,13 native preview scenarios, restore38/recovery34,52 drag/resize/reload cases and original deadlines. The preview509/513 and refusal516/517/520 evidence is component evidence. Production provider519, full native resource drainage and full GUI ownership/fidelity remain unqualified; GUI814/toolkit391 are separate ABI lanes. Neither a log nor this review closes those gates.

## Verified primary-source evidence

Each row records the precise claim used; recommendations below are local inferences. Dynamic documentation years are retrieval/documentation dates rather than original publication claims.

| ID | Primary source, title/year, direct link | Supporting claim and applicability limit |
|---|---|---|
| A1 | Patterson et al., *Recovery Oriented Computing: Motivation, Definition, Techniques, and Case Studies*, Berkeley TR2002, [author-institution PDF](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2002/Archive/CSD-02-1175.pdf) | Abstract and sections2-3 motivate measuring repair and testing recovery mechanisms rather than assuming rare faults vanish. Internet-service case studies do not prove desktop deadlines or justify arbitrary restart/replay. |
| A2 | Amershi et al., *Guidelines for Human-AI Interaction*, CHI2019, [author-hosted full paper](https://www.microsoft.com/en-us/research/wp-content/uploads/2019/01/Guidelines-for-Human-AI-Interaction-camera-ready.pdf) | Guidelines8-9 discuss dismissal/correction; paper evaluates guidelines with49 practitioners and20 products. AI interactions differ from deterministic native mutations; use only as HCI motivation for understandable correction and explicit uncertainty. |
| O1 | OpenTelemetry maintainers, *Handling sensitive data*, current2026, [official documentation](https://opentelemetry.io/docs/security/handling-sensitive-data/) | Data minimization and allowlisted redaction are supported; small predictable identifiers remain identifiable after hashing. Collector configuration does not validate this project's schema or export boundary. |
| O2 | systemd maintainers, *systemd-coredump*, current2026, [official repository manual source](https://raw.githubusercontent.com/systemd/systemd/main/man/systemd-coredump.xml) | Crash handling separates journal metadata and core storage; retention and availability of each differ. Documents executable/process/environment/memory-related metadata, so generic crash evidence is not safe ordinary diagnostics. No evidence here establishes the installed service configuration or that collecting a dump restores shell state. |
| O3 | thiserror maintainers, *thiserror*2.0 documentation, current2026, [official crate documentation](https://docs.rs/thiserror/latest/thiserror/) | Typed error enums/structs can carry display messages, source chains and backtraces separately. Rust mechanics are an analogy for separating machine category from presentation; do not introduce Rust or this dependency into Elm. |
| O4 | OpenTelemetry maintainers, *Logs Data Model*, current2026, [official specification](https://opentelemetry.io/docs/specs/otel/logs/data-model/) | Distinguishes event timestamp from observed timestamp and structured severity/attributes. A telemetry timestamp is not a native deadline authority; trace identifiers do not replace project identity tuples. |
| S1 | W3C, *Understanding WCAG2.2 SC4.1.3 Status Messages*, current2026, [official guidance](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html) | Status must be programmatically exposed without requiring focus, including via native accessibility APIs. Informative web guidance does not prove native speech/braille behavior or prescribe the project's deduplication key. |
| S2 | Ewaschuk, *Monitoring Distributed Systems*, Google SRE book2016, [author organization chapter](https://sre.google/sre-book/monitoring-distributed-systems/) | Separates symptoms from causes and recommends actionable low-noise alerts, latency distributions and collection simplicity. Operational paging experience motivates restraint; desktop notification policy and budgets need local validation. |

Six distinct source organizations/projects/publications were directly opened successfully; A1/A2 are full academic documents, O1-O4 maintained OSS official documentation/code. Failed guessed links were not used as evidence. No source establishes that full OpenTelemetry infrastructure, systemd capture changes or thiserror are appropriate dependencies here.

## Prioritized adoption proposals

### ERR-01 — preserve uncertainty in a structured reporting contract (priority1)

Reason: users need to know whether nothing happened, something may have happened, or an action is still running. Sources A2/O3 motivate recovery and distinct machine/presentation information. Existing mapping: ELM-ARC-007/008/014, W04 and W11; **refinement**, not a new transaction state machine. Typed errors already exist in some recovery paths; unify their reporting boundary incrementally.

Requirement: each report should identify outcome knowledge, stable reason category, affected action, safe next step and correlation identity. “Cancelled” is not automatically proof of no native effect; text must follow the receipt contract. Distinguish unsent local refusal, authority refusal, invalid evidence, capability unavailable, resource exhaustion and Unknown. Avoid showing raw decoder/backtrace/errno text to users. The precise constructors and localized copy catalog are implementation choices. Do not change strict wire decoders casually to add optional arbitrary details.

Alternative: status-only messages are cheaper but obscure safe recovery; raw native messages reduce mapping work but leak details and blur semantics. Cost: category registry, compatibility review and differential fixtures. Validation: enumerate every existing outcome/recovery reason; every class has reviewed text and enabled-action oracle; corrupt or future reasons fail closed without fabricating a terminal outcome.

EARS draft: WHEN an operation report is presented, the shell SHALL derive its message and available recovery actions from a validated correlated outcome and SHALL distinguish definitive refusal from Unknown without implying completion or authorizing replay.

OpenSpec drafts:
- GIVEN an admitted restore with lost receipt, WHEN transport disconnects, THEN the report states that completion is unconfirmed, preserves Unknown and offers no automatic repeat.
- GIVEN an exact unsent certificate and a simultaneous late receipt for a different request, WHEN reports are reduced, THEN refusal is attached only to the certified request and the foreign receipt cannot alter its message or actions.

### ERR-02 — one announcement owner and outcome-aware deduplication (priority1)

Reason: two read-only projections must not create two speech interruptions for one failure. Sources S1/S2 support non-focus announcements and low noise; A2 supports accessible correction. Mapping: ELM-UI-009/010 and W08; **duplicate obligation with refined validation**. Keep a single controller-owned announcement stream; projections render details and controls.

Requirement: attention-needed transitions have identity-correlated status, reachable recovery details and preserved focus under the frozen interruption/DND policy. Deduplicate repeated receipts, not distinct changes such as Unknown later becoming verified Committed. A stable semantic outcome identity is required; its serialized representation and AT transport are choices. Delivery acknowledgment cannot be conflated with physical AT output.

Alternative: per-view live regions are simple locally but duplicate output on multiple surfaces; one modal per failure interferes with focus and ordinary work. Cost: semantic routing, native AT integration and multi-output transcript qualification. Validation: count announcements against distinct eligible transitions, observe focus and speech/braille, include duplicate receipts and surface recreation. Preserve existing policy thresholds; freeze any missing quantitative oracle through S02/P0 rather than inventing one.

EARS draft: WHEN an eligible correlated outcome transition requires attention, the controller SHALL publish one accessible status through the designated announcement owner, retain focus and suppress repeats of that outcome while preserving later distinct outcome transitions.

OpenSpec drafts:
- GIVEN bar and popup projections on two outputs with stable focus, WHEN the same refusal receipt is delivered repeatedly and a popup recreates, THEN one eligible announcement occurs and recovery detail remains reachable.
- GIVEN Unknown was announced and the original deadline has elapsed, WHEN a valid late correlated receipt settles knowledge, THEN a distinct policy-eligible update is exposed without restarting the effect or changing its deadline; foreign-epoch receipts produce no such update.

### ERR-03 — bounded allowlisted diagnostics independent of authority (priority2)

Reason: source-specific error strings and recovery records are useful for debugging but dangerous universal log bodies. O1/O4/S2 support minimization, structured events and separate symptom/cause views. Mapping: ELM-DEL-017, W04/W11 and the frozen performance contract; **refinement**.

Requirement: ordinary diagnostics have an explicit allowlist, bounded retention/admission and loss accounting. Preserve outcome category, component/build/schema version and enough opaque scoped correlation for triage. Exclude secrets, draft content, captured pixels, raw commands, arbitrary titles/paths and raw port payloads. Persistent recovery remains a separately protected correctness mechanism; dropping diagnostic records must never release a reservation or change admission. Authority metadata is not automatically export-safe.

Alternative: unrestricted verbose logs simplify one incident at privacy/resource cost; aggregate-only metrics lose sequence context. Cost: event schema, producer audits and saturation tests. A ring buffer and separate counters are possible implementations, not mandated architecture. Validation: sensitive canaries across nested values and error strings; resource saturation, failure to write and malformed events preserve controller decisions. Measure log-rate, whole-process CPU/wakeups/memory, export cost and retention against `elm-performance/spec.md` ELM-PER obligations; the performance owner freezes numeric limits from P0 workloads before acceptance.

EARS draft: WHILE ordinary diagnostics are enabled, the diagnostics subsystem SHALL admit only allowlisted bounded records and SHALL report record loss without collecting excluded content or altering native authority, operation outcomes or deadlines.

OpenSpec drafts:
- GIVEN a decoder failure containing a secret canary and window title, WHEN a diagnostic record is produced, THEN only allowed category/context fields appear and neither canary nor title is retained.
- GIVEN diagnostic capacity is exhausted during a pending effect, WHEN further records arrive and a terminal receipt races, THEN loss is observable, memory stays within the frozen budget and receipt settlement is identical to diagnostics-disabled execution.

### ERR-04 — recovery evidence distinguishes restored availability from past success (priority1)

Reason: users otherwise mistake a functioning shell after restart for proof that the previous window action succeeded. A1/O2 motivate tested recovery and separation of crash evidence from repair. Mapping: ELM-ARC-014/026, ELM-QA-002/003, W05/W10/W11; **refinement**.

Requirement: recovery reports distinguish invalidation, reconciliation, restored availability and unresolved historical outcome. Preserve native original time origin through queues/restart. A crash record cannot serve as completion proof. Do not auto-replay Unknown, relax coherent snapshot admission or erase history on presentation dismissal. Implementation choices include a recovery phase model or derived status record.

Alternative: automatic retries may appear faster but are prohibited here; generic “recovered” banners omit the critical uncertainty. Cost: recovery phase/report integration and protected fault campaign evidence. Validation: original restore38/recovery34 with unchanged identity/oracle/deadline, held effects, missing/corrupt journal, unavailable storage, frontend/authority epoch replacement and stale proof. Component replay supplements rather than replaces native acceptance.

EARS draft: WHEN a failed frontend or authority recovers, the shell SHALL report verified current availability separately from unresolved historical outcomes and SHALL admit new effects only after native reconciliation under the original deadline and identity contracts.

OpenSpec drafts:
- GIVEN an admitted effect and crash before durable settlement, WHEN a fresh epoch receives a coherent snapshot, THEN availability may recover while the previous effect remains unconfirmed and is never replayed.
- GIVEN a storage-full recovery failure and matching-looking geometry from a replacement incarnation, WHEN reconciliation is attempted, THEN geometry alone cannot clear the historical reservation, no new dependent effect is admitted and the original recovery deadline remains enforced.

### ERR-05 — explicit diagnostics export boundary (priority2)

Reason: ELM-DEL-017 protects ordinary logs but does not alone define what a shareable bundle contains. O1/O2/O4 provide concrete risk/structure evidence. Mapping: ELM-DEL-017 and security delivery validation, W11; **new export behavior if the product elects to provide export**, subordinate to existing privacy obligations.

Requirement: a user-requested bundle declares its schema, time/scope, component versions, included categories and omissions; it passes the same privacy allowlist and a final export-specific audit. Do not attach core dumps, screenshots, environment or journals by default. Local export authorization is not authorization to upload/send. Export cancellation or failure leaves recovery records intact. Filename/destination selection, compression and format are choices.

Alternative: copying a journal manually is cheaper but produces unreviewable privacy and scope surprises; automated cloud uploads introduce unsupported product scope. Cost: bundle builder, accessible review and export fault testing. Validation: unpack and schema-check artifacts; canary and content scans; stale-epoch snapshot race, cancellation, disk-full and symlink/path defenses; measured export overhead must meet frozen performance budgets.

EARS draft: WHEN the user requests a diagnostic export, the shell SHALL produce an inspectable local bundle containing only validated export-allowed evidence and declared omissions, without exporting excluded content, sending it externally or modifying recovery authority.

OpenSpec drafts:
- GIVEN diagnostics and an available core dump containing private memory, WHEN the user requests the ordinary bundle, THEN the bundle includes allowed metadata and states that core/pixels/content are omitted.
- GIVEN export is assembling records while frontend epoch changes, WHEN cancellation or disk-full occurs, THEN no success is reported, partial-artifact disposition is explicit, and neither old nor fresh recovery reservation is changed.

## Rejected alternatives, acceptance gaps and research unknowns

Reject introducing Elm Signals, distributed reporting controllers, JavaScript safety timers, replay queues for Unknown, plaintext raw-port logging and default core/screenshot attachment. Defer a full OpenTelemetry Collector deployment, remote incident service and statistical root-cause classifier: evidence supports schema discipline, not their runtime cost or applicability. Defer automatically restarting the compositor; coherent reversible release retains application windows and the accepted shell configuration.

The workplan must resolve announcement interruption policy and deduplication horizon, export destination safety, build/schema compatibility, and budget ownership before implementation claims. History exhaustion must never be “fixed” by deleting reservations; the current restart advice in `Shell.status` deserves qualification against sticky history/anti-replay semantics rather than assuming restart clears the condition. No reviewed source proves that restart is sufficient.

A practical acceptance sequence is typed reporting fixtures, state-and-command replay including malformed/stale evidence, bounded diagnostic fault controls, then serialized protected native recovery/AT campaigns on the owning ABI. Numeric diagnostic or announcement budgets remain unfrozen unless supported by the frozen P0 contract and measurement; original operation deadlines never move. All tasks remain unchecked. This independent report expresses no unanimous agreement; ERR-01 through ERR-05 are candidates for the later shared-matrix vote and dissent round.
