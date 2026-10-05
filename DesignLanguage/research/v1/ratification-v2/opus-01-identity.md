# Exact-v2 ratification — opus-01-identity

**Vote: I accept all 30 contracts in candidate-v2 as written, with no blocking conditions.** I recommend consensus on this exact version. Unanimity exists only if all five reviewers accept the same hash.

**Hash:** I could not compute SHA-256; my session has no hashing tool. The requested hash is `63f5311d840a736d109993d096ccb444adb14057acbe1e9f29ab2e3e805a8754`, which is what `candidate-v2.sha256` declares. I am relying on the coordinator's independent computation, and my vote applies to the JSON content I read under that hash.

**What I read:** `candidate-v2.json` and `.md`, the five ballots in `consensus/` (all v1 votes were "revise" with consensus not recommended), and the supplemental source needed to check the corrections. Nothing here claims native or full-release acceptance.

**The four corrections, checked against source:**
- **DL-004.** Focus and outcome cues are now required only where the declared per-surface policy lets a control hold focus. Otherwise the outcome stays perceivable and focus follows DL-005's fallback. This fixes my v1 blocker and opus-04's: blocked controls are disabled in `Surface.elm:68/90`, and ELM-ADOPT-030 stays authoritative.
- **DL-017.** It now records the shipped call `Taskbar.primary False`. That is correct: it appears at `Surface.elm:87/90/91/167` and `TaskbarShell.elm:83`. Pending feedback is limited to Apply decisions. The zero-family and pinned-to-Launch rows are marked unreachable, which is also correct, since `Taskbar.groups` only builds groups with at least one family. This fixes opus-03's blocker.
- **DL-018.**
  - It preserves the Source labels Live, Historical, Loading and Unavailable (`PreviewLifecycle.elm:25,142,364-369`) and the authorized Historical pixels.
  - Its deferral now covers only retention beyond the existing unexpired, privacy-matched lease. The source behaviour it relies on is real: frames past their expiry are retired (`:224-227`), and lock or generation changes revoke the preview (`:277,369`).
  - Current, Placeholder and Earlier frame are now proposed terms only.

  This fixes my blocker and those of opus-02, opus-03 and opus-05.
- **DL-030.** It names the Apple Human Interface Guidelines, keeps the iOS design language the user requested, and explicitly labels macOS desktop guidance as supplementary. My v1 objection was that macOS was left out, and this resolves it.

**Unchanged contracts:** I compared DL-001–003, 005–016 and 019–029 in the v1 and v2 Markdown, and the text is identical. My v1 acceptances therefore still hold.

**Earlier dissent:** My v1 votes were "revise" on DL-004, DL-018 and DL-030. All three are resolved in v2. The nonblocking items stay open and are listed below.

