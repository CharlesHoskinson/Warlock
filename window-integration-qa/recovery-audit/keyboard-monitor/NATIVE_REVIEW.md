# Private native candidate v5 review

## Frozen source and offline evidence

`native/plugin-v5.cpp`, `native/key_policy.hpp`, `native/libkeyboard-monitor-private-v5.so`, and `native/source-v5.diff` are the review artifacts. The plugin has been loaded only in two isolated private compositor attempts; neither attempt proves the complete physical-path gate. It has never been loaded on the main compositor. The library compiles against installed Hyprland 0.56.2, commit `efb50993780079460b0cbed1363e2166a2de1d9f`; installed compositor and compiler both identify GCC 16.2.1 20260810. All three exact mangled hook targets occur once in the installed binary's dynamic symbols.

The private ABI proof uses actual official Orca/AT-SPI factories but fabricated packets. The standalone C++ replay uses real libxkbcommon states and the candidate's policy/mask filter, without a compositor. Neither establishes a global reader command. `nativeInputProved` remains false.

- 19 named Quint scenarios and 2,000 samples at 100 steps pass.
- 70 deterministic policy/XKB checks pass, including permission revocation, per-device cleanup, keymap release identity, capture repeat counts, custom double taps, conflicting independent grabs, Caps and Num Lock correction.
- The existing ten private ABI checks pass with actual `AtspiDeviceA11yManager` clients.

## Changes from initial native design

Packets consistently use the PRE-event convention verified in both KWin and Mutter, with keysym derived from that same lookup state. v4 post-event packet semantics were rejected. Captured locking keys' depressed Lock contributions are removed from observer lookup so a suppressed Caps+h stays lowercase; raw held Shift/Ctrl and accepted preexisting locks remain represented. The packet helper is shared by plugin/replay. Detailed primary ordering and packet examples are in `EVENT_ORDER.md`.

Modifier-only packets rebuild a changed keymap before filtering. Named XKB modifiers remap lock correction and establish the first new-map packet against the remapped accepted baseline, rather than clearing parity blindly. Ordinary presses between standalone custom modifier taps disarm the tap; the exact Caps→H→Caps outcome is tested. Mutter's primary `is_a11y_modifier_first_click` records the last keysym for every event; KWin's snapshot has a different timer policy, so the consecutive-tap choice is explicit in this contract.

Captured releases and repeats remain suppressed after device permission or IME routing is revoked, and no directed event is emitted for a forbidden packet. Fresh forbidden keys call the original functions. Hardware release routes survive keymap changes; symbolic states rebuild under the new map. Device destruction removes only that device's routes. Captured repeats do not increment XKB held counts. D-Bus dispatch performs at most 32 messages per five millisecond timer tick.

Virtual lock packets use accepted XKB shadow state for route-associated lock bits, plus persistent raw/accepted lock parity. This is needed because actual libxkbcommon enables Caps/Num Lock on down and disables on the next up. Raw XOR correction alone delays the accepted next down transition. The replay demonstrates the correction for a real XKB Num Lock cycle. Actual native virtual modifier batching, non-US layouts, keymap changes and explicit masks still require the isolated proof; this implementation is a review candidate.

Init rejects any runtime outside `/tmp/kbn-*`, requires directory mode 0700 owned by the current user, requires `HYPR_A11Y_BRIDGE_PRIVATE=1`, and requires a real owned bus socket at exactly `<runtime>/bus` matching the configured D-Bus address. The short runtime prefix keeps Hyprland's Unix socket path under its length limit. It cannot accidentally claim the main session manager name with an inherited main bus address. No config, autostart, loaded library, reader status or reader wrapper was changed.

## Unload and core source analysis

Exact installed `PluginSystem.cpp` calls a void exit function on normal unload, removes function hooks, and then calls `dlclose`. Init failure uses `unloadPlugin(..., true)` and skips the exit function. The API cannot veto unload. See the primary source snapshots under `sources/`.

