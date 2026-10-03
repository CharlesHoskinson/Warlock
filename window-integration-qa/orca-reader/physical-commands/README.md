# Orca keyboard path on Hyprland

## Results

The original physical fixture found a genuine key-consumption defect with no foreign input grabs. Orca recognized Insert+Ctrl+Down and moved ObjectNavigator into the first child, while the same key also changed the native controls/taskbar arrow selection. KP_Enter recognized Where Am I and also activated/dismissed Task View. The original reader trace and failed assertions are retained in `before-keygrab-fix/`.

With the explicit reader-process Legacy key-grab compatibility fix, the bounded fixture passed17/17 checks, including13 actual key-driven Orca commands and a separate assertion that every navigation/presentation command preserved the native keyboard container selection. The exact controls Minimize, Task View activation, and v62 taskbar preview activation passed. `after-keygrab-fix/` preserves the complete report, Orca trace and generated silent utterances. No Orca ExecuteCommand RPC is used in this fixture; the only reader RPC is the observation getter.

These are real compositor-delivered Wayland key events injected with a temporary virtual keyboard using the standard evdev US keymap and hardware codes (Insert110→Qt118, Control29→37, Down108→116, Return28→36). They exercise the same Qt/AT-SPI event route used by hardware. A human-operated physical keyboard was not tested. The helper releases held keys on normal exit and Hyprland releases any remaining pressed keys when the virtual keyboard disconnects. Neither compositor keyboard options nor user bindings were changed. `input:resolve_binds_by_sym` remained its original false value. Reader flags returned to false/false; only disposable windows were operated on; user identities and initial focus/cursor were preserved.

The narrow v62 regression separately passed7/7 checks: exact active app minimize, minimized accessible description, exact restore/focus, original geometry, inactive app raise without minimize, user identities, and unchanged desktop catalog bytes. This is direct AT-SPI activation regression evidence, distinct from the real-reader keyboard evidence. The minimized description is awaited because the motion backend commits the native workspace before the asynchronous taskbar snapshot arrives. No broad13/19 rerun was needed for the isolated reader-process compatibility change.

## Confirmed source mismatch

Signed Arch Orca50.2 calls Device.new_full and registers command KeyDefinitions with keysym populated and keycode0 (`orca/keybindings.py::_create_key_definitions`). Official AT-SPI2.60.6 falls back to DeviceLegacy when org.freedesktop.a11y.Manager has no owner. That Legacy class inherits the base add_key_grab, which stores the zero keycode, and notify_key compares only grab.keycode against the real event hardware code. It still emits key-pressed/key-released signals, explaining recognition without consumption. The keyboard watcher callback return cannot correct that matching decision.

`../legacy_keygrab_compat.py` supplies the real GDK hardware keycode only when the reader device is AtspiDeviceLegacy. It changes registration metadata; reader command functions, focus handling, object navigation and generated presentation remain Orca's own code. It is opt-in with ORCA_QA_LEGACY_GRAB_FIX=1 or `../run-orca-hyprland`, and can be disabled by returning to `../run-orca`. No package file, service or global settings were changed. The QA speech adapter remains silent.

Official GNOME2.60.7 was also downloaded and verified against its published SHA256 checksum. The same keycode-only matching is present, so updating to that version alone does not address this issue. `atspi-legacy-keysym-grab-proposal.patch` is an unapplied upstream source proposal allowing keysym-only grabs to match in the shared implementation; it is not claimed as a built/tested library repair.

## Global keyboard scope

The session bus reports no owner of org.freedesktop.a11y.Manager. The exact installed Hyprland0.56.2 checkout (efb50993780079460b0cbed1363e2166a2de1d9f) contains no org.freedesktop.a11y.KeyboardMonitor implementation. AT-SPI therefore reports AtspiDeviceLegacy in the real reader observation. Qt6.11.2's QSpiApplicationAdaptor captures key events, calls the registry DeviceEventController NotifyListenersSync, and discards consumed events or reposts unconsumed ones. The Qt-focused tests prove this toolkit route only. Global Orca command interception while a non-AT-SPI Wayland client is focused remains absent; implementing the compositor keyboard-monitor interface or a separately declared compositor shortcut adapter would be a different integration project. Simply enabling AX flags or assigning an Orca launch shortcut cannot provide that service.

## Strict native Wayland configuration

The earlier stock Orca/Xwayland-enabled run emitted XKB BadValue from its xkbcomp restoration operation under the QA virtual-keymap switches, before and after the basic key-grab fix. The tested strict wrapper `../run-orca-native-wayland` unsets DISPLAY only in the reader process and maps the Orca virtual modifier using the public Device.map_modifier API with actual GDK hardware codes. This avoids reader XKB server writes and Legacy's XKeysymToKeycode dependency.

The strict run passed the full17-check fixture with13 real Wayland key-driven commands and no XKB restoration warning. `strict-wayland-pass/` preserves the raw reader trace/report and explicit restoration snapshots: initial focus/cursor, original input option, physical keyboard devices, all keyboard layout/lock/main fields, pointer devices, and layer surfaces restored; the session AX flags returned to false/false. Fcitx5 recreated its ephemeral virtual keyboard resource address during focus transitions, while its keyboard fields were unchanged. No user application was stopped. The raw reader stdout retains a harmless CLI speech-factory lookup message: the CLI looks only for an orca namespace module while the speech manager supports the top-level custom module. The reader trace and utterance log confirm the silent adapter was actually used. This is not an audible synthesis failure or an XKB warning.

The strict wrapper is a supported reproducible QA artifact, with silent output and private reader paths. It was not installed as a system/default Orca command or added to autostart. The old candidate name delegates to the supported wrapper; the simple Xwayland-enabled compatibility wrapper remains separately available for reproducing the earlier result.

## Reproduction

```sh
# Compile only; no GUI access required.
wayland-scanner client-header virtual-keyboard-unstable-v1.xml virtual-keyboard-client.h
wayland-scanner private-code virtual-keyboard-unstable-v1.xml virtual-keyboard-protocol.c
cc -std=c11 -Wall -Wextra evdev-keyboard.c virtual-keyboard-protocol.c -o evdev-keyboard $(pkg-config --cflags --libs wayland-client xkbcommon)

# Requires exclusive GUI ownership; silent actual reader.
ORCA_QA_LEGACY_GRAB_FIX=1 ORCA_QA_NATIVE_WAYLAND_MODIFIERS=1 python live_reader_physical.py
python live_v62_activation.py
```

Primary evidence: signed packaged Orca source in the private prefix, checksum-verified [GNOME2.60.6 source](https://download.gnome.org/sources/at-spi2-core/2.60/at-spi2-core-2.60.6.tar.xz), [GNOME2.60.7 source](https://download.gnome.org/sources/at-spi2-core/2.60/at-spi2-core-2.60.7.tar.xz), exact local Hyprland checkout, and the captured [Qt6.11.2 application adaptor](https://github.com/qt/qtbase/blob/v6.11.2/src/gui/accessible/linux/qspiapplicationadaptor.cpp). No audible synthesis, braille, human usability, or global non-toolkit input success is claimed.
