I've verified the candidate against the full source, bridge and styles, and I'm writing up the vote. One acceptance line contradicts the shipped focus behaviour; everything else checks out.

---

# Peer review and vote: opus-04-accessibility-motion on candidate-v1

**Overall:** I accept 29 of the 30 contracts as worded. I vote **revise on WARLOCK-DL-004** because one of its acceptance examples can't be met by the shipped surfaces without changing a frozen focus policy. So I don't recommend declaring consensus on candidate-v1 as it stands.

**What I checked:**
- I read candidate-v1.json and candidate-v1.md in full. The 30 contracts match between the two files.
- All 60 proposals are routed. My 12 (AM-01 to AM-12) map to DL-003, 004, 005, 006, 007, 008, 009, 011, 012, 015, 016, 025 and 028.
- I could **not compute the SHA-256 myself**: this read-only session has no hashing tool. `candidate-v1.sha256` states `3bef8fec…66e3e2`, which matches the hash I was given. Someone with a shell should confirm it before counting votes.
- I read the supplemental Elm modules (`Surface`, `Desktop`, `TaskbarShell`), the bridge (`activation.js`, `context.js`, the bar and popup adapters), `shell.css`, and the brand `preview.js`.

## Findings from the supplemental source

1. **Pending and Unknown controls can't hold focus today.**
   - Every blocked control is published with `enabled=False`, which becomes HTML `disabled`. That covers menu rows (`Surface.elm:65-68`), picker rows (`:75-77`), bar groups (`:87-98`) and application entries (`:52-55`).
   - So when a user presses Enter on a menu item, every row disables and the focused row loses focus.
   - The bridge already allows for this: Escape is handled at document level "including when a disabled row blurs focus" (`context.js:45-48`). The refocus observer skips disabled rows (`:69-73`), and native focus requests skip them too (`popup-adapter.js:20`).
   - **This is why I'm blocking DL-004** (below). It is also a real gap that DL-005's declared-fallback requirement should cover.
2. **This also refutes an earlier finding.** opus-03's F6 ("Pending items look enabled") was based on the original packet. At the rendered surface, Pending rows are disabled.
3. **Several accessible names don't start with the visible label.** DL-007 will report all of these when its validator first runs:
   - Bar groups show the window label (e.g. "Firefox") but are named with a changing verb in front: "Minimize Firefox", "Choose a window from …", "Unavailable …" (`Surface.elm:91-98`). The family-count detail isn't in the name at all.
   - "Applications" is named "Open applications" (`:84`).
   - "Windows" is named "Close applications and return to windows" (`:57`).
   - These pass the weaker WCAG 2.5.3 "contains" test but fail DL-007's "begins with" rule and the ELM-ADOPT-017 stable-name guardrail.
4. **Focus return and Escape already exist in source.**
   - Escape in a menu sends `Menu.Dismiss` (`Surface.elm:148`).
   - Escape in the picker or applications popup triggers the close control (`activation.js:99-106`).
   - After a matching observation on the same output, `Desktop.returnFocus` focuses the invoking group (`Desktop.elm:143, 151, 191-199`). If that group no longer exists, focus is simply not set; the fallback isn't declared anywhere.
   - In a menu, Tab moves only between the selected row and Close (`context.js:56-60`). Space does nothing in menus, and there is no typeahead.
5. **The browser layer already ignores keys during IME composition.** Activation ignores keys while `isComposing` and cancels a pending press on `compositionstart` (`activation.js:95-96, 143-146`; `context.js:43`). This is Source evidence at the browser level only; native IME qualification is still open.
6. **The prepared-choice timer is not a time limit on the user.** `ChoiceDeadline` (2 s) runs only after the user has chosen; it waits for the native refresh. On expiry it clears the choice and shows "Window information took too long. Refresh windows, then choose again." plus a Refresh windows control (`Desktop.elm:155-167, 222-227`; `Surface.elm:100`). That matches DL-016, so **I withdraw my earlier WCAG 2.2.1 concern from AM-08.**
7. **Motion is already compliant, trivially.** The product surfaces have no transitions or animations (`shell.css`). The brand preview starts still, pauses when hidden, and follows reduced motion live (`preview.js:23-37`). The product side therefore meets DL-015 only because nothing moves; native preference observation is still unqualified.
8. **Styling and announcement gaps:**
   - `shell.css` uses hard-coded colours that aren't Warlock tokens (`#17202a`, `#7ed7ff`, `system-ui`). That falls short of DL-002's target.
   - The existing 3 px focus outline does meet DL-006's minimum.
   - Disabled controls show only `opacity:.55`, with no reason text.
   - The bar (visually hidden) and the popup render the **same** `notice` string as two polite live regions (`Surface.elm:125`), which confirms DL-011's duplicate-announcement risk.
