# Sprint delivery plan

Planning baseline: `c7c80d43043f20169140a2ce968d4a75c2140a9f92c7e753283d7ce36b844146` (242 requirements, 417 scenarios), architecture commit `d99d677`. Every requirement has one primary delivery slot and its unchanged OpenSpec acceptance scenario IDs in [sprint-backlog.json](delivery/sprint-backlog.json). All items remain backlog; prior model experiments do not complete implementation stories.

## Cadence and capacity

Use two-week sprints with planning, a midpoint risk review, a working-demo/review and a retrospective. Dates start only after staffing and Sprint 1 readiness are settled. The planning assumption is three experienced implementers covering Elm/product, native/graphics and QA/integration, with independent verification available. Six gross engineer-weeks per sprint permits at most 4.5 planned engineer-weeks; reserve 1.5 for investigation, integration and defects. These are capacity limits, not estimates of the unrefined stories. One developer requires a fresh forecast; do not divide work by agent count.

Sixteen mandatory delivery slots describe a nominal 32-week sequence under those assumptions, not a completion promise. The authoritative roadmap range remains 30–60 engineer-weeks before 25–40% contingency. Capacity reserves and roadmap contingency are overlapping allowances, not two separately multiplied promises. Record estimates and staffing in planning, then forecast from actual completed work. A slot can require additional sprints; carryover never relaxes its gate. P1 host and P4 capture decisions trigger explicit re-estimation.

## Sprint sequence

| Slot | Goal | Prerequisite | Requirement items |
| --- | --- | --- | --- |
| S01 | Baseline and inherited acceptance | Baseline reviewed | 11 |
| S02 | Product policy and measured budgets | S01 | 9 |
| S03 | Native host and protocol spikes | S02 | 26 |
| S04 | Accelerated and accessible host selection | S03 | 14 |
| S05 | Typed Elm policy and reliable authority | S04 | 30 |
| S06 | Canonical layering and focus | S05 | 28 |
| S07 | Taskbar vertical slice | S06 | 12 |
| S08 | Switcher and shell interaction lifecycle | S07 | 14 |
| S09 | Retained family captures | S08 | 9 |
| S10 | Minimize and restore transactions | S09 | 15 |
| S11 | Graphics fault and resource qualification | S10 | 12 |
| S12 | Launcher, menus and system integration | S11 | 9 |
| S13 | Task View, snapping and physical outputs | S12 | 10 |
| S14 | Accessibility and representative user flows | S13 | 8 |
| S15 | Reproducible release and recovery | S14 | 13 |
| S16 | Integrated release qualification | S15 | 10 |
| C00 | Optional compositor feasibility | S06 | 3 |
| C01 | Optional compositor roles and lifecycle | C00 | 2 |
| C02 | Optional compositor outputs and seat | C01 | 1 |
| C03 | Optional compositor IME and portals | C02 | 2 |
| C04 | Optional compositor isolation and policy | C03 | 2 |
| C05 | Optional compositor compatibility qualification | C04 | 1 |
| C06 | Optional compositor hardware and cutover | C05 | 1 |

## Planning and acceptance rules

Before commitment, split large requirement stories into implementation, experiment and acceptance subtasks; estimate them with the responsible engineer, list dependencies and fit the selected work within capacity. The complete slot backlog is a scope queue, not a demand to finish every listed item in two weeks. Story count is not effort. The requirement owner remains accountable even when multiple roles implement subtasks.

Definition of ready: stable requirement/scenario oracle, named owner and independent verifier, estimate and dependencies, available hardware/fixtures, and a concrete demo. Experiments have a timebox and an evidence-based decision; a failed feasibility result is useful evidence but does not mark the requirement done. Sprint 1 can begin without downstream numeric budgets; Sprint 2 must freeze those before candidate qualification.

Definition of done: reviewed implementation, applicable compiler/replay/fuzz/Quint checks, all mapped acceptance scenarios at the required evidence level, source/runtime/ABI hashes, retained failures and exit/retirement receipts, documentation and rollback/config migration where applicable. Mark done only when independently accepted; blocked, failed, partial and deferred are distinct states. Conditional cases need an applicability decision and evidence, never an assumed pass.

Formal models and pure Elm reducers are developed with each feature. Preserve counterexamples and replay them as typed message fixtures. UI/UX, accessibility, privacy and bounded resource behavior are part of each slice; S14 adds complete-system qualification rather than postponing them until the end. Native GUI runs remain serial through protected QA, while CPU work can run independently.

Host selection includes a minimal accessibility-tree probe in S04; complete taskbar/switcher semantics close in S08 and all surfaces in S14. IME begins on the minimal field in S04 and reruns on actual launcher/settings fields in S12/S14. S08 validates proxy handoff using an isolated deterministic fixture; S09–S11 qualify actual retained family captures. Packaging foundations may be implemented early, but release requirements close only after their S15/S16 evidence.

