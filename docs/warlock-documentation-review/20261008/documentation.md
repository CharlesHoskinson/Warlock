# Warlock documentation audit: navigation, completion claims and remaining work

**Basis:** I read the frozen inputs and spot-checked the current source, plugin and catalog v6 with Read/Glob/Grep only. I ran nothing. Nothing here is GUI acceptance.

## Prioritized findings

### P0-1: The root README contradicts the current publication state and points readers at a superseded handoff
- `inputs/README.md:73` says "No remote is configured. Nothing has been pushed". The same file links GitHub at `:3`. `DesignLanguage/catalog/WORKPLAN.md:63` records a verified remote at `382523ab…`. The stated fact is that the public default branch is `feature/elm` at `9a4fdd52…`.
- `README.md:8` says "Start with the current handoff". That file, `docs/HANDOFF.md:1`, is dated **2026-10-03**. The v2 loop at `docs/warlock-build-loop/v2/INSTRUCTIONS.md:3` replaced its workflow on Oct 7.
- `README.md:70-71` cites "462 CPU tests" for the capture candidate, but `docs/HANDOFF.md:29` cites "V28: 444 CPU checks". Neither number names a source tuple.
- The contents table (`README.md:16-26`) omits `implementation/warlock/`, `DesignLanguage/`, `plugins/`, `openspec/` and `docs/warlock-build-loop/`. It also never links `CONTRIBUTING.md`.
- **Edit:** Replace `:5-12` and `:66-73` with a status block:
  - The active product is `implementation/warlock/`, on default branch `feature/elm`. `main` is older and not current.
  - The current workflow is the v2 INSTRUCTIONS plus `STATE.json`.
  - The ledger records 0 accepted requirements and `releaseAccepted: false`.
  - The 2026-10-03 handoff and the 462/444 counts are historical.
- Add table rows for the missing directories and a short "Contributing" section (see P1-6).

### P0-2: The two design-language workplans contradict each other
- `DesignLanguage/WORKPLAN.md:11-15` leaves inventory, tokens, catalog, qualification and publication **unchecked**. `DesignLanguage/catalog/WORKPLAN.md:11-15` has the same items **checked**, plus DL-023…029 `[x]` (`:42-48`). Both files use the same H1.
- `DesignLanguage/README.md:10` says "The website implementation remains in progress". `catalog/v6/README.md:3` calls `v6/index.html` "the final browser catalog".
- The DesignLanguage README links neither the catalog nor `layered-windows/v1/`.
- **Edit:** Make `DesignLanguage/WORKPLAN.md` canonical:
  - Check items 11–15 with "(selected 49-module closure; see `catalog/finish-receipt.json`)".
  - Mark DL-023…029 `[x] (catalog scope only)`.
  - Retitle `catalog/WORKPLAN.md` to "Catalog closure record", or reduce it to a pointer.
- In the DesignLanguage README, replace `:10` with "Catalog v6 complete for its frozen source closure; product adoption and native qualification open." Then link `catalog/v6/README.md` and `layered-windows/v1/README.md`.

### P1-3: The catalog's "all current widgets" claim no longer matches source
- `DesignLanguage/README.md:10` promises "all current widgets". `catalog/v6/README.md:3` claims "all 49 selected Elm modules".
- `catalog/v6/registry.json` lists `Popup/SurfaceRenderer/Taskbar.elm`. It has **no** entries for `Snap`, `Notifications`, `SystemMenu`, `Files`, `JumpList`, `Settings`, `Transfer`, `MotionPreferences`, `PointerOwnership` or `Shortcuts.elm`.
- All of those modules exist in `implementation/warlock/src/` and are described as user surfaces in `implementation/warlock/README.md`:
  - snap chooser `:68-80`, Settings `:83-91`, Notifications `:93-107`, System `:109-122`
  - Files `:125-137`, jump lists `:139-159`, High contrast `:222-239`, Task View Move `:267-284`, Motion `:314`
- **Edit:** Add to `catalog/v6/README.md:3`: "Registry frozen at the selected closure; later surfaces (list) are not catalogued." Add a new unchecked workplan item to regenerate the registry from the current closure. DL-023 stays closed only for the old scope.

