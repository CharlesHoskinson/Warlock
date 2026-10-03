# Global keyboard monitor: staged contract and proof boundary

## Scope

The goal is actual Orca global commands while a non-AT-SPI Wayland client such as Foot has native keyboard focus. A toolkit's AT-SPI forwarding, an Orca event watcher without consumption, or fabricated D-Bus key packets does not establish this behavior.

No main compositor plugin, D-Bus name, autostart, reader wrapper, or accessibility bridge has been installed or changed by this staging work. Main `ScreenReaderEnabled` remains false. The default routing invariant is that no registered client with explicit subscriptions/grabs means normal typing, compositor shortcuts, toggle state and input protocols retain their existing flow.

## D-Bus ABI

Session bus name `org.freedesktop.a11y.Manager`, object `/org/freedesktop/a11y/Manager`, interface `org.freedesktop.a11y.KeyboardMonitor`:

| Member | Signature | Contract |
| --- | --- | --- |
| WatchKeyboard / UnwatchKeyboard | `()` → `()` | Observe all keys; watching alone never consumes them. |
| GrabKeyboard / UngrabKeyboard | `()` → `()` | Temporary complete interception; ungrab retains selected key grabs and watching. |
| SetKeyGrabs | `(au,a(uu))` → `()` | Replace this caller's custom modifier keysyms and exact keysym/modifier pairs. |
| KeyEvent | `(buuuq)` | Directed signal: released, XKB modifier mask, keysym, Unicode scalar or zero, hardware keycode. |

Directed packets consistently describe state BEFORE the event: raw held non-locking/custom modifiers combined with accepted pre-event latched/locks. Keysyms use that same lookup state, with stored press identity retained for paired release after a map change. This matches KWin's `processKey` ordering and Mutter's `meta_key_event_new_from_evdev` before XKB update. An ordinary Caps/Num unlock release therefore still carries the prior lock bit; a following key carries the unlocked state. This is a compatibility convention, not a post-state correction. Physical suppression and explicit virtual accepted-shadow lock filtering are separate routing obligations.

