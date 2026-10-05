I accept all 30 contracts in candidate-v2 and recommend ratifying it at the requested hash, `63f5311d840a736d109993d096ccb444adb14057acbe1e9f29ab2e3e805a8754`. That's my vote only. It becomes consensus only if all five reviewers accept this same hash, and every ballot on file today is still a v1 ballot.

**Hash limit:** I did not compute that hash; this session has no hashing tool. It matches `candidate-v2.sha256`. I compared the 26 unchanged contracts with v1 by reading them, not by a byte diff, and saw no differences.

**The four corrections, checked against the source and the v1 ballots:**
- **DL-004:** the new acceptance wording is substantively my v1 correction, and it also covers opus-01's. Pending and Unknown focus now depends on the declared per-surface policy, and focus falls back as DL-005 declares. In today's source those controls are disabled (`Surface.elm:52-55, 65-68, 75-77, 87-98`). My blocking objection is resolved.
- **DL-017:** this matches opus-03's correction exactly. The shipped code always calls `Taskbar.primary False` (`TaskbarShell.elm:83`, `Surface.elm:87-91`). Pending feedback is limited to Apply decisions, and the pinned-to-Launch row is marked unreachable from shipped groups.
- **DL-018:** this covers what opus-02, 03 and 05 asked for, plus most of opus-01's. The existing preview labels stay as they are: "Live preview", "Historical preview", "Preview loading", "Preview unavailable" (`PreviewLifecycle.elm:365-369`), along with the fidelity text and the authorized Historical display. "Current", "Placeholder" and "Earlier frame" are proposed terms, and any rename waits for the ELM-ADOPT-028 review. Only new retention is deferred; expiry, the lock check (`:369`) and `previewEligible:false` don't change.
  - One part differs from opus-01's request: opus-01 wanted "Current" to simply mean today's Live state. v2 instead makes any rename wait for that review. I think that's consistent with the frozen policy, but only opus-01 can say whether it resolves their objection.
- **DL-030:** the iOS reference the user asked for stays, with macOS desktop guidance explicitly labelled as supplementary. I consider that a faithful resolution. opus-01, 02 and 03 had asked for broader "all platforms" wording, so they need to confirm it.

**Prior disagreement, kept on record:**
- Focusable disabled menu items remain a gated future target. The current skip-disabled behaviour stays labelled as Source.
- The withdrawn AM-08 timing concern stays withdrawn.
- No native or full-release claim is made.

