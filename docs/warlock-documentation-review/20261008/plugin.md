# Warlock contributor documentation audit (auditor 1 of 3)

**Scope.** Read-only. Baseline prose comes from the frozen `inputs/` snapshot. Claims are checked against current `plugins/warlock-contributor`, `implementation/warlock`, `DesignLanguage/catalog/v6`, and the argparse source in `scripts/warlock.py:1054-1114`. I executed no CLI or host client, so host-validation statements rest on the recorded `qa/validation-v014.json`. This audit makes no GUI acceptance claim.

## Prioritized findings

### P1. The catalog and DesignLanguage docs never mention the contributor plugin or how to contribute

- **Catalog navigation:** `catalog/v6/catalog.js:9-10` defines Foundations and Practice (`patterns, accessibility, library, references, evidence, changelog`). There is no contribute route.
- **Catalog text:** the only "plugin" string is the ABI phrase at `catalog.js:53`.
- **Catalog README:** `catalog/v6/README.md` covers serving and receipts only.
- **DesignLanguage README:** `DesignLanguage/README.md:10` still says "The website implementation remains in progress. It will explain…" and never links `catalog/v6/index.html`, `CONTRIBUTING.md` or the plugin.

### P1. The catalog documents a frozen source closure, not the editable product, and nothing tells contributors

- `catalog/v6/qa/generate.py:27-30` hashes every module against `DesignLanguage/research/v1/consensus-inputs/implementation/warlock-preview-provider-v1` and asserts equality.
- Component pages are labelled "GUI519-derived closure" (`generate.py:11`, `catalog.js:30`).
- The editable candidate is `implementation/warlock/`, which inherits GUI143 (`implementation/warlock/README.md:3`, INSTRUCTIONS `:13`).
- Consequence: anyone reading catalog behavior as current product behavior will be wrong.
  - Current `src/Effects.elm:12` adds `Pin | Unpin | Maximize | RestoreGeometry | …`.
  - `Provider.elm:418` swaps labels between "Always on top" and "Unpin window".
  - The catalog's menu inventory (`generate.py:19`) predates these changes.

### P1. `verify-plan` does not cover the active slice, and the README implies it covers "pins"

- **Active slice:** `STATE.json:10-46` is `observed-pin-max-state`, ELM-UX-016, `in-progress`.
- **No mapping for it:** `warlock.py:441-524` has no ELM-UX-016 branch. Native `modes` stay empty, so it suggests no native candidate.
- **What it does suggest for the slice's files:**
  - `Taskbar/Surface/SurfaceRenderer/ActionProjection.elm` get flagless `check-search.py` (`:489-496`).
  - `Effects.elm` gets `check-feedback.py` (`:497-498`).
  - `Provider.elm`, `NativeProvider.elm` and `Shell.elm` fall to `unmapped` (`:499-500`).
- **Decisive runners exist but are never suggested:**
  - `qa/check-search.py --pin-max` (`check-search.py:3,46-49`).
  - `qa/native-pin-max.py`, which takes no arguments (`:7`).
- **Misleading README wording:** `README.md:222` says "The map covers … pins". That means ELM-UX-004 catalog pins (`--pins`, `--taskbar-pins`, `:495,517-518`), not always-on-top.

### P2. "Pin" names three different things

1. ELM-UX-004 persistent taskbar pins: `implementation.md:14`, `Surface.elm:244` ("Unpin " ++ label).
2. UI-008 `--pinned-menus`.
3. ELM-UX-016 always-on-top `Effects.Pin/Unpin`: `MenuBridge.elm:146`, `Surface.elm:382-383`.

Neither the docs nor the implementation map distinguish them.

### P2. Pin/MAX is undocumented in the product README

- The current `implementation/warlock/README.md` has no match for maximize, MAX, "pin to" or "always on top", even though `README.md` is a declared slice path (`STATE.json:39`).
- The only account is `qa/evidence/pin-max/README.md:3-5`, with manifest disposition `implemented-unverified` (`manifest.json:53`).

### P2. The implementation map is stale

`references/implementation.md:7-17` covers only the early slices. It has no rows for:

- pin/MAX
- snap
- transfer
- settings, high contrast, motion
- notifications, system, Files, jump lists
- attention, keyboard shell, drag ownership
- IME, AT
- picker previews

All of these are described in `implementation/warlock/README.md:68-322`.

### P2. The two workplans contradict each other

- `DesignLanguage/WORKPLAN.md:11-15` (current, confirmed) leaves the inventory, tokens, catalog, qualification and publish items unchecked.
- `DesignLanguage/catalog/WORKPLAN.md:11-15,61` checks them and records closure.
- `DesignLanguage/README.md:6` links the stale file.
- `catalog/WORKPLAN.md:63` hard-codes the remote `382523ab…`, which no longer matches the stated public `feature/elm` head `9a4fdd52…`.

### P2. Onboarding defaults to someone else's in-progress slice