No sprint needs a main-desktop restart to count as a demo. Demonstrate isolated/nested candidates with representative apps and preserved drafts. Production activation occurs only after the final acceptance packet and the session authorization contract are satisfied.

## Dependency and scope management

Default execution follows the listed prerequisites; no host-dependent effect work commits before host qualification. Product/CPU prototyping and native layering diagnosis may run earlier against frozen contracts, without claiming later delivery gates. Replan parallel lanes only when staffing, interface readiness and serial QA capacity justify it. Do not unlock a successor merely because its predecessor reached a date.

Maintain a dependency/decision log with host choice, native preview route, hardware/AT availability and inherited case recovery. At each review publish planned versus accepted scope, remaining gates, defects, decisions and next-sprint capacity. After two sprints forecast using observed throughput and cycle time; keep estimates for large integration and native campaigns explicit. New requirements get EARS/OpenSpec scenarios and backlog mapping before being accepted into a sprint.

C00 is optional feasibility after S06 and may run alongside later shell work only with separate capacity. C01–C06 are initial two-week discovery/implementation slots for separately authorized compositor work, not a six-sprint replacement estimate. P8 remains 40–100+ engineer-weeks and must be expanded into additional slices after C00. If implementation or compatibility does not fit a slot, add follow-on sprints with preserved acceptance mappings; do not declare a compositor delivered from a prototype. No-go leaves mandatory shell release on Hyprland.

## Per-sprint backlog and review gates

### S01 — Baseline and inherited acceptance

Make every inherited acceptance obligation executable and establish the project controls.

Deliverables: Frozen source/ABI and case ledger, owners and original-deadline fixtures; project backlog and QA operating contract.

Exit gate: Every inherited case has its original identity/oracle/deadline or a blocking missing-evidence entry; no historical CPU pass is relabeled native.

Demo: show the stated behavior or experiment outcome with matching acceptance receipts; disclose failures and unexecuted scenarios.

- [ ] **ELM-ARC-001** — Create a frozen architecture baseline manifest. Owner: Native host lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-DEL-001** — Freeze the migration ledger and map each inherited case. Owner: Release integration lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-DEL-002** — Maintain staffing, contingency and critical-path estimates. Owner: Release integration lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-001** — Freeze inherited evidence and derivative lineage. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-002** — Recover exact campaign manifests and record one-to-one mappings. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-016** — Validate complete traceability and reconcile independent audits. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-001** — Inventory original gates without converting historical CPU results into native passes. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-005** — Assign accountable and verifier roles to every requirement. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-006** — Freeze supporting source/corpus lineage beside document audit evidence. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-035** — Inventory and hash-pin inherited native campaign definitions and unexecuted cases. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-001** — Inventory taskbar, launcher, switcher, Task View, snap, menus, settings, notifications and Files integration. Owner: Desktop experience lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.

### S02 — Product policy and measured budgets

Freeze what correct and usable behavior means before judging candidate implementations.

Deliverables: Versioned scene/switcher policy, workload budgets, readability matrix and participant usability protocol; isolated layering diagnosis.

Exit gate: Numeric applicable budgets and usability criteria are frozen; Heroic/Brave regression fixtures and native diagnosis evidence are retained.

Demo: show the stated behavior or experiment outcome with matching acceptance receipts; disclose failures and unexecuted scenarios.

- [ ] **ELM-GNO-001** — Freeze the Windows product scene-policy table. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-GPU-002** — Create acceleration evidence categories. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-021** — Measure current shell and obtain reviewed budget sheet before candidate comparison. Owner: Performance qualification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-020** — Publish complete measured workload matrix. Owner: Performance qualification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-021** — Define budget schema completeness and applicable metrics. Owner: Performance qualification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-032** — Schedule independent native layering qualification. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UI-003** — Freeze exact switcher sequence oracles. Owner: Elm policy lead; verifier: Independent acceptance reviewer. Acceptance: 5 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UI-013** — Freeze readability and reflow acceptance matrix. Owner: Accessibility lead; verifier: Independent acceptance reviewer. Acceptance: 5 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UI-021** — Freeze usability protocol and formative/release acceptance gates. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 2 unchanged scenario(s) in the machine backlog.

### S03 — Native host and protocol spikes

Display a minimal Elm surface through isolated host candidates with a validated transport boundary.

Deliverables: GTK/WebKit and comparative Qt host prototypes; surface/input-region adapters; lossless schema, clock/queue/refusal tables; protected lifecycle harness.

Exit gate: A real native shell surface, passthrough regions and versioned decoder/ABI rejection fixtures pass; no main-desktop activation.

Demo: show the stated behavior or experiment outcome with matching acceptance receipts; disclose failures and unexecuted scenarios.

