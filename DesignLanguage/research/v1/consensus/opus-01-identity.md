# Peer review of candidate-v1 — opus-01-identity

**My vote: accept 27 contracts, revise 3 (DL-004, DL-018, DL-030).** I do not recommend consensus on candidate-v1. All three corrections are narrow wording fixes that make the candidate match the shipped source and the user's named references. Once they are applied, I expect to accept candidate v2.

This review stayed read-only, and I started no agents. I read all five reports, `candidate-v1.json` and `.md`, the supplemental manifest, and the identity-relevant supplemental source: `shell.css`, `tokens.css`, `asset-manifest.json`, the font provenance, the vector marks, `build_identity.py`, `preview.js`, `Surface.elm`, `Provider.elm`, `PreviewLifecycle.elm`, `context.js` and `popup-adapter.js`. Nothing here claims native acceptance.

**Hash:** I could not compute SHA-256 with my read-only tools. `candidate-v1.sha256` states `3bef8fec…e3e2`. My vote applies to the JSON content I read under that stated hash, and the coordinator must confirm the bytes. The `.md` text matches the JSON contract by contract. All 60 source proposals are routed: WL-ID, OPUS05-CAT, AM, WLK-WGT and WLD-DESK each map 12 of 12.

## Findings from the supplemental source

1. **The shipped shell does not use the Warlock identity yet.** `shell.css:1` uses hard-coded `#17202a`, `#f4f6f7`, `#263544` and `#7ed7ff` with the `system-ui` font. It uses no brand tokens. The catalog must label Warlock-styled shell specimens as Proposed (DL-002, DL-025). The current focus ring (3 px `#7ed7ff`) is about 7.8:1 on buttons and about 10:1 on the background, so it already meets DL-006's contrast floor.
2. **The bar status is visible to screen readers only.** `.bar [role=status]` is clipped to 1 px in `shell.css:1`. While the popup is closed, persistent conditions show only through the Reconnect and Refresh controls, not as readable text. This is the Source baseline for DL-011.
3. **Accessible names already conflict with DL-007's prefix rule.**
   - Taskbar groups use `label = window title` and `ariaLabel = "Minimize "/"Activate "/… ++ title` (`Surface.elm:91-98`).
   - "Applications" has the name "Open applications" (`:84`).
   - "Windows" has the name "Close applications and return to windows" (`:57`).
   - Picker labels embed a changing verb ("Restore"/"Activate" + title, `:77`), so those labels are not stable.

   WCAG's "contains" test passes for these, but DL-007's "begin with" test fails. These are expected validator findings, not a reason to revise DL-007.
4. **"Selected" means the keyboard cursor, not a checked state.** `Surface.elm:67` sets "Selected" from `menu.selected`, the navigation cursor. `context.js:58,71-72` then uses `[aria-current="true"]` to move DOM focus. Any change to DL-005 or DL-007 semantics must update that bridge selector in the same change. `AlwaysOnTop checked` is a requested target value (`Provider.elm:228`), and no checked state is rendered, so DL-007's rule that state comes from observation is consistent.
5. **Pending and blocked controls are disabled and lose focus.** `Surface.elm:68,75,90` set `enabled=ready`. `popup-adapter.js:20` skips disabled targets, and `context.js:45` handles a row that becomes disabled and drops focus. This directly affects DL-004's acceptance wording (below).
6. **The preview already ships four states.** `PreviewLifecycle.elm:364-371` renders "Live preview", "Historical preview" (with retained pixels), "Preview loading" and "Preview unavailable". Locked scopes hide the title, and a fidelity line reads "Window family" or "Client content". DL-018's "Current" and "Earlier frame" vocabulary does not match this.
7. **Brand asset gaps.**
   - No W-letterform asset exists for sizes below 24 px.
   - `warlock-mark-mono.svg` hard-codes `color="#F5F0E8"`. Used as an `<img>` on a light background it would be invisible, but the brand calls for a dark monochrome mark there.
   - In light mode, `tokens.css` maps `--w-ink` to parchment, which mixes reference names with role names (supports DL-002).
   - `asset-manifest.json` records absolute local `originalFile` paths under `/home/hoskinson/.codex/…`.
8. **The provider admits only 8 action kinds.** `Menu.Action` has 12 constructors, but `Provider.elm:204` admits eight. `Taskbar.primary` is always called with `pinned=False` in the bar (`Surface.elm:87-91`), so the Launch row of its truth table is unreachable in today's bar.

## Blocking corrections

**DL-004.** The acceptance "A focused Pending control shows both states" cannot be met under the Source policy (finding 5) or under ELM-ADOPT-030, which DL-008 keeps authoritative.
- Replace that acceptance item with: "Where the declared per-surface focus policy keeps a Pending control focusable, the focused control shows both focus and Pending; otherwise the declared fallback applies and Pending remains perceivable on the control."

