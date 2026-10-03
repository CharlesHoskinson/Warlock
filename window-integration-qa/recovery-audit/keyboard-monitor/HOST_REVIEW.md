# Private host keyboard trial correction

## Retained failures

`native-attempt-1` retains the original GVariant parser exception before command input. Its immediate catalog comparison failed; later catalog hashes match accepted historical evidence, but this cannot retroactively establish that attempt's exact restoration.

`native-attempt-2` retains the genuine host command failure. Eight acceptance checks passed, including actual Orca 50.2 selecting DeviceA11yManager and entering learn mode through private native virtual keyboard input with Foot focused. The host Insert+h sequence instead reached Orca as Escape then character `1` and wrote `1b31` to Foot. Its PrepareUnload returned true, its private plugin was unloaded, and all eleven restoration checks passed against durable catalog bytes. No main plugin was loaded.

## Source classification and limits

Installed wtype is 0.4-2; its [v0.4 source](https://github.com/atx/wtype/blob/v0.4/main.c) assigns synthetic keycodes starting at one according to requested keysyms. Insert+h therefore produces codes 1 and 2. Installed Aquamarine is 0.15.0-2; its [v0.15.0 Wayland backend](https://github.com/hyprwm/aquamarine/blob/v0.15.0/src/backend/Wayland.cpp) forwards wl_keyboard key codes in CWaylandKeyboard without importing a keymap. Exact Hyprland source applies the configured keyboard map and CKeyboard feeds those forwarded codes into updatePressed. With US evdev, codes 1 and 2 mean Escape and `1`. Source snapshots and SHA256 values are in `sources/provenance.json`.

This explains the observed mismatch before bridge policy; it requires a pre-plugin typing baseline to establish the classification natively. It does not waive the bridge's separate native device keymap replacement gate, and it does not establish physical hardware support.

## Frozen corrected runner

`native_probe_host.py` uses the unchanged v5 source/library. Before loading the plugin, it focuses the exact disposable main host client and runs wtype `x`, recording expected/actual bytes without reclassifying a mismatch as a pass. It then uses the existing reader evdev-keyboard helper with a stable US map and code 30, asserting an exact `a` byte. That helper remains scoped to the host and closes with its own held-key releases.

The normal private virtual baseline, F12 compositor bind and actual official Orca learn-mode trial remain. A separate private registered watch-only client, `host_event_observer.py`, records directed real KeyEvent packets (`released`, mask, keysym, unicode, evdev+8 keycode). It creates no grabs or fake packets. The subsequent host Insert+h sends evdev 110 and 35 with paired real releases, requires an actual learn-mode utterance and unchanged Foot bytes, and records the observer's exact packet evidence. Escape exits learn mode. Both reader and observer exit before quiescent PrepareUnload and native unload.

The runner now compares all original main keyboard addresses, layouts/options, Caps/Num Lock and active selection as a twelfth preservation gate. It retains the original eleven state gates and durable 0600 exact catalog backup. It does not restore files from historical content. Any failure is preserved before correction.

Execution remains blocked until root explicitly grants the GUI slot for `python3 native_probe_host.py --execute --host-path`. There are no changes to v5, main services, settings, autostart or reader profiles. Forced/error unload with captured held keys remains unproved.
