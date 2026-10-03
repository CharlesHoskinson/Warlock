# Independent delivery and requirements audit — GPT-6.1 Sol

Verdict: **changes required before planning acceptance**. Counts: **0 critical, 3 high, 3 medium, 0 low**. Five findings block planning acceptance; the evidence-closure limitation should be corrected for independently reproducible corpus claims.

Input: `review-packet.md`, SHA-256 `9b7f47af2664ab40322cf40241d04f69348a0a6064b20b1cec34a37713436b6b`. I checked all 36 `draft-manifest.json` entries against the copied `draft-packet` bytes: no missing files or hash mismatches. The frozen registry contains 181 requirements. The frozen `validation.json` identifies that registry hash and records successful structural/OpenSpec validation. That result is credible within its stated format scope; it did not catch the task-generation and semantic coverage defects below.

## Findings

### SOL-D-001 — HIGH — planning blocker

Affected: ELM-QA-016, ELM-DEL-002. Location: `openspec/changes/elm-desktop-pivot/tasks.md / P0–P8`.

The frozen task list has 1,629 checkbox rows for 181 distinct task IDs. Each ID occurs nine times, once under every phase heading. For example P1-ELM-ARC-002 occurs under P0 and all eight other headings. Checking its P1 box leaves eight duplicate boxes unresolved; interpreting heading placement instead schedules P8 work in P0. The claimed phase/task map is therefore not executable even though strict format validation passed.

Correction: Filter tasks by requirement.phase during generation; emit each task ID once under its matching phase. Add validation requiring unique task IDs, an exact one-to-one registry/task bijection and phase-prefix/heading equality. Regenerate as a new audited derivative while retaining the frozen packet.

### SOL-D-002 — HIGH — planning blocker

Affected: ELM-ARC-023, ELM-QA-019, ELM-QA-020, ELM-DEL-024, ELM-UX-031. Location: `docs/elm-roadmap/requirements.json / scenarios; corresponding OpenSpec capability scenarios`.

Normative requirement text is repeated in OpenSpec, but the single scenario per bundled requirement does not exercise its full conjunction. qa-019 only opens/cancels a popup during IME and screen-reader operation: it can pass without braille, keyboard-only coverage or reduced-motion behavior. qa-020 tests mixed-scale preview transfer, leaving rotation, hotplug and high-refresh unexercised. architecture-023 merely says each route has evidence OR blocks release, permitting a failed compatibility campaign to satisfy the scenario. delivery-024 can pass one urgent-update review without an update cadence or rollback assignment; ux-031 only rejects an expired action and never proves a valid action dispatch. These are semantic scenario gaps, not implementation failures.

Correction: Split independent obligations into stable atomic requirement IDs or add named scenarios per independently verifiable obligation. Make acceptance scenarios assert successful required behavior; give negative gate-block tests separate names. Define fixture/expected observations for braille, keyboard-only traversal, reduced-motion final state, rotation/hotplug/high-refresh, valid notification action dispatch and maintenance fields. Validate obligation-to-scenario coverage rather than only presence/count.

### SOL-D-003 — HIGH — planning blocker

Affected: ELM-REN-002, ELM-REN-003, ELM-GNO-008, ELM-KDE-005, ELM-DEL-017, ELM-REN-027. Location: `docs/elm-roadmap/requirements.json / mandatory retained-preview security versus optional compositor portal requirements`.

The mandatory shell retains independently owned preview pixels after a source stops, but no mandatory requirement defines their visibility or capture admission during screen lock or permission/session revocation. ELM-KDE-005 covers ordinary live-scene eligibility, not retained preview leases, and capture portal/revocation ELM-REN-027 is conditional on compositor replacement. A retained pre-lock draft preview displayed by the shell, or a capture queued before lock completing afterward, is not explicitly forbidden by the mandatory preview requirements. Redacting diagnostic logs does not address this display/capture boundary.

Correction: Add mandatory EARS requirements: WHILE native session lock is active, the host SHALL suppress application previews and reject new application capture admission; WHEN native lock, capture permission revocation or session replacement invalidates a capture generation, the capture authority SHALL cancel pending captures and revoke presentation access to its retained leases before subsequent publication. Define unlock reconciliation and permitted private retention versus destruction policy. Add queued-capture/lock, retained-preview/lock, revocation and stale-unlock native scenarios with independent pixel observations. Bind to P2 authority policy and P4 capture qualification, retaining compositor-specific portal gates separately.

### SOL-D-004 — MEDIUM — planning blocker

Affected: ELM-DEL-002. Location: `docs/elm-roadmap/ROADMAP.md / Phases; contributions/rendering.md / Phase estimates`.

The integrated estimates do not reconcile rendering-specific lower bounds: roadmap P4 is 4–8 engineer-weeks while rendering alone estimates 6–12; P6 is 2–4 versus rendering 4–8; optional P8 is 20–50+ versus rendering 40–100+. Overlap can remove double counting but cannot by itself explain an integrated range lower than a component range for the same deliverables. The reported 19–36 mandatory sum is arithmetically correct for the roadmap but has no documented reconciliation with the component assumptions.

Correction: Publish an authoritative phase work breakdown reconciling included/reused/excluded rendering tasks, staffing and range assumptions. Revise integrated ranges or explicitly disposition the component estimate with a rationale. Preserve 25–40% contingency separately; label P8 scenarios/resource assumptions and critical-path uncertainties. No calendar commitment is needed now.

### SOL-D-005 — MEDIUM — planning blocker