### P1-4: The pin/MAX feature (ELM-UX-016) has a draft and a failed observation, but the docs and ledger don't show it
- **Source draft (uncommitted per git status):**
  - `src/Provider.elm:418` shows "Always on top"/"Unpin window" only when `supported "pin" && supported "unpin"`.
  - `src/Effects.elm:212` refuses a duplicate or unavailable pin request.
  - `src/GeometryProjection.elm:18,58` decodes `pin {pinned, eligible}` only for protocol 3.
  - `native/geometry-effects.inc:88` commits "already-applied" when `m_pinned==desired`.
- **State:** `STATE.json:10-47` has this slice `in-progress`. `requirement-ledger.json:7421-7428` still says `unadjudicated` / "Existing evidence not yet adjudicated". Per `INSTRUCTIONS.md:43`, a known failed native observation belongs in `failed` or `partial`. "Unadjudicated" now understates what is known; it still does not mean the code is missing.
- **Likely mechanism (I did not verify it):** In `assets/context.js:36-38`, a secondary-click release only invokes if:
  - the release lands on the *same element* and the same node;
  - the publication/lease stamp is unchanged (`same(pending.shown, stamp(node))`);
  - the pointer moved ≤5 px.

  If a preview arrives and republishes or reflows rows between press and release, that release is silently dropped. This matches the reported failure.
- **Edit:** Commit the draft, then use `record` to log a `failed` scenario observation with its evidence hash. Add a three-sentence bounded README paragraph only after that commit. Do not loosen the stamp check without authority review; reserving the preview slot's geometry is the safer first candidate.

### P1-5: `STATE.json` is internally stale
- `nextOriginalSlice` (`:616-632`) still names `live-motion-preference`. Its reason still treats the motion override as future work. But `recentSlices` (`:540-614`) records it `completed-partial` with `investigationStopped: true`.
- `nextSlices` (`:48-57`) still lists "persistent catalog pins", which is recorded as implemented at `:204`.
- **Edit:** Set `nextOriginalSlice` to the real next selection, which is UX-016 completion. Prune `nextSlices` items that are already done, and keep their open obligations.

### P1-6: The plugin's implementation map misses current surfaces and has a terminology collision
- `references/implementation.md:7-17` has no row for:
  - geometry/pin/MAX (`GeometryProjection.elm`, `Provider.elm`, `native/geometry-effects.inc`)
  - snap, transfer, settings/motion, notifications/system/Files, jump lists or previews
- Its "Persistent pins" row (`:14`) means *taskbar* pins (ELM-UX-004). UX-016 "pin" means always-on-top. Contributors will pick the wrong files.
- The plugin README (`README.md:222`) says the `verify-plan` map covers "feedback, search, pins, Task View, popup and owning-core routes". Geometry changes therefore fall through as unmapped.
- **Edit:**
  - Rename the row to "Taskbar pins (ELM-UX-004)".
  - Add an "Always-on-top pin/MAX (ELM-UX-016)" row, with `check-native-authority.py` and the native feedback runner as evidence.
  - Add rows for the surfaces listed above.
- **Root README section (requested):** "Contributing: use `plugins/warlock-contributor` (see `CONTRIBUTING.md`). A checker pass is structural compliance, not GUI acceptance. The CI workflow is a template only." This matches `plugins/…/README.md:327`; no `.github/workflows/` exists.

### P2-7: The integration README never separates feature-complete from release-ready
- `implementation/warlock/README.md` is a 323-line chronological log with no per-feature status. Its preview claims also need reconciling:
  - `:7` says "controlled preview curtain remains closed";
  - `:316` says the picker "now displays authorized native family thumbnails" and that the curtain stays "separate".
- `DesignLanguage/WORKPLAN.md:55` still says "Next is typed native enrollment…preview13". Source now shows a partial picker thumbnail delivery (`README.md:316-318`).
- **Edit:** Add a top table with columns feature | original IDs | user-visible | owner-observed native | failed/open obligations | accepted (always "no" today).