- [ ] **ELM-ARC-002** — Publish an ownership table and executable boundary probe. Owner: Native host lead; verifier: Independent acceptance reviewer. Acceptance: 2 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-ARC-003** — Define the envelope schema and Elm decoders. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-ARC-004** — Implement validation at both trust boundaries. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 2 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-ARC-005** — Implement identity-bearing effect messages. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-ARC-021** — Build isolated comparative host spikes. Owner: Native host lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-ARC-022** — Implement host surface-role adapters. Owner: Native host lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-ARC-024** — Implement webview origin and capability enforcement. Owner: Native host lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-ARC-025** — Add an ABI preflight gate to native host startup. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-DEL-006** — Qualify both host dependency graphs without assuming interchangeability. Owner: Release integration lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-DEL-013** — Package offline assets and deny network/navigation at host boundary. Owner: Native security lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-DEL-014** — Implement and test CSP with packaged Elm and adapter assets. Owner: Native security lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-009** — Carry protected qa_run.py preflight into every reviewed runner. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-010** — Review launch/teardown contracts and install a campaign exclusion guard. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 4 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-011** — Implement ordered closure receipts and negative abnormal-exit fixtures. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-012** — Track wait status and retirement receipts for all process groups. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-013** — Add protected target ownership checks and session preservation assertions. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-002** — Specify buffer acquisition, lease references, fences and retirement. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-007** — Define lossless authority encoding and decoder rejection. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-012** — Specify clock domain and reboot/lifetime deadline invalidation. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-014** — Qualify shell input-region passthrough. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-015** — Test stalled-frontend native input/frame continuity. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-027** — Qualify chord journal privacy. Owner: Native security lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-029** — Qualify all five operational QA controls. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-030** — Record preservation hashes and forbidden mutations. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-034** — Freeze a complete executable protocol schema and refusal table. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-TEA-005** — Freeze minimal interop surface and modern Elm practices. Owner: Native host lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.

### S04 — Accelerated and accessible host selection

Select a host from measured rendering, input and lifecycle evidence.

Deliverables: Hardware webview render probe, separately qualified WebGPU result, hybrid-device ledger, IME and minimal native accessibility/chord probes; host ADR.

Exit gate: Nonsoftware webview composition and measured budgets pass; actual IME/popup/focus/AT route passes; unavailable WebGPU is honestly conditional.

Demo: show the stated behavior or experiment outcome with matching acceptance receipts; disclose failures and unexecuted scenarios.

- [ ] **ELM-DEL-026** — Qualify hardware acceleration for GTK/WebKit and Qt candidates. Owner: Release integration lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-DEL-027** — Test disabled acceleration and honest fallback status. Owner: Release integration lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-GPU-001** — Qualify the actual host GPU path. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 2 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-GPU-003** — Qualify WebGPU origin and sandbox. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-GPU-004** — Implement capability negotiation and API rejection. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 2 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-GPU-005** — Build isolated render and compute qualification probes. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-GPU-010** — Compare available GPU profiles without assuming power hints choose an adapter. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-022** — Build paired workload measurement and distribution reporting. Owner: Performance qualification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-024** — Pin host/build/driver versions; probe nonsoftware adapter/backend and demonstrate rendering, readback and display presentation. Owner: Performance qualification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-026** — Separate accelerated and software results with backend-verdict checks. Owner: Performance qualification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-025** — Qualify adapter/driver changes and hybrid GPU profiles. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UI-012** — Qualify IME arbitration and geometry first on minimal host, then actual fields. Owner: Accessibility lead; verifier: Independent acceptance reviewer. Acceptance: 8 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-012** — Preserve native pre-ready key journal and single commit guard. Owner: Elm policy lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-028** — Validate IME integration before choosing webview host. Owner: Accessibility lead; verifier: Independent acceptance reviewer. Acceptance: 2 unchanged scenario(s) in the machine backlog.

### S05 — Typed Elm policy and reliable authority

Implement one receipt-driven path from a pure Elm reducer to validated native effects.

Deliverables: Domain types/replay, bridge sequencing and gap barrier, cancel/deadline/dedup/dependency guards, bounded queues, authenticated session and settings boundary.

Exit gate: Named Quint/fuzz/replay tests and native stale/cancel/Unknown rejection pass; no effect is inferred from send or transport acceptance.

Demo: show the stated behavior or experiment outcome with matching acceptance receipts; disclose failures and unexecuted scenarios.

