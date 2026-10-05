# Ratification of candidate-v2 (opus-05-catalog-craft)

**I accept all 30 contracts in candidate-v2 and recommend consensus. Consensus exists only if all five reviewers accept this exact version.**

**Hash.** The version under vote is `63f5311d840a736d109993d096ccb444adb14057acbe1e9f29ab2e3e805a8754`. I did not compute it myself, because this session has no shell hashing tool. That value is what `candidate-v2.sha256` states and what the request names; I'm relying on the coordinator's computation.

**The 26 unchanged contracts.** I checked every EARS requirement and guardrail line in `candidate-v2.json` against v1. Unchanged text sits at the same line positions with the same wording. I compared by reading, not by byte hash.

**v1 ballot history.** In v1, five revise objections covered four contracts:
- DL-004: opus-01 and opus-04.
- DL-017: opus-03.
- DL-018: opus-01, opus-02, opus-03 and me.
- DL-030: opus-01, opus-02 and opus-03.

My v1 revise on DL-018 is part of that record. Each v2 change resolves its objection on the source:

- **DL-004.** Focus is now conditional on each surface's declared policy, with the DL-005 fallback otherwise. That matches the shipped behavior: Pending rows are disabled (`Surface.elm:65,68`), Escape still works at document level (`context.js:45-47`), and the outcome shows through the row detail "Awaiting native confirmation" or the status line. ELM-ADOPT-030 still governs.
- **DL-017.** It now records the shipped call `Taskbar.primary False` (`TaskbarShell.elm:83`, `Surface.elm:87-96`). The zero-family and pinned rows are marked as reachable only through the function, and pending feedback applies only to Apply. All of that is accurate.
- **DL-018.** This resolves my blocking correction. The source labels Live preview, Historical preview, Preview loading and Preview unavailable stay unchanged (`PreviewLifecycle.elm:364-375`). Authorized Historical display is neither removed nor relabeled. "Current", "Placeholder" and "Earlier frame" are proposed catalog terms only, and any rename or added Live evidence is gated on ELM-ADOPT-028 review. The deferral now covers only new retention.
- **DL-030.** It keeps the iOS reference the user asked for and labels the macOS desktop guidance as supplementary. That fixes the misattribution.

I'm making no native-acceptance or full-release claim.

