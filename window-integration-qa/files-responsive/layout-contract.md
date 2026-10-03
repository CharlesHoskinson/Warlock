# Files responsive layout contract

Written before staged QML edits. Scope: GUI layout only, copied source; the running explorer, scripts, operations, fileops.qnt and persisted user state remain untouched.

Source: [Microsoft snap guidance](https://learn.microsoft.com/en-us/windows/apps/desktop/modernize/ui/apply-snap-layout-menu) recommends a minimum width of 500 effective pixels or less, preferably 330. Live Files requires 900×560 and cannot accept common snap widths.

## Required behavior

- Minimum client size 330×320. Preserve default 1320×800. At 330, 487, 500, 533, 800 and 1320 pixels, all rendered sizes are nonnegative and search/path fields are editable, clipped and at least 100 pixels wide.
- Toolbar uses one row from width1000; two rows from600; three below600. All original navigation and toolbar actions remain available. Hidden-files and pin/refresh buttons move to the search row below600.
- Sidebar docks from width900; otherwise explicit menu button or Ctrl+B opens it over the main area. Navigation and Escape dismiss the compact sidebar. All collections and tree remain reachable through scrolling at short heights.
- Details dock only when the main area can leave at least350 pixels for files (main width>=650). Compact selection keeps the full file list visible; Details or Ctrl+I explicitly opens a scrolling overlay. Close/Escape dismisses it. Selection, metadata, preview and all existing action callbacks stay intact.
- Compact folder header has bounded title/subtitle and a separate row for New Folder/New File. Zoom slider hides below560; Ctrl+plus/minus remains available. List keeps name and size; kind appears from480 and modified from650. Sorting any field remains available through Sort. Grid always has at least one positive-width column; thumbnail height shrinks in short viewports so a complete regular-folder cell, including name and metadata, fits at330×320.
- Home stacks media, collections, storage and recent files below900; filters wrap into reachable rows; pinned tiles have at least150 pixels unless a single tile occupies the available width. Dashboard scrolls vertically.
- Status gives selection/item summary priority; secondary fields progressively hide, and no text overlaps. Toasts, preview title and footer are bounded.
- Context menu fits inside the viewport and scrolls, including keyboard tracking of the active row. Prompt fits the viewport and scrolls long text while accept/cancel remain reachable. Path completions fit the available vertical space. Existing operations, validation, payloads and shortcuts are preserved.

## Evidence gates

1. Parse every changed QML with Qt's qmlformat. Instantiate actual copied QML offscreen with isolated HOME/FILES_STATE; exercise sizes and UI states, collect actual layout rectangles and assert above bounds. No native interaction claim from offscreen evidence.
2. Later, root coordinates copied native fixture: no original explorer PID restart. Exercise330×320,500×320,533px third,487px quarter,800px half; navigate/filter/list/grid/details/sidebar/menu/prompt/preview; verify compact actions still target fixture files and snap geometry accepts requested sizes. Preserve original apps/focus/cursor/catalog/state.
3. Hash all original/staged scripts and fileops.qnt; they must match. A deployable artifact excludes QA-only host diagnostics.

Native compatibility remains unverified until gate2. No silent screen-reader or braille claim is part of this layout work.

## Safe same-process reload contract (added before persistence edits)

- Preserve a hidden original explorer without briefly mapping it from its inherited FILES_OPEN=home. Initialization must wait for PersistentProperties.loaded; restored/migrated sessions skip FILES_OPEN entirely.
- Host uses explicitly identified PersistentProperties and JSON strings (no JavaScript objects tied to the old engine). Keep UI JSON separate from entries/shown JSON to avoid serializing directory metadata on every scroll/selection change.
- Initial legacy migration is explicit ui-migration.json, guarded by exact Quickshell processId and instanceId. The legacy state IPC contains basename-only clipboard/selection, so import only an idle Home snapshot with empty selection/clipboard and no preview/prompt; otherwise fail closed and do not open a window. Retain history/hIdx/cwd/filter/sort/mode/zoom/hidden/details. A cold new process cannot consume a stale migration for another instance.
- Subsequent reloads preserve full absolute selection/clipboard, entries/shown, navigation/UI preferences, visible/hidden state and scroll positions. File-operation subprocesses in flight are outside this migration gate; root deploys only after confirming idle state and no prompt. Successful reload popup is inhibited.
- Fixture must actually reload an old copied GUI into the candidate at the same PID, with FILES_OPEN=home inherited, and prove hidden state/history preserved; then reload candidate again with nonempty absolute clipboard/selection and prove persistence. No original process freeze/deploy by this agent.
