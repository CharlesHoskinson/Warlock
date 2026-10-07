# Product/UX review: Warlock after the last 24h (opus_product)

## Bottom line
The day produced no change a user can see. Nothing was installed. The controlled preview is fixed at opacity 0. The work went into preview-realm retirement, drain and restart plumbing, and each step was wrapped in freeze and publish ceremony. The completion gate is all-or-nothing, so no single original requirement can ever be closed. That gate is the root defect. The empty `completedRequirementIds` list mostly reflects that defect and poor bookkeeping; it does not prove that zero requirements are satisfied.

## Findings, ranked by severity

**F1 (fatal): there is no path to close an individual requirement.**
- `INSTRUCTIONS.md:5` and `:40` allow completion only for the "full GUI release".
- In `implementation-status.json:35`, `completedRequirementIds` is `[]`. The active slice listed there is `elm-recovery-delivery-general-reviewed-v656`, a lane that differs from the preview work being done.
- None of the OpenSpec product changes has a single task checked: `elm-desktop-pivot/tasks.md` 0/242, `elm-release-closure` 0/37, `elm-design-adoption` 0/36, `elm-right-click` 0/11.
- The only change with checked tasks is the internal `warlock-preview-actor-retirement` (36/75).
- The process rewards internal contracts and has no exit for product requirements.

**F2 (fatal): evidence cannot be traced to original requirements.**
- A grep for `ELM-[A-Z]+-\d{3}` across the three current component reports (`component-report-gui143…`, `…window-restart-198-201`, `…combined-restart-204-207`) finds zero original requirement IDs. They mention only the bare label "S09".
- Meanwhile the HANDOFF created CONTROL-035 through CONTROL-049 (`HANDOFF.md:415–867`).
- New internal contracts are being invented faster than original EARS are referenced. Even where real evidence exists, it cannot be credited to a requirement.

**F3 (critical): the main visible feature was deliberately hidden all day.**
- The native curtain stays at opacity 0 (`HANDOFF.md:402`, `:499–513`).
- Setting it to 1 was used as the "expected failure" (GUI128/Native139).
- Every "red19200 pixels" pass (for example `:471–482`) is offscreen WebKit reference pixels. `:482` says plainly "offscreen pixels grant no physical reveal authority".
- The controlled route is a "presentation-only placeholder" (`:399`). The previews in ELM-UX-005/006/007 cannot reach a user.

**F4 (critical): the native passes demonstrate fixtures, not user journeys.**
- Stimuli are synthetic: a "synthetic peer", a "foreign-green fixture", a red test client, and "explicit private API stops" of WebKit (`:760`).
- These are legitimate fault-injection controls. None is a representative journey ("open taskbar group → pick window → it activates") tied to a scenario name in `requirements.json`.

**F5 (high): archival duplication makes each commit enormous.**
- `source-deltas-94-143.json`: v94 changed 4 files and v95 added 3.
- Yet each commit in `git-24h.json` records 184 to 1208 `productSourceFiles` and 540 to 16,515 `qaFiles`.
- I summed the `qaFiles` of the first ~42 product commits shown (the grep output was truncated): about 194k QA files.
- Roughly half the commits are "Record public…" publication-only commits with 0 product files.
- Whole `warlock-preview-provider-vNN` directory copies stand in for git history.

**F6 (high): trivial bugs cost full freeze-and-publish cycles.**
- GUI123/Native133 failed because the HTML requested `native-preview-renderer.js` but the compiler produced `native-visual-renderer.js` (`:423–426`).
- PUBLIC95 failed on a script-name collision (`:544–548`).
- Freezer count-audit and "nominal count" failures (`:342–345`, `:409`) were each preserved as held evidence and each required a fresh derivative.

**F7 (medium): disclaimers are being used as rationalization.**
- Almost every HANDOFF paragraph ends with "full release gates remain open; installed desktop preserved" and then "Next PUBLICnnn".
- Honest scoping has turned into permission to keep going: the next step is always another publication, never a user outcome.
- The loop's own instruction, "Do not end at a plan or successful component" (`INSTRUCTIONS.md:26`), ends up pushing it deeper into the same lane.

## Measured facts and uncertainties
- **Measured:**
  - The latest production C/Elm change is GUI143 (`HANDOFF.md:769`).
  - CONTROL-048/049 state "No production source changed" (`:814`, `:862`).
  - A user-facing view exists: `SurfaceRenderer.elm:63–72` renders bar buttons (`control-group`) and a popup ("Choose a window", "Applications", "Window actions") with ARIA roles.
- **Unverified: whether existing evidence already satisfies original scenarios.**
  - Native198–201 used real pointer minimize/restore, actual application pixels and keyboard, and never replayed Unknown (`:797–805`). That may count for ELM-ARC-002 `architecture-002` and part of ELM-UX-008.
  - I did not confirm that the pointer stimulus went through a taskbar selection.
  - ELM-ARC-004 `decoder-native-to-elm` may be met by the strict decoders (`SurfaceRenderer.elm:14–35`). Its verification text requires a native or bridge trace, which I did not locate.
