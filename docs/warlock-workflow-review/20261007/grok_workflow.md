The build loop is the defect. It demands a fresh tree every change, forbids stopping while any gate is open, and treats a full release as the only completion event. The agent followed that text. The captured day produced 90 commits, 45 of them zero-product "Record…" publications, and left `completedRequirementIds` empty. Original EARS stayed `proposed`. The controlled preview curtain is still opacity 0.

## Findings

**S1 — Fatal. The loop makes non-delivery a successful iteration.** `inputs/docs/warlock-build-loop/v1/INSTRUCTIONS.md` lines 21 and 24 require a fresh derivative, and another fresh derivative on failure. `inputs/docs/elm-roadmap/BUILD-LOOP.md` line 27 repeats it. `inputs/AGENTS.md` line 7 makes it standing policy. Instruction line 26 says not to end on a successful component while other work remains. Line 40 completes the goal only at a full GUI release. `loop-state.json` `advanceRule` forbids completing a requirement without accepted evidence, and `nextWork` names internal W01/W07 tickets. The agent met every sentence by never closing a requirement and always copying a tree.

**S2 — Fatal. Check counts and copies became the progress metric.** `inputs/git-24h.json` has 90 commits from `8b9c5938` (2026-10-06 15:49 −06) through head `261addb0` (2026-10-07 15:06 −06). Its warning says path counts are repeated archival copies, not features. The first commit lists 519 product files and 13,062 QA files. `1c052f99` ("Drain original native duties") lists 305 product files and 1,703 QA files under `warlock-preview-provider-v139`. In `source-deltas-94-143.json`, v94's real change is reordering one native query and adding `nextReadiness`. v97 adds `control-reservations-test.cpp` and `control-reservations-test-v2.cpp`: the same 63-line fixture, overflow pad 3850 versus 3980. `component-report-gui143-shared-process-drain.json` sets `passed: true` while `nativeAcceptance`, `physicalConcealmentQualified`, `physicalRevealQualified`, `hardwarePresentationQualified`, `reloadRecoveryQualified`, and `fullReleaseAccepted` are false, and it splits one drain across native v187–v194. `component-report-combined-restart-204-207.json` sets `passed: true`, says "No production source changed," and includes `native202` and `native203` with `passed: false`. The last four commits (`b341185b`, `5066a649`, `45242221`, `261addb0`) have `productSourceFiles: 0`.

**S3 — Fatal. The integration ledger was abandoned.** `implementation-status.json` has `completedRequirementIds: []` while `requirementsInProgress` still lists `ELM-GNO-002` and `ELM-UI-001`. `loop-state.json` `observedUTC` is 2026-10-05 and `currentSlice` is `elm-recovery-delivery-general-reviewed-v656`. The day's commits are preview-provider publications. `requirements.json` opens with "proposed; implementation acceptance pending." Inspected objects `ELM-ARC-016`, `ELM-ARC-018`, `ELM-ARC-019`, `ELM-GNO-002`, `ELM-GNO-008`, `ELM-UI-001`, and `ELM-DEL-025` are still `"status": "proposed"`. An empty completed list does not prove zero original scenarios have evidence. It proves this lane stopped recording them. `sceneCoreV8` has `inactiveOwnMonitorPredicateRepaired: true`, `predicateAcceptanceOnly: true`, and `productSceneAcceptance: false`. That is partial `ELM-GNO-002`: a predicate repair, missing native acceptance, stranded in a stale file.

**S4 — High. A second requirements system was written and qualified.** `OUTGOING-CONTROL-CONTRACT.md` adds CONTROL-001–006. `NATIVE-ADMISSION-CONTROLS.md` adds CONTROL-007–008, a five-slot quota, and `5 * 8 + 2 * (2 * subjectLimit) + 1`. The original sentence is `ELM-ARC-016` / `architecture-016` (control capacity reserved independently of preview). That ID was not updated. The contract says the primitive "remains inactive in WebKit" and that the gap is not permission to close the release. That disclaimer became permission to open the next internal EARS. `FRP-ELM-WORKPLAN.md` records that five reviewers did not compile, test, or activate the desktop, then installs W01–W12 as the order of work. `loop-state.json` `nextWork` follows W01/W07, not `ELM-ARC-018`.

**S5 — High. User-visible behavior stayed fenced off.** `controlled-preview-host.h` `controlled_curtain` sets opacity `0.0` and the comment forbids raising it on decoder/RAF acceptance. `preview_client.hpp` initializes `previewEligible` to false and rejects a true probe. `shared-host.c` logs `previewEligible=0`. `inputs/docs/HANDOFF.md` (2026-10-03) still asks for click-to-focus with a draft open, minimize/restore, and taskbar previews while minimized. `ELM-DEL-025` is the journey that demonstrates those flows. It completes the goal. It does not have to block one scenario.