### P2-8: Ledger vocabulary and layered-window status
- The ledger uses requirement-level `"in-progress"` for UI-004, UI-005, UI-007, UX-004 and UX-029. That value is not in the `INSTRUCTIONS.md:43` vocabulary.
- My tally: 210 unadjudicated, 27 partial, 5 in-progress, 0 accepted. Define the value or map it to an existing one.
- `layered-windows/v1/README.md:20-21` says visual implementation is open, and its WORKPLAN has no checkboxes. But `implementation/warlock/README.md:74` says the snap chooser "uses the shared color, glow, shadow and shading language".
- **Edit:** Note "partial product adoption (snap chooser only), unqualified".

## Remaining implementation checklist (all source-grounded)

1. **UX-016 pin/MAX:** Make context-menu selection stable when a preview arrives (P1-4). Then rerun native pin/unpin on a maximized family that overlaps a float, checking scene, hit target and displayed state.
2. **UI-017:** Fix normal owned-client exit with outstanding picker custody (`STATE.json:105`; `README.md:322`).
3. **UI-014/018 motion:** Cover the mid-flight intermediate frame and proxy, the switcher/Task View/snap overlays, and the post-disable normal-profile effect (`STATE.json:586-589`).
4. **Drag ownership:** The original two-output journey never began because of an output-geometry setup failure (`README.md:214-220`). Caption/edge and cancellation are also open.
5. **IME (UX-028):** Candidate-panel traversal, commit and cancellation are unverified (`README.md:262-265`).
6. **Native AT:** Two Orca attempts failed, and the corrected inspector has not been rerun (`README.md:246-252`). This blocks AT claims on every surface.
7. **Coverage gaps:**
   - Transfer: modal, minimized and cross-output cases (`README.md:282-284`).
   - Switcher: lock/exclusive-input and other-output (`STATE.json:389`).
   - UI-007: keyboard and context paths (`STATE.json:123`).
8. **Renderer semantics:** Keyed popup identity, popup h1 nesting, checked semantics and a single announcement route (`catalog/v6/README.md:15`; `DesignLanguage/WORKPLAN.md:53`).
9. **Original gates:** preview13/restore38/recovery34/drag52, S02 resource/presentation budgets, multi-output/fractional-scale/HDR hardware and journeys, all on one coherent tuple (`layered-windows/v1/WORKPLAN.md:10`; `INSTRUCTIONS.md:9,52`).
10. **Release:** A reproducible package and reversible deployment/rollback (`STATE.json:56`). Omarchy routes are still uninstalled (`README.md:178-182`).
11. **Evidence work (not implementation):** Adjudicate the 210 unadjudicated requirements. Many may already be implemented.

## Claims that must stay bounded

- **Feature-complete ≠ release-ready.** `releaseAccepted: false` and `requirementAccepted: true` count = 0.
- **UX-016 is incomplete.** "Draft compiles and 13 replay checks pass" is component evidence only.
- **Catalog v6:** DL-023…029 are closed for the frozen 49-module closure only. The 42 + 104 browser checks are not WCAG, native AT or native acceptance.
- **Every "physically observed" README passage** is owner-observed in a private session. None is independently accepted or installed on the desktop.
- **Native AT, IME, resource, hardware and power obligations** remain unqualified.
- **"Published to GitHub"** means bytes exist on a branch, nothing more. The CI workflow is a template, not live CI.
- **Unadjudicated requirements are not evidence of missing implementation.**

## Recommendation

1. **Make two docs-only commits first:** the root README status/navigation/contributing section, then reconciliation of the two DesignLanguage workplans and the catalog scope note. These are low-risk and fix the most visible contradictions.
2. **Publish the UX-016 draft only as explicit work-in-progress, if at all.** Commit it with its failed native observation recorded and no README completion language.
3. **Don't sweep in everything for "merge everything".** Leave out the untracked QA build/profile directories (catalog README `:15` excludes them from publication) and the dirty frozen derivative paths (`elm-shared-observation-recovery-v121`, `elm-unsent-operation-disposition-v122`; see `INSTRUCTIONS.md:13,15`).
4. **Get explicit owner confirmation before merging into `main`.** `main` is older, and the merge is an outward-facing change.
5. **Next product slice:** context-menu stability under preview arrival (checklist item 1), then picker client-exit custody (item 2).