```json
{
 "reviewerId":"opus-01-identity",
 "candidateVersion":"candidate-v2",
 "candidateSHA256":"63f5311d840a736d109993d096ccb444adb14057acbe1e9f29ab2e3e805a8754",
 "votes":[
  {"id":"WARLOCK-DL-001","vote":"accept","reason":"Unchanged from v1; preserves Warlock identity and schema-1 values."},
  {"id":"WARLOCK-DL-002","vote":"accept","reason":"Unchanged; three-tier tokens; the shell is Proposed relative to the current shell.css."},
  {"id":"WARLOCK-DL-003","vote":"accept","reason":"Unchanged; contrast floors consistent with computed token ratios."},
  {"id":"WARLOCK-DL-004","vote":"accept","reason":"v2 makes focus cues conditional on declared per-surface focusability with the DL-005 fallback; resolves my v1 blocker."},
  {"id":"WARLOCK-DL-005","vote":"accept","reason":"Unchanged; consistent with ELM-ADOPT-016."},
  {"id":"WARLOCK-DL-006","vote":"accept","reason":"Unchanged; catalog ring; native treatment qualified separately."},
  {"id":"WARLOCK-DL-007","vote":"accept","reason":"Unchanged; matches the ELM-ADOPT-017 guardrail; existing name mismatches become findings."},
  {"id":"WARLOCK-DL-008","vote":"accept","reason":"Unchanged; skip-disabled labelled Source; focusable-disabled menus a guarded target."},
  {"id":"WARLOCK-DL-009","vote":"accept","reason":"Unchanged; Escape maps to Menu.Dismiss by MenuId and keeps obligations."},
  {"id":"WARLOCK-DL-010","vote":"accept","reason":"Unchanged; defers to ELM-ADOPT-029."},
  {"id":"WARLOCK-DL-011","vote":"accept","reason":"Unchanged; single announcement owner."},
  {"id":"WARLOCK-DL-012","vote":"accept","reason":"Unchanged; no automatic Unknown replay."},
  {"id":"WARLOCK-DL-013","vote":"accept","reason":"Unchanged; 24px applies to the catalog only."},
  {"id":"WARLOCK-DL-014","vote":"accept","reason":"Unchanged; continuity without freezing revisions."},
  {"id":"WARLOCK-DL-015","vote":"accept","reason":"Unchanged; matches brand motion policy and S02 bounds."},
  {"id":"WARLOCK-DL-016","vote":"accept","reason":"Unchanged; original deadlines fixed; expired choices unavailable."},
  {"id":"WARLOCK-DL-017","vote":"accept","reason":"v2 records the shipped Taskbar.primary False call (Surface.elm, TaskbarShell.elm:83), unreachable Launch and zero-family rows, and Apply-only pending; verified in source."},
  {"id":"WARLOCK-DL-018","vote":"accept","reason":"v2 preserves Source Live/Historical/Loading/Unavailable and authorized Historical pixels; deferral narrowed to new retention; expiry and lock revocation verified in PreviewLifecycle.elm; resolves my v1 blocker."},
  {"id":"WARLOCK-DL-019","vote":"accept","reason":"Unchanged; capability-driven content."},
  {"id":"WARLOCK-DL-020","vote":"accept","reason":"Unchanged; guarded extension."},
  {"id":"WARLOCK-DL-021","vote":"accept","reason":"Unchanged; host ownership and gates kept."},
  {"id":"WARLOCK-DL-022","vote":"accept","reason":"Unchanged; settings declare their guarantees."},
  {"id":"WARLOCK-DL-023","vote":"accept","reason":"Unchanged; registry built from the supplement closure."},
  {"id":"WARLOCK-DL-024","vote":"accept","reason":"Unchanged; Read-mode site structure."},
  {"id":"WARLOCK-DL-025","vote":"accept","reason":"Unchanged; scoped evidence; native label requires receipt and ABI tuple."},
  {"id":"WARLOCK-DL-026","vote":"accept","reason":"Unchanged; shipped Elm modules with a labelled simulated authority."},
  {"id":"WARLOCK-DL-027","vote":"accept","reason":"Unchanged; source strings never silently rewritten."},
  {"id":"WARLOCK-DL-028","vote":"accept","reason":"Unchanged; offline-capable with bundled fonts."},
  {"id":"WARLOCK-DL-029","vote":"accept","reason":"Unchanged; provenance and bounded finish review."},
  {"id":"WARLOCK-DL-030","vote":"accept","reason":"v2 names the Apple HIG with the requested iOS design language and explicitly labelled supplemental macOS desktop guidance; resolves my v1 blocker."}
 ],
 "blockingCorrections":[],
 "nonblockingAdvice":[
  "DL-001: add a dark monochrome mark and a W-letterform asset below 24px; warlock-mark-mono.svg hard-codes color #F5F0E8.",
  "DL-002: state that forced-colors roles resolve to system colors; rename light-theme --w-ink in schema 2; label Warlock-styled shell specimens Proposed (shell.css uses non-brand colors and system-ui).",
  "DL-005/DL-007: update the context.js [aria-current=true] focus hook atomically with any menu semantics change; seed the label-in-name validator with existing taskbar, Applications, Windows and picker findings.",
  "DL-011: record that the Source bar status region is visually hidden.",
  "DL-019: distinguish the 8 provider-admitted actions from the 12 Menu.Action constructors.",
  "DL-026: label brand preview.js as an illustration, not an Elm behavior demo.",
  "DL-029: redact absolute local originalFile paths when publishing provenance.",
  "Gold-for-Unknown remains an open design question across reviewers; text and glyph cues remain mandatory."
 ],
 "sourceGaps":[
  "SHA-256 of candidate-v2.json not computed in this session (no hashing tool); relies on the coordinator's independent computation.",
  "Raster art PNGs and font woff2 binaries not in the packet; their manifest hashes are unverified.",
  "Frozen per-control naming policy, right-click24 and S09 preview13 policy texts not supplied.",
  "Space-key menu activation path and native focus restoration in host.c not fully traced."
 ],
 "consensusRecommended":true
}
```