**DL-018.** Source already shows retained historical pixels (finding 6), and ELM-ADOPT-028 freezes that policy. Add this guardrail:
- "The Source states Live preview, Historical preview, Preview loading and Preview unavailable (PreviewLifecycle.elm:364-369), including Historical display of retained pixels under the frozen historical/live/unavailable policy and S09 preview13 assertions, are documented as Source and unchanged. 'Current' denotes the Source Live state. The deferral applies only to the proposed 'Earlier frame' relabel and any new retention or dimming behavior."

**DL-030.** "Apple iOS HIG" narrows the reference family the user named, and it mislabels the macOS-relevant sources the candidate already cites (for example, the-menu-bar).
- Replace it with: "Apple Human Interface Guidelines (all platforms, including macOS)."

## Nonblocking advice

- **DL-001:** Add a dark monochrome mark and a W-letterform asset. Leave the brand faces unchanged; Impeccable's face-reflex rule is overridden because the brief pins these faces.
- **DL-002:** State explicitly that forced-colors and high-contrast roles resolve to system colors rather than reference hex, as DL-014 already says. Rename the light-theme `--w-ink` when schema 2 is introduced.
- **DL-007:** Seed the validator with the known findings from finding 3. Treat any frozen naming policy as precedent.
- **DL-005 / DL-007:** Change the `context.js` `aria-current` focus hook atomically with the semantics change.
- **DL-017:** Mark the pinned and Launch rows as unreachable in today's bar.
- **DL-019:** Distinguish the 8 provider-admitted actions from the 12 type-level constructors.
- **DL-026:** Label `preview.js`'s JavaScript update loop as a brand illustration.
- **DL-029:** Publish prompt text and hashes, but redact absolute local paths.
- **Unresolved:** gold for the Unknown state (AM-02 disagrees). Keep it unresolved; it is not blocking.