- `CONTRIBUTING.md:8-14` and plugin `README.md:13` show `start --owner your-name`.
- That adopts `STATE.activeSlice` (`warlock.py:1191`), which is the in-progress pin/MAX slice with an existing owner (`STATE.json:3`).
- New Claude Code, Codex or Grok contributors should be told to use `plan` → `preflight` → `start --slice-file` unless they own that slice.

### P3. Machine-local paths are presented without a portability note

- `/home/hoskinson/window-integration-qa` is hard-coded at:
  - `workflow.md:8`
  - INSTRUCTIONS `:71`
  - `warlock.py:455`
  - catalog `generate.py:4`
- `workflow.md:17` gives the rule for other machines, but neither the catalog README nor CONTRIBUTING says that catalog regeneration and CPU QA require this launcher or a reviewed equivalent.

### P3. Minor accuracy issues

- **Hook timeout wording:** `README.md:282` says "five-second checker timeout". The inner subprocess timeout is 5 s (`session_hook.py:32`), but the host hook timeout is 10 s (`hooks/hooks.json:9`, `codex.json:9`). State both.
- **CI wording:** `README.md:327` says the CI template uses "project checks". The template runs `--json check` without `--project-only` (`warlock-contributions.yml:26`). Either align the wording or verify the behavior on a recordless checkout.
- **`self-test` placement:** it appears in the quick-start block (`README.md:9`) but is described as optional (`:88-89`). Mark it optional there.
- **Typography:** missing spaces in "on30", "Cross-review60", "all49", "allB1–B3", "exact959" (`DesignLanguage/README.md:3`, both workplans).

### Verified accurate (no change needed)

- **Subcommands:** every subcommand in `README.md:7-19` and `:36-341` exists with matching flags.
- **`claim`:** cannot emit `accepted` (`warlock.py:1094-1095`).
- **Output flags:** `--markdown` and `--json` are mutually exclusive (`:1125-1126`).
- **Record ignore rule:** records must be Git-ignored (`:1136-1138`), and `.gitignore:5` supplies the ignore.
- **Manifests:** both are `0.14.0`.
- **Marketplaces:**
  - `.claude-plugin/marketplace.json` matches `warlock-contributor@warlock`.
  - `.agents/plugins/marketplace.json` exists.
- **Hosts:** Grok passive-hook early return matches `session_hook.py:18-20`.
- **Links:** the AAR, ROADMAP, `consensus.md` and the design-language INSTRUCTIONS all resolve.

## Proposed catalog section: "Contribute" Practice page

**Where it goes.**
- Add `['contribute','Contribute']` to `patterns` in `catalog.js:10`, between `evidence` and `changelog`.
- Mirror it as a "Contributing" section in `catalog/v6/README.md`.
- Link both from `DesignLanguage/README.md`.
- Whether v6 is edited in place or a new derivative is created is an owner decision, because `AGENTS.md:8` freezes versioned components.

**Draft content.**

1. **Purpose.** "The Warlock contributor plugin is a shared offline Python checker and skill (`warlock-contribute`), with thin Claude Code, Codex and Grok packaging. It scaffolds work against original EARS scenarios, protects other contributors' drafts, suggests proportional checks and keeps evidence scoped. It runs no builds and accepts no GUI oracle."

2. **Actual commands.** Run from the repository root:
   - `warlock.py doctor`
   - `status`
   - `capabilities`
   - `remaining --requirement ID --markdown --limit 3`
   - `inspect --requirement ID --scenario NAME`
   - `--json plan … > .warlock-contributor/x.json`
   - `preflight --slice-file …`
   - `start --owner … --slice-file …`
   - `extend`, `verify-plan [--selected]`, `claim`, `record`, `handoff`, `report --markdown`, `review`

   Product continuations begin and end with `docs/warlock-build-loop/v2/loop.py check`. Design, documentation and plugin work use `warlock.py check --project-only` before and after.

3. **Integration points.**
   - Product source lives in `implementation/warlock/`.
   - Originals live in `docs/elm-roadmap/requirements.json` and `openspec/changes/elm-desktop-pivot/specs/`.
   - Design contracts WARLOCK-DL-001…030 live in `DesignLanguage/EARS.md` and `openspec/changes/warlock-design-language/`.
   - Native campaigns run through `loop.py native --runner`. CPU QA and catalog regeneration require the protected `qa_run.py` launcher (machine-local path) or a reviewed equivalent.

4. **Limitations.** Include all of the following:
   - This catalog renders a frozen GUI519-derived closure (`warlock-preview-provider-v1` inputs), not current `implementation/warlock`.
   - Browser demonstrations carry no native authority.
   - Plugin records are self-attested.
   - Hooks are advisory, and Grok's hook delivers no context.
   - Codex hooks need manual installation and trust.
   - The CI template is not active.
   - `verify-plan` is not complete coverage.

5. **Implementation-first workflow.**
   - A design change that affects product behavior is implemented in the runnable Elm root, through its typed messages, effects and native authority, under an original requirement slice.
   - A DL ticket supports that slice but never substitutes for it (INSTRUCTIONS `:16`, `WORKPLAN.md:3`).
   - The catalog is updated afterward, as documentation of the delivered source.