```json
{
  "reviewerId": "opus-05-catalog-craft",
  "candidateVersion": "candidate-v2",
  "candidateSHA256": "63f5311d840a736d109993d096ccb444adb14057acbe1e9f29ab2e3e805a8754",
  "votes": [
    {"id":"WARLOCK-DL-001","vote":"accept","reason":"Unchanged from v1; brand and schema-1 preservation."},
    {"id":"WARLOCK-DL-002","vote":"accept","reason":"Unchanged; token tiers are a target; shell.css literals remain labeled Source."},
    {"id":"WARLOCK-DL-003","vote":"accept","reason":"Unchanged; composited contrast and explicit classification."},
    {"id":"WARLOCK-DL-004","vote":"accept","reason":"v2 makes focus conditional on declared policy with DL-005 fallback, matching Source disabled Pending rows (Surface.elm:65,68) and ELM-ADOPT-030."},
    {"id":"WARLOCK-DL-005","vote":"accept","reason":"Unchanged; declared fallback covers Source focus loss."},
    {"id":"WARLOCK-DL-006","vote":"accept","reason":"Unchanged; catalog focus floor; native separately qualified."},
    {"id":"WARLOCK-DL-007","vote":"accept","reason":"Unchanged; prefix rule per ELM-ADOPT-017; Source failures reported, not rewritten."},
    {"id":"WARLOCK-DL-008","vote":"accept","reason":"Unchanged; skip-disabled is Source; focusable disabled menu items are a gated future target."},
    {"id":"WARLOCK-DL-009","vote":"accept","reason":"Unchanged; matches context.js/Surface.resolve mapping; dismissal retains obligations."},
    {"id":"WARLOCK-DL-010","vote":"accept","reason":"Unchanged; defers to ELM-ADOPT-029."},
    {"id":"WARLOCK-DL-011","vote":"accept","reason":"Unchanged; single announcement owner target."},
    {"id":"WARLOCK-DL-012","vote":"accept","reason":"Unchanged; no automatic Unknown replay."},
    {"id":"WARLOCK-DL-013","vote":"accept","reason":"Unchanged; 24px scoped to the catalog."},
    {"id":"WARLOCK-DL-014","vote":"accept","reason":"Unchanged; permits legitimate publication/lease and generation changes."},
    {"id":"WARLOCK-DL-015","vote":"accept","reason":"Unchanged; S02/023/024 preserved."},
    {"id":"WARLOCK-DL-016","vote":"accept","reason":"Unchanged; matches Desktop ChoiceDeadline and ExpirePrepared; deadlines fixed."},
    {"id":"WARLOCK-DL-017","vote":"accept","reason":"v2 records shipped Taskbar.primary False, function-only rows and pending for Apply only; accurate to TaskbarShell.elm:83 and Surface.elm:87-96."},
    {"id":"WARLOCK-DL-018","vote":"accept","reason":"v2 preserves Source Live/Historical/Loading/Unavailable labels and authorized Historical display under frozen S09/ADOPT-028; proposed terms do not rename; deferral narrowed to new retention. Resolves my v1 blocking correction."},
    {"id":"WARLOCK-DL-019","vote":"accept","reason":"Unchanged."},
    {"id":"WARLOCK-DL-020","vote":"accept","reason":"Unchanged; current launcher has no search."},
    {"id":"WARLOCK-DL-021","vote":"accept","reason":"Unchanged."},
    {"id":"WARLOCK-DL-022","vote":"accept","reason":"Unchanged."},
    {"id":"WARLOCK-DL-023","vote":"accept","reason":"Unchanged; supplemental closure inventory."},
    {"id":"WARLOCK-DL-024","vote":"accept","reason":"Unchanged."},
    {"id":"WARLOCK-DL-025","vote":"accept","reason":"Unchanged; scoped evidence; native label requires receipt, scenario and ABI tuple."},
    {"id":"WARLOCK-DL-026","vote":"accept","reason":"Unchanged; shipped Elm plus labeled simulated authority."},
    {"id":"WARLOCK-DL-027","vote":"accept","reason":"Unchanged."},
    {"id":"WARLOCK-DL-028","vote":"accept","reason":"Unchanged."},
    {"id":"WARLOCK-DL-029","vote":"accept","reason":"Unchanged."},
    {"id":"WARLOCK-DL-030","vote":"accept","reason":"v2 names Apple Human Interface Guidelines with the user-requested iOS design language and explicitly supplemental macOS desktop guidance."}
  ],
  "blockingCorrections": [],
  "nonblockingAdvice": [
    "DL-018: when documenting 'authorized, unexpired, privacy-matched lease', cite the exact PreviewLifecycle.authorized predicate (PreviewLifecycle.elm:134-135: connected, present, not locked, GPU ready, owned, binding/clock/generation match, unexpired, client coverage) rather than paraphrasing.",
    "Carry forward the v1 nonblocking items: Source label-in-name findings (Surface.elm:57,84,98), Space/typeahead absence and the Tab toggle in menu mode (context.js), duplicate polite status regions, and DL-023 coverage of Launch statuses, preview statuses and all Surface.elm control identities.",
    "Retain the v1 ballot history: my v1 revise on DL-018 is resolved by v2, not withdrawn."
  ],
  "sourceGaps": [
    "Candidate-v2 SHA-256 not independently computed (no shell hashing tool); identified from candidate-v2.sha256 and the request.",
    "Unchanged contracts compared to v1 by reading line-aligned EARS/guardrail text, not by byte hash.",
    "Native focus restoration after Escape, AT tree, IME, keyboard scope and hardware presentation are not evidenced; nothing here is native or full-release acceptance.",
    "host.c and shared-host.c reviewed only for key handling."
  ],
  "consensusRecommended": true
}
```