Custom modifier grabs include other keys pressed while that modifier is held. A single standalone modifier tap is consumed; a sufficiently prompt second standalone tap passes normally. Suppression covers toggle state as well as ordinary delivery. Methods and signals are scoped to a D-Bus caller, and its grabs end with connection loss. [Public protocol](https://raw.githubusercontent.com/KDE/kwin/master/src/org.freedesktop.a11y.xml).

## Registration and actual client

Official AT-SPI supports application IDs: `Device.new_full(app_id)` requests `<app_id>.KeyboardMonitor`; its default registration is `org.a11y.atspi.KeyboardMonitor`. The compositor protocol does not specify an Orca-only allowlist. This candidate therefore validates the exact unique sender's owned KeyboardMonitor registration, supports independent caller state, and removes state when that identity disappears. Registration alone grants no subscription or interception. Current Mutter/KWin permissions are stricter implementation policies. [Official AT-SPI factory and backend](https://raw.githubusercontent.com/GNOME/at-spi2-core/main/atspi/atspi-device-a11y-manager.c), [Mutter implementation](https://raw.githubusercontent.com/GNOME/mutter/main/src/backends/meta-a11y-manager.c).

The tested installed backend is the reader prefix's signed AT-SPI 2.60.6 source at `orca-reader/physical-commands/at-spi2-core-2.60.6/atspi/atspi-device-a11y-manager.c`; current official source confirms the same application-ID construction.

Orca's signed local 50.2 factory calls `Atspi.Device.new_full("org.gnome.Orca")`. With a real manager owner, official AT-SPI chooses `AtspiDeviceA11yManager` and requests watching/grabs through this ABI. The reader agent's DeviceLegacy compatibility shim is bypassed. [Official Orca factory](https://raw.githubusercontent.com/GNOME/orca/main/src/orca/ax_device_manager.py).

## Native integration design for review

Use a fresh, separate plugin built against the exact installed Hyprland commit `efb50993780079460b0cbed1363e2166a2de1d9f`. Its D-Bus service and policy run on the compositor event loop; key processing must use local subscription state and queue directed signals without a synchronous external roundtrip. No loaded `.so` is overwritten.

The actual installed binary exports the relevant functions, and `native_abi_types.cpp` checks their installed-header member/call ABI offline. The proposed call points are `IKeyboard::updatePressed`, `CInputManager::onKeyboardKey`, and `IKeyboard::updateModifiers` with explicit physical/virtual handling.

Hyprland's physical callback calls `updatePressed`, emits its key event, and then updates XKB if the first call reported a change. Therefore cancelling only the public key event cannot meet the toggle suppression contract. The physical guard must decide before native pressed/XKB bookkeeping, retain the exact device/key/press route, and suppress normal delivery plus XKB/LED changes for captured input. Other keys follow the original functions intact. [Exact compositor source](https://github.com/hyprwm/Hyprland/tree/efb50993780079460b0cbed1363e2166a2de1d9f/src/devices).

Virtual keyboards provide modifiers explicitly after key events. Their incoming modifier state must be filtered using the captured press/release route: suppress grabbed depressed modifiers, preserve unrelated latched/layout changes, and retain a per-device lock parity correction when a suppressed toggle changes the virtual client's reported locks. Otherwise Caps/Num Lock can leak into core despite the key being captured. Observer modifier state needs separate raw non-locking state combined with accepted lock state. This remains a native execution proof obligation. A private-only candidate implements route-associated accepted-XKB shadow state plus raw/accepted parity, with standalone real-XKB replay evidence; actual compositor behavior is not inferred from the private ABI check.

Routes are recorded by native device plus hardware key, independently of a later modifier/layout/grab change. A press already delivered to an app retains its matching release even if a grab starts. A captured press retains a suppressed release even if its subscriber disappears; this bounded release tombstone prevents an orphan native release. Fresh unrelated keys pass immediately after disconnect. Device removal, keymap replacement, service loss, input suspension and plugin unload must clear routing safely without forwarding an unmatched press/release or leaving native modifiers stuck. Custom modifier tap state must reset on changed registrations/grab definitions, permission change, keymap change, an intervening chord or any intervening ordinary press after modifier release. Thus Caps→H→Caps is captured as a new first tap. This candidate chooses consecutive standalone taps; official Mutter updates its last keysym on each event in [the native seat implementation](https://raw.githubusercontent.com/GNOME/mutter/main/src/backends/native/meta-seat-impl.c).

The plugin must preserve IME, input capture, shortcut processing, existing keyboard sharing and permission checks for passed events. Disabled/unallowed devices must not become observable through this bridge. Keyboard-specific support must not fabricate pointer accessibility; a PointerLocator request lacking truthful surface metadata should report `org.freedesktop.a11y.UnknownToplevel`.

## Evidence now available

- `keyboard_monitor.qnt` and `_test.qnt`: 19 named scenarios pass; 2,000 samples with up to 100 steps find no invariant violation. They cover default typing/shortcuts, watch-only behavior, exact strokes, paired releases, toggle suppression, modifier double taps/chords/timeouts, independent clients, unauthorized callers, disconnect and service loss. The abstract alphabet does not establish actual layouts or hardware timing.
- `private_abi_proof.py`: ten checks pass using the official Orca factory and a second actual public AT-SPI client. Actual methods/grab signatures, lock variants, backend selection, directed signal decoding/custom virtual modifiers and disconnect cleanup pass. Private runtime/config exist before D-Bus starts; main socket inode/connectivity and reader status remain unchanged. `ATSPI_USE_A11Y_MANAGER_DEVICE=1` is confined to this headless private environment because it has no Wayland display.
- Fabricated ABI packets are labelled throughout `private-abi-report.json`; `nativeInputProved` is false. No real Orca command handling or native keyboard consumption is claimed.
- A private-only exact-ABI plugin v5 compiles; 70 deterministic policy/XKB checks pass. It has been loaded only in disposable private compositors. The bounded native official Orca command trial passed 15 acceptance and 12 restoration checks; the first wider policy trial passed 34 checks before an invalid permission-reload fixture assumption. See `NATIVE_RESULTS.md` and the retained attempt directories. No main plugin load has occurred.
- Primary source snapshots/provenance/hashes are under `sources/`.

## Required isolated native proof

After root reviews the fresh plugin diff/ABI and grants a GUI slot, create the private runtime/config/D-Bus/accessibility environment before starting the nested Wayland compositor. Load only the separately named candidate. Keep its host window visible for real input. Start actual Orca through the reader agent's unchanged strict Wayland wrapper, focus a disposable non-AT-SPI Foot terminal, and generate actual native key events.

Acceptance must show actual Orca command actions and terminal bytes, with no duplicate command characters: global learn mode/help/toggle actions, ordinary typing and compositor shortcuts, Shift/Ctrl combinations and key releases, Caps/Insert custom modifiers, first/second standalone modifier taps, Caps/Num lock state, grab changes and caller death while keys are held, and later ordinary input. Confirm actual DeviceA11yManager, directed events and identity, then terminate only private processes. Verify original main clients, focus, cursor, physical outputs, catalog, accessibility socket and reader-disabled state. Physical keyboard and virtual keyboard results must be classified separately. Main load/autostart remains subject to root coordination.

## Native permission transition control contract

The abstract SetPermission(false) event requires an actual change to the keyboard's core m_allowed state; loading an ignored config declaration is insufficient. Exact Lua hlPermission registers rules only during first launch (sources/hyprland-LuaBindingsConfigRules.cpp:618). It deliberately ignores permission declarations during reload. The first native policy attempt therefore never revoked permission and remains a failed fixture assumption, with no bridge defect or revocation success inferred.

The repaired private trial declares the exact native-input device-name deny at startup. Startup enforcement is true, and the plugin loads under its declared allow rule before the input producer exists. The policy phase temporarily disables enforcement before creating its own producer. While a selected h is captured, it reenables enforcement and schedules an explicit hl.device refresh for that same name. Core applyConfigToKeyboard then reevaluates the static deny and sets m_allowed=false before its unchanged-keymap return (sources/hyprland-InputManager.cpp:1268). The real captured repeat/release must remain suppressed without directed observations, fresh denied a must reach no Foot bytes, and the route must become quiescent. Restoring enforcement=false plus the same device refresh must restore observed ordinary input. These byte/packet obligations stay mandatory. Main enforcement is never changed.