- [ ] **ELM-ARC-006** — Add effect-boundary freshness guards. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 2 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-ARC-007** — Implement receipt state transitions. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 5 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-ARC-008** — Implement an acknowledged dependency scheduler. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 4 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-ARC-009** — Implement bounded request deduplication with explicit expired-ID refusal. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-ARC-010** — Implement snapshot and delta sequencing. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-ARC-011** — Retain native chord acquisition and replay it to Elm. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-ARC-012** — Implement cancellation checks at the final native effect boundary. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 3 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-ARC-013** — Carry immutable absolute deadlines through request state. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-ARC-014** — Implement uncertain-effect recovery. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-ARC-015** — Define queue bounds and test admission saturation. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 3 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-ARC-016** — Implement separate control and preview admission. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-ARC-026** — Implement epoch-based supervised shell recovery. Owner: Native host lead; verifier: Independent acceptance reviewer. Acceptance: 2 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-DEL-010** — Implement peer credentials and session-bound bridge authorization. Owner: Native security lead; verifier: Independent acceptance reviewer. Acceptance: 3 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-DEL-011** — Define least-authority bridge method and argument validation. Owner: Native security lead; verifier: Independent acceptance reviewer. Acceptance: 2 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-DEL-012** — Preserve Files authorization and native credential boundaries. Owner: Native security lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-DEL-015** — Implement schema validation and atomic migration backups. Owner: Native security lead; verifier: Independent acceptance reviewer. Acceptance: 4 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-DEL-017** — Define redaction policy and keyring reference-only integration. Owner: Native security lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-004** — Generate exact-name selectors and reconcile per-scenario execution. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-005** — Define typed evidence levels and enforce gate-specific verifier rules. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-006** — Build reducer replay oracle with frozen observation adapters. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-007** — Fuzz decoders and native commit boundaries with shrinking and durable seeds. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-008** — Preserve inherited model coverage and add Elm protocol transition models. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 8 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-001** — Define dependency-scoped authority revisions and bounded activation progress. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 2 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-008** — Implement gap barrier and coherent resynchronization. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-009** — Define non-coalescible control event set. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-010** — Qualify full control-queue fail-closed behavior. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-011** — Test dedup eviction and identity expiration. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-TEA-001** — Design domain types and pure derived projections. Owner: Native host lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-TEA-002** — Implement deterministic reducers and replay fixtures. Owner: Native host lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-TEA-003** — Qualify effect interpreter and decoder boundaries. Owner: Native host lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.

### S06 — Canonical layering and focus

Make eligibility, painting, hit testing and focus agree under a committed native policy.

Deliverables: Shared scene transaction, modal/transient constraints, MAX/pin behavior, minimize focus succession, cross-workspace activation, lock/protected capture policy.

Exit gate: Heroic inactive-minimized and Brave MAX regressions, genuine blocker/no-focus cases and scoped workspace races pass with pixel/input receipts.

Demo: show the stated behavior or experiment outcome with matching acceptance receipts; disclose failures and unexecuted scenarios.

- [ ] **ELM-GNO-002** — Implement a shared native scene-eligibility predicate. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 4 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-GNO-003** — Order eligibility filtering before stack sorting. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-GNO-004** — Implement and replay transient constraint chains. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-GNO-005** — Add invalid-family transaction refusal. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-KDE-001** — Implement canonical stack transaction and consume committed revisions. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-KDE-002** — Define policy table; keep MAX distinct from active fullscreen. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-KDE-003** — Maintain constraints and test family removal, modal opening and stale generation. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-KDE-004** — Add Heroic regression fixture with inactive win-minimized special workspace. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-KDE-005** — Factor canonical eligibility snapshot with explicit operation-specific policy. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-KDE-007** — Test current family and genuine blockers; do not infer modality from stacking alone. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 2 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-KDE-009** — Add expected revision checks and unknown-outcome reconciliation. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-LAY-001** — Create minimized/inactive-workspace eligibility regression. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 2 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-LAY-002** — Implement canonical scene-revision publication and hit/focus observation. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-015** — Retain native stacking correction and extend painted/click truth tests. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 4 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-016** — Complete MAX pin/unpin/return paths and B11–B24 predicates. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-018** — Keep GTK, Qt and Xwayland modal semantics and real no-focus blocker coverage. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-002** — Add native lock authority to preview/capture eligibility. Owner: Native security lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-013** — Qualify ordinary MAX precedence. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-016** — Define eligibility domains and minimized enumeration. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-017** — Qualify ancestor eligibility propagation. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-018** — Qualify native lock isolation. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-024** — Enforce lease capability admission. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-026** — Define capture source authorization and protected-surface exclusions. Owner: Native security lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-031** — Preserve the corrected original B11 premise and remaining named pin/input cases. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UI-001** — Implement identity-bound minimize focus succession. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 3 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UI-002** — Implement visible cross-workspace/output activation. Owner: Desktop experience lead; verifier: Independent acceptance reviewer. Acceptance: 4 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-015** — Use native family relations and prohibit shell draft reconstruction. Owner: Desktop experience lead; verifier: Independent acceptance reviewer. Acceptance: 2 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-016** — Implement pin/MAX intent state with committed-state presentation. Owner: Desktop experience lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.

### S07 — Taskbar vertical slice

Ship an isolated selectable Elm taskbar with truthful actions and feedback.

Deliverables: Left layout/catalog/pin/group projection, primary-action table, overflow, pending/refusal/Unknown feedback and AT announcements.

Exit gate: Zero/single/group/active/minimized action fixtures, delayed/refused outcomes and keyboard overflow pass without duplicate effects.

Demo: show the stated behavior or experiment outcome with matching acceptance receipts; disclose failures and unexecuted scenarios.

