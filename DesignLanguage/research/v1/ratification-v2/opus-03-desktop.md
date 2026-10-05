# Ratification of candidate-v2 (reviewer opus-03-desktop)

**I accept all 30 contracts in candidate-v2 as written, with no blocking corrections.** From my side, I recommend ratifying v2. Unanimity only exists once all five reviewers accept this same hashed version, and the five ballots I read are all for v1. Nothing here claims native acceptance or a full release.

**Hash:** the requested version is SHA-256 `63f5311d840a736d109993d096ccb444adb14057acbe1e9f29ab2e3e805a8754`. It matches `candidate-v2.sha256`. I could not compute it myself because this session has no hashing tool. I also could not byte-compare v1 and v2. Reading the 26 unchanged contracts against v1, the wording looks the same.

**My three v1 revise votes are now resolved:**
- **WARLOCK-DL-017** records the shipped `Taskbar.primary False` call. It marks the zero-family and pinned-to-Launch rows as reachable only at the function level, and limits pending feedback to Apply decisions.
- **WARLOCK-DL-018** keeps the Source preview labels and their fidelity text: Live preview, Historical preview, Preview loading and Preview unavailable. Authorized Historical display stays as it is. Current, Placeholder and Earlier frame are proposed catalog terms only. Any rename, or any new evidence requirement for Live, waits for the ELM-ADOPT-028 review. Only retention beyond the existing authorized, unexpired lease is deferred, and native492 `previewEligible:false` is preserved.
- **WARLOCK-DL-030** now names the full Apple Human Interface Guidelines and explicitly labels the macOS desktop guidance as supplementary, so the macOS menu-bar and window citations are correctly attributed. The iOS emphasis comes from the coordinator's account of the user's request. The prompt I was given cited the platform-general HIG URL.

**WARLOCK-DL-004:** I accepted it in v1. Reviewers opus-01 and opus-04 correctly showed that its "focused Pending" requirement conflicted with Source, which disables blocked controls (`Surface.elm:65-68,87-98`; `popup-adapter.js:20`). The new conditional wording resolves that.

**Remaining disagreements are on record but don't block:**
- Title case versus sentence case for menu commands.
- Gold as the colour for Unknown.
- Whether disabled menu items should be focusable. Source skips them, and the focusable target stays guarded.
- Material 3 claims rest on inaccessible or snippet-only pages.

