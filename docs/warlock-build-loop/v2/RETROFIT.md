# Retroactive architecture, QA and documentation debt

Standing user requirement, October 29, 2026: apply the new architecture and QA workflow to existing Warlock code and build documentation using Diátaxis. This register tracks work, not completion claims. Full original requirements and scenarios remain authoritative. [Architecture review](ARCHITECTURE-REVIEW.md), [research](ELM-ARCHITECTURE-RESEARCH.md), [contracts/fuzzing](FUZZING-CONTRACTS.md), and the [product documentation](../../warlock/index.md) form the standing process.

## Retrofitting existing code

Inventory the active candidate's Elm, native, adapter, asset and release/QA modules by existing ownership and original requirement. Archived versions and frozen evidence remain historical; do not rewrite them to conform to new style. Audit existing code as well as new edits. An absent contract/test is an open evidence gap, not proof of a product bug. A prior accepted scenario is not automatically invalidated by a documentation policy change; requalify relevant changed behavior and dependencies.

For each bounded migration, identify its original scenarios and observed coupling/defect; map state, event, effect, subscription and native resource owners; record preconditions, postconditions and preserved invariants; and check implementation/model correspondence. Prefer opaque validated domain values and explicit boundary errors. Distinguish construction guarantees from local overlays and from native authority that can expire after decoding.

Exercise actual production transitions with applicable existing replays, valid reachability witnesses and meaningful negative/lifecycle/property tests. Add missing sequence fuzzing with recorded seed/budget/minimized failures for the changed risk; preserve counterexamples and source/tool hashes. Compile changed roots/units, relink when required, and use protected native/AT/IME/resource observations for claims that need them. A module move or passing model alone does not discharge retroactive QA debt.

Update the appropriate documentation quadrant and wiki lessons with the actual change and evidence. Record the decision, remaining gap and next migration. Close a debt item only with source revision, proportional verification and independent review. A debt item can span several original scenarios; do not replace the original acceptance ledger with this register.

Product work stays WIP=1 and native QA WIP=1. Parallel agents may prepare disjoint proposals/reviews and documentation; root integrates selected production changes. Deliver the shortest justified production improvement, not an endless audit or blanket rewrite. Keep original deadlines, Unknown/no-replay, ABI identity, drafts and preserved failures.

## Sprint debt queue

The register below is a starting inventory, not an ordered backlog or proof that unlisted code has been assessed. At each sprint, triage the selected existing boundary and keep a small queue in the sprint handoff or a linked owned record. Do not edit frozen evidence or turn every unreviewed component into a new blocker. Use these fields:

| Field | Required content |
| --- | --- |
| Original behavior | Existing requirement IDs and exact scenario names; any additional whole-EARS clause remains explicit. Supporting debt IDs never replace original identities. |
| Current baseline | Source revision/paths, implemented behavior, accepted evidence and its relevance, retained failures and stopped investigations. Unadjudicated does not mean unimplemented. |
| Boundary triage | State/event/effect/subscription/resource owner; contract or lifetime risk; existing production-route tests and model correspondence. Distinguish observed defect, missing evidence and proposed cleanup. |
| Selected change | One reversible production migration or fix, owner, declared paths and smallest decisive check. A support-only task names the concrete original behavior it unblocks. |
| Verification delta | Changed behavior/dependencies to requalify, positive and negative/lifecycle checks, applicable property/sequence coverage and independent review. Keep component, native, AT/IME, resource and release verdicts separate. |
| Documentation | Tutorial, how-to, reference and explanation each name an updated page or an explicit unaffected disposition; include command/source and local-link checks. |
| Carry-forward | Remaining original obligations and debt, why deferred, next concrete action, and any preserved no-progress count/timer. Completed support work does not reset a stopped investigation. |

