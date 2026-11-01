# Why window action status remains accessible

Warlock keeps one Elm policy authority for native window actions. `Effects` and
`Shell` correlate an operation with its Pending, Committed, Refused, Cancelled
or Unknown result. `Surface` projects that state into the taskbar and open
views. The projection has existing context rules: when Task View is open and
`recoveryNeeded` is true, its status includes the current window operation and
outcome. A current workspace navigation notice can be prepended, so the window
result and the retained view guidance can both remain visible. Other open
surfaces keep their own existing notice precedence.

The shared `SurfaceRenderer` uses a `role="status"` region for this text. It now
sets `aria-live="polite"` for nonempty, non-Ready status and keeps empty/Ready
states hidden. This change improves the accessibility signal in the compiled
component without changing Shell/Effects authority, outcome priority, recovery
behavior, or dispatch policy.

The protected compiled Elm and headless Chromium run exercises Restore
Pending, Refused and Unknown in two ways. The browser fixture checks the
rendered status text, accessible name, polite live-region category, narrow
layout, focus stability for a stable taskbar control, status publications
without a new UI action, and the observation-control event. A separate compiled
`TaskViewReplay` drives the real Elm `Desktop.update` route through
`OverviewChoose`, its emitted Restore intent, correlated Pending/Refused/Unknown
receipts, stale input, duplicate suppression and read-only Unknown refresh.
The route exposed several real defects. After an Unknown receipt and fresh
read, manually reopening Task View discarded the selected workspace. Repeating
the Open Task View action discarded it again. A separate interleaving let a
different recovered Unknown transaction replace a Refused restore while its
fresh read was pending, but the old origin could still reopen. Recovery now
requires the current binding and complete intent to match. A Refused return
also requires that same intent to remain the current Refused transaction until
the fresh read arrives. Reopening with a vanished workspace falls back to All,
and activating Open Task View while it is already open is an idempotent no-op.
These transitions do not reissue Restore.

The feedback Quint model stores the rendered choice and live-region category as
state, checks them against the UI-007 projection policy, and includes explicit
wrong-priority and disabled-live-region mutants. A second bounded context model
tracks origin/current intent, status, workspace presence, focus target and
mutation count. Its tests include repeated-open, vanished-workspace and
mismatched-refusal mutants. Both models abstract the native runtime; neither
proves dispatch, physical keyboard focus, compositor pixels or assistive
technology behavior. The separate `TaskViewReplay` checks actual Elm reducer
transitions through a deterministic fixture, not a live native window system.

These results are compiled Elm and browser component evidence. Native
compositor presentation, physical keyboard focus, actual assistive-technology
output/actions, the frozen numeric feedback policy, and independent
original-scenario review remain open.

## Scope

The participant slice covers only ELM-UI-007 `restore-pending`,
`restore-refused` and `restore-unknown`. Pin, snap, jump-list and settings
outcomes, committed/cancelled journeys, real reducer and recovery paths, other
focus contexts, whole ELM-UI-007 and release acceptance remain separate
obligations.

## Evidence

- Status projection: [`Surface.elm`](../../../implementation/warlock/src/Surface.elm)
- Taskbar renderer: [`SurfaceRenderer.elm`](../../../implementation/warlock/src/SurfaceRenderer.elm)
- Protected check: [`check-feedback.py`](../../../implementation/warlock/qa/check-feedback.py)
- Correspondence model: [`action-feedback-priority.qnt`](../../../implementation/warlock/qa/action-feedback-priority.qnt)
- Recovery-context model: [`overview-recovery-context.qnt`](../../../implementation/warlock/qa/overview-recovery-context.qnt)
- Recovery-context tests: [`overview-recovery-context_test.qnt`](../../../implementation/warlock/qa/overview-recovery-context_test.qnt)
- Current protected evidence index and exact report/source tuple: [`README.md`](../../../implementation/warlock/qa/evidence/ui007-restore-context-20261101/README.md)
- Retained Unknown-context implementation: [`OverviewRecovery.elm`](../../../implementation/warlock/src/OverviewRecovery.elm)
- Actual route replay: [`TaskViewReplay.elm`](../../../implementation/warlock/qa/TaskViewReplay.elm)
- Original requirement and scenario oracles: [`requirements.json`](../../elm-roadmap/requirements.json)