```json
{
  "reviewerId": "opus-04-accessibility-motion",
  "candidateVersion": "candidate-v2",
  "candidateSHA256": "63f5311d840a736d109993d096ccb444adb14057acbe1e9f29ab2e3e805a8754",
  "hashVerification": "Not independently computed (no hashing tool in this read-only session). Requested hash matches candidate-v2.sha256. Unchanged contracts compared to v1 by reading, not byte diff.",
  "votes": [
    {"id":"WARLOCK-DL-001","vote":"accept","reason":"Unchanged; preserves brand and philosophy."},
    {"id":"WARLOCK-DL-002","vote":"accept","reason":"Unchanged; shell.css literals remain a documented target gap."},
    {"id":"WARLOCK-DL-003","vote":"accept","reason":"Unchanged; composited contrast and explicit inactive classification."},
    {"id":"WARLOCK-DL-004","vote":"accept","reason":"Corrected acceptance makes focus conditional on declared policy with DL-005 fallback; consistent with Source disabled Pending controls."},
    {"id":"WARLOCK-DL-005","vote":"accept","reason":"Unchanged; declared fallback covers focus loss on disable."},
    {"id":"WARLOCK-DL-006","vote":"accept","reason":"Unchanged; existing 3px outline meets floor; native separately qualified."},
    {"id":"WARLOCK-DL-007","vote":"accept","reason":"Unchanged; validator reports existing label-prefix failures."},
    {"id":"WARLOCK-DL-008","vote":"accept","reason":"Unchanged; skip-disabled labelled Source, focusable menu items gated."},
    {"id":"WARLOCK-DL-009","vote":"accept","reason":"Unchanged; matches Source Escape/Dismiss/returnFocus."},
    {"id":"WARLOCK-DL-010","vote":"accept","reason":"Unchanged; ADOPT-029 authority, no F6/global shortcut."},
    {"id":"WARLOCK-DL-011","vote":"accept","reason":"Unchanged; single announcement owner."},
    {"id":"WARLOCK-DL-012","vote":"accept","reason":"Unchanged; no fabricated refusal, no Unknown replay."},
    {"id":"WARLOCK-DL-013","vote":"accept","reason":"Unchanged; 24px is catalog-only."},
    {"id":"WARLOCK-DL-014","vote":"accept","reason":"Unchanged; preference changes cannot rebind or activate."},
    {"id":"WARLOCK-DL-015","vote":"accept","reason":"Unchanged; consistent with brand preview Source and ADOPT-023/024."},
    {"id":"WARLOCK-DL-016","vote":"accept","reason":"Unchanged; ChoiceDeadline is a post-choice native wait with a safe refresh path."},
    {"id":"WARLOCK-DL-017","vote":"accept","reason":"Records shipped Taskbar.primary False, unreachable pinned rows, pending only for Apply; verified in TaskbarShell.elm:83 and Surface.elm:87-91."},
    {"id":"WARLOCK-DL-018","vote":"accept","reason":"Preserves Source Live/Historical/Loading/Unavailable labels (PreviewLifecycle.elm:365-369), authorized Historical display and preview13; new terms and renames gated; only new retention deferred."},
    {"id":"WARLOCK-DL-019","vote":"accept","reason":"Unchanged."},
    {"id":"WARLOCK-DL-020","vote":"accept","reason":"Unchanged; composition-safe guarded search."},
    {"id":"WARLOCK-DL-021","vote":"accept","reason":"Unchanged."},
    {"id":"WARLOCK-DL-022","vote":"accept","reason":"Unchanged."},
    {"id":"WARLOCK-DL-023","vote":"accept","reason":"Unchanged; full supplemental closure is the inventory basis."},
    {"id":"WARLOCK-DL-024","vote":"accept","reason":"Unchanged."},
    {"id":"WARLOCK-DL-025","vote":"accept","reason":"Unchanged; scoped evidence, native label needs receipt/scenario/ABI tuple."},
    {"id":"WARLOCK-DL-026","vote":"accept","reason":"Unchanged; shipped modules, fixture-only authority, no Unknown retry."},
    {"id":"WARLOCK-DL-027","vote":"accept","reason":"Unchanged."},
    {"id":"WARLOCK-DL-028","vote":"accept","reason":"Unchanged; reduced motion and forced colors exercised."},
    {"id":"WARLOCK-DL-029","vote":"accept","reason":"Unchanged."},
    {"id":"WARLOCK-DL-030","vote":"accept","reason":"Keeps user-requested iOS reference and explicitly labels supplemental macOS desktop guidance."}
  ],
  "blockingCorrections": [],
  "nonblockingAdvice": [
    "DL-005: declare the menu fallback while rows are disabled (e.g. control:menu-close); popup is not keyed in Source.",
    "DL-007: seed the validator with Source failures at Surface.elm:57, :84 and :98; keep the operation verb as description; change the context.js aria-current focus hook in the same change as any semantics update.",
    "DL-011: bar and popup render the same notice in two polite live regions; designate one route before native AT qualification.",
    "DL-015: product reduced motion should be a typed native observation (portal, then GTK settings); WebView media query only as fallback.",
    "DL-018/DL-030: opus-01, 02 and 03 should confirm that the v2 wording resolves their v1 objections (the 'Current' deferral, and iOS with supplemental macOS rather than all platforms)."
  ],
  "sourceGaps": [
    "No declared per-surface focus fallback when the focused control is disabled during Pending/Unknown; DOM focus is lost.",
    "shell.css uses non-token literal colors and system-ui; disabled controls have only opacity, with no reason text.",
    "No typeahead; Space is unbound in menu mode; no arrow navigation in picker/applications popups.",
    "No typed checked/selected field; aria-current is derived from the detail string 'Selected'.",
    "Native AT, IME, reduced-motion/contrast observation and presentation evidence are absent; no native or full-release acceptance is claimed.",
    "Candidate SHA-256 not independently recomputed in this session; all consensus ballots on file are v1, so v2 ballots from the other four reviewers are not yet visible."
  ],
  "consensusRecommended": true
}
```
