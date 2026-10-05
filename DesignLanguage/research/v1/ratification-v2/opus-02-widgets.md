# Exact-v2 ratification of candidate-v2: opus-02-widgets

**I accept all 30 contracts, and I recommend consensus on this exact version.** Unanimity still depends on the other four ballots on this same hash.

**Hash:** The requested version is candidate-v2, SHA-256 `63f5311d840a736d109993d096ccb444adb14057acbe1e9f29ab2e3e805a8754`. I could not compute that hash myself because this session has no shell or hashing tool; my vote is bound to the coordinator-computed value. I did check that `candidate-v2.json` and `candidate-v2.md` agree on the four changed contracts, and that `changesFromV1` lists exactly DL-004, DL-017, DL-018 and DL-030.

**How the four changes resolve the v1 blocking corrections (checked against supplemental source):**
- **DL-004** now makes focus conditional on the declared per-surface policy and falls back to DL-005. This matches the source, where blocked controls are published with `enabled=False` (`Surface.elm:65-98`). It adopts the opus-04 and opus-01 wording.
- **DL-017** records the call that actually ships, `Taskbar.primary False`, confirmed at `TaskbarShell.elm:83` and `Surface.elm:87-91,167`. It marks the pinned-to-Launch and zero-family rows as unreachable, and limits pending feedback to Apply decisions.
- **DL-018** now preserves the Source Live/Historical/Loading/Unavailable labels and the authorized Historical display (`PreviewLifecycle.elm:135-147,364-375`). It defers only new retention beyond the existing lease, and leaves expiry/lock revocation and native492 unchanged. This resolves my v1 objection exactly.
- **DL-030** now reads "Apple Human Interface Guidelines (iOS design language, with supplemental macOS desktop guidance)". `request.json:27` does name the Apple iOS HIG for one reviewer topic, and macOS desktop guidance is now explicit. This resolves my mis-scoping objection.

Of the 26 contracts left unchanged, I accepted all but DL-018 and DL-030 in v1. My recorded v1 dissent on those two still stands as history; it is resolved by v2. I make no native or full-release claim.

```json
{
 "reviewerId":"opus-02-widgets",
 "candidateVersion":"candidate-v2",
 "candidateSHA256":"63f5311d840a736d109993d096ccb444adb14057acbe1e9f29ab2e3e805a8754",
 "votes":[
  {"id":"WARLOCK-DL-001","vote":"accept","reason":"Unchanged from v1; brand and philosophy preserved."},
  {"id":"WARLOCK-DL-002","vote":"accept","reason":"Unchanged; token tiers are a target over Source shell.css literals."},
  {"id":"WARLOCK-DL-003","vote":"accept","reason":"Unchanged; composited measurement and inactive classification."},
  {"id":"WARLOCK-DL-004","vote":"accept","reason":"Focus now conditional on declared policy with DL-005 fallback; matches Source disabled blocking."},
  {"id":"WARLOCK-DL-005","vote":"accept","reason":"Unchanged; popup unkeyed in Source, keyed identity is the target."},
  {"id":"WARLOCK-DL-006","vote":"accept","reason":"Unchanged; existing 3px outline meets the floor."},
  {"id":"WARLOCK-DL-007","vote":"accept","reason":"Unchanged; consistent with ELM-ADOPT-017; validator reports Source failures."},
  {"id":"WARLOCK-DL-008","vote":"accept","reason":"Unchanged; skip-disabled labeled Source, focusable menus gated."},
  {"id":"WARLOCK-DL-009","vote":"accept","reason":"Unchanged; Msg mapping with source status."},
  {"id":"WARLOCK-DL-010","vote":"accept","reason":"Unchanged; defers to ELM-ADOPT-029, no global shortcut."},
  {"id":"WARLOCK-DL-011","vote":"accept","reason":"Unchanged; addresses duplicate polite regions."},
  {"id":"WARLOCK-DL-012","vote":"accept","reason":"Unchanged; no automatic Unknown replay."},
  {"id":"WARLOCK-DL-013","vote":"accept","reason":"Unchanged; 24px catalog-only."},
  {"id":"WARLOCK-DL-014","vote":"accept","reason":"Unchanged; legitimate generation changes allowed."},
  {"id":"WARLOCK-DL-015","vote":"accept","reason":"Unchanged; native timing under frozen gates."},
  {"id":"WARLOCK-DL-016","vote":"accept","reason":"Unchanged; deadlines fixed, expired choices unavailable."},
  {"id":"WARLOCK-DL-017","vote":"accept","reason":"Records shipped Taskbar.primary False (TaskbarShell.elm:83, Surface.elm:87-91); unreachable rows labeled; pending only for Apply."},
  {"id":"WARLOCK-DL-018","vote":"accept","reason":"Preserves Source Live/Historical labels and authorized historical display under frozen S09; only new retention deferred. Resolves my v1 correction."},
  {"id":"WARLOCK-DL-019","vote":"accept","reason":"Unchanged; capability-driven content with reasons."},
  {"id":"WARLOCK-DL-020","vote":"accept","reason":"Unchanged; guarded extension."},
  {"id":"WARLOCK-DL-021","vote":"accept","reason":"Unchanged; host ownership and gates."},
  {"id":"WARLOCK-DL-022","vote":"accept","reason":"Unchanged; settings guarantees."},
  {"id":"WARLOCK-DL-023","vote":"accept","reason":"Unchanged; full closure registry."},
  {"id":"WARLOCK-DL-024","vote":"accept","reason":"Unchanged; Read-mode IA."},
  {"id":"WARLOCK-DL-025","vote":"accept","reason":"Unchanged; scoped evidence records."},
  {"id":"WARLOCK-DL-026","vote":"accept","reason":"Unchanged; shipped Elm with fixture authority."},
  {"id":"WARLOCK-DL-027","vote":"accept","reason":"Unchanged; inventory without rewriting frozen strings."},
  {"id":"WARLOCK-DL-028","vote":"accept","reason":"Unchanged; offline accessible catalog."},
  {"id":"WARLOCK-DL-029","vote":"accept","reason":"Unchanged; versioned provenance and bounded review."},
  {"id":"WARLOCK-DL-030","vote":"accept","reason":"Names full Apple HIG with the request's iOS reference (request.json:27) and explicit supplemental macOS guidance; resolves my v1 correction."}
 ],
 "blockingCorrections":[],
 "nonblockingAdvice":[
  "Retain v1 advice: registry must cover all Surface.elm:57-101 controls; record label-in-name Source failures (Surface.elm:57,84,98); document menu key map incl. unbound Space, Tab toggle and aria-current-driven focus (context.js:56-73); migrate bridge focus logic with any typed selected field.",
  "DL-018: catalog copy should state that 'Current'/'Earlier frame' are unratified terms and render Source labels verbatim alongside them."
 ],
 "sourceGaps":[
  "Candidate SHA-256 not independently computed in this session (no hashing tool); relied on coordinator-computed hash.",
  "native/host.c and shared-host.c not fully reviewed; native focus restoration and menu-navigation handling unverified here.",
  "Original S01-S16/right-click24 scenario oracles not in packet."
 ],
 "consensusRecommended":true
}
```
