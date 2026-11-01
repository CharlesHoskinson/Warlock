# UI-007 restore context evidence

This record covers only ELM-UI-007 `restore-pending`, `restore-refused` and
`restore-unknown`.

## Result

The protected run combines the compiled status component with a compiled
`TaskViewReplay` through the production Elm `Desktop.update` path. It passes 78
replay assertions and 16 headless Chromium component checks. The replay checks
the emitted Restore wire against its complete binding, protocol, request,
generation, incarnation, operation and context key; visible status names the
actual `Files` family; pending duplicate dispatch leaves the transaction,
unresolved set and counters unchanged; refusal waits for a current read before
restoring the selected workspace; and Unknown refresh accepts reads without
replaying the mutation. Reopening Task View after the Unknown read returns to
the retained workspace when it still exists. A fresh snapshot with that workspace
removed falls back to All and emits no mutation. Repeated Open Task View preserves
the current workspace. If a different recovered Unknown intent replaces a Refused
transaction while its fresh read is pending, the old origin is discarded and does
not reopen.

The first protected current-source run, `1793492035912683385`, failed the new
Unknown-context assertion because `OpenOverview` reset `overviewWorkspace`.
`OverviewRecovery` now exposes the retained origin only while the current
binding and exact transaction intent still match; `OpenOverview` uses that
validated origin for its workspace and focus target. The source fix is covered
by the passing run. A subsequent interim run, `1793492080773537803`, exposed an
overly strict test assumption that a blocked duplicate must leave every shell
notice unchanged. It emitted no second mutation and left effect identity and
counters unchanged; the final assertion now checks those contract fields.
Terra-3's follow-up source review exposed a repeated-open reset and a competing
Unknown transaction arriving during Refused recovery. Protected REDs
`1793492565410354197` and `1793492619345822651` reproduced each route. The reducer
now makes repeated open a no-op and requires the exact Refused intent to remain
current before returning. The latest replay covers these regressions. All RED
and interim reports remain in their original QA run directories.

## Protected Elm/browser report

- Original stable report: [`report.json`](report.json), run
  `../../runs/1793492175747133805/`, SHA-256
  `39ca15cd42b3749cabee83f0ae5e9c35b28b17ad0a6f69266130d879aa762f89`.
- Latest follow-up report on current GitHub main (`d7fe7f77c`): [`followup-1793493270321072790-report.json`](followup-1793493270321072790-report.json), SHA-256
  `4177ebf0911c0e17d058b4b1c73322b95acb40255aee7b4cb872bca451380c68`.
- Protected launcher: `window-integration-qa/qa_run.py`
- Command: `python3 -B window-integration-qa/qa_run.py -- python3 -B implementation/warlock/qa/check-feedback.py`
- Result: compiled Main, Bar, Popup, FeedbackReplay and TaskViewReplay; typed
  feedback and route replay; headless Chromium. `passed=true`,
  `nativeAcceptance=false`, `fullReleaseAccepted=false`.
- Latest Task View replay: [`followup-1793493270321072790-task-view.json`](followup-1793493270321072790-task-view.json), 78 assertions.
- Latest browser report: [`followup-1793493270321072790-browser-report.json`](followup-1793493270321072790-browser-report.json), 16 checks. Screenshots: [`followup-1793493270321072790-feedback-narrow-refused.png`](followup-1793493270321072790-feedback-narrow-refused.png) and [`followup-1793493270321072790-feedback-wide-unknown.png`](followup-1793493270321072790-feedback-wide-unknown.png).
- Exact compiled input paths and SHA-256 values are recorded in each protected
  report's `inputs` map; implementation and Quint sources are retained in this
  branch alongside the reports.
- The first reproduction and subsequent assertion correction are retained in
  [`failed-runs/`](failed-runs/); they are not overwritten by the final pass.

## Quint model result

The model is a rendered-choice contract for `Surface.recoveryNeeded` and the
renderer live-region category. It does not model the reducer, native delivery,
focus, keyboard, compositor or assistive technology. Wrong-priority and
disabled-live-region mutants are explicit named tests.

- Model: [`action-feedback-priority.qnt`](../../action-feedback-priority.qnt)
- Tests: [`action-feedback-priority_test.qnt`](../../action-feedback-priority_test.qnt)
- Quint: 0.33.0, TypeScript simulator backend.
- Model and test typecheck passed; 9 named tests passed, including both
  sensitivity tests.
- Safety sample: 1,000 traces, max 8 transitions, seed `52012`; no violation.
  Pending, pending without workspace notice, Refused, Unknown, Committed,
  Cancelled and closed-overview witnesses were each reached in more than 690
  traces.
- Quint stdout and source-bound result: [`quint/report.json`](quint/report.json)
  and [`quint/`](quint/).

The additional bounded context model includes current intent/status, retained
workspace presence, focus selection, repeated open and native mutation count.
It has five positive route tests and three explicit faulty-transition tests.
Under the protected QA runner, all eight named tests passed; a 5,000-trace
sample (max 8 steps, seed `52012`) passed four invariants. Existing and vanished
workspace witnesses occurred in 271 and 1,091 traces. This model is a reducer
correspondence aid, not native or physical-focus proof.

- Model and tests: [`overview-recovery-context.qnt`](quint/overview-recovery-context/overview-recovery-context.qnt)
  and [`overview-recovery-context_test.qnt`](quint/overview-recovery-context/overview-recovery-context_test.qnt)
- Captured commands and hashes: [`Quint run README`](quint/overview-recovery-context/README.md)

## Acceptance boundary

This is compiled Elm/reducer and browser component evidence. It is not a native
window-system result or independent original-scenario verdict. Native
compositor rendering, physical keyboard focus, actual assistive-technology
announcement and action behavior, frozen numeric feedback policy, and the
independent original oracle remain open. The original 242 requirements / 417
scenarios and `releaseAccepted=false` are unchanged.

## Model review follow-up

Sol's review found a missing exact-focus-count assertion in the repeated-open model test and correctly noted that the four sampled invariants do not detect two explicit reducer mutants. The model was updated with an exact focus-command postcondition and a focused-only extra-Focus mutant; the mutant test passes. Quint-correspondence review confirmed the claims and hashes. The v2 packet adds observational reachability flags: all eight normal model actions were reached in the 5,000-trace, max-8-step sample, and nine named tests pass. The Unknown-with-workspace witness appears 271 times and the vanished-workspace fallback 1,091 times; the mismatched-return forbidden witness occurs zero times in the non-mutant sample. Named directed tests, not the sampled safety run, detect explicit mutants. An exact rerun using CLI seed argument `52012` reproduced the counts; Quint's printed suggested seed `0x5acec` did not, so both outputs and hashes are retained. See [`the latest follow-up packet`](quint/overview-recovery-context/followup-20261101-v2/README.md); the earlier v1 packet is preserved.
