# Private v6 startup and retirement review

## Scope

The v5 library and every prior report remain frozen. This v6 library is restricted to an owned private `/tmp/kbn-*` runtime and its own session bus; it cannot initialize on the main compositor. No reader wrapper, autostart setting, desktop config, or production plugin was changed.

`service_lifecycle.qnt` and its tests precede the new code. Six named scenarios and 2,000 samples of 100 steps pass. `reader_reconnect_test.py` has six passing control-flow tests using doubles; these are not official-reader or native proof. The exact installed Hyprland ABI build passes. `lifecycle-stage-report.json` pins 17 dependencies; the runner verifies all of them before starting.

## Native changes from v5

`native/v5-to-v6.diff` adds irreversible retirement before stopping policy. Every public KeyboardMonitor request after retirement receives ServiceRetired. False retirement does not modify subscriptions. Quiescence includes raw/accepted virtual lock correction and pending controlled lock transitions; state deletion cannot remove an unload obligation.

Startup matches trusted bus NameOwnerChanged before ListNames/GetNameOwner adoption. Snapshot/reconciliation has a 1.5 second deadline, at most 256 registration lookups and 1,024 queued dispatches; normal dispatch remains at most 32 messages per timer tick. The Manager name becomes available only after adoption. Only signals from the bus daemon change registrations. Name adoption creates no policy entries.

The private Probe interface remains a private QA endpoint. Production must omit it and expose prepare_unload through narrow exact-instance compositor Lua/IPC, as directed by root. The staged source has no production initialization path.

## Reader replay uses the actual public path

The signed Orca 50.2 public CommandManager.get_keyboard_commands returns the current command dictionary; set_active_commands rebuilds the official diff without applying preferences. Its diff honors active/suspended commands and NumLock keypad exclusions. KeyBinding.remove_grabs clears its IDs after public InputEventManager removal. Public unmap_all_modifiers clears recorded device-specific mappings. Public stop_key_watcher disconnects handlers; public start_key_watcher replaces the retained old device reference on Atspi >=2.60. AXDeviceManager.deactivate/activate therefore replaces both managers through the actual Device factory without writing either private `_device` field.

The reconnect adapter tracks explicitly requested watch, full keyboard grab, and pause through scoped public method wrappers. This preserves learn mode and other explicit full-grab uses. The owner epoch is rechecked through GetNameOwner before replay; queued callbacks carrying a stale owner or epoch do nothing. Current command flags and definitions remain unchanged. DISPLAY must be absent; importing the adapter is passive.

Official AtspiDeviceA11yManager constructs WatchKeyboard only once and does not replay on owner change. Disposal removes its pending refresh timeout and signal proxy references. The adapter retires old IDs/mappings before replacing the actual device. It does not infer grabs from registrations, manufacture key events, or persist interception.

Primary installed sources: Orca command_manager.py:1921–2014,2044–2087; input_event_manager.py:60–178; keybindings.py:272–290; ax_device_manager.py; orca_modifier_manager.py:120–158,269–323; at-spi2-core-2.60.6/atspi/atspi-device-a11y-manager.c:457–477,542–577,709–739.

## Prepared native run

`python3 native_probe_lifecycle.py --execute` requires a new root GUI grant. It creates the private runtime before D-Bus; copies the existing silent reader profile; launches a dedicated nested Wayland compositor and real Foot byte receiver; starts real Orca in Legacy before loading v6; uses public monitor callers for registration churn and native-input for actual Wayland keys.

The oracle includes directed paired Insert/h and h packets, actual learn utterances, real terminal bytes, actual backend/device state, and actual Caps/Num state. Tests include owner churn overlapping load, previous/current registration authorization, Legacy→Manager, false held-key retirement preserving subscriptions, dirty Caps and Num unload refusal and real reconciliation, irreversible rejection of all five public policy requests, requested learn full-grab replay across actual unload/load, unchanged active/suspended command flags, and same surviving virtual keyboard clean lock parity across another unload/load.

All prior 12 main preservation gates remain: original client identities and states, keyboards/locks/main device, plugin list, focus/cursor, accessible socket inode/connectivity, reader disabled, exact catalog bytes with durable 0600 backup, outputs, config errors, and all fixture processes exited. Reports retain native keys, reader events, and failures. The runner performs no main plugin load or physical host input; native evidence will remain virtual-device/private-session evidence.

Production remains gated on actual private startup/restart results, management authority packaging, and the separate PointerLocator review owned by root. Forced raw core unload remains unsupported. Main compositor restart and physical hardware input/hotplug remain untested.
