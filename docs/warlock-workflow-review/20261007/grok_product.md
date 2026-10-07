The next slice must not be native preview-effect uncertainty. That is another cleanup primitive. The shell the user clicks did not change, the preview they would look at is forced invisible, and a real focus failure was already found and set aside.

## Findings

**1. Fatal: the queued next task is CONTROL-050 under another name.** `docs/warlock-preview/v93/HANDOFF.md` lines 869–875 close CONTROL-049 and name "actual native preview-effect uncertainty" as the next implementation slice. `openspec/changes/warlock-preview-actor-retirement/tasks.md` lines 552–554 and 566–567 still have open items for uncertain renderer recovery and "all asynchronous delivery-error/process schedules." `NATIVE-ADMISSION-CONTROLS.md` lines 1043–1045 leave the same item open. This continues CONTROL-001 through CONTROL-049, a contract series that does not exist in `docs/elm-roadmap/requirements.json`. Each earlier purpose in `source-deltas-94-143.json` says the primitive comes before WebKit activation, physical reveal, or release. Fifty provider versions later (v94–v143), those user-visible gates are still open. Another uncertainty schedule will not open them.

**2. Fatal: a day of commits delivered no installed behavior.** `controlled-preview-host.h` lines 141–145 set the controlled popup to opacity 0 and state that nothing on this route raises it. `shared-host.c` lines 868 and 875 print `previewEligible=0` on client start and completion. `preview_client.hpp` line 226 refuses a probe unless `previewEligible` is false. `component-report-gui143-shared-process-drain.json` lines 38–49 mark physical concealment, physical reveal, hardware presentation, workload, RSS, and native acceptance false. The handoff repeats that the installed desktop, drafts, and foreign edits were preserved. I did not watch the live session. The code and reports are enough: a person at this machine cannot see a thumbnail or get a new window action from this work.

**3. Severe: the last two "successes" did not change the product.** `component-report-window-restart-198-201.json` and `component-report-combined-restart-204-207.json` record real minimize and restore, lost receipts, no replay, pixels, and keyboard inside a private GUI143/core16/plugin19/AQ155 session. Both handoff passages (lines 813 and 861) say no production C or Elm source changed. Native202 and Native203 failed focus preconditions after popup dismissal. Successors re-established focus with compositor and pointer input and left popup-dismissal focus restoration unqualified (handoff lines 854–859; tasks.md lines 604–606). That is a user-visible hole on a path that already moves windows. Modeling preview-effect Unknown does not fix it.

**4. Severe: original user scenarios were frozen while internal contracts grew.** `source-deltas-94-143.json` has 50 version purposes and no change to `Taskbar.elm`, `TaskbarShell.elm`, `Shell.elm`, `Menu.elm`, or `Bar.elm`. `git-24h.json` lists 90 commit titles from 2026-10-06 15:49 through the packet end. About half are "Record public … qualification." The first commit in that window touches 519 product paths and 13,062 QA paths. The Elm decision table already exists and was not integrated further:

- `Taskbar.elm` lines 25–36 implement Launch, Restore, Minimize, Activate, and Picker.
- `TaskbarShell.elm` line 83 calls `Taskbar.primary False`, so a pinned app with zero windows cannot launch. That is `ELM-UI-004` scenario `taskbar-zero` (`requirements.json` lines 5093–5102).
- `TaskbarShell.elm` lines 76–77 drop `Primary` when `valid` is false, and `Shell.elm` lines 60 and 66–67 set `Reconciling` and treat pending work as unavailable. The click disappears. `ELM-UI-007` (`requirements.json` lines 5243–5244) requires correlated pending, refused, and unknown feedback, not a silent discard.

The 2026-10-05 plan already ranked this above more preview machinery. `FRP-ELM-WORKPLAN.md` lines 29–54 put W07 press identity and focus, then W01 batch liveness, ahead of further W03 preview work. `loop-state.json` lines 34–35 still say that, with `observedUTC` 2026-10-05 and `activeSlice` `elm-recovery-delivery-general-reviewed-v656`. The 24-hour log did not follow it.

**5. High: the empty completion list is stale bookkeeping, and it is also why nothing ever finishes.** `implementation-status.json` line 35 has `completedRequirementIds: []`. That file's slice is v656, two days before GUI143. It is not a ledger of this preview lane, so it does not prove zero original requirements have evidence. It also shows the process never closes a scenario. GUI141 and GUI143 are real safety repairs for a known reload and a known shared-process drain, and their own reports still say `nativeAcceptance: false`. Those repairs must stay evidence. They must not be promoted into `ELM-REN-013` or `ELM-REN-003`, which require capture retirement and a drawable retained frame (`requirements.json` lines 3256–3267 and 3496–3507). `ELM-UI-004` is not done because `primary` matches a table on paper.