- [ ] **ELM-DEL-009** — Implement per-component feature selection and conflict prevention. Owner: Release integration lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UI-004** — Implement taskbar decision table with matching pointer/keyboard routes. Owner: Elm presentation lead; verifier: Independent acceptance reviewer. Acceptance: 6 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UI-007** — Implement shared action-state and recovery presentation. Owner: Desktop experience lead; verifier: Independent acceptance reviewer. Acceptance: 15 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UI-008** — Implement accessible dense-layout overflow and menu discovery. Owner: Elm presentation lead; verifier: Independent acceptance reviewer. Acceptance: 3 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UI-010** — Implement non-focus-stealing accessible outcomes. Owner: Accessibility lead; verifier: Independent acceptance reviewer. Acceptance: 10 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UI-015** — Freeze and qualify bounded operation feedback. Owner: Desktop experience lead; verifier: Independent acceptance reviewer. Acceptance: 3 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-002** — Implement left anchored taskbar layout with scale-aware reserved work area. Owner: Elm presentation lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-003** — Port catalog projection without replacing desktop-file parsing semantics. Owner: Elm presentation lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-004** — Implement identity-based pin ordering with restart reconciliation. Owner: Elm presentation lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-005** — Implement window grouping and native validated selection. Owner: Elm presentation lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-008** — Port click-to-activate and restore intent path. Owner: Elm presentation lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-009** — Derive highlights from native observations rather than optimistic clicks. Owner: Elm presentation lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.

### S08 — Switcher and shell interaction lifecycle

Complete native chord handling and usable shell focus scopes.

Deliverables: MRU chord reducer, forward/reverse/cancel/retire fixtures, multi-output projections, focus scopes and subscriptions; proxy/modal handoff contract.

Exit gate: Release-before-open, cancellation, incarnation reuse, native popup changed/same/stale routes and actual taskbar/switcher accessibility pass.

Demo: show the stated behavior or experiment outcome with matching acceptance receipts; disclose failures and unexecuted scenarios.

- [ ] **ELM-ARC-017** — Implement canonical multi-output policy projections. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-ARC-018** — Bind action validation to native family and hit-order observations. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-GNO-006** — Add overlapping-window pixel and input receipt tests. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 4 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-GNO-007** — Validate pin-maximize-restore as a Windows policy difference. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-GNO-009** — Add a workspace-change effect-boundary race campaign. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-LAY-003** — Qualify atomic restore eligibility and stale overlay retirement. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 2 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-018** — Finish real private-Quickshell source closure and carry routes to Elm host. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-033** — Define modal redirection and proxy-to-live publication linearization. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 2 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-TEA-004** — Implement state-derived subscriptions and bounded demand. Owner: Native host lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UI-011** — Implement scope-stack focus restoration and fallback. Owner: Accessibility lead; verifier: Independent acceptance reviewer. Acceptance: 6 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-011** — Port chord reducer with forward and reverse ordinals. Owner: Elm policy lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-013** — Implement native cancellation boundary and focus-preservation replay. Owner: Elm policy lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-014** — Handle close and incarnation reuse during chord. Owner: Elm policy lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-025** — Gate host selection on real accessibility-tree export. Owner: Accessibility lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.

### S09 — Retained family captures

Keep authorized preview pixels valid after their source stops.

Deliverables: Opaque lease/fence API, source-stop ownership, frame identity/timestamps, composed-family fidelity and explicit preview states.

Exit gate: Native source-stop and family pixel/fence/capability fixtures pass; historical/live/unavailable labels match actual source state.

Demo: show the stated behavior or experiment outcome with matching acceptance receipts; disclose failures and unexecuted scenarios.

- [ ] **ELM-ARC-019** — Implement opaque preview handles and retirement proofs. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-003** — Prove source-stop survival in the selected host rather than assume QML behavior transfers. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-004** — Bind frame keys to compositor lifetime, window incarnation and acquisition revision. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-005** — Specify timestamp origins and distinguish queue, seed, upload and presentation. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-014** — Design composed-family capture; reject unsupported fidelity claims. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 5 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-023** — Qualify acquire fences and release access. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UI-016** — Qualify explicit preview source states. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-006** — Represent minimized entries and retained preview freshness separately. Owner: Elm presentation lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-007** — Add explicit unavailable-preview view and lifetime-key validation. Owner: Elm presentation lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.

### S10 — Minimize and restore transactions

Restore correctly within the original deadline using inert proxies and current native authority.

Deliverables: Minimize/seed/live workflows, reversal/cancellation/retirement, native caption/edge integration, live reduced-motion profiles.

Exit gate: Original baseline38/recovery34 and case-34 deadline oracle pass; atomic proxy-to-live handoff and exact normal retirement receipts hold.

Demo: show the stated behavior or experiment outcome with matching acceptance receipts; disclose failures and unexecuted scenarios.