Normal trial cleanup first calls private `org.omarchy.KeyboardMonitorProbe.PrepareUnload`. It returns false while any captured key is held. It returns true only after captured routes are quiescent, then ends subscriptions/grabs. Only after true may the harness unload the private library. Accepted native held keys remain in native bookkeeping and receive their natural real releases; this plugin never synthesizes their release or clears native pressed vectors. This avoids duplicate or unmatched delivery.

Forced normal unload with captured keys held, or an error ejection after live initialization, remains unproved. Direct Wayland timer and D-Bus resources also rely on the exit function. Candidate init exceptions clean up installed hooks, timer and bus before rethrowing; a fatal init signal cannot be declared equivalent to this exception path. No main deployment is suitable until these boundaries are reviewed and tested. If cleanup cannot become quiescent in the trial, terminate only the private compositor and its fixture clients rather than claim a safe live unload.

## Concrete private native trial plan

Execution requires root's explicit GUI slot. All launch and input are private except the narrowly bounded host focus/input trial below.

1. Snapshot main client address/PID/stableId and geometry/workspace states; physical output JSON; active focus and cursor; taskbar catalog hashes; main `org.a11y.Bus` socket device/inode/connectivity and `ScreenReaderEnabled=false`; active plugin list. Guard against unrelated input grabs before any input.
2. Create `tempfile.TemporaryDirectory(prefix='kbn-')` with mode 0700. Set private runtime, config, data and cache before launching `dbus-daemon --session --nofork --address=unix:path=<runtime>/bus --print-address`. Clear main D-Bus/accessibility/session/signature/display variables. Keep only an absolute host Wayland display socket for the Aquamarine parent connection. Start `AQ_BACKENDS=wayland` nested Hyprland with a disposable Lua config, no shell/autostart/live plugins. Ensure its visible host window exists; record its PID/signature and use that exact signature for every native query/load.
3. Load only frozen `libkeyboard-monitor-private-v5.so` into that nested instance. Verify private manager ownership, introspection signatures, no config errors and default passive state. Ordinary nested typing and a disposable nested shortcut must work before a reader subscribes.
4. Reader agent explicitly authorized a scoped launcher reproducing its strict wrapper: same signed Orca 50.2 prefix, Python/GI/library paths, `GDK_BACKEND=wayland`, DISPLAY unset, strict modifier shim and silent factory arguments, using private copies of QA data/config/cache. Existing wrappers/shared QA profiles remain untouched. Launch actual Orca against nested Wayland and private D-Bus/accessibility services; read its existing QAObservation getter solely to confirm actual DeviceA11yManager and state. No ExecuteCommand RPC will substitute for input.
5. Focus a disposable native Foot with a raw terminal-byte receiver. Use the existing reader agent's actual Wayland virtual-keyboard protocol helper against the nested display for Insert+h learn mode, ordinary typing, Escape, Caps/Insert/Shift/Ctrl sequences and paired releases. Check actual Orca utterances/actions and exact received terminal bytes. Run private generic client watch/selected/full-grab cases for lock state, subscription changes, disconnect while held, permission revoke, keymap replacement and device destruction. These helpers may configure the public protocol; all native key packets originate in Wayland.
6. Separately test the compositor's physical pre-XKB path by focusing the visible nested host window and feeding a bounded host virtual keyboard sequence after verifying main focus identity. The nested Aquamarine keyboard uses `CKeyboard`; classify it as the compositor physical input path via a Wayland host, never physical hardware. Avoid keys bound by the main compositor. Verify typing/Orca actions and accepted modifier/LED state. Any unavailable physical-path case stays open.
7. Stop only private reader/test clients; ensure captured keys release; call PrepareUnload and require true. Unload only the exact nested plugin. Verify ordinary post-unload input. Terminate nested Foot/compositor/private accessibility services/bus by their recorded PIDs/process groups; never target the main compositor or user apps.
8. Restore original main focus/cursor only after checking the original client's identity still matches, and compare every snapshot. Preserve socket identity/connectivity, reader-disabled state, original clients/outputs/catalog/plugins. Release the GUI slot with acceptance/restoration matrices and all failed attempts retained.

Main compositor restart and physical hardware hotplug remain separate untested gates.
