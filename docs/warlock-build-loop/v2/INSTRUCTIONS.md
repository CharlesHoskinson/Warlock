# Warlock implementation loop

Effective October 7, 2026, following the [nine-reviewer AAR](../../warlock-workflow-review/20261007/AAR.md). These instructions supersede v1's scheduling, derivative-copying, reporting and automatic validation sequence. Preserve historical source and evidence. The user requested implementation, not another research or infrastructure program.

## Outcome

Deliver one coherent Warlock Elm window system covering the frozen 242 requirements / 417 scenarios, mandatory S01–S16, additive right-click requirements, adopted FRP/Elm and design-language contracts, Warlock branding and the Omarchy vocabulary/keybindings. Preserve optional C00–C06 feasibility gates. The full original scope remains; this workflow changes execution, not acceptance standards.

Completion requires applicable original scenario oracles, one reproducible source/core/plugin/toolchain tuple, representative journeys, native presentation/input, AT/IME, measured resource/performance budgets and reversible deployment/rollback with drafts preserved. A bounded feature can be accepted before the release. Do not claim a whole release from component passes.

## Current source and inputs

- `implementation/warlock/` is the only new product integration candidate. It begins with GUI143 source, recorded by `ANCESTRY.json`. Edit it incrementally and use Git history. Existing versioned directories and accepted/failed reports remain frozen; reference unchanged artifacts by hash.
- Read `STATE.json`, the selected row of `requirement-ledger.json`, its original requirement object in `docs/elm-roadmap/requirements.json`, and the files to change. Read historical reports only to resolve a specific question. Do not reread every handoff on every continuation.
- Preserve the five already-dirty files and other workers' paths. A stale lane label does not prove a worker is running. Compare relevant old-lineage modules before adopting them; do not merge older prototypes wholesale or change ABI identity by name alone.
- Warlock philosophy, design-language and FRP adoption plans remain product constraints. Their W/CONTROL/DL tickets are supporting work, not substitutes for original requirement closure.

## Mandatory contributor plugin

At the beginning and end of every product implementation continuation, run `python3 -B docs/warlock-build-loop/v2/loop.py check`. This invokes the shared offline plugin with `--require-record`; a missing participant record cannot silently skip the contract. Scaffold the selected slice with `plugins/warlock-contributor/scripts/warlock.py start --owner <owner>`. Preserve old records and select a new `--record` when moving slices. Explicitly adopt only your own declared dirty source paths with an ownership note. Read [the contributor guide](../../../CONTRIBUTING.md) and [plugin contract](../../../plugins/warlock-contributor/references/contract.json) for the CLI and evidence fields.

The plugin applies the AAR's source ownership, original scenario identities, evidence freshness, proportional checks and no-progress rules. It neither executes builds nor accepts a GUI oracle. Explicit user-requested plugin/support work calls `python3 -B plugins/warlock-contributor/scripts/warlock.py check --project-only` before and after with proportionate checks; it needs no fabricated GUI slice and cannot count as original GUI closure. Host hooks are advisory and host trust/discovery limits do not replace mandatory calls. This repository's loop uses the plugin even without installing an AI-client extension.

## One implementation cycle

