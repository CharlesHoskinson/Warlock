# Cross-display native file drag gate

Status: native execution PASS on deployed paired v14 plugin / whole-window motion helpers / widget_v64. Eight paths produced 11 passing acceptance assertions and 11 passing restoration checks. GUI slot released and all fixtures cleaned. Evidence: `native-cross-display-report.json` and `acceptance-matrix.json`. Three actual native FileList copies each contained 262166 bytes with SHA256 `b002780c5fbf3b1cef1fab39ab213606e0c342175f95fbf01d59a87fbd3819f2`.

## Acceptance

- A GTK source exports a native `Gdk.FileList` and URI list with COPY action. A GTK receiver accepts the native list, copies the actual payload into its own temporary destination, reads the copy back, and records byte count and SHA256. Payload includes binary bytes and a filename containing spaces.
- The source is on the existing physical display. Destinations and the actual Omarchy taskbar are on a named temporary 1920x1080 output at scale 1.5. Pointer extent and logical offsets come from actual monitor geometry.
- Direct cross-display drop establishes native input/transfer baseline.
- Leaving the destination taskbar before dwell preserves minimization. Singleton dwell restores the captured destination on its home output and preserves native drop.
- Group dwell opens the destination chooser without restoring either peer. Actual preview geometry selects exactly one peer, restores it, and preserves native drop into that receiver.
- Escape clears drag state and popups on every output; later motion cannot reopen the cancelled chooser.
- Removing the temporary output while its chooser is open removes the orphan widget, clears drag/chooser state, and preserves both unselected minimized clients.
- Source bytes remain intact, and GTK never requests source deletion.

This is actual native multioutput input with a temporary headless output. It does not establish physical cable hotplug or physical display content visibility.

## Candidate API

`stage_diagnostics.py SOURCE DESTINATION` stages an additive patch without editing SOURCE. `state()` retains its existing fields. Root-level diagnostic functions provide all output instances to `stateAll()` and one identified output to `stateForMonitor(monitor)`. Geometry adds monitor origin/logical size, actual bar offset, and task item height. Queries contain no focus, popup, restore, or input actions.

Root's motion agent applied this patch to its fresh `minimize-motion-stage/whole-window/widget_v64` candidate. The copied v62/v63 artifacts here are patch references, not deployment targets.

## Run in the allocated slot

```bash
python3 /home/hoskinson/window-integration-qa/recovery-audit/cross-display/native_cross_display.py --execute
```

Without `--execute`, the runner only prints staged status. It does not query or change the desktop.

## Preservation and cleanup

Before mutation, the runner requires the new diagnostic API and snapshots original client address/PID/stable ID, workspace/pinned state/geometry/fullscreen, focus, cursor, monitor configuration, main accessibility socket inode/connectivity, and exact bytes or absence of:

- `~/.config/omarchy/virtual-desktops.json`
- `~/.config/omarchy/taskbar-settings.json`
- `~/.config/omarchy/taskbar-order.json`
- `~/.config/omarchy/taskbar-session-order.json`

It refuses an existing output named `WINDOW-PARITY-FILE-DRAG-QA` and layouts with negative origins, which the current unsigned absolute virtual pointer cannot address. Existing monitor mode/position/scale is frozen through temporary Lua evaluations while adding the output. The live manifest and compositor startup files are never edited.

Cleanup first cancels any held native drag, then releases the pointer button. It terminates only recorded fixture processes; removes only their closed-window minimize sidecars; removes the uniquely named temporary output; restores the four files byte for byte or removes them if originally absent; reloads the original compositor configuration; and restores original focus and cursor. Report restoration checks require original clients, geometry, outputs, config errors, catalog bytes, drag state, and accessibility socket preservation. No main compositor restart or existing app termination occurs.

Evidence goes to `native-cross-display-report.json`, including actual native events, copied hashes, acceptance checks, and restoration checks. Fixture payload/copies are confined to a temporary directory and removed after the report is captured.

## Offline evidence

Python compilation passed for all three staged Python files. A real local GTK/GDK binding check created and inspected a native `Gdk.FileList` and its content provider. `test_diagnostics.js` executes the actual extracted candidate helper against two independent output contexts and checks fractional geometry, bottom bar offset, preserved fields, and absence of actions. The motion agent reports both QML parse checks passing for the fresh paired candidate. These checks do not count as native cross-display acceptance.

## Native fixture correction evidence

Earlier attempts are retained. Restore/focus can warp the cursor to the exact point chosen by a fixture. An absolute move to that same point provides no genuine native DnD entry; both source and receiver now receive real nonzero motion before button-down or release. Receiver entry events and real copied bytes verify the correction. Queued pointer dwell commands are awaited before assertions. Five transient diagnostic reads returned `Target not found.` while IPC monitor ownership changed; the final run records and retries them. The output-removal scenario uses a fresh disposable source after the independent Escape scenario. No deployed behavior helper or plugin was changed to obtain this result.