```json
{
  "reviewerId": "opus-03-desktop",
  "candidateVersion": "candidate-v2",
  "candidateSHA256": "63f5311d840a736d109993d096ccb444adb14057acbe1e9f29ab2e3e805a8754",
  "votes": [
    {"id":"WARLOCK-DL-001","vote":"accept","reason":"Unchanged; preserves Warlock name, sigil, tagline, faces and schema-1 values."},
    {"id":"WARLOCK-DL-002","vote":"accept","reason":"Unchanged; token tiers are a target and current shell.css literals remain Source findings."},
    {"id":"WARLOCK-DL-003","vote":"accept","reason":"Unchanged; measured composited pairs and explicit applicability."},
    {"id":"WARLOCK-DL-004","vote":"accept","reason":"Now conditional on declared focus policy; consistent with Source disabling blocked controls and DL-005 fallback."},
    {"id":"WARLOCK-DL-005","vote":"accept","reason":"Unchanged; keyed identity and declared fallback."},
    {"id":"WARLOCK-DL-006","vote":"accept","reason":"Unchanged; floor met by existing 3px ring; native separately qualified."},
    {"id":"WARLOCK-DL-007","vote":"accept","reason":"Unchanged; label-prefix validator reports Source failures without rewriting."},
    {"id":"WARLOCK-DL-008","vote":"accept","reason":"Unchanged; skip-disabled is Source, focusable menu disabled is a gated target under ELM-ADOPT-030."},
    {"id":"WARLOCK-DL-009","vote":"accept","reason":"Unchanged; Dismiss retains obligations; source-status rows document Space as unbound."},
    {"id":"WARLOCK-DL-010","vote":"accept","reason":"Unchanged; defers to ELM-ADOPT-029, no global shortcut."},
    {"id":"WARLOCK-DL-011","vote":"accept","reason":"Unchanged; one owner, no success toasts."},
    {"id":"WARLOCK-DL-012","vote":"accept","reason":"Unchanged; observation-only reconcile, no Unknown replay."},
    {"id":"WARLOCK-DL-013","vote":"accept","reason":"Unchanged; 24px catalog-scoped."},
    {"id":"WARLOCK-DL-014","vote":"accept","reason":"Unchanged; identity/authority continuity without freezing revisions."},
    {"id":"WARLOCK-DL-015","vote":"accept","reason":"Unchanged; reduced motion under S02/023/024."},
    {"id":"WARLOCK-DL-016","vote":"accept","reason":"Unchanged; matches ChoiceDeadline expiry and RetryWindows path."},
    {"id":"WARLOCK-DL-017","vote":"accept","reason":"Records shipped Taskbar.primary False, unreachable Launch rows and pending only for Apply; my v1 correction resolved."},
    {"id":"WARLOCK-DL-018","vote":"accept","reason":"Preserves Source Live/Historical/Loading/Unavailable labels and authorized Historical display; only new retention deferred; my v1 correction resolved."},
    {"id":"WARLOCK-DL-019","vote":"accept","reason":"Unchanged; capability-driven content documenting all Menu.Action constructors."},
    {"id":"WARLOCK-DL-020","vote":"accept","reason":"Unchanged; guarded search extension."},
    {"id":"WARLOCK-DL-021","vote":"accept","reason":"Unchanged; host-owned workspaces, no hover flyout, scope retained."},
    {"id":"WARLOCK-DL-022","vote":"accept","reason":"Unchanged; settings declare guarantees."},
    {"id":"WARLOCK-DL-023","vote":"accept","reason":"Unchanged; full supplemental closure is the inventory basis."},
    {"id":"WARLOCK-DL-024","vote":"accept","reason":"Unchanged; Read-mode IA with Not yet specified markers."},
    {"id":"WARLOCK-DL-025","vote":"accept","reason":"Unchanged; scoped evidence, Native label requires receipt, scenario and ABI tuple."},
    {"id":"WARLOCK-DL-026","vote":"accept","reason":"Unchanged; shipped Elm with fixture-only authority."},
    {"id":"WARLOCK-DL-027","vote":"accept","reason":"Unchanged; inventory without silent rewrite."},
    {"id":"WARLOCK-DL-028","vote":"accept","reason":"Unchanged; reflow and offline local assets."},
    {"id":"WARLOCK-DL-029","vote":"accept","reason":"Unchanged; hash/changelog reconciliation and bounded finish review."},
    {"id":"WARLOCK-DL-030","vote":"accept","reason":"Names the full Apple HIG and explicitly labels supplemental macOS desktop guidance; my v1 concern resolved."}
  ],
  "blockingCorrections": [],
  "nonblockingAdvice": [
    "DL-007/009: aria-current is the menu roving-focus hook (context.js:58,71-72); migrate bridge focus atomically with any typed selected/checked field.",
    "DL-009/010: label Shift+F10/ContextMenu, picker Escape->control:close, menu Escape->Dismiss and Tab Close/selected toggle as Source; Space unbound in menu mode.",
    "DL-004/005: declare the menu focus fallback (e.g. control:menu-close) when rows become disabled during Pending/Unknown.",
    "DL-019: classify geometry-path Restore/Minimize rows as supported-but-unavailable; PinToTaskbar is never produced by Provider; confirm AlwaysOnTop 'checked' semantics.",
    "DL-027: record 'Working…' vs 'Applying window change…' copy inconsistency and missing lang attribute in bar.html/popup.html.",
    "DL-029: redact absolute local originalFile paths when publishing asset provenance.",
    "DL-030: the Apple HIG root URL is platform-general; keep iOS-versus-macOS attribution per citation.",
    "Preserved disagreements (non-blocking): title vs sentence case for menu commands; gold for Unknown; focusable disabled menus; Material 3 snippet-only evidence."
  ],
  "sourceGaps": [
    "SHA-256 of candidate-v2.json not computed in this session (no hashing tool); value taken from candidate-v2.sha256 and the coordinator.",
    "Byte-identity of the 26 unchanged contracts versus v1 checked by reading, not by byte comparison.",
    "All five consensus/*.vote.json ballots are v1 ballots; no other reviewer's v2 vote was available to me.",
    "right-click24 and original S09 preview13 scenario texts not in packet.",
    "Native host C, compiled bundles, font binaries and raster art not fully reviewed or supplied; no native receipts exist."
  ],
  "consensusRecommended": true
}
```
