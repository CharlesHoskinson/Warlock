# Files compact keyboard and accessibility stage

This is a separate, undeployed candidate at `app/`, based on the root-deployed responsive Files GUI. The original explorer PID667402 remained hidden and was neither edited nor reloaded during this work.

## Concrete gaps found

The previous custom buttons used only MouseArea, without Tab focus, keyboard activation or accessibility role/name/action. Sidebar collections/tree, folder delegates and Home cards likewise lacked explicit named reader actions. The standalone Files process did not import the native Qt accessibility factory repair already tested in controls/taskbar. Adding focusable controls also requires forwarding unhandled descendant keys to the existing Explorer command handler, which is a sibling item.

The spec was written first in `contract.md`. The candidate adds:

- Named buttons and filters, disabled-state gating, keyboard activation and visible focus; labeled path/filter/prompt text fields; decorative glyph exclusion.
- Forwarding of unhandled content keys to existing Explorer shortcuts. Text editing, completion, buttons, menus and prompts consume their own keys.
- Prompt Tab/Backtab trapping among input, Cancel and accept; existing Escape/Return callbacks and operation payloads remain.
- Sidebar collection focus, scrolling, arrows/Tab and Escape; tree row focus and arrows for expansion, collapse and parent navigation.
- Actual focused menu rows with named press actions and captured action strings before dismissal.
- Roving folder list/grid focus, full filename/path/selection metadata and existing activation/selection callbacks; keyboard context-menu invocation.
- Named Home filters, media/collection cards, pins, recent rows and storage blocks, with focus scrolling and existing callbacks.
- A separate copy of the tested V4 Qt accessibility extension. Its binary is unchanged and guarded for Qt 6.11.2.

## Evidence

| Artifact | Result | Meaning |
|---|---:|---|
| `parse-check.json` | 26 PASS | Actual Qt QML parsing |
| `offscreen-keys-report.json` | 58 PASS | Qt events delivered to the real offscreen QQuickWindow |
| `offscreen-report.json` | 120 PASS | Actual copied QML geometry at 12 sizes and 10 UI states |
| `native-reader-report.json` | 26 PASS +13 preservation | Physical app keys and actual Orca on a copied 330×320 Wayland window |

The Qt key fixture exercises real toolbar activation/shortcut routing; prompt trapping; minimum size; file list/grid item focus; current-file menu and menu-row focus; compact sidebar/tree traversal; Home filter and collection activation. Its event helper exists only in `qa-app/`. No compositor input or reader compatibility is inferred from that offscreen result.

The native fixture used official locally extracted Orca 50.2 with the strict native Wayland QA wrapper and silent speech adapter. Physical Tab/Return/file arrows/F2 followed actual reader focus to buttons, full filenames and Rename text. Native prompt Tab trapped correctly. Actual Orca ObjectNavigator traversed parent/children/siblings to Sort, and its PerformAction opened the existing menu. The menu row, compact sidebar collection and Home filters produced named reader focus and logged utterances. See `focusTrace` and `utterances.jsonl`.

No direct AT-SPI action substituted for reader actions. Setup focused a named Qt item through QA IPC, then native keys and real Orca handled subsequent behavior. ObjectNavigator commands used Orca's public local D-Bus command interface; global physical Orca command interception is covered by the separate earlier reader work and compositor-bridge audit, not this test.

## Preservation and limitations

All 13 checks passed: original native identities/geometries, focus, cursor, layers, clipboard/primary raw and MIME hashes, catalog/dashboard bytes, original Files public state/PID/hidden state, accessibility flags, accessibility socket inode and prior responsive manifest bytes. Clipboard contents were compared in memory and never printed or saved. Reader/fixture were stopped normally; no QA instance remains running. No system packages, global reader command or accessibility service were installed/restarted.

Actual native reader actions on gallery cells, tree rows, media/pinned/recent/storage cards and details controls are still unverified. Their staged declarations and broader Qt event/geometry checks do not establish complete Files reader compatibility. Offscreen coverage of virtualized recent/tree/list delegates also does not prove every large-directory edge case. The 15-QML candidate should remain staged until root reviews the scoped evidence and any remaining required gates.

Initial fixture failures are retained in `native-fixture-hide-remap-failure.json` and `native-role-label-fixture-failure.json`: hiding/remapping during size setup invalidated the captured native identity, and this installed AT-SPI calls the role `button`, rather than the fixture's assumed `push button`. Neither established a Files action regression. Final native size setup uses a targeted compositor resize and retains identity. A previous prompt Tab failure was also an expected object-name mismatch in the fixture; explicit per-control trapping was independently verified afterward.

Qt logs contain unsupported AT-SPI Window:Destroy subscription warnings. Final configuration had no QML errors/undefined role assignments. A stage-time undefined Accessible.Menu enum was corrected to the installed PopupMenu role before final geometry/native evidence.

## Locked source / deployment boundary

- `source-hashes.json`: `32b38cab2c457fcfb30eb4d13c6534f4eafe430656b06b8cc72078b2276f9559`
- `keyboard.patch`: `61d71cc5058d4d802de78c0408bf06a570a0ee93c8cdab6bbf5d41a033f2928e`
- V4 binary: `3e79329aa2c9b4008cbf7bd39b859fc6f578a89a03ac10cfb01b9b4f6e67c46a`

All 15 changed QML files have baseline/candidate hashes. Ten scripts and fileops.qnt match live. Candidate source contains no QA IPC/event injection. The absolute file import currently points to the isolated stage's copied V4 extension because Quickshell intercepts relative URLs; any deployment needs a durable reviewed native extension URL and a corresponding new source lock. Never overwrite a loaded native library.

The existing stateful host and migration guards remain. Root owns any future controlled deployment and preservation checks; this agent did not deploy. Construction scripts record initial edits, but final source/patch/hash lock is authoritative after manual refinements. Native scripts require an explicit GUI slot.

Primary Qt sources are linked in `contract.md`; actual installed Qt 6.11.2 and the V4 bridge source were used for ABI and role behavior. No audible speech or braille behavior is claimed.

## Preservation scope clarification

The26 native reader fixture catalogBytes gate hashes virtual-desktops.json only. It does not establish taskbar-settings/order/session-order preservation. The next native fixture must privately retain all four exact byte snapshots and restore only its own ordered-catalog changes.

The frozen candidate is superseded for further staging by guard-stage after retained-probe/report.json confirmed hidden native/raw action dispatch, modal CtrlL escape, media peer rebinding, and focused-row reload loss. Existing26 evidence remains unchanged and does not claim those guards.
