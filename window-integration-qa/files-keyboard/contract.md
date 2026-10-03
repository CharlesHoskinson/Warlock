# Files keyboard and accessibility contract

Written before separate candidate edits. Baseline is the locked responsive candidate, now deployed by root to the hidden original explorer. This stage never edits the live app, scripts, file-operation semantics or user state.

## Required routing

1. Visible enabled buttons expose meaningful names, roles, state and the same press action as their pointer callback. Tab/Shift+Tab reach them; Return/Space activates once, and disabled controls cannot activate. Focus has a visible indicator. Decorative glyphs do not become reader targets.
2. Unhandled keys from focused descendants reach the existing Explorer command handler. Input editing/completion, control activation, menu navigation and modal handling consume their keys first. This preserves existing Ctrl+L/F/B/I, navigation, selection and file-operation shortcuts.
3. A prompt traps Tab among its input, Cancel and accept controls, supports Shift+Tab, Escape and Return, and exposes dialog/input labels. No focus escapes to an underlying destructive action. Existing operation mode/payload/validation callbacks remain intact.
4. Menus expose named enabled rows, follow actual focus when arrow selection changes, scroll the focused row into view, and keep their existing chosen action. Escape closes. Keyboard invocation of a file context menu uses the current file identity.
5. Compact sidebar opening reaches a collection/tree control. Tab, activation, Escape and tree arrows remain usable, with focus scrolling through the clipped sidebar/tree. Tree expansion and navigation use the existing callbacks and capture primitive identity before model changes.
6. Folder list/grid use roving keyboard focus at the selected current row/cell. Existing arrow/shift-selection/open/preview semantics remain. Accessible name includes the full filename, role/selected state reflect the item, and reader activation targets its original path. Group headers and decorative cell content are not extra actionable targets.
7. Home filters, media, collection cards, pinned folders, recent files and storage blocks each need named keyboard/reader actions and focus scrolling. A toolbar-only result cannot establish complete Files accessibility.
8. The standalone Files qs process imports its own exact Qt6.11.2 V4 factory repair. Readers remain silent/logged in fixtures. Native AT-SPI and actual Orca proof are separate evidence gates; QML declarations or direct AX calls alone do not prove reader compatibility.

## Evidence gates

- Parse candidate QML, compare all script/spec hashes, and instantiate real copied QML offscreen. Deliver Qt keyboard events to the offscreen QQuickWindow; prove routing, enabled state and modal trapping. This establishes Qt event behavior only.
- Keep the responsive120-case geometry matrix and same-process migration tests intact. Candidate source never contains QA IPC or event injection.
- Request a coordinated GUI slot for bounded physical input and actual silent Orca navigation/actions against isolated fixture files. Preserve original explorer/processes/focus/cursor/catalog/clipboard/a11y state.
- Report unimplemented areas explicitly. No Files reader or full keyboard compatibility claim before complete folder/Home coverage and actual reader evidence.

## Primary sources

[Qt Accessible](https://doc.qt.io/qt-6/qml-qtquick-accessible.html) requires role/name/action for custom controls. [Qt Item focus](https://doc.qt.io/qt-6/qml-qtquick-item.html#activeFocusOnTab-prop) and [keyboard focus routing](https://doc.qt.io/qt-6/qtquick-input-focus.html) describe traversal and propagation. These web pages currently show6.12; this stage uses only properties already present in installed6.11.2. Native bridge private ABI remains version guarded.
