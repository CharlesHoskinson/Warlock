# Windows 11 window behavior audit for this Omarchy desktop

Checked against Microsoft's [title bar guidance](https://learn.microsoft.com/en-us/windows/apps/design/basics/titlebar-design), [Snap guide](https://support.microsoft.com/en-us/windows/experience/snap-your-windows), [keyboard shortcuts](https://support.microsoft.com/en-us/windows/keyboard-shortcuts-in-windows-dcc61a57-8ff0-cffe-9796-cb9706c75eec), [taskbar guide](https://support.microsoft.com/en-us/windows/experience/personalization/customize-the-taskbar-in-windows), [Always On Top](https://learn.microsoft.com/en-us/windows/powertoys/always-on-top), and [motion guidance](https://learn.microsoft.com/en-us/windows/apps/design/motion/).

| Behavior | Current implementation | Audit result |
| --- | --- | --- |
| Click a floating window to focus and raise it | Hyprland click focus and floating windows | Works for ordinary workspaces; the old scratchpad-based minimize flow caused the reported obstruction. New minimizations use a separate hidden workspace. |
| Minimize and restore a specific window | Title-bar button, taskbar icon, `SUPER+DOWN` | Implemented through `hypr-windowctl` and `special:win-minimized`; prior workspace and pin state are restored. Existing scratchpad entries stay untouched. |
| Maximize and restore with prior geometry | Title-bar button/double-click, `SUPER+UP`/`SUPER+DOWN` | Implemented through Hyprland maximized mode. Tested with a disposable window, including minimize/restore while maximized. |
| Close the title-bar's own window | Patched hyprbars address substitution | Implemented; async actions carry the owning address rather than using later active focus. |
| Move and resize by title bar or border | Hyprbars and Hyprland border resize | Implemented; title-bar drag reports release directly. Alt/Super drag moves and resizes but does not edge snap because Hyprland Lua exposes no release callback for those paths. |
| Edge/corner drag snapping | `snap.lua` title-bar hook, seven zones | Implemented; heuristic snap while a mouse button remains held was removed. |
| Keyboard snapping and layout chooser | `SUPER+ARROWS`, `SUPER+Z` chooser | Implemented for halves, quarters, maximize. No hover flyout attached to Maximize. |
| Snap Assist suggestions and Snap Groups | None | Not implemented. Requires a separate compositor-aware chooser and group persistence in the shell. |
| Always-on-top pin | Title-bar pin, `SUPER+P`, `SUPER+CTRL+T` | Implemented. Pin state is targeted by address; pinned windows are raised again after focus changes. This is distinct from pinning an app launcher to the taskbar. |
| Active-window highlight | Border, inactive dim/shadow, taskbar underline | Implemented. |
| Smooth transitions | Hyprland spring move/resize, title-bar and preview fade | Implemented for move/resize/pin indicator. Accessibility toggle for reduced motion is not yet connected. |
| Running app taskbar icons | `hoskinson.windows` bar widget | Implemented on the left, one icon per window, including minimized windows. |
| Hover preview | Per-window compositor thumbnail plus title | Implemented. Hyprland's toplevel export captures the current window buffer by stable ID, including the tested minimized Brave window, without changing focus. |
| Pinned app launchers, app grouping, Jump Lists | None | Not implemented; these are separate taskbar features. |
| Win+M/Win+Shift+M/Win+Home | `hypr-windowctl` commands | Implemented. `SUPER+Home` replaces Omarchy's prior Restore window width binding. |
| Right-click title-bar system menu | None | Not implemented. |
| Rounded floating and square snapped corners | Theme-controlled global rounding | Partial; per-state corner changes are not implemented. |

## Verification

- Quint model: `window.qnt` and `window_test.qnt`; six scenario tests and 2,000 seeded random traces pass.
- Lua implementation harnesses: `fuzz_snap.lua` passes 6,000 randomized geometry cases and drag regressions; `test_pin.lua` passes focus/pin regressions and 4,000 randomized operations.
- Live Hyprland: `hyprctl reload` and `hyprctl configerrors` clean; the patched hyprbars plugin loaded; minimize/restore/maximize/pin were exercised on a disposable window.

Quint checks the specified state machine and the Lua harness runs the actual Lua files behind mocks. Neither proves the pixels or every application-specific Wayland behavior, so manual drag and hover checks still matter.

## Full Windows 11 window-management parity expansion

The first table scoped the original window-control implementation. The user
expanded the target to the complete Windows 11 window-management workflow on
2026-09-30. The checklist below is the remaining acceptance scope. A row is
not complete merely because a command exists: mouse, keyboard, taskbar, and
workspace paths must agree on the resulting window state.