Use [quint-llm-kit](https://github.com/quint-co/quint-llm-kit) for behavioral models and implementation against them. Read its `quint-modeling` skill when creating or auditing a model, `quint-execute-spec` when implementing an existing model, and `quint-lang` for language/CLI details. Use the installed skills when available; their lightweight CLI workflow works across contributing clients. Keep the model linked to the selected original EARS/scenario and actual source functions. Check executable initialization, positive reachability witnesses and safety invariants incrementally with typecheck and sampled runs; retain counterexamples and explain the abstraction's limits. Run explicitly selected named tests as well. A sampled/model pass remains separate from native GUI acceptance. Preserve existing user authorization and original acceptance properties; a new model must not weaken an original requirement to fit broken code.

1. **Select one product slice (WIP=1).** Record 1–3 original IDs, exact original scenario names, before/after user behavior, source paths, owner and the smallest decisive verification. Native execution is also WIP=1. Parallel help, if authorized, addresses this slice only.
2. **Implement in the candidate.** Integrate the change into the runnable application. A supporting safety/infrastructure task must name an observed blocker and the original scenario it unblocks. Do not mint another CONTROL series or source directory because more schedules can be imagined.
3. **Verify proportionately.** Compile changed Elm entry points or native units and relink. Run the direct behavioral regression and one meaningful negative/lifecycle case. Use Quint/fuzz when concurrency, authority or reducer invariants change. UI/layout/message changes do not automatically require a new model. Broaden regression at integration milestones or when a concrete failure/dependency warrants it.
4. **Match evidence to the original verification text.** Bridge evidence is sufficient where the original says native **or bridge**; native, keyboard, AT, physical presentation and hardware claims need the evidence each requires. Browser rendering is component evidence. Run the relevant original native journey when ready, using the protected serialized launcher below. Do not automatically rerun the entire 119-command suite for a document, fixture or independent view change.
5. **Record the result.** Add the source revision, immutable evidence reference/hash, exact oracle, evidence scope, missing observations and reviewer disposition to the scenario row. Close a scenario only when its own obligations pass, and a requirement only when all applicable scenarios and verification obligations pass. Source changes invalidate only relevant evidence, not every unrelated accepted scenario.
6. **Commit the actual delta and continue.** Publish owned changes in a normal batch under existing authorization. No separate publication-receipt commit, no copied QA trees, no new public version counters. Retain failed reports locally and commit the minimal auditable report/evidence needed by the claim. Do not discard evidence required for reproducibility.

## Stop waste, preserve progress

After two consecutive qualification-only iterations, or 45 minutes without a production fix or an original-scenario verdict, stop expanding that investigation. Record the exact missing observation and pick another bounded mandatory product slice. The timer never authorizes bypassing a safety boundary. A failed scenario is useful diagnosis, not a delivered feature.

Do not mark the whole goal blocked merely because this threshold was reached. Follow the host tool's repeated-blocker rule; continue independent required product work where possible. Do not pause the goal without an explicit user request. No new review council, skill installation, plugin or broad research unless it resolves a concrete implementation obstacle or the user requests it.

Reports lead with what the user can now see/do, original IDs/scenarios advanced, what failed, and the next code change. Report available incremental time/token telemetry; call unavailable figures unavailable. Count neither commits, copied files, models, check totals nor administrative closures as GUI features. Report at least every 30 minutes across the loop, and keep active-turn commentary timely.

## Acceptance ledger

`requirement-ledger.json` preserves all 242/417 identities. `unadjudicated` means the older evidence has not been checked; it does **not** mean no implementation exists. Per scenario distinguish `unadjudicated`, `missing`, `implemented-unverified`, `partial`, `failed`, `blocked`, and `accepted`. Every accepted entry includes its original oracle and verification scope, immutable evidence/hash, source tuple and independent reviewer disposition. Requirement acceptance and release acceptance are separate fields.

Bounded existing-evidence reconciliation accompanies the same product slice. Candidate closures include ARC-014 and REV-005, but do not accept them from favorable prose alone. ARC-014's lost-ack/same-effect retry ambiguity and REV-005's missing-mapping admission oracle need explicit disposition. Administrative acceptance is reported separately from usable GUI delivery.

## First product sequence

1. **Visible window-action feedback, ELM-UI-007:** Pending, Refused and Unknown must be visibly distinct after an action, with existing read-only recovery reachable and no repeated effect. Fix the current hidden bar status and the recovery message that masks Pending/Unknown. Compile actual views, check typed-state projection, visibility at narrow/wide widths, duplicate suppression and persistent Unknown. Native/AT acceptance remains a separate verdict.
2. **Taskbar and focus journeys, ELM-UI-004 / ELM-UX-005 / ELM-UX-008 / ELM-UX-024:** demonstrate inactive activation, active minimize, minimized restore, exact group selection and dismissal with real recipients. Investigate the retained Native202/203 focus failures; do not add a manual focus workaround to qualify restoration. Close only exact covered scenarios. Integrate persistent catalog pins/zero-window launch under UI-004/UX-004 next.
3. **Launcher search, ELM-UI-005 / ELM-UX-029:** current-query/catalog selection, frozen exact/prefix/token ranking over localized metadata, no-match/unavailable, one Enter launch and query-preserving refusal. Reuse native launch authority; never execute user text as a command. Preserve IME/preedit semantics and qualify them with actual native evidence.
4. Continue switcher/Task View/workspaces, snap/pin/drag/output navigation, visible authorized preview/fallback, settings/notifications/Files/right-click and design-language/Omarchy integration. Schedule original preview13/restore38/recovery34/drag52, AT/IME/hardware/resource/journey gates at the matching integration milestone, then package and prepare reversible deployment.

Visible preview reveal is a product obligation; the existing controlled opacity-0 curtain and ineligible root scope stay until the actual native ownership/presentation conditions are implemented. Do not turn every remaining asynchronous schedule into a prerequisite for unrelated shell delivery.

## Protected execution and authority

Keep one authoritative immutable Elm policy for each responsibility; projection-only view models do not create effect authority. Compose related subsystems through typed events and one integration root. Do not add an independent frontend/native window policy, or perform a wholesale root rewrite merely because several Elm programs exist.

Preserve exact owning core/plugin ABI, source/toolchain identity, original deadlines/clocks, grants/incarnations, Unknown/no-replay, actual custody retirement, failed evidence and the five crash-noise fixes in `docs/crash-noise/HANDOFF-codex-window-qa.md`.

Native GUI campaigns run serially:

```sh
python3 -B docs/warlock-build-loop/v2/loop.py native --runner /absolute/reviewed/runner.py
```

CPU/browser QA uses the unchanged protected launcher:

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B /absolute/reviewed/check.py
```

Maintain core limit 1, valid parent Wayland socket, private owned session directory, exact ABI pair, no DRM/XWayland fallback, and normal owned-helper cleanup. Prepare actual deployment/rollback/preservation checks before any genuinely required session-activation approval; do not restart the user's main compositor incidentally.

Only the host goal tool arms automatic continuation. These files are instructions, not a daemon. Keep the full goal active until achieved, explicitly paused/cancelled, budget-limited, or blocked under the tool's actual rule.
