# Why window action status remains accessible

Warlock keeps one Elm policy authority for native window actions. `Effects` and
`Shell` correlate an operation with its Pending, Committed, Refused, Cancelled
or Unknown result. `Surface` projects that state into the taskbar and open
views. The projection has existing context rules: when Task View is open and
`recoveryNeeded` is true, its status includes the current window operation and
outcome. A current workspace navigation notice can be prepended, so the window
result and the retained view guidance can both remain visible. Other open
surfaces keep their own existing notice precedence.

The shared `SurfaceRenderer` keeps the visible bar and popup status mirrors
passive (`aria-live="off"`). `OutcomeAnnouncements` is the single speech policy;
its current-session Restore candidate uses the exact binding, typed intent,
protocol, issued-request provenance and changed Pending/Refused/Unknown status.
`OutputController` selects the announcement recipient, and `Announcement` checks
publication, lease and sequence. Actual AT speech and delivery of these new
Restore cases through the full scoped owner remain unobserved. Disconnected and
older-frontend recovery need separate correlation work.

The bar uses one stable scrollport DOM node. Changed accepted feedback advances
an opaque UInt64 epoch and requests a local viewport reset, revealing the new
prefix. Identical feedback retains scroll and focus; invalid or stale frames do
not allocate a reset. Counter exhaustion withdraws the target without reuse.
A static injective escape keeps control DOM IDs out of the status namespace;
this prevents aliasing between distinct raw IDs, not every possible same-ID
incarnation or multi-mount lifetime.

Current protected evidence has 298 status checks, 480 Restore checks across 32
seeded full-width allocator cases, ten directed model cases, and 255 compiled
browser checks. The browser measures the actual inner clip, reaches each wrapped
recovery line by keyboard scrolling, and checks same-node focus and immediately
captured scroll retention at 621px/200% text size. Unqualified launch remains
disabled. See the [component observation](../../../implementation/warlock/qa/evidence/ui007-status-scroll-20261101/component-observation.json).

The earlier projection campaign established status text, accessible names,
narrow layout and recovery context. Its generic polite-bar assumption is
historical; it does not qualify the current single-announcer policy. A separate compiled
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

The earlier feedback Quint model stores the rendered choice and a generic
live-region category, including wrong-priority and disabled-live-region mutants.
That generic speech-category assumption belongs to the earlier candidate; its
source and evidence remain retained and are not claimed as current announcer
correspondence. The current `status-scroll.qnt` models epoch/task retirement and
sampled reachability, not native focus, speech, deadlines or UI acceptance. A second bounded context model
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