Affected: ELM-QA-016, ELM-DEL-002. Location: `docs/elm-roadmap/requirements.json; TRACEABILITY.md; ROADMAP.md / Workstreams and ownership`.

ELM-QA-016 requires each requirement to map to an owner, but registry rows have no owner field and TRACEABILITY has no owner column. Workstream roles exist only as a general table. Cross-cutting rows such as ELM-GPU-010 and ELM-QA-014 have multiple plausible role owners; no explicit rule maps them to an accountable owner or independent verifier. The recorded format pass therefore does not prove this claimed mapping.

Correction: Add accountableOwnerRole and verifierRole to each canonical row, or a complete explicit ID-to-role mapping, and generate the traceability columns. Role assignments suffice before staffing; validate nonempty mapping and separate author versus acceptance reviewer where independence is required.

### SOL-D-006 — MEDIUM — evidence limitation

Affected: ELM-QA-001, ELM-QA-014, ELM-QA-016. Location: `docs/elm-roadmap/audits/draft-manifest.json; contributions/gnome-layering.md / whole-system corpus; contributions/kde-layering.md / corpus scope`.

The 36 frozen manifest entries all hash-match their copied files, but the packet freezes only prose claims about whole-source archives/documentation closure, not the referenced source/archive/corpus manifests or crawl receipts. It also hashes generation.json containing author-input hashes without freezing those companion JSON inputs. An auditor reproducing this exact packet cannot establish the 5,747-URL closure, archive completeness or contribution-input lineage from included bytes; changing an out-of-packet evidence file would not change the review packet hash. This is an evidence-closure limitation, not proof that the corpus claims are false.

Correction: Create a fresh audit evidence manifest containing the referenced corpus/source/archive inventory and crawl receipt files plus generation input JSON, with hashes and retained-body/archive hash roots. Include a mechanically checked scope definition and closure/count/failure summary. Large source bodies may remain in the immutable local archive if the retained root and verifier bind them; distinguish acquisition completeness from studied subset. Bind final dispositions to both document and supporting-evidence manifests.

## Preserved controls that pass this planning review

The roadmap is candid that it is a plan, not deployed parity. P0–P6 have deliverables, rough engineer-week ranges, gates and a dependency graph; P7/P8 are separately optional. The 19–36 sum is correct as arithmetic, and three engineers are expressly not treated as dividing the serial/native critical path by three. My estimate finding concerns unreconciled component assumptions, not the legitimacy of ranges or optional go/no-go decisions.

The unchanged 38 restore-baseline, 34 fault/recovery and 52 drag/resize/reload counts are preserved throughout, including fault case 34's independently preserved time origin. The original two-second restore deadline and helper/worker/receipt/cursor deadlines survive retries and migration. The plan preserves B14 failure, Bv4 B11 failure/B12 omission and incomplete pin/input predicates. Actual popup changed/unchanged/cancelled/stale routes precede the two-process × three-slot, twelve-helper reliability campaign. Neither bounded seven-case stacking acceptance nor V29 CPU evidence is promoted to full native parity.

Exact-name Quint selection, tool/model hashes, seeds and separately identified invariant traces are required; corrected restore45/producer14 and retained 503 names across 39 models are explicitly distinguished from old skipped counts or newly rerun models. One coherent frozen source/runtime/ABI tuple gates release. Native ownership, protected launcher/session preservation, serial campaigns and normal-exit/retirement receipts are retained.

Shell activation, upgrade, settings migration and rollback have meaningful safeguards: versioned assets, atomic settings with pre-migration copies, compatible downgrade settings, interrupted-upgrade recovery, existing application/draft preservation and offline recovery without compositor restart. Remote code/navigation, arbitrary operations, credentials in web content and ABI mismatches are forbidden. GPU discovery, native acceleration, webview composition and WebGPU execution are separate claims; unavailable hardware/assistive technology and software fallback do not silently become passing hardware gates. Numeric performance budgets being frozen in P0 is an appropriate planning gate, not a present defect.

Windows parity is expressly bounded to the required behavior inventory and inherited scenarios, not every Windows API. The plan includes taskbar, groups/actions, previews, launcher, switcher/Task View, snapping/workspaces, focus/modal/pin/MAX, gestures, settings/themes, notifications/system adapters, Files, IME/AT and multi-output. I found no reason to demand an all-Elm compositor or force optional P8 onto the mandatory shell critical path. The full behavior claim still requires correction of scenario undercoverage and capture-lock security above.

OpenSpec normative sentences are sourced from the same registry, so there is no observed text divergence. One scenario per sentence and strict parsing do not establish behavioral equivalence for compound requirements. EARS form alone similarly cannot establish atomicity, observable success criteria or conjunctive route coverage.

Corpus prose appropriately limits its claims to pinned full tracked sources and reachable documentation scopes, preserves three GNOME 404s and distinguishes acquisition from reading. I do not dispute those scopes or invent a requirement to acquire every upstream website. The review packet alone does not contain the supporting acquisition evidence necessary to reproduce their exact counts.

## Audit limits and disposition requirements

This audit inspected frozen planning bytes and the repository's AGENTS/HANDOFF guidance. It made no desktop changes, ran no native campaign, installed nothing and performed no git operation. It did not rerun OpenSpec, replay historical QA/Quint proofs or execute corpus acquisition. Findings concern planning correctness and specified acceptance, not invented implementation failures.

Preserve this packet and report unchanged. Corrections should produce a new versioned packet, retain stable finding IDs with dispositions, and bind the final validation/audit acceptance to its new document and evidence hashes. No planning disposition can fill an open native, hardware, accessibility or production activation gate.