9. **The "pinned" taskbar row can't happen yet.** `Taskbar.primary` is always called with `pinned=False` (`Surface.elm:87`, `TaskbarShell.elm:83`), so the zero-family pinned → Launch row is unreachable in the current integration.

## Blocking correction

**WARLOCK-DL-004, acceptance item 1.** "A focused Pending control shows both states" can't be satisfied: as finding 1 shows, the shipped surfaces disable every Pending/Unknown control, so none can be focused. Meeting it would mean changing the focus policy, which DL-008 and ELM-ADOPT-030 keep gated. Replace it with:

> "Where the declared per-surface policy lets a Pending or Unknown control hold focus, its focus treatment and outcome cue are both perceivable; where policy removes it from focus, the outcome stays perceivable through status or description and focus follows the declared DL-005 fallback."

## Nonblocking advice

- **DL-005:** declare a menu fallback for while rows are disabled (e.g. the Close control), and key the popup like the bar already is.
- **DL-007:** run the validator against the actual bar-group names, and keep the operation verb as description, not name.
- **DL-015:** product surfaces should get reduced-motion as a typed native observation (portal, then GTK setting). Don't rely on the WebView's CSS media query alone; WebKitGTK only follows the dedicated setting from 2.54.
- **DL-017:** mark the pinned/Launch rows "unreachable in current integration".
- **DL-011:** with one shared notice string, pick a single live region before any native AT qualification.

