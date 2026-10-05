# Peer review of Warlock design language candidate-v1: opus-02-widgets

**My vote: 28 accept, 2 revise (DL-018, DL-030).** I do not recommend consensus on this exact version. Both corrections are one-sentence wording fixes, and once they are made I would accept every contract.

**What I checked:**
- **The candidate itself.** I compared `candidate-v1.json` and `candidate-v1.md` contract by contract. The EARS text, acceptance, guardrails and source-proposal routing match for all 30 contracts.
- **The hash.** I could not recompute the SHA-256: this session had no shell or hashing tool. My votes are bound to the supplied hash `3bef8fec…e3e2`.
- **The other reports.** I searched all five reports for points where they conflict.
- **Source.** I checked the candidate's claims against the supplemental closure: `Surface.elm`, `SurfaceRenderer.elm`, `PreviewLifecycle.elm`, `Presentation.elm`, `shell.css`, `activation.js`, `context.js`, `bar-adapter.js`, `popup-adapter.js` and `adapter.js`.
- **Not read in full:** native `host.c` and `shared-host.c`.

## What the supplemental source showed

1. **The real control set is larger than my original inventory** (`Surface.elm:57-101`):
   - Bar: `bar:applications` or `bar:reconnect`, `bar:group:*`, `bar:refresh-windows`, `bar:recovery-refresh`.
   - Popup: `control:close` (labelled "Windows" in applications mode, "Close" in the picker), `control:refresh`, `control:acknowledge` ("I checked; allow another launch"), `entry:*`, `family:*`, `menu:N:i`, `control:menu-close`, `control:recovery-refresh`.
   - DL-023 is correct to require the full closure.
2. **Several current controls fail DL-007's visible-label-prefix rule:**
   - Taskbar group: shows "Firefox", but its accessible name is "Activate Firefox"/"Minimize …" (`Surface.elm:91-98`).
   - `bar:applications`: shows "Applications", named "Open applications".
   - The applications-mode close button: shows "Windows", named "Close applications and return to windows".
   - The verb in the name is transient state, which ELM-ADOPT-017 already says belongs in the description.
3. **`aria-current` is load-bearing in the bridge.** `context.js:58,69-73` moves focus to `[aria-current="true"]` and uses it as the Tab target. Replacing it (DL-007) needs a coordinated bridge change, not just a renderer change.
4. **Source keyboard map** (`context.js`, `activation.js`):
   - In menu mode, Escape, Up/Down, Home/End and Enter post `surface-menu-navigation` to native.
   - **Space is not bound in menu mode.**
   - Tab toggles between the selected row and Close.
   - Shift+F10 and the ContextMenu key open the context menu.
   - In picker and applications mode, Escape activates `control:close`.
   - Enter/Space activation is guarded against IME composition, key repeat and modifier keys.
5. **Pending or blocked items are shown by disabling the HTML control,** with the detail text "Awaiting native confirmation". That removes focus, so DL-004's "a focused Pending control shows both states" is a Proposed target, not current Source.
6. **The taskbar is called as `Taskbar.primary False`** (`Surface.elm:87-91`). Pins are hard-coded off, so the "zero pinned → Launch" row of DL-017's truth table cannot be reached in the current bar.
7. **Preview tiles already have four Source states:** Live, Historical, Loading and Unavailable, with the visible text "Live preview" / "Historical preview" / "Preview loading" / "Preview unavailable" (`PreviewLifecycle.elm:25,137-147,364-375`). Historical frames are authorized, unexpired frames from an older scene or content revision, and they are displayed. Expired or locked frames are not. DL-018's "Earlier frame is deferred" can be read as suppressing this existing display, which the original S09/preview13 assertions cover. That is why I vote revise.
8. **Two live regions confirmed.** The bar status is screen-reader-only (clipped in `shell.css`) but still `aria-live=polite`, and it carries the same `Surface.notice` text as the visible popup status. This supports DL-011.
9. **`shell.css` doesn't use the brand yet.** It uses `system-ui` and literal colors that are not brand tokens. The existing focus outline is a single 3px `#7ed7ff` line with 1px offset, which already meets DL-006's ≥2px minimum. Disabled controls use `opacity: .55`, which DL-003 has to classify and measure.

