# Actual Orca reader compatibility QA

Orca 50.2 is extracted from signed official Arch packages into `prefix/`. No root install, package database edit, service installation, or global Orca preferences are used. `packages.json` records exact archived package URLs, SHA-256 hashes, and signature verification. `setup.py` reproduces the prefix and verifies signatures against the installed official Arch keyring.

Run setup with `python setup.py`. With exclusive physical GUI ownership, run `python live_reader.py`.

`run-orca` uses the packaged Orca entry point, native event loop, focus manager, presentation generators, ObjectNavigator, WhereAmIPresenter, and action execution. Its output factory writes the generated speech to `utterances.jsonl` without connecting to a synthesizer. Braille and sounds are disabled only in the reader process. GSettings uses the memory backend; all reader paths point into this QA directory. The observation customization exports reader focus and navigator state without setting either. The actual navigation/action tests call Orca's own supported D-Bus commands rather than direct AT-SPI `do_action` calls.

The fixture enables and restores the session accessibility status, creates only disposable windows, dismisses its overlays, stops the reader, and restores initial app focus/cursor. It does not create or modify desktops, alter taskbar settings, or operate on user window identities. `report.json`, `reader.debug`, `reader.stdout`, and `utterances.jsonl` provide evidence.

This verifies reader object navigation, AT-SPI focus event handling, semantic announcement generation, and reader action execution. It does not verify hardware braille, audible speech synthesis, human usability, or Orca physical keyboard interception on Hyprland. Physical arrow/Tab keys exercise the shell's own keyboard navigation; Orca commands are dispatched through its D-Bus API.

Initial live startup exposed an existing accessibility socket issue: the advertised `/run/user/1000/at-spi/bus_0` refused new connections while the established service remained running. `initial-bus-failure.json` preserves that failed startup separately. The bus was repaired by an authorized user-service restart. Qt widgets required their own process restart to re-register their accessible trees. The file explorer and user applications were kept running.

Primary references:

- [Official Arch Orca package and dependency list](https://archlinux.org/packages/extra/any/orca/)
- [GNOME Orca source mirror](https://github.com/GNOME/orca)
- [Official Orca manual](https://man.archlinux.org/man/extra/orca/orca.1.en)
- [GNOME Orca command help](https://gnome.pages.gitlab.gnome.org/orca/help/commands.html)
- [GNOME Orca speech factory selection](https://github.com/GNOME/orca/blob/main/README.md)

The extracted Orca 50.2 source in `prefix/usr/lib/python3.14/site-packages/orca/` is the exact implementation used by this fixture, including `dbus_service.py`, `object_navigator.py`, `speech_manager.py`, and `speechserver.py`.

## Results

The clean V4 run passed all sixteen checks: fifteen actual Orca reader semantics/actions checks and user-window identity preservation. Five controls checks cover announcement, retained selected-item focus, sibling navigation, locating Minimize, and Orca PerformAction minimizing the exact disposable window. Four Task View checks cover selected-window announcement, desktop tab focus, close-child discovery, and native activation of the exact disposable window. Six taskbar checks cover selected-preview locus, announcement, arrow navigation, close-child discovery, exact native preview activation, and app-actions menu focus.

`evidence-v4-clean/` preserves the complete reader report, actual Orca debug trace and generated utterances, plus native AX regression evidence: controls13/13 and shell19/19 passed. The controls stale-node check accepts the inaccessible/rejected stale action now produced by the current bridge and still verifies the restored window remains unchanged. `results-classification.json` distinguishes the clean passing run from the preserved earlier run.

The earlier raw report in `evidence-before-grab-resolution/` is preserved unchanged. Its final Task View/taskbar native-focus timeouts occurred during unrelated exclusive sudo-askpass surfaces traced by root to an external Claude process. The clean exact backend-focus checks now pass. The fixture detects known authentication/lock surfaces before starting and records them when scenarios fail.

Actual reader testing found and addressed three issues that filtered direct AT-SPI enumeration had missed:

- Qt emitted a real keyboard focus-container event after the synthetic selected-child focus, overwriting Orca's focus locus. Keyboard handlers now belong to an ignored child item, and the fresh V3 native Quick item interface validates the current private accessibility flag even when Qt cached the interface before QML set ignored.
- Hidden snap/layout controls remained reachable through Orca ObjectNavigator. Interactive items now apply ignored status according to their mode/open/visibility, with delayed selected-item focus when Task View/taskbar opens.
- Replacing JS array Repeater models recreated accessible objects on arbitrary title/snapshot changes. Keyed ListModel reconciliation keeps window, preview, desktop, menu and app-button objects alive across payload updates.

Live candidates at handoff: controls imports fresh V4; Task View manifest uses overlay_v13; taskbar manifest uses widget_reader_v3. The taskbar includes the keyed app-button delegate lifetime fix. The same AX patches and V4 import are in the motion agent's widget_v62 source, together with its requested motionRefresh IPC. Motion helpers are a separate coordinated deployment.

## Focused controls shutdown defect

`controls-teardown-symbolized.txt` preserves the actual coredump backtrace. It resolves RootWrapper shutdown after QGuiApplication teardown, followed by ProxyWindowContentItem destruction, Qt clearFocusInScope, and QInputMethod::commit(this=0x0). Local Quickshell launch.cpp constructs a stack RootWrapper, deletes its GUI application after the event loop, then destroys RootWrapper on scope exit. Qt's focus teardown calls inputMethod()->commit without a null guard. No bridge frame on the stack alone would establish bridge innocence; the observed ownership order and null input-method receiver explain the failing path.

`native-shutdown/quickshell-root-before-app.patch` is the reviewable source ownership correction and has not been applied to installed Quickshell. `native-shutdown/WindowAccessibilityV4` is the tested fresh workaround candidate: its aboutToQuit hook recursively clears Quick leaf, scope and content focus while the GUI application still exists. The compiled offscreen probe loads this actual V4 plugin, starts with an active focused Quick leaf, verifies focus clears, deletes the GUI application before the window, and exits zero (`offscreen-probe.log`). This establishes the tested native mechanism, not a full Quickshell lifecycle fix. The exact disposable copied-controls normal `qs kill` test also passed with leafActiveFocus=true immediately before shutdown and process exit zero (`disposable-controls-report.json`). The original live V3 controls were hidden, shut down normally, then relaunched with fresh V4; no loaded shared object was overwritten. A SIGKILL workaround is not counted as a shutdown repair.

The reader was stopped, disposable windows closed, user native window identities preserved, and the original session AX flags false/false restored. The clean run restored initial focus/cursor. Restoration during the earlier external grab could not be guaranteed.

## Later physical command audit

The [physical command report](physical-commands/README.md) records a separate genuine keyboard-consumption defect in stock Orca50.2 with AT-SPI DeviceLegacy. Recognition worked while keys leaked into the native shell controls. An opt-in reader-process registration compatibility fix passed17/17 checks with13 real Wayland key-driven Orca commands, and the new v62 motion frontend passed the focused7/7 AX activation regression. The earlier16-check command-RPC run remains separate evidence. Global non-toolkit keyboard interception remains absent. The strict native Wayland QA wrapper subsequently passed the full17-check key-driven fixture with no XKB restoration warning and explicit restoration evidence; `run-orca-native-wayland` is the supported isolated silent QA launcher. It is not a system/default Orca installation.
