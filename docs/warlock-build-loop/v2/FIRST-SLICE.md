# First implementation result: visible window-action feedback

**ELM-UI-007** — `restore-pending`, `restore-refused`, `restore-unknown`.

Before: taskbar status occupied a visually clipped one-pixel element, and generic recovery text replaced the Pending/Unknown distinction. After: the current operation and window receive visible, distinct applying/refused/not-confirmed messages. The message stays in reserved taskbar space while controls scroll independently, so it does not cover the controls. Existing read-only recovery remains available; a status update issues no action.

Production changes are confined to `implementation/warlock/src/Surface.elm`, `src/SurfaceRenderer.elm` and `assets/shell.css`, plus the three regenerated Main/Bar/Popup artifacts. Native code, effect reducers, launch authority and controller dispatch are byte-identical to held GUI143. Long target labels are bounded, the outcome appears first, full text remains in the accessible name/title, and forced-colors mode uses system colors.

Validation passed through the protected launcher: four focused Elm compilations (Main, Bar, Popup, the typed-state fixture), actual policy projection, and sixteen checks on the compiled browser view. The checks reproduced the old stylesheet's hidden status, demonstrated each new message, tested 320px and wide layouts, revealed the last overflow control by keyboard focus, preserved a keyed focused control during status updates, emitted one keyboard recovery-control action, cancelled a stale held Space press, and retained Unknown without automatic action. Browser exited normally.

The first fixture compile failed because its flags type was unspecified. That report remains in ignored `qa/runs/1791409394527867267/report.json`; the fixture was fixed in place. There was no new product tree, model campaign or full 119-command rebuild.

Evidence: [compact manifest](../../../implementation/warlock/qa/evidence/window-feedback/manifest.json), [complete component report](../../../implementation/warlock/qa/evidence/window-feedback/report.json), [browser observations](../../../implementation/warlock/qa/evidence/window-feedback/browser-report.json), [wide capture](../../../implementation/warlock/qa/evidence/window-feedback/feedback-wide-unknown.png), [narrow capture](../../../implementation/warlock/qa/evidence/window-feedback/feedback-narrow-refused.png).

**Implemented and component-verified; not original native/AT accepted.** These three scenario rows remain partial. Applicable native keyboard/pixel and assistive-technology observations on the owning tuple remain required, as do UI-007's pin/snap/jump-list/settings scenarios. The main desktop is unchanged. Next action: run the focused feedback journey against the compiled candidate package in the protected private native session, then continue the taskbar/focus journey.

The replacement full-scope host goal was created after the nine-reviewer AAR and v2 workflow installation. Its actual state is available through the goal tool; repository documents alone do not arm continuation.