- [ ] **ELM-ARC-020** — Expose separate commit and presentation evidence. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-GNO-008** — Separate transition visual ownership from application hit eligibility. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-KDE-006** — Separate effect/preview visual ownership from live-window interaction authority. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-003** — Extract the original case-34 bound and add a late-completion negative fixture. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-006** — Implement minimize policy with native visibility receipts and saved geometry. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-007** — Define seed-to-live transition and refusal if a usable frame is absent. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-008** — Carry absolute deadline in each transaction and refuse deadline reset on retry. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-009** — Add cancellation checks at each native effect boundary and renderer submission. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-010** — Model interruption, repeated commands and deterministic geometry interpolation. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-011** — Share commit/cancel semantics between animated and reduced-motion routes. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-013** — Record ownership ledger and normal-exit evidence; disappearance alone is insufficient. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UI-014** — Implement live reduced-motion preference changes. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 4 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UI-018** — Qualify mid-flight and overlay motion preference changes. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 3 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-021** — Integrate caption/edge gestures without webview-dependent hit decisions. Owner: Desktop experience lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-022** — Define reduced-motion profile and retain native motion receipts. Owner: Desktop experience lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.

### S11 — Graphics fault and resource qualification

Survive lock, revocation, output changes and GPU loss without stale pixels or runaway work.

Deliverables: Native preview interoperability, device/allocation failure handling, privacy/unlock, transfer budgets, generation transforms and demand-driven quiescence.

Exit gate: Fault/lock/fence/output cases and whole-tree preview budgets pass; device loss retires invalid storage or exposes unavailable state.

Demo: show the stated behavior or experiment outcome with matching acceptance receipts; disclose failures and unexecuted scenarios.

- [ ] **ELM-DEL-028** — Gate optional WebGPU by pinned-engine hardware probes and device-loss tests. Owner: Release integration lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-GPU-006** — Keep GPU ownership and frame scheduling in the renderer. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-GPU-007** — Implement bounded device-loss recovery. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 2 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-GPU-008** — Qualify the preview interoperability path. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-025** — Add device-loss and allocation fault tests to native capture/motion qualification. Owner: Performance qualification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-012** — Measure allocations and implement admission limits with control-traffic priority. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-019** — Handle fractional scale, negative coordinates, rotation and hotplug. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-003** — Make lock/revocation/session transitions invalidate capture and publication generations. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 3 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-004** — Specify retained-pixel privacy and unlock reconciliation. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 3 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-019** — Qualify device-loss retained-frame outcomes. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-022** — Enforce preview-import budgets. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UI-017** — Implement demand-driven preview and GPU work. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 3 unchanged scenario(s) in the machine backlog.

### S12 — Launcher, menus and system integration

Deliver complete discoverable application and settings journeys.

Deliverables: Generation-safe search, jump lists, settings/themes entry points, notifications, system adapters, Files integration and first-use help.

Exit gate: Current-query launch/refusal and notification identity cases pass; adapters expose unavailable state; Files semantics and shortcut preferences persist.

Demo: show the stated behavior or experiment outcome with matching acceptance receipts; disclose failures and unexecuted scenarios.

- [ ] **ELM-UI-005** — Implement query-generation-safe search states. Owner: Desktop experience lead; verifier: Independent acceptance reviewer. Acceptance: 5 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UI-020** — Implement discoverable guidance and preference-safe enablement. Owner: Desktop experience lead; verifier: Independent acceptance reviewer. Acceptance: 2 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-010** — Define jump-list providers and dispatch identity-bound actions. Owner: Elm presentation lead; verifier: Independent acceptance reviewer. Acceptance: 2 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-029** — Implement launcher search and correlated launch outcome. Owner: Desktop experience lead; verifier: Independent acceptance reviewer. Acceptance: 2 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-030** — Create settings schema, validation and migration UI. Owner: Desktop experience lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-031** — Build notification center with native notification lifecycle adapter. Owner: Desktop experience lead; verifier: Independent acceptance reviewer. Acceptance: 3 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-032** — Integrate volume, network, power and session adapters with explicit availability. Owner: Desktop experience lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-033** — Integrate omarchy-files launch/reuse contract without rewriting file operations. Owner: Desktop experience lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-034** — Scope separate Files migration; update spec before semantic implementation changes and run model-based tests. Owner: Desktop experience lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.

### S13 — Task View, snapping and physical outputs

Make workspace and output journeys visibly correct and recoverable.

Deliverables: Overview navigation/transfer, snap chooser, exclusive/menu policy, output-removal recovery and physical display acceptance.

Exit gate: Workspace transfer/refusal, scale/rotation/hotplug and active fullscreen/pin/modal policies pass; no invisible focus trap remains.

Demo: show the stated behavior or experiment outcome with matching acceptance receipts; disclose failures and unexecuted scenarios.