## Blocking corrections

- **DL-018:** Add to the acceptance: *"The existing Source Live/Historical/Loading/Unavailable states, visible labels and authorized Historical frame display are preserved under the frozen S09 historical/live/unavailable policy. 'Current' and 'Earlier frame' are proposed catalog terms. They do not rename, suppress or extend those Source states until the ELM-ADOPT-028 review."*
- **DL-030:** Replace "Apple iOS HIG" with *"Apple Human Interface Guidelines (including the macOS menu, focus and keyboard guidance used by DL-007/008/019)"*. The user named the whole HIG, the product is a desktop, and the candidate's own citations are to `menus.json` and `focus-and-selection.json`.

```json
{
 "reviewerId":"opus-02-widgets",
 "candidateVersion":"candidate-v1",
 "candidateSHA256":"3bef8fec0517273501f94d26f79a29f4f38d22e5d2dcb6d29ccb4b5ef966e3e2",
 "votes":[
  {"id":"WARLOCK-DL-001","vote":"accept","reason":"Preserves schema-1 brand and philosophy; decoration grants no authority."},
  {"id":"WARLOCK-DL-002","vote":"accept","reason":"Token tiers are a target; shell.css literals are Source to migrate, not contradicted."},
  {"id":"WARLOCK-DL-003","vote":"accept","reason":"Composited-pair measurement and explicit inactive classification cover disabled opacity .55."},
  {"id":"WARLOCK-DL-004","vote":"accept","reason":"Matches Menu/Surface blocking (no second intent); focused-Pending is properly a proposed target."},
  {"id":"WARLOCK-DL-005","vote":"accept","reason":"Popup is still unkeyed in supplemental SurfaceRenderer.elm:63; keyed identity is warranted."},
  {"id":"WARLOCK-DL-006","vote":"accept","reason":"Existing 3px focus-visible outline meets the >=2px floor; the two-tone ring is an initial catalog treatment only."},
  {"id":"WARLOCK-DL-007","vote":"accept","reason":"Consistent with ELM-ADOPT-017; validator surfaces current failures without rewriting frozen oracles."},
  {"id":"WARLOCK-DL-008","vote":"accept","reason":"Labels skip-disabled as Source; focusable disabled menus remain a gated future target under ELM-ADOPT-030."},
  {"id":"WARLOCK-DL-009","vote":"accept","reason":"Escape/navigation route through native with exact stamp; Msg mapping plus source status covers unbound Space."},
  {"id":"WARLOCK-DL-010","vote":"accept","reason":"Defers to ELM-ADOPT-029; no F6/global shortcut."},
  {"id":"WARLOCK-DL-011","vote":"accept","reason":"Source has two polite regions with identical notice; single owner is correct."},
  {"id":"WARLOCK-DL-012","vote":"accept","reason":"Matches 'read observations without retrying actions'; no automatic Unknown replay."},
  {"id":"WARLOCK-DL-013","vote":"accept","reason":"24px limited to catalog; native geometry contracts untouched."},
  {"id":"WARLOCK-DL-014","vote":"accept","reason":"Allows legitimate publication/lease and generation changes while preserving targets."},
  {"id":"WARLOCK-DL-015","vote":"accept","reason":"Still-by-default catalog; native timing remains under S02/023/024."},
  {"id":"WARLOCK-DL-016","vote":"accept","reason":"Original deadlines unchanged; expired choices unavailable."},
  {"id":"WARLOCK-DL-017","vote":"accept","reason":"Truth table mirrors Taskbar.primary; decisions never labeled confirmed."},
  {"id":"WARLOCK-DL-018","vote":"revise","reason":"'Earlier frame is deferred' is ambiguous against existing Source Historical frame display (PreviewLifecycle.elm:142,366) covered by frozen S09 policy."},
  {"id":"WARLOCK-DL-019","vote":"accept","reason":"Omit unsupported, reason for unavailable, checked state from observation; documents all Menu.Action constructors."},
  {"id":"WARLOCK-DL-020","vote":"accept","reason":"Search is a guarded extension; current source documented as having none."},
  {"id":"WARLOCK-DL-021","vote":"accept","reason":"Host ownership and gates stated; no browser placement claims."},
  {"id":"WARLOCK-DL-022","vote":"accept","reason":"Settings documentation constraints only; Proposed until integrated."},
  {"id":"WARLOCK-DL-023","vote":"accept","reason":"Full closure supersedes ten-module inference; supplemental reveals additional controls that must be covered."},
  {"id":"WARLOCK-DL-024","vote":"accept","reason":"Read-mode IA with Not yet specified markers."},
  {"id":"WARLOCK-DL-025","vote":"accept","reason":"Scoped evidence records; Native label requires receipt, scenario and ABI tuple."},
  {"id":"WARLOCK-DL-026","vote":"accept","reason":"Shipped Elm functions with labeled fixture authority; no competing JS policy."},
  {"id":"WARLOCK-DL-027","vote":"accept","reason":"Inventory with source locations; frozen strings never rewritten."},
  {"id":"WARLOCK-DL-028","vote":"accept","reason":"Offline, reflow, forced-colors and reduced-motion coverage."},
  {"id":"WARLOCK-DL-029","vote":"accept","reason":"Hash/changelog reconciliation, provenance and bounded review."},
  {"id":"WARLOCK-DL-030","vote":"revise","reason":"'Apple iOS HIG' mis-scopes the user-named Apple HIG for a desktop product; candidate cites macOS menu/focus guidance."}
 ],
 "blockingCorrections":[
  {"id":"WARLOCK-DL-018","correction":"Add acceptance: 'The existing Source Live/Historical/Loading/Unavailable states, visible labels and authorized Historical frame display are preserved under the frozen S09 historical/live/unavailable policy; Current and Earlier frame are proposed catalog terms that do not rename, suppress or extend those Source states until the ELM-ADOPT-028 review.'"},
  {"id":"WARLOCK-DL-030","correction":"Replace 'Apple iOS HIG' with 'Apple Human Interface Guidelines (including macOS menu, focus and keyboard guidance)'."}
 ],
 "nonblockingAdvice":[
  "DL-023: registry must include Surface.elm:57-101 controls: bar:applications, bar:reconnect, bar:group:*, bar:refresh-windows, bar:recovery-refresh, control:close (two labels by mode), control:refresh, control:acknowledge, entry:*, family:*, menu:N:i, control:menu-close, control:recovery-refresh.",
  "DL-007/027: record current label-prefix failures (bar groups 'Firefox' vs 'Activate Firefox'; bar:applications; applications control:close 'Windows') as findings migrated under ELM-ADOPT-017 without altering frozen oracles.",
  "DL-007/009: aria-current drives focus and Tab in context.js:58,69-73; any replacement needs a coordinated bridge change and a surfaceProtocol decision by the owning lane.",
  "DL-009: source key map: menu mode Escape/Up/Down/Home/End/Enter -> native surface-menu-navigation; Space unbound in menu mode; Tab toggles selected row and Close; Shift+F10/ContextMenu opens context menu; picker/applications Escape activates control:close.",
  "DL-004/008: source conveys blocked/Pending by HTML-disabling controls with 'Awaiting native confirmation', which drops focus; label focused-Pending as Proposed.",
  "DL-017: Surface.elm calls Taskbar.primary False, so the pinned/Launch row is unreachable in the current bar; mark row reachability.",
  "DL-005: menu row identities are positional (menu:N:i) and items are immutable per MenuId; keyed-preservation tests apply to picker/application entries.",
  "DL-012: inventory Surface.notice strings and reservationReason; document acknowledge as explicit user action, not replay."
 ],
 "sourceGaps":[
  "Candidate SHA-256 not independently recomputed (no hashing tool in this read-only session); JSON and Markdown text compared manually and match.",
  "native/host.c and shared-host.c not fully reviewed; native focus restoration and native handling of surface-menu-navigation/Escape unverified here.",
  "Original S01-S16/right-click24 scenario oracles not in packet; cannot confirm whether any frozen oracle asserts current ariaLabel strings.",
  "MenuBridge provider item construction (toggle labels, reasons) only partially reviewed."
 ],
 "consensusRecommended":false
}
```

No native acceptance is claimed. The Warlock brand and all prior release scope are preserved.