Before integration, compare the delivered change with this queue entry. Retain failed baseline/counterexample evidence and record the final source revision and actual checks. An accepted scenario stays accepted on its recorded tuple unless a relevant behavior or dependency changed; a refactor does not silently accept new routes or invalidate unrelated evidence. Close the bounded debt item only after its declared source, QA, review and documentation obligations are met. Carry unfinished work forward without marking the original requirement or release complete.

## Initial register

These entries are observations/proposals as of October 29, not a completed whole-code audit. Track unreviewed ownership areas and newly found debt as the retrofit proceeds.

| ID | Existing area and evidence | Required retroactive work / next action | Status |
| --- | --- | --- | --- |
| DEBT-01 | SurfaceRenderer owns snapshot codec and HTML; OutputController/Presentation import it | Extract opaque pure SurfaceSnapshot, preserve codec/action/local-edit semantics; compile actual roots and run production-route equivalence, negative/lifecycle and seeded property checks. Original UI004/UX005/UI016 remain unchanged. | Implemented; three-root compile and bounded contracts/replays pass. [Evidence](../../../implementation/warlock/qa/evidence/pure-surface-snapshot-20261029/manifest.json); original native obligations unchanged. |
| DEBT-02 | OutcomeAnnouncements imports Html-bearing Announcement message/encoding | Pure AnnouncementMessage seam implemented; fresh three-root build, encoder equivalence and refusal replay pass. Notification replay retains byte-identical pre-existing failure; see DEBT-12. Preserve original accessible behavior obligations. | Implemented structural extraction; no original/native acceptance |
| DEBT-03 | Build/package input lists and qualification depend on multiple immutable historical receipts | Consolidate a reviewed current production target/recipe without losing exact source, tool, object order, provider and ABI checks; keep old evidence immutable. | Frontend capture/build/validate implemented with reviewed 229-input lock, protected three-root build and 34 checks; [evidence](../../../implementation/warlock/qa/evidence/current-frontend-build-20261030/LIMITS.md). Local unchanged-native composition validation now has [retained 4,105-input/42-check evidence](../../../implementation/warlock/qa/evidence/current-native-composition-20261030/LIMITS.md); The current composition was consumed by the isolated native attention fixture: original UX009 independently accepted with 52/52 checks, actual AT state, pixels, physical activation and normal cleanup; [scope and retained failures](../../../implementation/warlock/qa/evidence/attention-native-composed-20261030/LIMITS.md). The later [receipt-corrected composition](../../../implementation/warlock/qa/evidence/receipt-current-composition-20261030/LIMITS.md) qualifies the Effects change with capture 9, contracts 51 and release selection 23 while preserving all native identities and permission decisions. Full native/source provenance, other runtime routes and release gates remain open. |
| DEBT-04 | shared-host.c textually includes host.c; native callbacks/globals share lifecycle | Map actual resource owners and extract one owner at a time; preserve ordering, failure/drain policy and callback custody before changing scheduling. Native regression required for changed ownership. | Identified; no lifecycle repair claimed |
| DEBT-05 | Actual compiled Desktop/ShortcutPreferences baseline reproduces draft loss on matched Refresh/reopen and mismatched pending-read settlement | Baseline report `a6bc101e7fa683b5027759477f9bb640791db26c62c30b8da71039b93b7eacb3`: 15 checks, 10 positive controls and exactly 5 expected preservation failures on unchanged reducer `d9196ada…`. Preserve this RED trace. The refined local model passes 26 named checks and six sampled invariants; the authored correction passes a fresh three-root build, all original 15 regression checks, unchanged legacy 15 checks and 200 seeded production sequences. Independent source correspondence review `ca9bd2e9…` is ready and the bounded correction is integrated in `c5cf882f1`; [canonical evidence](../../../implementation/warlock/qa/evidence/shortcut-draft-preservation-20261029/manifest.json) preserves baseline, failures and current checks. Reads never auto-save/apply/replay. | Bounded correction integrated; original UI020 native/guidance/restart/AT/offline obligations remain open |
| DEBT-06 | First-enable guidance/help and optional-use witnesses are incomplete | Assess visible keyboard-reachable offer and use-before-onboarding against original UI020; preserve explicit shortcut choices and separate offline recovery. | Original behavior/evidence gap; open |
| DEBT-07 | Current native trial reports WebKitJavascriptError601 across several receivers and host exit1 before guidance | Retain actual receiver/error evidence; unsupported value and termination cause unproven. Existing investigation stopped after two qualifications; do not retry unchanged or call diagnostics a repair. | Observed failure; unresolved |
| DEBT-08 | Loading/authorized-historical/current-live/unavailable preview and pin/top behavior has separate remaining native obligations | Preserve Windows-like semantics in every migration; review original applicable native, keyboard, accessibility and resource oracles. | Incomplete original obligations |
| DEBT-09 | AT/IME/resource and representative whole-system journeys remain separate gates | Connect relevant current implementation routes, models and actual observations; do not infer from HTML or generic fuzzer passes. | Incomplete original obligations |
| DEBT-10 | Reproducible packaging, draft preservation and reversible Omarchy deployment incomplete | Prove current package composition, isolated install, actual draft survival and rollback before treating a main-session trial as ready. | Incomplete original release obligations |
| DEBT-11 | Product docs and engineering lessons scattered between source, handoffs and external journal | Maintain versioned Diátaxis docs and LLM wiki, link authoritative status/evidence and review command correctness at integration. | Four Diátaxis quadrants established, including the [retrofit how-to](../../warlock/how-to/retrofit-existing-code.md); command/link review and behavior-specific coverage remain ongoing |
| DEBT-12 | NotificationAnnouncementReplay fails six DND/urgency/control assertions identically before and after message extraction; all emitted frames remain closed | Establish actual setup/control reachability and diagnose the cause in a separately selected slice. Preserve expectations and both [failed traces](../../../implementation/warlock/qa/evidence/pure-announcement-message-20261029/manifest.json); no automatic policy waiver or unchanged retry. | Fixture admission defect corrected: current native idle observation now enters the real incoming route; all original 14 plus 10 admission/reachability controls pass, with unchanged model 10 named tests and bounded safety/witnesses. [Evidence and limits](../../../implementation/warlock/qa/evidence/notification-admission-20261030/LIMITS.md). No production policy change or original native/AT acceptance; retained six failures remain historical. |
| DEBT-13 | Actual output retirement + expected projection + exact late Committed outcome cleared unresolved/issued records while the current transaction stayed Unknown | Correct exact-intent/protocol settlement independently of current observed output; preserve current scene, newer request and no replay. Fresh three-root build, 12 named model tests/five bounded samples and 200 fixed-route parameter cases pass; [retained baseline, fixture failure and results](../../../implementation/warlock/qa/evidence/receipt-output-lifecycle-20261030/LIMITS.md). | Bounded correction verified; original Committed/Pending/Refused/disconnect-Unknown fixtures individually accepted on immutable source a4168e633; native delivery/Cancelled/full proof-release remain separate |
| DEBT-14 | Native Restore cancellation lacked an authenticated decision owner/channel; local withdrawal could not certify no native mutation | First opt-in owner/parser/typed-executor implementation now compiles with exact owning ABI, bounded owner/formatter checks and unchanged-provider closure. [Evidence/limits](../../../implementation/warlock/qa/evidence/native-restore-cancellation-20261030/LIMITS.md). Complete actual host/adapter/Elm opt-in, durable ACK custody, scoped Escape, dependency/resource proofs, new source composition and native interleavings; retain broader original operation obligations. | Native source plus strict client integrated; [real native two-order fixture](../../../implementation/warlock/qa/evidence/native-cancellation-client-20261030/LIMITS.md) passes with normal cleanup. All ARC012 cases remain partial for original generation-retirement/Escape gaps; optional V7 persistence now passes [store fault/restart/capacity checks](../../../implementation/warlock/qa/evidence/cancellation-store-20261030/LIMITS.md) after retained restart/provenance repairs; [internal coordinator wiring](../../../implementation/warlock/qa/evidence/cancellation-coordinator-20261030/LIMITS.md) now passes real-store ordering/lifetime tests with strict doubles; no original acceptance or routed production daemon/Elm workflow |