- [ ] **ELM-KDE-008** — Test active fullscreen transitions, other-output focus, pin exceptions and modal children. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-020** — Run serial physical multi-display and cadence qualification. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 5 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-017** — Specify exclusive/render/menu exceptions and regression isolation. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-020** — Serialize transfer and cancellation with output removal and snap policy. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UI-006** — Implement complete overview journeys. Owner: Desktop experience lead; verifier: Independent acceptance reviewer. Acceptance: 5 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UI-019** — Implement reachable hot-unplug recovery. Owner: Desktop experience lead; verifier: Independent acceptance reviewer. Acceptance: 2 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-017** — Build Task View from canonical workspace/window projection. Owner: Desktop experience lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-018** — Implement transfer transaction and refused-state feedback. Owner: Desktop experience lead; verifier: Independent acceptance reviewer. Acceptance: 3 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-019** — Implement snap chooser and native placement reconciliation. Owner: Desktop experience lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-020** — Invalidate snap transactions on scale, transform and hotplug changes. Owner: Desktop experience lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.

### S14 — Accessibility and representative user flows

Qualify every migrated surface through keyboard, speech, braille and real application flows.

Deliverables: Full semantic control inventory, focus scopes, supported text/reflow themes, IME reruns on actual surfaces and formative usability results.

Exit gate: Every surface passes keyboard/AT and configured usability thresholds; original pin/input/popup/drag and representative app cases have exact receipts.

Demo: show the stated behavior or experiment outcome with matching acceptance receipts; disclose failures and unexecuted scenarios.

- [ ] **ELM-ARC-023** — Create the native host compatibility campaign. Owner: Native host lead; verifier: Independent acceptance reviewer. Acceptance: 8 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-017** — Define and execute real application compatibility scenarios. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 2 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-019** — Create accessible-name/focus/IME fixtures and conduct actual assistive-technology sessions. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 5 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UI-009** — Qualify full-surface native accessibility semantics. Owner: Accessibility lead; verifier: Independent acceptance reviewer. Acceptance: 9 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-023** — Publish chord map and implement focus traversal for every migrated surface. Owner: Accessibility lead; verifier: Independent acceptance reviewer. Acceptance: 10 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-024** — Implement focus scopes and native focus return. Owner: Accessibility lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-026** — Execute audible and braille navigation campaign on deployed host. Owner: Accessibility lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-027** — Add measured theme fixtures at supported text scales. Owner: Accessibility lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.

### S15 — Reproducible release and recovery

Build a deployable candidate with independently usable recovery.

Deliverables: Dependency/ABI locks, SBOM/notices, offline build and target matrix, atomic installation/settings migration, restart/suspend/interrupted-upgrade and rollback tooling.

Exit gate: One release tuple is reproducible; restart/resync and offline rollback restore compatible settings; only qualified targets are advertised.

Demo: show the stated behavior or experiment outcome with matching acceptance receipts; disclose failures and unexecuted scenarios.

- [ ] **ELM-ARC-027** — Build and exercise a shell-only rollback procedure. Owner: Native host lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-DEL-003** — Create a complete dependency lock manifest. Owner: Release integration lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-DEL-004** — Create a clean offline reproducibility campaign. Owner: Release integration lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-DEL-005** — Generate SBOM and license approval ledger. Owner: Release integration lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-DEL-007** — Publish target matrix and optional Ubuntu qualification work. Owner: Release integration lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-DEL-008** — Design versioned installation and atomic activation paths. Owner: Native security lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-DEL-016** — Implement downgrade settings selection and restoration receipt. Owner: Release integration lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-DEL-018** — Qualify restart and resynchronization recovery. Owner: Release integration lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-DEL-019** — Implement atomic release selection and interruption drills. Owner: Release integration lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-DEL-020** — Ship independently executable rollback tooling and instructions. Owner: Release integration lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-DEL-021** — Preserve ordered teardown and normal-exit receipts. Owner: Release integration lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-DEL-022** — Add hash-bound native pair preflight. Owner: Release integration lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REV-028** — Qualify suspend/resume recovery. Owner: Release integration lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.

### S16 — Integrated release qualification

Produce a concrete release decision from one coherent tuple.

Deliverables: Combined regression and UX ledger, whole-tree performance/power/soak, high-refresh evidence, incident runbook and activation review packet.

Exit gate: All applicable mandatory gates pass with the same source/runtime/ABI tuple; failed/unobserved outcomes block release; authorized activation has rollback receipts.

Demo: show the stated behavior or experiment outcome with matching acceptance receipts; disclose failures and unexecuted scenarios.

- [ ] **ELM-DEL-023** — Create final gate ledger and concrete activation review packet. Owner: Release integration lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-DEL-024** — Publish support and incident maintenance runbook. Owner: Release integration lead; verifier: Independent acceptance reviewer. Acceptance: 3 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-DEL-025** — Prepare representative user-flow acceptance script and receipts. Owner: Release integration lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-GPU-009** — Qualify degraded recovery and release refusal. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-014** — Publish immutable per-run gate receipts with bounded claim scopes. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-015** — Run coherent release regression after component qualification. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-023** — Instrument process-group accounting and bounded-resource soak. Owner: Performance qualification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-021** — Benchmark native motion without per-frame Elm JSON; set budgets from baseline. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-022** — Instrument both host candidates and document observer overhead and missing stages. Owner: Graphics lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-UX-035** — Create coherent release UX matrix and reversible rollout plan. Owner: Desktop experience lead; verifier: Independent acceptance reviewer. Acceptance: 2 unchanged scenario(s) in the machine backlog.

