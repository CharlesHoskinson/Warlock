# Design-language documentation audit: Warlock integration candidate

**Scope.** I compared the frozen prose in `.warlock-contributor/documentation-audit-20261008/inputs/` (written **IN/** below) with the current source in `implementation/warlock/` (**IMPL/**), the catalog in `DesignLanguage/catalog/v6/` (**CAT/**) and the plugin. I only read files. I did not run anything, so this is not GUI acceptance.

## Prioritized findings

### P0-1 — The design language has no rule for keeping a target's geometry stable, and the source moves picker rows when a preview arrives

- **Source evidence:**
  - `IMPL/assets/shell.css:3` sets thumbnails to `height:auto;max-height:120px`.
  - `IMPL/assets/shell.css:5-14` switches a picker row to a 160px grid only through `button:has(.preview-image)`. The comment says Loading and Unavailable rows "retain their ordinary flow".
  - `IMPL/src/PreviewVisual.elm:108-115` renders Loading/Unavailable as text spans and Live/Historical as an `<img>`. These are different shapes, so a row changes size when Loading becomes Live.
  - `IMPL/src/Surface.elm:280` builds the row detail from the changing confirmed state ("Maximized • Always on top", "Awaiting native confirmation", Minimized/Open).
  - `IMPL/assets/context.js:37` refuses a right-button release if the item, node or publication/lease stamp changed since the press. This is correct and safe behavior.
- **Oracle:** ELM-UX-016 requires the shown pin/MAX state to agree "with native state and visible hit target" (`IN/docs/elm-roadmap/requirements.json:6343,6351`).
- **Documentation gap:**
  - `IN/DesignLanguage/EARS.md:77-79` (DL-013) covers target *size* only.
  - DL-018 (`:107-111`) covers preview freshness but not layout.
  - `IN/DesignLanguage/DESIGN.md:9` is silent on this.
  - `IN/implementation/warlock/README.md:24-26` says focus survives "late preview-content growth". That covers keyboard focus, not where the pointer target is, and readers could take it as the latter.
- **Edit — add to DESIGN.md's Operate-mode paragraph:**
  > "Actionable rows reserve their final geometry before asynchronous content arrives. Picker rows always allocate the thumbnail column and fixed thumbnail box in Loading, Historical, Unavailable and Live states, and status/detail text uses a fixed line budget. Content arrival never moves a target under a held press. A gesture whose target identity changes between press and release is refused, never redirected."
- **Catalog follow-up:** add a specimen showing a Loading→Live transition with identical bounds.
- **Do not** relax `context.js:37` in docs or code to make the journey pass.

### P0-2 — The catalog calls itself "current", but its source snapshot predates the candidate

- **Claim:** `IN/DesignLanguage/catalog/v6/README.md:3` says "14 current source component families across all 49 selected Elm modules".
- **Evidence that the snapshot is older:**
  - In `CAT/src/Provider.elm:396`, protocol 2 does not include AlwaysOnTop, and `:416` has no pin items.
  - The current source has both: `IMPL/src/Provider.elm:396-398,418`.
  - `CAT/source/assets/shell.css` contains no `high-contrast` and no `data-motion`. The current `IMPL/assets/shell.css:75-108` has both.
  - `CAT/ANCESTRY.json:3` confirms "Original source49 … unchanged".
- **Consequence:** DL-023 to DL-029 are closed only for that pinned snapshot (`IN/DesignLanguage/catalog/WORKPLAN.md:42-48,61`). DL-023's own rule ("fail on an uncovered rendered surface") would fail against the current source.
- **Edits:**
  - Change "current source" to "the pinned source49 snapshot (see ANCESTRY.json)".
  - Add: "Not covered: High contrast theme, the native reduced-motion profile and motion settings, Always-on-top/Maximize rows, and picker thumbnails. Regenerate as v7 before claiming current coverage."

### P1-3 — Native palette, glow and shadow are only partly adopted, and one sentence overclaims

- **Source evidence:**
  - The shell uses its own slate/cyan values: `#17202a`, `#263544`, `#7ed7ff` (`IMPL/assets/shell.css:1`).
  - The snap chooser uses gradients and an `0 0 18px #80c7f045` glow (`:48-55`).
- **Approved values:** the layered tokens are `#10111A` / `#1B1E2B` / `#B7A2FF` (`DesignLanguage/layered-windows/v1/tokens.json:9-17`). DESIGN.md:3,7 says the ink/parchment palette with lilac/mint/gold is authoritative.
- **Overclaim:** `IN/implementation/warlock/README.md:74` says the snap region "uses the shared color, glow, shadow and shading language". `IN/DesignLanguage/layered-windows/v1/README.md:20-21` says visual implementation is still open.
- **Edits:**
  - Change README:74 to "uses a provisional shell palette and glow; the layered-window tokens are not yet adopted natively (layered WORKPLAN step 4)."
  - Add a "Native adoption status" line to DESIGN.md.

### P1-4 — The focus indicator deviates from DL-006, and the deviation is not recorded

- **Requirement:** DL-006 asks for "at least a 2 CSS pixel **outer** indicator" (`IN/DesignLanguage/EARS.md:37`).
- **Source:** the product deliberately uses inset focus rings:
  - bar: `shell.css:33`, inset box-shadow;
  - High contrast: `:80-81`, `outline-offset:-4px`;
  - the rationale is in the comment at `:75-76`.
- **Inconsistency:** the launcher search uses a different focus ring (`:24`, 2px `#86c8ff`) from buttons (`:1`, 3px `#7ed7ff`).
- **Edit:** add a recorded deviation to the WORKPLAN integration priorities: "Native focus is inset (≥3px) where overflow would clip an outer ring. DL-006's product scope stays open until 3:1 is measured against both adjacent colors. Unify the search focus token."
- Do not rewrite the voted EARS text.

### P1-5 — Always on top lacks checked semantics, and its label clashes with taskbar pinning

- **Source evidence:**
  - `IMPL/src/Provider.elm:418` flips the menu label between "Unpin window" and "Always on top".
  - No `aria-checked` exists anywhere. `SurfaceRenderer.elm:95` emits only `aria-pressed`/`aria-current`.
  - "Unpin" already means taskbar pinning: `Surface.elm:244` ("Unpin " ++ app) and `Menu.elm:132` (`PinToTaskbar`). `Surface.elm:383` repeats "Unpin window" in the status notice.
- **Requirements affected:** DL-007 (`EARS.md:43`, checked state derived from observation) and DL-019 (`:115`).
- **Edit — add a content rule to DESIGN.md:**
  > "Always on top is a checkable item with a stable label and checked state from admitted native observation. 'Pin/Unpin' is reserved for the taskbar."
- **Related noise:** `Surface.elm:261` repeats the committed window state and the word "Selected" in every menu row's detail. Recommend one status line instead.

### P1-6 — The reduced-transparency and effects-off preferences are specified but don't exist

- **Spec:** `DesignLanguage/layered-windows/v1/EARS.md:43` and the layered README:15-16 require both.
- **Source:** neither appears in `IMPL/src`, the CSS, the adapters or `native/*.c`.
- **Reduced motion is consistent:** `shell.css:103-108` applies only the profile Elm projects, with no media-query inference. That matches DL-015.
- **Edits:**
  - In the layered README, state that effects-off and reduced transparency are not implemented.
  - In DESIGN.md, state that there is deliberately no `prefers-reduced-motion` fallback in product CSS.

### P1-7 — Preview status creates extra live regions

- **Source:** `PreviewVisual.elm:109` gives every Local preview its own `role=status aria-live=polite`, so a picker can contain several live regions.
- **Requirement:** this conflicts with DL-011's single announcement owner (`EARS.md:65-67`).
- **Duplicated text:** `:108` renders "Preview unavailable" twice in one element.
- **Edit:** cite these lines in the WORKPLAN integration priorities (line 53 already mentions duplicated live regions in general).

### P2-8 — Documents disagree with each other, and several typos remain

- **Checklist drift:** `IN/DesignLanguage/WORKPLAN.md:11-15` is unchecked, while `catalog/WORKPLAN.md:11-15` is checked. Make one canonical and link the other.
- **Status drift:** `IN/DesignLanguage/README.md:10` says the "website implementation remains in progress", but catalog v6 is published.
  - Replace with: "catalog v6 is published for the pinned source scope; product adoption is open."
- **Contradictory sentence:** `catalog/WORKPLAN.md:61` says DL030's matrix is "implemented … while its product scope remains open, including the reference decision matrix". Delete the final clause.
- **Missing spaces:** "on30" (README:3, WORKPLAN:9), "with43", "checks,23" (WORKPLAN:55), "all49", "allB1–B3" (catalog/WORKPLAN:61).
- **Missing link:** the root `IN/README.md:12` links the brand docs but not `DesignLanguage/README.md`. Add the link.

### P2-9 — The plugin has no design-language section

- **Current guidance:** `plugins/warlock-contributor/references/implementation.md:39-42` only says to read the relevant `DesignLanguage/` contract.
- **Unmapped route:** plugin README:237 leaves preview transport unmapped.
- **Edit 1 — add a row to the implementation map:**
  > | Visual tokens, focus, contrast, motion, preview layout | `assets/shell.css`, `src/PreviewVisual.elm`, `src/SurfaceRenderer.elm`, `src/Surface.elm` | Focused `--high-contrast`, `--accessibility`, `--ime` and reduced-motion modes named in `implementation/warlock/README.md`; the catalog is visual evidence only |
- **Edit 2 — add a short "Design language" section to the plugin README:**
  - token tiers;
  - stable geometry;
  - checkable semantics;
  - inset-focus deviation;
  - "a catalog pass never closes a native gate".

## Remaining implementation checklist

- [ ] Reserve picker row geometry: fixed thumbnail slot in every preview state and a bounded detail height. Then rerun ELM-UX-016 native context selection with the preview arriving mid-press.
- [ ] Make Always on top checkable with a stable label, and remove the "Unpin window" wording.
- [ ] Adopt the layered tokens (palette, halo, shadow, shading) natively, and add the reduced-transparency and effects-off preference routes.
- [ ] Add a single announcement owner, keyed popup controls, and replace `aria-current` as the selection signal (`context.js:64,89`).
- [ ] Regenerate the catalog (v7) against the current source closure.
- [ ] Native AT: two Orca attempts failed (`IN/implementation/warlock/README.md:246-249`).
- [ ] IME candidate panel and cancellation (`:262-264`).
- [ ] Resource, fairness and custody: the quiescent-picker run failed exit with custody still outstanding (`:318,322`).
- [ ] The combined motion campaign fails (`:314`).
- [ ] The drag journey never started (`:214-218`).
- [ ] Multi-output, fractional-scale and HDR hardware (layered WORKPLAN:10).
- [ ] Independent original-scenario acceptance on one coherent tuple.

## Claims that must stay bounded

- Pin/MAX: compile plus 13 replay checks is component evidence only. ELM-UX-016's native journey **failed**, so the feature is incomplete.
- Catalog v6 checks (42 source/token + 104 browser) apply to the pinned source49 snapshot. They are not current-source coverage, native acceptance or full WCAG.
- High contrast (ELM-UX-027) and reduced motion are partial. Live-preference, overlay and AT coverage are open.
- Preview Live/Historical/Unavailable were observed natively. Physical Loading pixels, AT and capacity are open.
- No native accessibility, IME, resource or hardware obligation is qualified.
- Mechanism of the P0-1 failure: the source evidence above is *consistent with* the reported press/release reflow. I did not observe the failure directly.

## Recommendation

1. **Publish** the documentation corrections (P0-2 through P2-9) together with the Pin/MAX draft on `feature/elm`, clearly labeled as partial or incomplete.
2. **Do not** merge to `main` and **do not** mark ELM-UX-016 or any DL-001 to DL-022 product contract complete.
3. **"Merge everything" should exclude** the untracked `DesignLanguage/catalog/v*/qa/*/mutable-elm-home/` and `profile/` directories shown in git status. The catalog README:15 itself excludes them from publication.
4. **Next work:** land the P0-1 geometry rule first, because it is the blocking defect behind the only failed Pin/MAX native observation.