## Settings migration retrofit — ELM-DEL-015

The actual schema-1 settings save overwrote the original without a backup; the
protected RED baseline is retained. The correction preserves exact original
bytes and confirms backup durability before active replacement.
[Original acceptance and independent review](../../../implementation/warlock/qa/evidence/settings-migration-verification-20261030/acceptance.json)
accept all four original scenarios and the current settings-storage EARS. Evidence
separates 47 existing settings checks, 327 migration checks, 56 checks across
eleven actual abrupt process exits, and the model's 29 named tests/five bounded
samples. Other adopted fixed-schema stores and recovery imports are covered by
explicit source correspondence, not newly rerun runtime matrices.

The bounded migration debt is closed against those original oracles. Two-link
interruption remains recoverable but refuses automatic retry; post-rename sync
failure remains Unknown. Hardware power-loss, native settings UX, accessibility,
resource and release obligations are separate. The
[storage reference](../../warlock/reference/settings-storage.md) documents the
interface and limits. Cancellation's stopped investigation remains separate.

## Diátaxis documentation contract

Use the [primary Diátaxis framework](https://diataxis.fr/): tutorials teach through a guided learning experience; how-to guides help accomplish a defined task; reference provides accurate lookup material; explanation develops understanding and rationale. Keep each page's purpose clear and link across quadrants instead of mixing a long procedure with design discussion.

Write against actual current behavior and the intended reader. Name machine-specific prerequisites, version/source identity and meaningful limits. Tutorials must not require deploying a known failing host to the user's desktop; use a bounded safe learning path. How-to commands must be checked against the repository's actual tools and protection rules. Reference distinguishes implemented, verified and proposed interfaces. Explanation records decisions and rejected alternatives without presenting proposals as delivered architecture.

At each sprint/integration gate, update documentation for the changed behavior, contract, build, test or deployment path; check local links and command/source consistency. Use Scrapling for research/downloads. Documentation lint and reviewed commands are documentation evidence, not GUI acceptance. Maintain lessons/ideas in the wiki; keep durable product instructions in the appropriate Diátaxis quadrant.

## Completion evidence

The retrofit is complete only when the active ownership inventory and its applicable original boundaries have been assessed, relevant debt has been implemented or explicitly adjudicated against original requirements, proportional QA and independent review cover actual source, documentation matches the delivered system, and original release gates are satisfied. This page, a table status or a green linter does not establish that result.

Cancellation custody retrofit: [current isolation evidence](../../../implementation/warlock/qa/evidence/cancellation-isolation-20261030/LIMITS.md) retains
two reproduced storage defects and their fixes: typed full-key exclusion from
legacy retirement and locked V7 namespace ownership before legacy migration.
Nine store groups and three coordinator groups pass on the recorded source tuple;
the isolation model has 13 named tests/four bounded samples and does not model
namespace downgrade. C/Elm admission/delivery, physical Escape, generation resource
and original native/release obligations remain open. No new original acceptance.

## Applications feedback migration — ELM-UI-007

The selected restore Pending/Refused/Unknown slice exposed Applications masking already-existing window feedback. Source composition now preserves the launcher query/guidance and older unresolved recovery without any new effect authority. The initial input fixture RED and the actual masked-feedback/older-Unknown failures are retained. A passing browser container/AX check then missed vertically clipped leading text at320px; root and reviewer found it in the screenshot, so renderer alignment and a text-range regression are required. [Source-bound slice record](applications-window-feedback-20261031.json) carries current results and four Diátaxis dispositions. Original UI007/native/AT/release remains open; this is a bounded migration, not a whole-EARS closure.