### C00 — Optional compositor feasibility

Decide whether replacing Hyprland is justified by an isolated native prototype.

Deliverables: Substrate/license/maintenance ADR, Wayland/Xwayland protocol matrix and explicit scope/resource decision.

Exit gate: Representative native compatibility evidence and a documented go/no-go decision; a no-go does not block the mandatory shell.

Demo: show the stated behavior or experiment outcome with matching acceptance receipts; disclose failures and unexecuted scenarios.

- [ ] **ELM-ARC-028** — Produce the optional compositor feasibility decision. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-QA-027** — Specify optional compositor matrix and evidence-driven go/no-go gate. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-023** — Choose native framework after protocol, license, backend and maintenance evaluation. Owner: Native compositor lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.

### C01 — Optional compositor roles and lifecycle

Prove a minimal native substrate with real application lifecycle.

Deliverables: xdg roles/configure/ack, Xwayland window/focus integration and approved backend skeleton.

Exit gate: Representative native role/lifecycle and legacy X11 fixtures pass in nested sessions.

Demo: show the stated behavior or experiment outcome with matching acceptance receipts; disclose failures and unexecuted scenarios.

- [ ] **ELM-ARC-029** — Implement and validate the separately approved native compositor backend. Owner: Native authority lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-024** — Implement xdg roles, configure/ack lifecycle and legacy X11 focus/window management. Owner: Native compositor lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.

### C02 — Optional compositor outputs and seat

Prove native hardware/input lifecycle independently of Elm timing.

Deliverables: Outputs/modes/leases, input device lifecycle and suspend/resume.

Exit gate: Isolated hotplug and input/output transition fixtures pass without losing ownership.

Demo: show the stated behavior or experiment outcome with matching acceptance receipts; disclose failures and unexecuted scenarios.

- [ ] **ELM-REN-025** — Implement hotplug, modes, leases, suspend/resume and input-device lifecycle. Owner: Native compositor lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.

### C03 — Optional compositor IME and portals

Prove text input, capture consent and revocation.

Deliverables: Native IME/text-input and PipeWire/screencopy portal adapters.

Exit gate: Current-focus IME and session-bound portal consent/revocation fixtures pass.

Demo: show the stated behavior or experiment outcome with matching acceptance receipts; disclose failures and unexecuted scenarios.

- [ ] **ELM-REN-026** — Implement native text-input/input-method routes with focus and security isolation. Owner: Native compositor lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-027** — Integrate screencopy/PipeWire portal paths, revocation and session isolation. Owner: Native compositor lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.

### C04 — Optional compositor isolation and policy

Harden native isolation and bounded policy fallback.

Deliverables: Threat-model fixtures, lock/client/buffer isolation and asynchronous Elm policy snapshots.

Exit gate: Malformed clients and stalled frontend cannot bypass lock isolation or native input deadlines.

Demo: show the stated behavior or experiment outcome with matching acceptance receipts; disclose failures and unexecuted scenarios.

- [ ] **ELM-REN-028** — Threat-model IPC, protocol exposure, buffer parsing, lock surfaces and client isolation. Owner: Native compositor lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.
- [ ] **ELM-REN-029** — Implement asynchronous policy snapshots and bounded native policy fallback. Owner: Native compositor lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.

### C05 — Optional compositor compatibility qualification

Qualify all parity and compositor-specific behaviors on the new backend.

Deliverables: New backend release matrix and fresh compatibility receipts.

Exit gate: No Hyprland-only receipt substitutes for a new-compositor gate; all applicable mandatory scenarios rerun.

Demo: show the stated behavior or experiment outcome with matching acceptance receipts; disclose failures and unexecuted scenarios.

- [ ] **ELM-QA-028** — Extend release gates to the new compositor without inheriting Hyprland-only passes. Owner: Verification lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.

### C06 — Optional compositor hardware and cutover

Prepare a reversible hardware rollout after native acceptance.

Deliverables: Sacrificial hardware qualification and draft-preserving activation/recovery packet.

Exit gate: Hardware acceptance and independently rehearsed rollback pass before any authorized session cutover.

Demo: show the stated behavior or experiment outcome with matching acceptance receipts; disclose failures and unexecuted scenarios.

- [ ] **ELM-REN-030** — Stage nested then sacrificial hardware sessions; preserve user drafts before cutover. Owner: Native compositor lead; verifier: Independent acceptance reviewer. Acceptance: 1 unchanged scenario(s) in the machine backlog.

## First planning meeting

Start with S01: verify the existing archive and original campaign definitions; name the accountable implementers/verifier; refine and estimate its baseline/ledger stories; select the capacity-fitting subset; publish the sprint goal and review demo. Keep all unrecovered legacy cases visibly blocked. S02 preparation may collect measurements, but candidate host selection waits for frozen budgets and policy.