```json
{
 "reviewerId":"opus-01-identity",
 "candidateVersion":"candidate-v1",
 "candidateSHA256":"3bef8fec0517273501f94d26f79a29f4f38d22e5d2dcb6d29ccb4b5ef966e3e2",
 "votes":[
  {"id":"WARLOCK-DL-001","vote":"accept","reason":"Preserves name, sigil, tagline, faces and schema-1 values; tokens.json is generated by build_identity.py so the byte comparison is testable."},
  {"id":"WARLOCK-DL-002","vote":"accept","reason":"Three tiers fit the brand; shell.css currently ignores the brand tokens, so this is Proposed, not Source."},
  {"id":"WARLOCK-DL-003","vote":"accept","reason":"Floors match my computed contrast table; the light border at about 3.05:1 passes; checking against composited backgrounds is correct."},
  {"id":"WARLOCK-DL-004","vote":"revise","reason":"Acceptance 'A focused Pending control shows both states' conflicts with Source (blocked controls are disabled and lose focus, Surface.elm:68/90, context.js:45) and with ELM-ADOPT-030 authority."},
  {"id":"WARLOCK-DL-005","vote":"accept","reason":"Consistent with ELM-ADOPT-016; menu row identities are stable for each MenuId."},
  {"id":"WARLOCK-DL-006","vote":"accept","reason":"The catalog ring is defined; native treatment is separately qualified; the current shell ring already meets 3:1."},
  {"id":"WARLOCK-DL-007","vote":"accept","reason":"Matches the ELM-ADOPT-017 guardrail; existing taskbar, Applications and Windows names become reported findings, not silent rewrites."},
  {"id":"WARLOCK-DL-008","vote":"accept","reason":"Skip-disabled is correctly labelled Source (Menu.navigate, popup-adapter.js:20); the focusable-disabled menu target is guarded."},
  {"id":"WARLOCK-DL-009","vote":"accept","reason":"Escape maps to Menu.Dismiss by MenuId (Surface.elm:148), which keeps outstanding intents; documenting Space and typeahead status is honest."},
  {"id":"WARLOCK-DL-010","vote":"accept","reason":"Defers to ELM-ADOPT-029; no new global shortcut."},
  {"id":"WARLOCK-DL-011","vote":"accept","reason":"Target is sound; the Source bar status is screen-reader-only, which the catalog must record."},
  {"id":"WARLOCK-DL-012","vote":"accept","reason":"Consistent with the observation-only refresh and the explicit launch acknowledgement in Source."},
  {"id":"WARLOCK-DL-013","vote":"accept","reason":"24px is scoped to the catalog; native targets keep their frozen contracts."},
  {"id":"WARLOCK-DL-014","vote":"accept","reason":"Correctly relaxes my WL-ID-05 over-constraint on publication/lease identity; continuity protects identity and authority."},
  {"id":"WARLOCK-DL-015","vote":"accept","reason":"Matches the brand motion policy and the S02/ADOPT-023/024 bounds; preview.js already starts paused, pauses when hidden and honors reduced motion."},
  {"id":"WARLOCK-DL-016","vote":"accept","reason":"Original deadlines unchanged; expired choices are unavailable."},
  {"id":"WARLOCK-DL-017","vote":"accept","reason":"Truth table from Taskbar.primary; decisions are never labelled as native results."},
  {"id":"WARLOCK-DL-018","vote":"revise","reason":"Source already renders Live/Historical/Loading/Unavailable with retained historical pixels (PreviewLifecycle.elm:364-371); deferring 'Earlier frame' and using 'Current' without mapping misrepresents Source and risks altering frozen S09/ADOPT-028 policy."},
  {"id":"WARLOCK-DL-019","vote":"accept","reason":"Two-reason rule is sound; must distinguish provider-admitted kinds (Provider.elm:204)."},
  {"id":"WARLOCK-DL-020","vote":"accept","reason":"Guarded extension; Source without search is documented accurately."},
  {"id":"WARLOCK-DL-021","vote":"accept","reason":"Host ownership and gates preserved; no scope removal."},
  {"id":"WARLOCK-DL-022","vote":"accept","reason":"Implements philosophy section 8."},
  {"id":"WARLOCK-DL-023","vote":"accept","reason":"Supplement closure replaces inference; coverage covers preview states and actions."},
  {"id":"WARLOCK-DL-024","vote":"accept","reason":"Read-mode structure consistent with Impeccable and the GNOME and Fluent taxonomies."},
  {"id":"WARLOCK-DL-025","vote":"accept","reason":"Scoped evidence records; native-qualified label requires receipt, scenario and ABI tuple."},
  {"id":"WARLOCK-DL-026","vote":"accept","reason":"Shipped Elm modules plus a labelled simulated authority honors the single-policy rule."},
  {"id":"WARLOCK-DL-027","vote":"accept","reason":"Source strings inventoried, never silently rewritten."},
  {"id":"WARLOCK-DL-028","vote":"accept","reason":"Fonts are bundled with commit-bound provenance; offline operation is feasible."},
  {"id":"WARLOCK-DL-029","vote":"accept","reason":"Provenance and licenses retained; bounded finish review."},
  {"id":"WARLOCK-DL-030","vote":"revise","reason":"'Apple iOS HIG' narrows the user-named Apple HIG family and mislabels the macOS-relevant sources already cited."}
 ],
 "blockingCorrections":[
  {"id":"WARLOCK-DL-004","correction":"Replace acceptance 'A focused Pending control shows both states.' with 'Where the declared per-surface focus policy keeps a Pending control focusable, the focused control shows both focus and Pending; otherwise the declared fallback applies and Pending remains perceivable on the control.'"},
  {"id":"WARLOCK-DL-018","correction":"Add guardrail: 'Source states Live preview, Historical preview, Preview loading and Preview unavailable (PreviewLifecycle.elm:364-369), including Historical display of retained pixels under the frozen historical/live/unavailable policy and S09 preview13 assertions, are documented as Source and unchanged; Current denotes the Source Live state; the deferral applies only to the proposed Earlier frame relabel and any new retention or dimming behavior.'"},
  {"id":"WARLOCK-DL-030","correction":"Replace 'Apple iOS HIG' with 'Apple Human Interface Guidelines (all platforms, including macOS)'."}
 ],
 "nonblockingAdvice":[
  "DL-001: add a dark monochrome mark and a W-letterform asset for sizes below 24px; warlock-mark-mono.svg hard-codes color #F5F0E8 and is invisible as an <img> on light grounds.",
  "DL-002: state that forced-colors and high-contrast roles resolve to system colors, not reference hex; rename light-theme --w-ink (currently parchment) in schema 2.",
  "DL-002/DL-025: label any Warlock-styled shell specimen Proposed; shell.css uses non-brand hard-coded colors and system-ui.",
  "DL-005/DL-007: change the context.js [aria-current=true] focus hook atomically with any menu semantics change.",
  "DL-007: seed the validator with existing findings (taskbar groups, Applications, Windows, picker verb labels).",
  "DL-011: record that the Source bar status region is visually hidden (shell.css .bar [role=status]).",
  "DL-017: mark the pinned/Launch rows unreachable in today's bar (Taskbar.primary False).",
  "DL-019: distinguish the 8 provider-admitted actions from the 12 Menu.Action constructors.",
  "DL-026: label brand preview.js as an illustration, not an Elm behavior demo.",
  "DL-029: publish prompt text and hashes but redact absolute local originalFile paths in asset-manifest.json.",
  "Keep the gold-for-Unknown question open across reviewers (AM-02 disagrees); text and glyph remain mandatory."
 ],
 "sourceGaps":[
  "SHA-256 of candidate-v1.json not independently computed (no hashing tool available); coordinator must verify the bytes.",
  "Raster art PNGs and font woff2 binaries not in the packet; manifest hashes unverified.",
  "Frozen per-control naming policy, right-click24 and S09 preview13 policy texts not supplied.",
  "Space-key menu activation path and native focus restoration (host.c) not fully traced."
 ],
 "consensusRecommended":false
}
```
