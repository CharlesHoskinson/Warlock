# Peer review of candidate-v1 (opus-05-catalog-craft)

**Vote: 29 accept, 1 revise (WARLOCK-DL-018). I do not recommend recording consensus on candidate-v1.**

I read all five reports, `candidate-v1.json` and `.md` (they match, 30 contracts), `supplemental-manifest.json` and the full set of supplemental Elm modules, stylesheet, adapters and native files. I edited nothing and launched no agents.

I could not recompute the candidate's SHA-256 because I had no shell tool. `candidate-v1.sha256` states `3bef8fec…66e3e2`, which matches the hash in the request, but I haven't verified it independently.

## Findings from the supplemental source

These correct or sharpen my original report.

1. **Preview states already exist, and DL-018 doesn't match them.**
   - `PreviewLifecycle.elm:25` defines four states: `Live`, `Historical`, `Loading`, `Unavailable`.
   - The visible labels are "Live preview", "Historical preview", "Preview loading" and "Preview unavailable", plus fidelity labels "Window family" and "Client content" (`:364-375`).
   - `Historical` already draws an authorized, unexpired frame whose source is no longer live (`:137-143`).
   - Expired frames and locked scopes are already revoked (`:224-227`, `:277`).
   - DL-018 instead uses "Current", "Placeholder" and "Earlier frame", and defers "Earlier frame". Read literally, that removes or renames existing Source behavior. It also adds a presentation-evidence condition to the live label. ELM-ADOPT-028 forbids both until the frozen historical/live/unavailable policy is reviewed. This is my one blocking correction.
2. **Label-in-name: three current controls already fail DL-007's prefix rule.** The rule is correct as a target; these are Source findings to report, not to rewrite.

   | Control | Location | Visible label | Accessible name |
   |---|---|---|---|
   | Bar group | `Surface.elm:98` | "Firefox" | "Minimize Firefox" or "Choose a window from …" |
   | `bar:applications` | `Surface.elm:84` | "Applications" | "Open applications" |
   | Applications `control:close` | `Surface.elm:57` | "Windows" | "Close applications and return to windows" |

   Menu rows, picker entries, app entries, Reconnect, Refresh and Recovery all pass.
3. **Menu key bindings are in source.** I previously marked them "binding unverified"; they are not.
   - `context.js:42-67` forwards Escape, ArrowUp/Down, Home, End and Enter. `Surface.elm:144-155` maps them to `Menu.Dismiss`, `Navigate` and `Activate`.
   - The native proof route is in `shared-context.h:47-49,135-176`.
   - Space does nothing in menu mode: the zero-detail click is suppressed (`context.js:15-18`).
   - Tab toggles between Close and the selected row (`:56-59`).
   - Focus follows `aria-current="true"` (`:69-73`). Any change to selection semantics must migrate this adapter in the same derivative.
   - Typeahead does not exist.
4. **Product styling is not yet on Warlock tokens.** `shell.css:1` uses `system-ui` and literal colors (`#17202a`, focus ring `#7ed7ff`, 3 px). Disabled controls use `opacity:.55`. The bar's status region is visually hidden. DL-001, -002, -003 and -006 are therefore targets; the current styling must be labeled Source rather than claimed compliant.
5. **Focus loss while Pending.** When a menu operation is Pending, every row becomes disabled (`Surface.elm:65,68`), so the focused row drops focus. Only Escape stays live, at document level. This is the Source fallback that DL-005 and DL-008 require to be documented.
6. **Other details:**
   - `Taskbar.primary` is always called with `pinned=False` (`Surface.elm:87-96`, `TaskbarShell.elm:83`), so the "zero pinned → Launch" row in DL-017 is unreachable in the current bar.
   - Launch has its own statuses: Pending, Submitted, Refused, Unknown (`Launch.elm:275-291`).
   - Recovery after a launch Unknown is a manual "I checked; allow another launch" control (`Surface.elm:56`), which is compatible with "no automatic retry".
   - When the 2 s choice deadline expires, the choice is cleared and a "Refresh windows" path appears (`Desktop.elm:222-227`). That matches DL-016.

## Blocking correction (DL-018)

Replace the acceptance and guardrail wording with the following:

> "The catalog maps preview presentation to the Source statuses `Live`, `Historical`, `Loading` and `Unavailable` (`PreviewLifecycle.elm:25,364-375`), with their existing labels and fidelity text, governed by the frozen historical/live/unavailable policy and original preview13/S09. 'Current', 'Placeholder' and 'Earlier frame' are proposed catalog terms only. Renaming a label, or adding an evidence condition to `Live`, is a proposed refinement gated on ELM-ADOPT-028 review. The earlier-frame deferral covers only new retention beyond the existing authorized, unexpired accepted packet. It does not remove or alter `Historical`. Existing revocation on expiry or lock remains Source."