- **Not inspected:** `Taskbar.elm` icon/title rendering, and which route the legacy Native130/131 runtime serves to a user.

## Stop / Start / Retain
**Stop:**
- Per-slice vNNN directory copies.
- Per-slice public publication commits.
- New CONTROL-nnn contracts that are not mapped to an original ID.
- Treating "held failed evidence" as a reason to fork a new derivative for typo-class fixes.

**Start:**
- Keeping an evidence ledger keyed by requirement ID.
- Closing requirements one at a time at "native-accepted" scope.
- Developing in place on a branch, letting git hold history.
- Running one representative native journey per slice.
- Producing a reversible, non-main-session install of a usable build.

**Retain:**
- The opacity-0 curtain until a physical reveal gate exists.
- No Unknown replay.
- Strict-close drain before recovery.
- Original deadlines.
- Serial native campaigns.
- Pinning to the core16/plugin19/AQ155 ABI tuple.
- Held failures, for audit only.
- Isolated native serialization.
- User draft and main-desktop protection.

## Operating rules
1. **One product slice in progress at a time.** Each slice declares 1–3 original IDs, their exact scenario names from `requirements.json`, the before/after user-visible behavior, and the evidence scope (component, native or release).
2. **Escalate validation in steps.**
   - Elm/C unit tests and decoders, then the CPU build, then one native journey at the end of the slice.
   - Plus a fixed native regression set of at most 5 runs: normal, known-reload, shared-process-drain, combined-restart-204 and current-error.
   - Formal models (Quint) only when a race is the slice's subject.
3. **Integration.** Edit the current tree in place. No new `vNNN` directories. QA outputs stay outside git, with one hash manifest per slice committed. Publish at most once a day.
4. **Closure.** A requirement moves to `native-accepted` in `implementation-status.json` once its scenario has a native trace, hashes and a reviewer note. Release acceptance stays separate and does not block per-requirement closure (as INDEX.md says).
5. **Reporting and cost.**
   - Each slice report is at most 15 lines: IDs, behavior change, evidence path, tokens and hours spent.
   - Per-slice budget: about 400k tokens or 3 hours. If it is exceeded, stop and report.
   - Two consecutive slices that neither change user-visible behavior nor close an ID trigger an automatic stop and a report to the user.
6. **No invented gates.** Any new internal contract must name the original ID it unblocks, or it does not get written.

## First 3 product slices

**Slice 1 (first task, safe): taskbar group switching without previews.**
- **IDs:** ELM-UX-005 (list each eligible incarnation once and route selection to it), ELM-UX-007 (no preview available → show icon and title, never another incarnation's pixels), ELM-UX-008 (activate or restore through native authority, no scratchpad).
- **Why safe:** this is exactly the behavior that opacity 0 already forces. No reveal authority is needed.
- **Code paths:**
  - `SurfaceRenderer.elm` `view`, the `bar:group:` controls and the popup `picker` mode.
  - `Popup.elm` and `Bar.elm` ports.
  - `assets/bar-adapter.js` and `popup-adapter.js`.
  - The native activation path already exercised by Native198–201.
- **Verification:**
  - Elm decoder/view tests covering duplicate-incarnation refusal and the icon+title fallback.
  - One native journey: two apps, three windows (one minimized). Click the group; the popup lists 2 entries with titles and no preview pixels. Select the minimized window; native authority restores it, and focus plus application pixels are observed.
  - The fixed regression set.
- **Ledger:** close the three IDs at `native-accepted` scope.

**Slice 2: active/attention indicators plus a reversible trial session.**
- **ID:** ELM-UX-009, plus ELM-UX-001 (scope inventory with rollback destination) as the deployment record.
- **Deliverable:** something the user can actually run in a separate session, with rollback documented. The main desktop is never touched.

**Slice 3: Alt-Tab switcher.**
- **IDs:** ELM-UX-011 through ELM-UX-014, reusing the frozen eligible-window order and the stale-identity refusal logic that already exists.
- **After that:** previews (S09 / UX-006), and only after a physical reveal gate is designed as a product slice.

**In parallel, at most 1 hour:** an evidence-mapping pass that tests whether Native198–207 and the decoder suites satisfy the existing scenarios `architecture-002` (ELM-ARC-002), `decoder-native-to-elm` (ELM-ARC-004) and UX-008. Close what is proven, list what is not, and invent nothing.

## Risks
- **Legacy versus controlled route.** Building Slice 1 on the legacy route could mean rework. Mitigation: GUI117 made the view helpers shared, so build Slice 1 on `SurfaceRenderer` code that both routes use.
- **Activation correctness under Unknown.** Keep the existing no-replay rule.
- **Bookkeeping drift.** The ledger must be the only status source; retire the stale `activeSlice` field.

## Falsifiable success metrics (72 hours)
- At least 3 original IDs move to native-accepted in `implementation-status.json`, each with its scenario name and hashes.
- A user can launch a reversible Warlock session and switch windows from a taskbar group.
- Each slice commit has 60 or fewer product files and 300 or fewer QA files, with zero new `vNNN` directories.
- No new CONTROL-nnn contract appears without an original ID.
- Tokens per closed original ID are reported, with a target of 500k or less.
