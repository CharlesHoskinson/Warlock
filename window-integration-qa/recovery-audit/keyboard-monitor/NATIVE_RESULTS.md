# Private native KeyboardMonitor results

The frozen v5 bridge remains unloaded on the main compositor. Private attempt 3 passed 15 acceptance checks and 12 restoration checks. Reports, source, exact catalog backup, real packet stream, reader utterances and process logs are preserved under `native-attempt-3/`. Attempts 1 and 2 retain their failed outcomes.

| Gate | Result |
| --- | --- |
| Private config and default passive manager | PASS |
| No-reader ordinary typing and F12 compositor shortcut | PASS |
| Official Orca 50.2 selects AtspiDeviceA11yManager with DISPLAY unset | PASS |
| Real private virtual Insert+h enters learn mode on focused non-AT-SPI Foot | PASS |
| Exact virtual down/up packet pairs and full command consumption | PASS |
| Ordinary typing after learn-mode exit | PASS |
| Stable US host evdev Insert+h through nested CKeyboard pre-XKB path | PASS |
| Exact host down/up packet pairs and full command consumption | PASS |
| Captured routes quiescent before unload and normal typing after unload | PASS |
| Main client identities/full state, keyboard state, plugin list, focus/cursor, accessibility socket, disabled reader, catalogs, outputs, config errors and fixture cleanup | 12 PASS |
| Host wtype synthetic keymap translation before plugin load | FAIL: expected x/78, received Escape/1b |

Both command paths emitted the exact directed packet sequence `(released,keycode,keysym)` of `(false,118,65379)`, `(false,43,104)`, `(true,43,104)`, `(true,118,65379)`. Orca emitted real entering-learn-mode utterances on each path; no command bytes reached Foot. The terminal ended with hex `1b61616263647a`: initial pre-plugin wtype mismatch, stable host `a`, ordinary private `abc`, post-command `d`, and post-unload `z`.

Private compositor PID 3191187 used signature `efb50993780079460b0cbed1363e2166a2de1d9f_1790837294_1658133979` and runtime `/tmp/kbn-pas7v7yk`. All recorded private processes exited and the runtime was removed. The library was explicitly unloaded only after PrepareUnload returned true. Main accessibility socket remained device 84/inode 91312 and connectable; main ScreenReaderEnabled remained false. Original four application identities and states, keyboard Caps/Num Lock/active selection, focus and cursor were exact. Taskbar session-order bytes remained SHA256 `09c3f0bfbd9ad53dc69d7e74f3146e47dfb6fca54f846713fa31f8cdb1160fbf`.

The wtype failure is independently reproduced before plugin load. Versioned primary source explains the nested backend's lack of host keymap import; see `HOST_REVIEW.md`. Stable evdev host success proves the nested CKeyboard path under the configured US map. It does not prove physical hardware or non-US layout behavior, and it does not close native keymap replacement policy.

## Remaining gates

- Actual native watch-only Caps/Num/Shift packet ordering, custom Caps/Insert chords and double taps, selected/full-grab behavior and accepted lock restoration.
- Native permission/IME routing revocation, client disconnect or device destruction while captured keys are held, keymap replacement including modifier-only packets, and explicit virtual modifier batching.
- Registration adoption when a reader's KeyboardMonitor name predates manager startup; v5 intentionally does not implement it.
- Forced/error unload with captured keys held; the API cannot veto unload. Normal quiescent unload is proved here.
- Main bridge deployment and actual main compositor commands remain unauthorized and untested. Main compositor restart, physical hardware hotplug and physical keyboard behavior remain separate gates.

The GUI slot was explicitly released to root after cleanup. No main configuration, autostart, plugin, reader profile or service was changed.