## Nonblocking advice

- **DL-002:** migrating `shell.css` to tokens is a product change to a frozen component. Mark it Proposed and do it in a fresh derivative.
- **DL-003:** evaluate disabled text at the composited `opacity:.55`, or classify it explicitly.
- **DL-005:** surviving identity means the same surface identity under the same picker scope and generation. A new generation is intentionally a new identity. Keyed DOM is an implementation choice under ADOPT-016. The popup is currently not keyed.
- **DL-007 / DL-027:** report the three failing identities above as Source findings.
- **DL-009:** record that Space and typeahead are absent, and record the Tab toggle and focus-follows-`aria-current`.
- **DL-011:** bar and popup both render the same status text in polite live regions. Record this as a duplicate-announcement finding.
- **DL-017:** mark the pinned row as reachable only through the function.
- **DL-023:** coverage must include:
  - Launch statuses and the preview statuses and fidelity labels;
  - every `Surface.elm` control identity (`bar:applications`, `bar:reconnect`, `bar:refresh-windows`, `bar:recovery-refresh`, `control:acknowledge`, `control:menu-close`, `control:close`, `control:refresh`);
  - all notice strings.
- **DL-026:** menu keyboard demos need the shipped `context.js` (or must state that it is absent), since Tab, Escape and click suppression live there.
- **DL-030:** name the family "Apple Human Interface Guidelines" rather than "Apple iOS HIG". The menu and keyboard guidance cited is cross-platform.