Sources: Microsoft's [Snap guide](https://support.microsoft.com/en-us/windows/experience/snap-your-windows),
[taskbar guide](https://support.microsoft.com/en-us/windows/experience/personalization/customize-the-taskbar-in-windows),
[keyboard shortcuts](https://support.microsoft.com/en-us/windows/keyboard-shortcuts-in-windows-dcc61a57-8ff0-cffe-9796-cb9706c75eec),
[multitasking settings](https://support.microsoft.com/en-us/accessibility/windows/make-it-easier-to-focus-on-tasks),
and [titlebar guidance](https://learn.microsoft.com/en-us/windows/apps/design/basics/titlebar-design).

| Area | Acceptance requirement | Status at expansion |
| --- | --- | --- |
| Window identity and focus | Click any visible floating window, including one behind another app's draft, to focus and raise that exact window; modal dialogs remain attached to their owner. | Partial: normal click focus works; app-specific modal stacking needs QA. |
| Titlebar controls | Close, minimize, maximize/restore, pin, double-click, drag, and system menu always target the titlebar's window even as focus changes. | Partial: core controls target the address; system menu pending. |
| Drag and resize | Border/corner resize, titlebar drag, unsnap on drag, precise release snap, mouse capture through animations, and no stuck drag state. | Partial: titlebar release and Lua fuzz pass; Alt/Super drag lacks a release callback. |
| Snap Layouts | Hover maximize and Win+Z show usable layout choices, including halves/quarters, at the right monitor scale. | Partial: Win+Z menu exists; maximize hover pending. |
| Snap Bar | Drag to the top to expose layout targets and choose a target without requiring the edge. | Pending. |
| Snap Assist | After a partial snap, suggest eligible other windows to fill free zones, excluding minimized, hidden, and incompatible modal windows. | Pending. |
| Snap Groups | Automatically form groups from complementary snapped windows; recall the group or one member from the taskbar; dissolve/update on move, resize, close, workspace and monitor changes. | Pending. |
| Snap resizing | Resize neighboring snapped windows coherently when a shared boundary moves, without overlap or off-screen placement. | Pending. |
| Window shortcuts | Win+arrows, Win+Shift+arrows, Win+M/Shift+M, Win+Home, Win+Z, Alt+Tab/Shift+Alt+Tab match state transitions and restore geometry. | Partial: basic Win+arrows, M, Home, Z exist; monitor transfer, vertical maximize and task switcher pending. |
| Alt+Tab | Show an ordered visual task switcher, cycle while held, commit on release, and respect the configured current/all desktop scope. | Pending; Omarchy currently focuses immediately without a preview. |
| Task View | Show window and desktop thumbnails; create, switch, close, rename and reorder desktops; move windows between desktops. | Pending; existing Omarchy workspaces provide numeric switching only. |
| Desktop shortcuts | Win+Tab, Win+Ctrl+D/F4/Left/Right operate on Task View/desktops without losing windows when a desktop closes. | Pending. |
| Titlebar Shake | Shaking an active window minimizes others, and repeating restores precisely that set. | Pending; Win+Home command exists. |
| Taskbar launchers | Pin/unpin apps, persist/reorder icons, launch with zero windows, show active/running states, group by app and support the Windows combine modes. | Pending; current bar has one running icon per window. |
| Taskbar preview | Hover shows correct per-window title/thumbnail (including minimized windows); group previews allow individual focus/close and Snap Group recall. | Partial: last-visible preview works; group actions pending. |
| Jump Lists | Right-click a taskbar app for launch, app desktop actions and recent items where that app exposes them. | Pending; arbitrary Windows app-specific Jump Lists have no Linux equivalent. |
| Taskbar keyboard | Win+T and number shortcuts navigate/launch/focus taskbar apps, including Jump List access where available. | Pending. |
| Show Desktop and Peek | Click Show Desktop to hide/restore current desktop windows; hover briefly reveals the desktop and restores it on exit. | Pending. |
| Taskbar display behavior | Pinned/running icons and previews behave across monitors and workspace scope; badges/attention requests surface when supported. | Pending; compositor/app protocols must be audited. |
| Corners and motion | Floating windows are rounded; snapped/maximized windows are square; window and preview animation is smooth; reduced-motion mode disables motion. | Partial: spring and preview fade exist; state-specific corners and reduced motion pending. |
| Session and failure recovery | Reconcile closed/restarted windows, compositor/shell reloads, stale addresses, monitor unplug, scale change and canceled drags without ghost state. | Pending full QA. |

The initial monitor-crop capture path could not image a hidden window. A later
audit found Hyprland's toplevel export through `grim -T`; it now produces
per-window previews for minimized and obscured windows from the compositor's
available buffer, as checked live. Native Windows APIs
for arbitrary app Jump Lists, taskbar progress/badges, and window-sharing
buttons likewise require explicit Linux application/protocol support; these
are not complete merely because a shell fallback is drawn.
