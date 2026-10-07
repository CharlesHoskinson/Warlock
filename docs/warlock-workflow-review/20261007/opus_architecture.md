# opus_architecture review: real code progress vs. prototype sprawl

## Bottom line

There is real product code, and real defects were found and fixed on real WebKit. But the work is not converging into one application. Every change copies the whole tree into a new versioned directory. At least three lineages exist on what appear to be different ABI tuples, and none has been reconciled. The "single immutable Elm policy" is true within the preview subsystem only, not for the application. The last two full campaigns changed no production source. The preview route that got most of the custody engineering is inactive in the product and kept at opacity 0.

## Findings, ranked by severity

**F1 — Critical: every change copies the whole tree, so there is no trunk.**
- `implementation/warlock-preview-provider-v1`…`v143` are 143 full directories. Each has its own `src/Main.elm`.
- There are 358 `implementation/*/elm.json` projects (e.g. `elm-output-controller-v141/142/144/145`, `elm-shared-staged-menu-carrier{,-fixed,-complete}-v30x`).
- `git-24h.json` lists 90 commits.
  - Each "Qualify…" commit reports 184–1208 `productSourceFiles` and up to 16,515 `qaFiles` (lines 11–12, 3206–3207, 8852–8853).
  - Each is paired with a "Record public…" commit carrying 0 product files.
  - The real authored deltas are small: v94 changes 4 files (`source-deltas-94-143.json:7-29`). So the per-commit path counts mostly measure copying.
- The process mandates this. `INSTRUCTIONS.md:22` says: "Use fresh source derivatives for changes to frozen components."
- Result: no diff is reviewable, "current source" is ambiguous, and every reader pays for duplicates.

**F2 — Critical: three implementation lineages are unreconciled.**
- `loop-state.json:33` and `implementation-status.json:3` name `elm-recovery-delivery-general-reviewed-v656` as current. Its SPEC selects production 640 on "core205/Aquamarine155" (`v656/SPEC.md:5-6`).
- `INSTRUCTIONS.md:32` says to continue from `elm-preview-provider-host-v519` on core205/native492.
- The last 24 hours of work happened in `warlock-preview-provider-v86→v143` on "GUI143/core16/plugin19/AQ155" (`HANDOFF.md:797`; `component-report-combined-restart-204-207.json:6`).
- `INSTRUCTIONS.md:34` explicitly requires reconciling "lanes into one release tuple". That was never done.
- **Unverified:** whether core16 and core205 are different numbering schemes for the same artifact.

**F3 — High: there is no single application policy.** In v143:
- `Main.elm:28,61` is a `Browser.element` that owns the desktop/window policy (`Outputs.Model`) and renders `text ""`.
- `Popup.elm:27` holds a `RetainedPreviewPresenter` model inside WebKit.
- `NativePreviewPolicy.elm:11-13` is a `Platform.worker` holding the same `Preview.Model` in native JSC.
- `NativePreviewRenderer.elm` and `Bar.elm` are further programs.
- So the preview policy is instantiated once per route (legacy vs controlled), and the window policy is a separate program bridged only through native code.
- `HANDOFF.md:280` ("No second window policy") holds only for the preview subsystem. The `INSTRUCTIONS.md:7` mandate ("one immutable Elm policy state") is not met at application level.
- Policy timing also lives in port wiring rather than in the model: 2000 / 2000 / 10000 ms timers in `Main.elm:36-38`.

**F4 — High: effort went into a feature the user cannot see.**
- The controlled host is "QA-only" (`HANDOFF.md:399`). The driver "links but remains inactive in the actual legacy host" (`HANDOFF.md:368`).
- The curtain is mandatory opacity 0 and root preview is ineligible (`HANDOFF.md:874`).
- GUI94–143 is roughly 50 slices of retirement, ticket, custody and confirmation hardening for a route no user reaches.
- Internal `CONTROL-026…049` contracts replaced original EARS IDs as the unit of progress (`HANDOFF.md:191, 235, 788, 832`).

**F5 — High: the latest campaigns are QA-only.**
- `HANDOFF.md:814` and `:862` both say "No production source changed".
- The combined report confirms it: `controlledPreviewRecoveryQualified:false`, `wholeHostRestartQualified:false`, `nativeAcceptance:false` (report lines 23–31).
- The evidence is valid, but it is not product delta.

**F6 — Medium: closure bookkeeping is broken in both directions.**
- `completedRequirementIds: []` (`implementation-status.json:35`) is not proof that zero original requirements are satisfied.
- The combined report sets `actualWindowCommandRestartQualified:true` and `actualWindowCommandDurableUnknownQualified:true`, but maps them to no original ID.
- `requirementsInProgress` holds 28 IDs with no per-scenario verdicts.

**F7 — Medium: the handoff is too expensive to read.** `HANDOFF.md` is an 876-line append-only log of hashes and counts. Every continuation re-reads it.

## What the code actually shows

Genuine progress, verified at source level:
- **ELM-UI-004:** a pure taskbar decision table exists in `Taskbar.elm:25-36`. It covers zero windows (Launch/Unavailable), a single window (Restore/Minimize/Activate) and multiple windows (Picker).
  - **Unverified:** the EARS also requires distinguishing pin from always-on-top and an explicit new-instance action. I did not find either in this file.