```json
{
  "reviewerId": "opus-04-accessibility-motion",
  "candidateVersion": "candidate-v1",
  "candidateSHA256": "3bef8fec0517273501f94d26f79a29f4f38d22e5d2dcb6d29ccb4b5ef966e3e2",
  "hashVerification": "not independently recomputed (no hashing tool in read-only session); matches candidate-v1.sha256 and stated value",
  "votes": [
    {"id":"WARLOCK-DL-001","vote":"accept","reason":"Preserves brand values and philosophy; decoration never evidence."},
    {"id":"WARLOCK-DL-002","vote":"accept","reason":"Token tiers sound; shell.css literals are a documented target gap, not a contradiction."},
    {"id":"WARLOCK-DL-003","vote":"accept","reason":"Measured pairs with composited backgrounds and explicit inactive classification."},
    {"id":"WARLOCK-DL-004","vote":"revise","reason":"Acceptance 1 requires a focused Pending control, but the shipped Surface.elm disables all Pending/Unknown controls (HTML disabled), so it is unsatisfiable without changing the ADOPT-030/DL-008-gated focus policy."},
    {"id":"WARLOCK-DL-005","vote":"accept","reason":"Declared fallback requirement covers the observed focus loss when rows become disabled."},
    {"id":"WARLOCK-DL-006","vote":"accept","reason":"2px/3:1 floor is met by the existing 3px outline; native treatment separately qualified."},
    {"id":"WARLOCK-DL-007","vote":"accept","reason":"Exact visible-label prefix matches ADOPT-017; validator reports current failures without claiming compliance."},
    {"id":"WARLOCK-DL-008","vote":"accept","reason":"Skip-disabled labeled Source; focusable menu disabled is a gated future target."},
    {"id":"WARLOCK-DL-009","vote":"accept","reason":"Matches source Escape/Dismiss and returnFocus; dismissal retains outstanding intents."},
    {"id":"WARLOCK-DL-010","vote":"accept","reason":"Defers to ADOPT-029; no F6/global shortcut adoption."},
    {"id":"WARLOCK-DL-011","vote":"accept","reason":"One owner, once, no focus move; addresses the duplicated notice in two live regions."},
    {"id":"WARLOCK-DL-012","vote":"accept","reason":"No fabricated refusal; reconcile is observation-only with no Unknown replay."},
    {"id":"WARLOCK-DL-013","vote":"accept","reason":"24px is a catalog choice; native target contracts unchanged."},
    {"id":"WARLOCK-DL-014","vote":"accept","reason":"Preference changes cannot rebind or activate; revisions may legitimately change."},
    {"id":"WARLOCK-DL-015","vote":"accept","reason":"Consistent with brand preview source and ADOPT-023/024; product motion currently none."},
    {"id":"WARLOCK-DL-016","vote":"accept","reason":"Source ChoiceDeadline is a post-choice native wait with a safe refresh path; composition suppression exists at the browser layer."},
    {"id":"WARLOCK-DL-017","vote":"accept","reason":"Derives from shipped Taskbar.primary; decisions never labeled confirmed."},
    {"id":"WARLOCK-DL-018","vote":"accept","reason":"Honest freshness; earlier frame deferred; preview13 gates preserved."},
    {"id":"WARLOCK-DL-019","vote":"accept","reason":"All Menu.Action constructors documented; checkable state from observation."},
    {"id":"WARLOCK-DL-020","vote":"accept","reason":"Search guarded, composition-safe, no free-text execution."},
    {"id":"WARLOCK-DL-021","vote":"accept","reason":"Host ownership explicit; no release scope removed."},
    {"id":"WARLOCK-DL-022","vote":"accept","reason":"Settings declare guarantees; cannot retarget pending actions."},
    {"id":"WARLOCK-DL-023","vote":"accept","reason":"Full supplemental closure is the inventory basis; integration lanes tracked separately."},
    {"id":"WARLOCK-DL-024","vote":"accept","reason":"Read-mode structure with Not-yet-specified marking."},
    {"id":"WARLOCK-DL-025","vote":"accept","reason":"Scoped evidence records; native label requires receipt, scenario and ABI tuple."},
    {"id":"WARLOCK-DL-026","vote":"accept","reason":"Shipped Elm modules with fixture-only authority; no automatic Unknown retry."},
    {"id":"WARLOCK-DL-027","vote":"accept","reason":"Inventory with source locations; frozen strings untouched."},
    {"id":"WARLOCK-DL-028","vote":"accept","reason":"Reflow, reduced motion, forced colors and offline assets exercised."},
    {"id":"WARLOCK-DL-029","vote":"accept","reason":"Hash/coverage drift named; bounded finish review."},
    {"id":"WARLOCK-DL-030","vote":"accept","reason":"Primary-source matrix; snippet-only values non-binding; no platform marks."}
  ],
  "blockingCorrections": [
    {"id":"WARLOCK-DL-004","field":"acceptance[0]","replace":"A focused Pending control shows both states.","with":"Where the declared per-surface policy lets a Pending or Unknown control hold focus, its focus treatment and outcome cue are both perceivable; where policy removes it from focus, the outcome stays perceivable through status or description and focus follows the declared DL-005 fallback.","evidence":"Surface.elm:65-68,75-77,87-98,52-55 publish blocked controls with enabled=False; SurfaceRenderer.elm:62 renders HTML disabled; context.js:45-48,69-73 and popup-adapter.js:20 skip disabled focus."}
  ],
  "nonblockingAdvice": [
    "DL-005: declare the menu fallback while rows are disabled (e.g. control:menu-close) and key popup controls like the bar.",
    "DL-007: validator should flag bar groups (operation verb prepended, count detail omitted), 'Applications'/'Open applications' and 'Windows'/'Close applications and return to windows'; keep the operation verb as description.",
    "DL-015: product reduced motion should be a typed native observation (portal reduced-motion, then gtk-interface-reduced-motion/gtk-enable-animations); WebView CSS media query only as fallback.",
    "DL-017: mark pinned/Launch rows unreachable in current integration because Taskbar.primary is called with pinned=False.",
    "DL-011: bar and popup render the same notice string as two polite live regions; designate one route before native AT qualification.",
    "AM-08 WCAG 2.2.1 concern withdrawn: ChoiceDeadline measures native refresh after the user's choice, not user reading time."
  ],
  "sourceGaps": [
    "No declared per-surface focus fallback when the focused control becomes disabled during Pending/Unknown; DOM focus is lost.",
    "Popup controls rendered with List.map, not Html.Keyed (SurfaceRenderer.elm:63).",
    "shell.css uses non-token literal colors and system-ui; disabled controls have only opacity with no reason text.",
    "No arrow/typeahead navigation for picker and applications popups; Space does nothing in menus; no typeahead in menus.",
    "No checked-state field for AlwaysOnTop/PinToTaskbar; aria-current derived from detail string 'Selected'.",
    "Product reduced-motion and contrast preferences are not observed natively; native AT, IME and presentation evidence absent.",
    "SHA-256 of candidate-v1.json not independently recomputed in this session."
  ],
  "consensusRecommended": false
}
```
