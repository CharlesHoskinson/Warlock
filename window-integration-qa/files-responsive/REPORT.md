# Files responsive GUI and safe reload

The final candidate is `app/`. Eleven QML files change. The original running explorer PID667402 was neither edited nor restarted by this agent. Scripts and `spec/fileops.qnt` retain their original hashes.

## Verified results

| Evidence | Result | Scope |
|---|---:|---|
| `parse-check.json` | 26 PASS | Actual Qt qmlformat parses, without rewriting source |
| `offscreen-report.json` | 120 PASS | Actual copied QML at12 sizes and10 UI states, isolated HOME/state/cache |
| `native-report.json` | 42 PASS | Physical controls, compact layout, actual native sizing and Snap, original-state preservation |
| `reload-native-report.json` | 20 PASS +10 preservation | Actual same-PID old-copy→candidate watcher reload, then candidate→candidate reload |
| `quint-scenarios.log` | 7 PASS | Named breakpoint, overlays, fields and minimum gallery scenarios |
| `quint-seeded.log` | 1000×40 PASS | `allProps`, seed330320; logical layout only |

Minimum client size is330×320. Toolbar uses three rows below600, two from600 through999, one from1000. Sidebar docks from900; otherwise Ctrl+B or its button opens a scrolling overlay. Details dock only when main width is at least650, leaving350 pixels for files; compact selection keeps full file width, with explicit Ctrl+I/button overlay. Search/path, list, gallery filenames, dialogs and menus remain usable at the minimum size. The gallery thumbnail cap leaves room for the filename and metadata in its viewport. See `native-shots/330-grid-name-visible.png`.

Native330×320,487×320,500×320 and533×320 matched requested client sizes. At the compositor's1.6 scale, requested800×500 became801×500; this one-pixel rounding is recorded. Actual half/quarter/third Snap accepted the copied explorer. Half/quarter widths rounded785 to784; native tests allow exactly one pixel, and record both measurements. The model does not erase that physical rounding.

Physical checks cover folder/file prompts, path/history, filter/Escape, grid/list, sort, sidebar, details, scrolling actions, Rename and preview. An initial Rename click during kinetic scrolling failed; `native-before-scroll-settle.json` retains that failed trial. The corrected fixture waits for scrolling to settle before its single physical click; final source and behavior passed. No file operation was performed on user data.

## Reload preservation

The copied original inherited `FILES_OPEN=home`. Migration retained its same PID, history3/hIdx2 and hidden state. The initialization snapshot recorded `visible=false` and `backingVisible=false` before backing windows mapped. No native reload popup, extra user client or layer appeared.

The host reads PersistentProperties before Explorer reload, stores JSON strings in three independent properties, and suppresses FILES_OPEN for restored sessions. The one-shot legacy import requires exact PID+Quickshell instance and idle hidden Home with empty selection/clipboard, no preview and no prompt. Subsequent actual reload retained absolute clipboard/selection paths, view/sort/zoom, scroll/UI preferences,330×320 geometry, compact overlay requests, and pending prompt payload/text/selection. Configuration logs had no QML errors. Own copied processes terminated normally after hiding.

Legacy `files state` omits dashboard kind, sidebar tree expansion and the hidden window's last geometry. The first migration conservatively defaults these fields; they are not claimed preserved. Original state has empty clipboard/selection and no prompt, making the narrow migration guard applicable. Active file-operation subprocesses are outside the deploy gate. Future reload persistence is established for the tested UI fields, not arbitrary in-flight operations.

Original client identities/geometries, focus, cursor, layers, virtual-desktop catalog, explorer dashboard bytes/public state/PID, accessibility flags and physical keyboard settings were checked and restored. Clipboard and primary selection were compared using in-memory SHA256 of raw `wl-paste --no-newline` bytes and MIME-list bytes; contents were never printed or saved.

## Locked artifact and reproduction

- `source-hashes.json` SHA256: `0053c06d4973bd8560d22200be2ab3c6f557f44cf3f3039f32e2edfc13b05859`
- `responsive.patch` SHA256: `2158eb3eecf4e3e1cbd47e31bdff76462a3ce4053ebaf5d3483d1f8b60a0c6b3`
- All11changed QML files are individually locked by original/candidate hashes. Ten scripts plus `spec/fileops.qnt` are unchanged.

`stage_layout.py --baseline <unchanged original tree> --output <new directory>` recreates the candidate with baseline and candidate hash guards. Construction scripts in `construction-history/` are historical and do not reproduce final manual refinements. `prepare_fixture.py` adds diagnostics and a unique IPC/title only to `qa-app/`; these are absent from the deployable `app/`. Never regenerate an active fixture tree. Native scripts require an explicitly coordinated GUI slot.

Root owns deployment through reviewed `deploy.py`: exact hidden original identity, fresh idle state, private backup/migration, coalesced atomic11-QML writes while stopped, same-process reload and preservation checks. Prepare bytes before freezing; restore partial writes before resuming if installation fails. After a successful stateful host migration, reverting to the old host could reopen FILES_OPEN and lose history. Remove the private one-shot migration after verification. This agent did not execute deployment.

## Sources and evidence boundaries

[Microsoft Snap guidance](https://learn.microsoft.com/en-us/windows/apps/desktop/modernize/ui/apply-snap-layout-menu) motivates330 width. [Quickshell PersistentProperties](https://master.quickshell.org/docs/types/Quickshell/PersistentProperties) and local primary source `~/src/quickshell-accessibility/src/core/persistentprops.cpp`, `generation.cpp`, `proxywindow.cpp` establish loaded/reload ordering. No audible speech, braille, Files screen-reader compatibility or full Files keyboard accessibility is claimed by this responsive work. The remaining keyboard/accessibility audit is separate.


## Root deployment

Root installed the locked 11-QML candidate into original PID667402 without
restarting it. Exact public state/history and hidden pre-map initialization pass;
clipboard, catalog, dashboard, accessibility socket/flags, focus, cursor and
layers are preserved. Scripts and fileops spec are unchanged. Twelve acceptance
checks pass in `deployment-report.json`. An initial raw full-client JSON equality
gate failed and is retained under `attemptChecks`; independent original-window
identity/geometry/workspace/pin/fullscreen preservation is verified against the
immediately preceding serial native fixture checkpoint. Its cause was not
established and that raw equality result is not claimed passed.
