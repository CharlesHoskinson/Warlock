# Wider private native policy contract and trial plan

The existing formal contract is `CONTRACT.md`, with nineteen named scenarios in `keyboard_monitor_test.qnt` and seventy real XKB replay checks. This fixture will replay the following semantic obligations against unchanged v5 in a real private compositor. It introduces no test-only policy setter. Actual directed KeyEvent packets, exact Foot bytes and the native keyboard's Caps/Num Lock state are the oracles.

| Separate gate | Native stimulus | Required outcome |
| --- | --- | --- |
| Watch only | Shift down, H down/up, Shift up | Foot H; paired pre-event packets 0, Shift, Shift, Shift |
| Watch Caps and Num | Real lock down/up, ordinary H | Accepted native toggles and packet lock mask agree; watch consumes nothing |
| Selected stroke | h down/up with exact h grab | No Foot h; paired packets; a still passes |
| Grab definition change while held | h down, remove grab, h up | Original captured release remains consumed; later h passes |
| Full grab | Caps, Num, ordinary h down/up | No bytes or native lock changes; ungrab restores normal typing |
| Custom Caps chord | Caps+h and paired releases | No Caps toggle, lowercase h symbol, no bytes |
| Custom Insert chord | Insert+h and paired releases | No bytes, exact original keysym/keycode pairs |
| Consecutive custom double tap | Two standalone Caps taps inside repeat delay | Second tap passes normally, with native toggle |
| Intervening ordinary key | Caps tap, h, Caps tap | Second Caps stays captured; h passes |
| Capture repeat | Multiple h-down packets then one h-up | Repeats observable; one route releases; no bytes/held residue |
| Client disconnect while held | Captured h down, terminate its registered client, h up | Release remains consumed, only surviving watch client observes; future h passes |
| Independent device removal | Capture same h on devices 0/1, retire 0 without producer release | Device 1 still captured; release 1 clears final route; no bytes |
| Live device keymap replacement | Capture US h, replace with Dvorak, modifier-only packet, release same code | Captured release retains original h symbol; later code uses new layout |
| Locking keymap replacement | Capture Caps, replace Caps with Ctrl, send modifier-only packet | Captured release remains balanced; no accepted modifier/toggle residue |
| Permission revocation | Capture h, startup device-name deny becomes enforced, with explicit device refresh, repeat/release | No forbidden directed observations; captured tombstone drains silently; fresh denied input reaches no Foot bytes; allow restores ordinary typing |
| Enabled-device revocation | Capture h, private device disabled via config reload, release | Separate enabled guard drains route silently; reenable restores typing |
| IME-ignore transition | Capture h, same Wayland client obtains real input-method-v2 keyboard grab, repeat/release | Capture remains suppressed without forbidden observation; fresh IME-origin bytes pass normally; removing IME restores monitoring |
| Explicit virtual batching | Raw captured modifier and normal key packets before a later explicit mask | Accepted native mask/lock state and directed packet semantics stay consistent, or retain a genuine failure |
| Unload quiescence | PrepareUnload while captured h is down | Returns false without ending subscriptions; real release drains route; final quiescent unload works |

These cases remain distinct. A disabled-device test cannot substitute for permission revocation. A stable host US command cannot substitute for native device keymap replacement. IME-ignore is exercised with a real same-client IMEv2 grab, matching `CInputManager::shouldIgnoreVirtualKeyboard`.

The compiled `native-fixture/native-input` runs only in an owned 0700 `/tmp/kbn-*` runtime with a relative private Wayland socket. It supports two real virtual-keyboard devices, explicit maps/modifier masks, repeat packets, deliberate device retirement, and a real same-client IME grab. A registered private control client configures only the public watch/grab API and records real directed packets. Permission/device changes affect only the disposable Lua config and exact nested signature; no main config is touched.

Exact core source establishes that hlPermission registers rules only on first launch (`sources/hyprland-LuaBindingsConfigRules.cpp:618`); a reload declaration is ignored. Retained native-policy-attempt-1 passed 34 prior gates, then failed that incorrect fixture assumption. It proves neither bridge revocation failure nor success.

The repaired trial declares the exact producer device-name deny at startup, with enforcement true while the reviewed plugin loads under its own allow rule. Before creating its producer, the policy phase disables enforcement in the disposable config. Its permission case reenables enforcement and includes `hl.device({name=exactName,enabled=true})`, which schedules REFRESH_INPUT_DEVICES (`sources/hyprland-LuaBindingsConfigRules.cpp:1098`). `applyConfigToKeyboard` sets m_allowed from the predeclared deny before the unchanged-map return (`sources/hyprland-InputManager.cpp:1268`). Restoring enforcement=false plus the same explicit device refresh restores input. Every reload records exact private config bytes and the actual enforcement option; no config errors and the exact producer name are required. Observed denied fresh input plus a silently drained held capture remain mandatory.

Core ordinary client delivery suppresses unmatched releases through `CInputManager::m_pressed`, but the keybind manager's unmatched-release fallback calls handleKeybinds and can invoke a release-only bind. Forced raw plugin unload with captured keys held therefore remains an unsupported maintenance boundary. The planned tests enforce PrepareUnload, never synthesize duplicate native releases, and never force a loaded callback's removal. No failure may be waived by the fixture.

All inputs await root's coordinated GUI grant. Main application identities/full state, keyboard state, output layout, reader false, accessibility socket, plugin list, exact catalog bytes, focus and cursor are preserved using the attempt-3 runner's twelve gates. All failed runs are archived before correction.