- **Real WebKit defects were found and fixed:**
  - the rapid-input drain bug (GUI133→134, `HANDOFF.md:603-616`)
  - stale-error ordering (GUI136→137)
  - same-URI reload (GUI140→141)
  - shared-process drain (GUI142→143)
- **Worth keeping:** the pure-receiver infrastructure in GUI117–119 (`HANDOFF.md:275-330`). It is the right base for consolidating to one policy.

Also measured:
- 90 commits in 24h.
- About 7.9M tokens / 22.5h cumulative on the goal (INDEX). There is no 24h-only token figure.

Unverified:
- Whether the v640 and v143 copies of shared modules (e.g. `Shell.elm`, `TaskbarShell.elm`) have diverged. Diffing them is step 1 below.
- Native minimize focus succession (ELM-UI-001). Minimize/restore commands run natively in Native204–207, but no focus-successor oracle was observed.

## Stop / start / retain

**Stop**
- Copying whole directories per change.
- "Record public" commits as a separate unit of work.
- Minting CONTROL-0xx contracts in place of original IDs.
- Hardening inactive routes.
- Appending hash prose to `HANDOFF.md`.

**Start**
- One mutable trunk directory with git as the version history.
- One root Elm model.
- Per-scenario verdicts on original EARS IDs.
- User-visible slices.

**Retain**
- ABI-tuple identity checks and serial native QA.
- Unchanged original deadlines and oracles.
- No automatic replay of Unknown outcomes; no grant resets.
- Draft, desktop and foreign-edit protections.
- Held failure evidence, left at its existing paths and never rewritten.

## Integration path

1. **Trunk (one bounded session, no product behavior change).**
   - Create `implementation/warlock/` from v143. Record the parent path and commit in a single `ANCESTRY.json`.
   - Diff v640's production Elm and native sources against v143, module by module.
   - Port only divergences that carry behavior. Name the owning tuple once.
   - From then on, changes are git commits in this directory.
   - Old `vN` directories stay frozen as evidence and are referenced by commit hash, not copied. This reduces duplication without rewriting held evidence.
2. **One policy.** Compose `Outputs.Model` and `Preview.Model` into one root model hosted in the existing native JSC worker (`NativePreviewPolicy`, GUI116). Then:
   - `Main`, `Popup`, `Bar` and the renderer become pure view programs, built on the GUI117–119 receivers.
   - Delete the legacy `Popup` preview state once the controlled route is the default.
   - Do this incrementally: first move window policy into the worker behind an unchanged port contract, using the existing replay modules as regression.
3. **Close requirements as you go.** Add `docs/elm-roadmap/delivery/closure.json`. Per original scenario name, record:
   - the evidence path and sha
   - scope: native, component or model
   - verdict: satisfied, partial or missing

   Individual scenarios close at native scope without waiting for the full release. Component evidence never counts as native.

## Operating rules

- **WIP:** one product slice at a time, with at most one native campaign in flight. No new versioned directories.
- **Escalate validation in steps:** Elm unit/replay tests → one CPU build → native runs for that slice's original scenarios only. Run the inherited regression suite only when shared native or ABI code changes. Do not add new Quint models unless a slice introduces new concurrency.
- **Report briefly:** at most 15 lines per slice: original IDs and scenarios, verdicts, diff stat, failures, next step. Hashes belong in `closure.json`, not prose.
- **Control cost:** stop a slice after 2 failed native attempts or about 400k tokens and record the blocker. Read the diff, not directory copies.

## Recommended first three slices

1. **ELM-UI-004 (taskbar primary-action table).**
   - Code: `Taskbar.elm` `primary`/`selection` and `TaskbarShell.elm`. Add pin vs always-on-top and an explicit new-instance action, plus the keyboard route.
   - Verify: Elm tests over the scenarios starting at `requirements.json:5098` (taskbar-zero and its siblings), then one native run per scenario.
   - Why first: it is safe — no compositor restart, and the core logic already exists.
2. **ELM-UI-001 (minimize focus succession: focus-successor, focus-last, focus-unfocused).**
   - Reuse the Native204–207 minimize fixtures, which already provide real pointer, compositor focus and keyboard recipients.
   - Add the successor oracle. Implement it in the native authority if it is missing.
3. **ELM-ARC-019 / ELM-GNO-008 / ELM-KDE-006 (visible noninteractive preview).**
   - Make the controlled route the default in trunk. Allow one physical reveal for an eligible family under a native pixel oracle; Native136/184 already provide red19200 references.
   - Keep root preview ineligible. Delete the legacy Popup preview state.

Closure audit, run in parallel and cheaply: assess ELM-ARC-002 (only native authority mutates windows) against Native198–207 evidence. Mark it satisfied only if each named scenario has native evidence.

## Risks

- Merging v640 and v143 may surface conflicting Shell/Taskbar semantics. Resolve these explicitly; never by quietly picking one.
- Composing one policy risks regressing the custody guarantees. Keep the existing replay and C-coupled suites as gates for changes to that code.
- An early reveal could expose stale pixels. Keep the GUI137/141 guards.

## Falsifiable success metrics (next 24h)

- New `implementation/*-vN` directories: **0**.
- At least 60% of commits change production source.
- At least 6 original scenarios (UI-004 and UI-001) have native verdicts in `closure.json`.
- Shared Elm modules exist in exactly one copy in trunk.
- Exactly one root Elm model owns window and preview policy, or a dated plan says which port remains.
- `HANDOFF.md` growth: 40 lines or fewer.
- Tokens per closed original scenario are reported.