The loop instruction in `docs/warlock-build-loop/v1/INSTRUCTIONS.md` line 7 defines completion as the original gates for one coherent release: 242 requirements and 417 scenarios, plus right-click. The agent answered with versioned cleanup prototypes and a new CONTROL number. Path counts and check counts are not that release. I did not find an independent token counter in the packet. `INDEX.md` line 9 says about 7.9 million tokens and 22.5 hours cumulative, and says 24-hour token telemetry was not established. Treat that as an unverified parent snapshot.

## Stop, start, retain

Stop opening CONTROL-050, a v144 tree, another publication-only commit, and any slice whose purpose says "before reveal" or "all async schedules."

Start from the shell that already decides window actions. One scenario, one sacrificial session, the current v143 sources.

Retain opacity 0 on every unaccepted route, the GUI128 curtain detector, no automatic Unknown replay, original deadlines, core16/plugin19 until a scenario needs a bump, failed Native202/203 oracles, and the GUI141/143 drain evidence. Do not rewrite those reports to reduce duplication. Point at them.

## Operating rules

One work-in-progress item: one original scenario ID. A new internal primitive is allowed only when that scenario fails for lack of it, and the scenario ID is in the commit title.

Two consecutive slices that do not change what a person can see or do end the lane. "Before WebKit" after v94–v143 is that stop.

Elm replay covers the decision table. A native campaign runs only for the one scenario that claims pixels or focus. No second publication commit that only copies QA.

Report one paragraph: what the user could do before, what they can do after, the scenario ID, and the missing observation. Check counts go in an appendix.

Close scenarios in a ledger separate from the release. `completedRequirementIds: []` must not veto a scenario that has its named evidence, and a component pass must not fill that list.

## First three slices

**Slice A, do this first.** `ELM-UI-004` scenarios `taskbar-inactive`, `taskbar-minimized`, `taskbar-active`, and `taskbar-refusal`. Drive them through `Taskbar.primary` and `TaskbarShell.update` on the window-command path Native198–201 already ran. Pass `pinned` from real catalog state so `taskbar-zero` is not hard-disabled. If `valid` is false, keep the click identity and show `Shell.status` (`Shell.elm` lines 68–76: "Applying window change…", refused, or unconfirmed). Do not drop it. Verification: three pointer activations on one sacrificial window, pixels and focus before and after, one injected refusal that leaves the window put and shows the notice. Fail the slice if opacity, `previewEligible`, or a new CONTROL file changes.

**Slice B, the bug already paid for.** `ELM-UI-001` `focus-unfocused`, plus the Native202/203 popup-dismissal focus failure. After the preview popup closes, opener focus returns with no extra window effect and no manual compositor poke. The existing keyboard-recipient oracle passes unchanged. Do not weaken it and do not explain the miss with a preview-uncertainty model.

**Slice C, only after A and B, and only one frame.** `ELM-REN-003` source-stop retained frame, shown as a noninteractive object per `ELM-GNO-008` (`requirements.json` lines 1776–1777). One opted-in fixture client may set `previewEligible` true. Reveal that one accepted frame at opacity 1 in the QA host with the curtain detector still armed, then retire the lease. If that frame cannot be shown without a new uncertainty type, record the single missing observation and return to shell scenarios. Do not schedule every async fault first. The red19200 capture behind opacity 0 is not this slice.

W07 (keyed rows, press-time identity, Enter and Space) is the input half of slice A, as `FRP-ELM-WORKPLAN.md` lines 30–36 already specified. It is not a new research cycle.

## Risks and one-day metrics

Slice A may show that `Taskbar.Apply` never reaches the broker. That is the result. Do not detour into reservations or drain. Slice B may be an input-region bug. It is still smaller than a new CONTROL. Slice C can expose pixels the GUI128 detector was built to catch. Keep the detector. Do not make opacity 1 the default route.

Falsifiers for the next day: one sacrificial window minimizes, restores, and activates from the taskbar decision, and the user can see that. Native202/203 pass without a manual refocus and without a new CONTROL id. No new `warlock-preview-provider-vN` directory. No commit whose diff is only QA or "Record public." One original scenario ID is marked scenario-satisfied, or the ledger names the exact missing observation. The installed desktop stays unchanged. `nativeAcceptance: false` on a drain report does not count as the close.
