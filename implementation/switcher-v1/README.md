# Staged Alt+Tab release ordering correction

This candidate is not deployed. It addresses the observed sequence in which Alt
is released while Python is still gathering candidates: the old release helper
sees a closed shell and returns, then the late candidate payload opens an
exclusive overlay for up to 30 seconds.

`switcher-bindings.lua` replaces only the final Alt+Tab binding block in snap.lua.
Synchronous compositor callbacks allocate a generation and unique ordinal before
calling asynchronous `hl.exec_cmd`. Every Tab repeat carries its direction; Alt
release carries the chord's final ordinal. The selected compositor signature
binds every step/release to the shell. The Lua global serial survives ordinary
configuration reload and sends a new generation barrier on reload.

`hypr-window-menu switcher-step SESSION GENERATION ORDINAL DIRECTION` first asks
QML for a builder token; only the winning builder runs candidate queries. The
QML `SwitcherController` uses the actual `SwitcherState.js` reducer. Release may
arrive before any step or before candidates: it latches the final ordinal and
waits for candidates and all earlier steps. The shell never opens the switcher
after a release has been latched. Reordered or duplicate steps do not launch
duplicate builders. Explicit row selection survives a missing delayed step.

Cancellation, new generations, reload barriers and terminal-generation
tombstones reject stale readiness/release and revoke unclaimed restores.
Pending generation work expires after three seconds without opening an overlay;
an open chooser expires after 30 seconds. These are new staged switcher budgets,
not changes to the archived native acceptance campaigns.

The root shell launches one tracked restore `Process`, whose helper must atomically
claim the current shell epoch/generation/token once. The returned candidate must
carry address, PID and stableId, which reach the existing native windowctl guard.
Local QML Alt release does not send a second unlabelled commit. Arrow selection,
mouse selection and Enter share the same state. Other menus retain their existing
action paths and cancel pending switcher work when they supersede it.

## Deployment prerequisites and open limits

- Deploy the staged helper, full controls shell, controller, reducer and new Lua
  bindings together. Legacy `switcher`/`switcher-commit` commands explicitly refuse;
  an unlabelled switcher payload cannot open the staged shell. Legacy titlebar,
  layouts, assist and snapbar routes remain present.
- A supervised persistent controls shell must already be running before the
  new bindings are enabled. This candidate fails closed on unavailable IPC and
  intentionally supplies no uncoordinated startup fallback. A real startup and
  restart lifecycle still needs design and acceptance.
- A Lua reload barrier is delivered asynchronously. Old work may reach its
  native effect before the shell receives that barrier. Revocation is established
  after receipt, not atomically at compositor reload.
- One-use claiming and the native restore run in different processes. Cancellation
  or a new chord after claiming cannot be proved atomic with the later native
  focus operation. Closing that gap requires a compositor-owned generation guard
  or equivalent acknowledgement at the native operation boundary.
- The shell's epoch rejects stale builder readiness/claims across shell restarts,
  but Lua step/release messages do not yet bind to a pre-established shell epoch.
  Full restart recovery and delayed pre-restart input still require native tests.
- The complete controls shell requires Wayland `PanelWindow`; it cannot load
  under the offscreen platform. Actual source reducer/controller tests passed,
  but full overlay keyboard/mouse routing and coexistence with other menus remain
  unaccepted. Root owns any private native GUI run.

## Verification

The protected `qa_run.py` launcher ran 28 reducer scenarios (including all six
step/step/release orderings), eight Python protocol/identity checks, eight Lua
generation/reload checks, and ten actual offscreen Quickshell controller checks.
The tests exercise the production reducer, not a separate model. The controller
probe caught an initial inherited-property conflict, which was corrected before
passing. `PROOF.json` preserves hashes, pass evidence and failed probe attempts.
No native window effect or deployment has been accepted.