```json
{
  "reviewerId": "opus-05-catalog-craft",
  "candidateVersion": "candidate-v1",
  "candidateSHA256": "3bef8fec0517273501f94d26f79a29f4f38d22e5d2dcb6d29ccb4b5ef966e3e2",
  "votes": [
    {"id":"WARLOCK-DL-001","vote":"accept","reason":"Preserves brand and schema-1 values; shell.css system-ui styling is current Source, not a conflict."},
    {"id":"WARLOCK-DL-002","vote":"accept","reason":"Token tiers are a proposed target; shell.css literals are labeled Source under DL-025."},
    {"id":"WARLOCK-DL-003","vote":"accept","reason":"Composited-pair testing and explicit classification are correct."},
    {"id":"WARLOCK-DL-004","vote":"accept","reason":"Matches Menu outstanding-target blocking and Surface familyBlocked; no second intent."},
    {"id":"WARLOCK-DL-005","vote":"accept","reason":"Declared fallback requirement covers the Source focus loss when Pending disables rows."},
    {"id":"WARLOCK-DL-006","vote":"accept","reason":"2px/3:1 floor; native treatment separately qualified; current 3px outline is Source."},
    {"id":"WARLOCK-DL-007","vote":"accept","reason":"Prefix rule matches ELM-ADOPT-017; current failures are reported, not rewritten."},
    {"id":"WARLOCK-DL-008","vote":"accept","reason":"Skip-disabled labeled Source; focusable disabled menus remain a gated future target under ADOPT-030."},
    {"id":"WARLOCK-DL-009","vote":"accept","reason":"Escape/arrow/Home/End/Enter mapping exists in context.js and Surface.resolve; dismissal retains obligations."},
    {"id":"WARLOCK-DL-010","vote":"accept","reason":"Defers to ELM-ADOPT-029; no new global shortcut."},
    {"id":"WARLOCK-DL-011","vote":"accept","reason":"Single-owner target is correct; current duplicate regions become findings."},
    {"id":"WARLOCK-DL-012","vote":"accept","reason":"Consistent with source notices and the manual launch acknowledgement; no automatic replay."},
    {"id":"WARLOCK-DL-013","vote":"accept","reason":"24px is scoped to the catalog; native target contracts unchanged."},
    {"id":"WARLOCK-DL-014","vote":"accept","reason":"Guardrail correctly permits publication/lease and rendering-generation changes."},
    {"id":"WARLOCK-DL-015","vote":"accept","reason":"Website and native motion scopes separated; S02/023/024 preserved."},
    {"id":"WARLOCK-DL-016","vote":"accept","reason":"Matches Desktop ChoiceDeadline/ExpirePrepared: original deadlines fixed, expired choice unavailable with refresh path."},
    {"id":"WARLOCK-DL-017","vote":"accept","reason":"Derives from shipped Taskbar.primary; pinned row reachability is advisory."},
    {"id":"WARLOCK-DL-018","vote":"revise","reason":"Terms Current/Placeholder/Earlier frame do not match Source Live/Historical/Loading/Unavailable; deferral and the added Current evidence condition would alter existing Historical/Live behavior contrary to ELM-ADOPT-028."},
    {"id":"WARLOCK-DL-019","vote":"accept","reason":"Documents all Menu.Action constructors; three-group preference cannot omit actions."},
    {"id":"WARLOCK-DL-020","vote":"accept","reason":"Accurately states that the current launcher has no search; uses the typed launch path."},
    {"id":"WARLOCK-DL-021","vote":"accept","reason":"Keeps host ownership and release scope; no browser placement claims."},
    {"id":"WARLOCK-DL-022","vote":"accept","reason":"Settings stay Proposed; no retargeting or admission bypass."},
    {"id":"WARLOCK-DL-023","vote":"accept","reason":"Supplemental closure replaces subset inference; integration lanes tracked separately."},
    {"id":"WARLOCK-DL-024","vote":"accept","reason":"Matches proposed IA; linked headings allowed."},
    {"id":"WARLOCK-DL-025","vote":"accept","reason":"Scopes are not a ladder; Native label requires receipt, scenario and ABI tuple."},
    {"id":"WARLOCK-DL-026","vote":"accept","reason":"Shipped Elm functions plus a labeled simulated-authority panel; no competing JavaScript policy."},
    {"id":"WARLOCK-DL-027","vote":"accept","reason":"Findings kept separate from frozen source strings."},
    {"id":"WARLOCK-DL-028","vote":"accept","reason":"Reflow, local assets and offline operation; no native socket needed."},
    {"id":"WARLOCK-DL-029","vote":"accept","reason":"Hash/changelog reconciliation, licenses, provenance and bounded review."},
    {"id":"WARLOCK-DL-030","vote":"accept","reason":"Adoption matrix with rejections of platform marks and snippet-derived numbers."}
  ],
  "blockingCorrections": [
    {"id":"WARLOCK-DL-018","correction":"Map preview presentation to the Source statuses Live, Historical, Loading and Unavailable (PreviewLifecycle.elm:25,364-375) with existing labels and fidelity text under the frozen historical/live/unavailable policy and original preview13/S09. Treat Current, Placeholder and Earlier frame as proposed catalog terms only. Any label rename or added evidence condition for Live is a refinement gated on ELM-ADOPT-028 review. The earlier-frame deferral applies only to new retention beyond the existing authorized, unexpired accepted packet and does not remove or alter Historical. Existing expiry and lock revocation remain Source."}
  ],
  "nonblockingAdvice": [
    "DL-002: shell.css token migration is a frozen-component product change; label Proposed and implement in a fresh derivative.",
    "DL-003: evaluate disabled text at the composited opacity .55 (shell.css:1) or classify it explicitly.",
    "DL-005: surviving identity means the same surface identity within the same picker scope/generation; keyed DOM remains an implementation choice (ADOPT-016); popup is not keyed in Source.",
    "DL-007/027: report Source label-in-name failures at Surface.elm:98 (bar groups), :84 (bar:applications) and :57 (applications control:close).",
    "DL-009: document Space suppressed in menu mode (context.js:15-18), Tab toggling Close/selected (:56-59), focus following aria-current (:69-73) and absent typeahead.",
    "DL-011: bar and popup render the same notice in two polite live regions; record a duplicate-announcement finding.",
    "DL-017: Taskbar.primary is always called with pinned=False; mark the pinned row as function-only.",
    "DL-023: include Launch statuses, preview statuses/fidelity labels, all Surface.elm control identities and notice strings in coverage.",
    "DL-026: menu keyboard demos must include shipped context.js or declare its absence.",
    "DL-030: name the family Apple Human Interface Guidelines, not Apple iOS HIG."
  ],
  "sourceGaps": [
    "Candidate SHA-256 not independently recomputed (no shell tool); relied on candidate-v1.sha256.",
    "Native focus restoration after Escape (Desktop.returnFocus route through host.c/shared-host.c) not traced end to end.",
    "No native AT tree, IME, keyboard-scope or hardware evidence reviewed; nothing here is native acceptance.",
    "host.c and shared-host.c reviewed only for key handling, not fully.",
    "Visual rendering of shell.css not inspected; no screenshots available."
  ],
  "consensusRecommended": false
}
```
