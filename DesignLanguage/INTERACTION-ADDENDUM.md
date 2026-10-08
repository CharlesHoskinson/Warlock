# Stable targets and observed toggles

The 8 October documentation audit adds these implementation clarifications to the existing DL-005/007/013/014/018/019 contracts. The frozen thirty-contract consensus and original GUI requirements are unchanged. These statements are required design behavior, not delivered-feature claims.

- **WARLOCK-DL-TARGET-001 — event-driven:** WHEN asynchronous preview or status content changes while a control is pressed, the shell SHALL preserve the control's allocated target bounds through release and SHALL refuse any release whose admitted target identity no longer matches the press.
- **WARLOCK-DL-TARGET-002 — ubiquitous:** The picker SHALL reserve the same thumbnail slot and bounded status/detail geometry in Loading, Live, Historical and Unavailable states.
- **WARLOCK-DL-TOGGLE-001 — state-driven:** WHILE a window menu exposes Always on top, the shell SHALL use a stable label and checked state derived only from the current correlated native pin observation, with Pending and Unknown reported separately.
- **WARLOCK-DL-TOGGLE-002 — ubiquitous:** The shell SHALL distinguish taskbar application Pin/Unpin vocabulary from the window Always on top control.

The [OpenSpec clarification](../openspec/changes/warlock-stable-target-guidance/specs/warlock-stable-targets/spec.md) preserves positive, stale-identity, pending and unknown outcomes. Product implementation and native/accessibility observations remain open. The [current workplan](WORKPLAN.md) carries these findings.
