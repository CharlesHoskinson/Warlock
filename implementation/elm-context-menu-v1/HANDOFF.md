# Context-menu implementation handoff

The experimental Elm shell now opens a window-row menu using a matching
secondary-button release, Context Menu key, or Shift+F10. Restore and Minimize
use the existing authenticated native authority. No installed desktop changes
were made. Full Windows-style menus and the right-click contract remain open.

## Accepted bounded evidence

- `qa/host-build-1791068919790678430/report.json`: optimized Elm UI, JavaScript
  syntax, C host build with warnings treated as errors, and two host self-tests.
- `qa/replay-1791068928068376202/report.json`: 91 checks, using the compiled
  Elm reducer with external lifecycle fixtures and uint64/binding decoder cases.
- `qa/native-1791068940107201096/report.json`: real right-click and keyboard
  interaction in the protected private compositor. Menu opening and disabled
  actions send no effects; Escape returns DOM focus to the row; Menu and
  Shift+F10 open the menu; Enter on Dismiss sends no window action; minimize
  and restore each send one correlated intent and receive a committed result;
  closing the target retires its menu without a command. With the backend paused,
  pending actions remain keyboard reachable; Escape dismisses the menu without
  replaying or cancelling the command, which commits once after resumption.
  All 33 recorded native/helper checks and cleanup passed.

The native pair is the exact owning compositor/plugin recorded in
`../elm-input-region-fix-v23/qa/build-pair-manifest.json`. The UI is a shell-owned
WebKit layer surface, not a native application menu or general Wayland popup.
Native tests use one unit-scale output with animations disabled. Receipt and
fresh snapshot are separate steps; renderer/presentation acceptance is separate.

## Review fixes

Focus and hover now update the typed selected item. Tab and Shift+Tab stay within the enabled actions and Dismiss. Pending or
unknown commands focus the menu container. Dismiss intercepts its own
Enter/Space, so its keypress cannot bubble into the selected action. Stale
dismissal cannot move focus. Press captures the full binding; release must match
that binding and an unchorded logical secondary-button gesture. Stable window
identity uses compositor lifetime/session plus incarnation, while native dispatch
still validates the complete binding including frontend epoch. Reconnecting a
broker therefore does not clear an unresolved command for that same window.

## Preserved attempts

The first integrated native run at `qa/native-1791068612578115061` passed
right-click/disabled/Escape checks but timed out at the keyboard opener. The QA
fixture used evdev KEY_MENU139, which this XKB layout maps to XF86MenuKB.
The corrected fixture uses evdev127 (`<COMP>` aliased to `<MENU>`). The same
deadline and application implementation then passed. The earlier host build
at `qa/host-build-1791068533792967304` rejected a four-item Elm tuple; its
replacement is a named press record. Failed evidence was preserved.

## Remaining gates

No requirement IDs are marked complete. This does not qualify full native
system-menu operations, taskbar grouping, app-owned menu delegation, Files and
clipboard providers, nested menus, outside-click dismissal, capture/focus loss,
monitor-aware placement, transformed or fractional-scale outputs, accessibility,
IME, modal/exclusive/locked states, resource bounds, or combined release behavior.
Unknown operations remain blocked; the first adapter has no general reconciliation
service for old outstanding operations after another target starts a transaction.
The pure reducer's ledgers and trusted item constructors need bounded provider
validation before production use.

## Sampled model evidence

`qa/model-1791069016270841530/report.json` passed 24 named scenarios and
1,000 sampled traces of 40 steps. All nine action witnesses were reached.
The single-actor model serializes one unresolved command globally, a stricter
restriction than the Elm reducer's independent target ledgers. It is abstract
sampled safety evidence, not exhaustive verification or native acceptance.
[spec/README.md](spec/README.md) maps its checks and documents differences.

The approved Quint sketch is retained in `spec/menu-sketch.qnt`. Its runnable
type derivative changes only the reserved field name `action` to `actionId`.
The combined `qa/implementation-manifest.json` records separate source closures
and claim scopes. The original failed reports and successful earlier passes remain
unchanged. Full right-click acceptance and requirement completion stay open.