**S6 — Medium. The handoff is a second product.** `inputs/docs/warlock-preview/v93/HANDOFF.md` is an append-only publication log (GUI92 through GUI113 in the portion read) measured in blob counts, check counts, and PUBLIC hashes. The loop tells the next iteration to read it, so context is spent replaying disclaimers.

## Facts and uncertainties

Measured: 90 commits; 45 record commits; provider copies v94–v143 in the delta packet; curtain opacity 0; `previewEligible` false; `nativeAcceptance` false on the GUI143 and combined reports; integration ledger frozen at v656 on 2026-10-05; inspected original statuses are `proposed`.

Uncertain: 7.9 million tokens and 22.5 hours. `INDEX.md` calls that a cumulative host-goal snapshot and says no 24-hour token telemetry exists. No independent counter is in the packet. This day's tokens are unavailable. I did not recount all 242 statuses or rerun builds. Do not close `ELM-GNO-002` from the Oct 5 JSON; `sceneCoreV8` is partial evidence on an older slice until the predicate is shown on the current core16/plugin19 pair.

## Replacement

One writable tree: `implementation/warlock-preview-provider-v143`. Older `implementation/*` trees stay frozen and unread while implementing. Git plus one failed report retains a failure. A copied tree is not retention.

One ledger row per original scenario: id, scenario, state (`open`, `partial`, `closed`, `failed`, `blocked`), evidence path, commit, missing observation. Stop appending `v93/HANDOFF.md`. Do not rewrite frozen packets to dedupe them.

Each iteration: read that row and the files it names; patch the tip; run only the verification sentence's oracle, through the existing protected launcher when the sentence requires native; write one report; commit the patch and the row. Subject: `<ID> <scenario>: <state>`.

### Stop rules

1. No new `implementation/*-vN` directory.
2. The target is an ID in `requirements.json`. CONTROL-* and W* are not targets. A child scenario quotes a parent ID and a sentence already in that requirement.
3. Two iterations with no ledger transition: stop the goal.
4. WIP is one scenario. Do not resume v656.
5. A zero-product-file commit is not progress and is not required.
6. The report result is the scenario state. `passed: true` together with `nativeAcceptance: false` on a scenario whose verification requires native paint is a failed report.
7. If opacity is still 0, `previewEligible` is still false, or the focus precondition is still failed, the next iteration continues that scenario or marks it failed.
8. Keep ABI pairing, the native lock, `qa_run.py`, original deadlines, unknown-versus-confirmed settlement, draft and desktop protections, and one Elm policy. Do not extend a deadline or reset a grant to pass.
9. `ELM-DEL-025` and the S01–S16 gate complete the goal. A scenario closes when its own verification sentence is met.
10. No new review panel and no new workplan until three original scenarios are `closed` or `failed`.
11. Status is at most 15 lines: IDs, observed behavior, commit, oracle path and hash, what is open, next file. Check counts stay in the report file. Tokens are "unavailable" until a counter exists.

### First three slices

1. `ELM-GNO-002` / `gnome-layering-002` and `minimized-sticky`. Port only the repaired eligibility predicate if it is absent from the v143/core16/plugin19 pair. Oracle: one minimized window, including explicit sticky, is absent from paint and hit lists. Keep the fullscreen-permission negative inside this slice. Do not open `ELM-GNO-003`. One native campaign, one in-place retry.
2. `ELM-ARC-018` / `architecture-018`. The combined report already failed `native202` (27 checks) and `native203` (91 checks) on focus preconditions and left `popupDismissalFocusRestorationQualified` false. Fix that precondition in the current host. Oracle: one click on a visible region with a draft modal; native family policy sets focus and hit order. One retry, then `failed` if the precondition is still environmental.
3. After 1 and 2 change the ledger: `ELM-ARC-019` / `architecture-019` and the noninteractive half of `ELM-GNO-008` / `gnome-layering-008`. One minimized window, one retained frame, no JSON pixels, source receives no input. The curtain stays at 0 until a native presentation receipt exists (`ELM-ARC-020`). If that path is missing, stop and record the missing observation. Do not raise opacity from decoder or RAF success. Do not add CONTROL-009.

`ELM-UI-001` / `focus-successor` shares the minimize path. It waits until these three move.

## Risks and metrics

In-place edits can clobber a frozen packet if more than the tip is writable. State that only v143 is writable. Closing a scenario on a CPU trace repeats the inflation: where the verification sentence says native paint, Quint is `partial`. Slice 1 can honestly fail because the predicate lives on another ABI. A `failed` row is a successful process run.

Falsifiers before any further infrastructure: zero new version directories; at least one `requirements.json` scenario moves to `closed` or `failed` with evidence matching its then-clause; that commit is the edited files, and a provider-tree copy fails the session; the status names the scenario and does not lead with a check count; opacity and `previewEligible` change only in a commit naming `ELM-ARC-019` or `ELM-GNO-008`, and that report includes the native receipt or an explicit stop.

No new skill or plugin. The obstacle is the loop text. Another reviewer panel is how W01–W12 replaced the original list.