6. **Contributing design changes.**
   1. Name the DL contract and the original EARS ID.
   2. Edit tokens and CSS in the product.
   3. Verify the claim-specific browser and native evidence.
   4. Then regenerate the catalog from a declared source closure.
   5. Record findings, such as missing checked semantics, under "Current product findings".

## Other concrete edits

- **Plugin `README.md:222`:** replace "pins" with "persistent catalog pins (ELM-UX-004)". Add: "ELM-UX-016 always-on-top/MAX is unmapped. Inspect and run `qa/check-search.py --pin-max` through the protected CPU launcher and `qa/native-pin-max.py` (no arguments) through `loop.py native`."
- **`references/implementation.md`:**
  - Add a row "Always-on-top / MAX (ELM-UX-016)" covering `src/Menu.elm`, `MenuBridge.elm`, `Provider.elm`, `Effects.elm`, `Surface.elm`, `native/authority.cpp` and `native/geometry-effects.inc`, with the two runners above.
  - Add a "Pin terminology" note.
  - Add rows for the later slices using the flags documented in `implementation/warlock/README.md`. I did not verify those runner flags here.
- **`implementation/warlock/README.md`:** add a pin/MAX paragraph that paraphrases `qa/evidence/pin-max/README.md:3-5`, including the failed second native run and the `implemented-unverified` disposition.
- **`CONTRIBUTING.md:8-14` and plugin `README.md:13`:** show the `plan`/`preflight`/`start --slice-file` path for new contributors. Say that bare `start` adopts the current `activeSlice`.
- **`DesignLanguage/WORKPLAN.md:11-15`:** synchronize the checkboxes with `catalog/WORKPLAN.md`, or reduce it to a pointer to that file.
- **Remote hash:** relabel `catalog/WORKPLAN.md:63` as historical. Do not embed the live head.
- **`DesignLanguage/README.md:10`:** replace with a link to `catalog/v6/index.html`, the serve command and the Contribute page.
- **`README.md:282`:** state "5 s checker subprocess inside a 10 s host hook".
- **Typography:** fix the missing-space typos listed above.

## Remaining implementation checklist (ELM-UX-016 and beyond)

- [ ] **Fix the context gesture defect.** Preview arrival resizes the picker row between press and release, so the release reaches another family (`pin-max/README.md:5`).
  - The fix must hold target identity across press and release, or keep row geometry stable through preview arrival.
  - It must not use a focus workaround and must keep native authority intact.
- [ ] **Rerun the original native journey through `loop.py native`.** It must cover maximize, pin and unpin on a maximized family overlapping a float, the native scene and hit target, and agreement with the displayed state (`STATE.json:43-45`).
- [ ] **Confirm replay coverage.** The 13 passing replay checks must cover pending, stale and Unknown versus correlated states, with no replay of unresolved effects.
- [ ] **Decide checked semantics for the "Always on top" item.** The `src/` grep found no `aria-checked` (DL-007); applicable AT remains open.
- [ ] **Record and review.** Record a `partial` claim with explicit missing observations. Accepted status later requires the full commit hash plus an independent reviewer.
- [ ] **Release gates remain open:** native AT/IME, hardware, resource budgets, representative journeys, reversible deployment (INSTRUCTIONS `:9`), and the DL-001…022/030 product adoption.

## Claims that must remain bounded

- **Pin/MAX:** it compiles and 13 focused replays pass. That is component evidence only.
  - The native pin/MAX journey was never reached, and the disposition is `implemented-unverified`.
  - The feature is incomplete.
- **Catalog:** the 42 source/token and 104 browser checks cover the frozen GUI519-derived closure in a browser only.
  - They are not current-product evidence.
  - They are not native evidence.
  - They are not WCAG or AT evidence.
- **Plugin:**
  - A pass is structural compliance only.
  - Hooks are advisory and not shown to execute live.
  - The Claude and Grok "validation passed" result comes from the v0.14 packet and was not re-run here.
  - Codex live install and trust were not performed.
  - CI is a template and is not active.
- **Native accessibility, IME, resource and hardware obligations:** unqualified.
- **Release:** `releaseAccepted: false` (`STATE.json:58`). Merging or publishing does not change that.
- **Branch state:** the public `feature/elm` head and the older `main` are facts supplied by the owner. This audit did not verify them.

## Recommendation

1. Apply the documentation fixes above in one owned batch:
   - the Contribute page specification and README links
   - the `verify-plan` scope wording and implementation-map rows
   - the pin/MAX README paragraph
   - workplan synchronization
   - onboarding via `plan`/`start --slice-file`

   Validate the batch with `check --project-only` before and after.
2. Publish the pin/MAX work to `feature/elm` as an explicitly partial draft. Exclude the untracked `qa/build-*/mutable-elm-home/` and `check-*/profile/` directories (catalog `README.md:15`).
3. Do not merge to `main` or describe pin/MAX as complete until the gesture defect is fixed and the native ux-016 journey is observed. That merge is outward-facing and needs the owner's explicit confirmation.
4. Adding a `verify-plan` mapping for ELM-UX-016 is optional plugin work. The documentation correction alone resolves the misleading claim.
