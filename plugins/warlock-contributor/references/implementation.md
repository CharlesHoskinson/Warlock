# Find the implementation before adding code

Use this map when selecting source paths for a slice. Inspect the current exports
and call sites; paths identify responsibilities, not permission to edit every row.
The original requirement and OpenSpec determine which behavior belongs in the change.

| Work | Start here | Decisive component evidence |
| --- | --- | --- |
| Shell policy and typed transitions | `implementation/warlock/src/Desktop.elm`; integration ports in `src/Main.elm` | `src/DesktopReplay.elm` and the replay for the affected subsystem |
| Taskbar/popup presentation and feedback | `src/SurfaceRenderer.elm`, `src/Bar.elm`, `src/ActionProjection.elm` | `qa/check-feedback.py`; native presentation/input when required |
| Surface keyboard, focus and layout | `assets/bar-adapter.js`, `assets/popup-adapter.js`, `assets/context.js`, `assets/activation.js`, `assets/shell.css` | For UI-008, `qa/check-search.py --dense-taskbar` (overflow) or `--pinned-menus` (menus); corresponding native modes and original AT obligations remain separate |
| Single-family taskbar primary actions/state labels | `src/Taskbar.elm`, `src/TaskbarShell.elm`, `src/Surface.elm` | `qa/check-search.py --taskbar-primary`; native `qa/native-window-feedback.py --taskbar-primary` for exact receipt, MRU/desktop focus and window pixels; primary keyboard/AT remains separate |
| Catalog search and launch | `src/Catalog.elm`, `src/Launch.elm`, `adapter/catalog_authority.py` | `qa/check-search.py`, `src/CatalogReplay.elm`, `src/LaunchReplay.elm` |
| Persistent pins | `src/Desktop.elm`, `adapter/taskbar_preferences.py`, `adapter/taskbar_projection.py` | `qa/check-pin-storage.py`, `qa/pins.qnt` |
| Task View/workspace navigation | `src/Desktop.elm` and the current native authority | `qa/check-navigation-projection.py`, `qa/task-view.qnt`, `qa/workspace-navigation.qnt` |
| Pending/Refused/Unknown outcomes | `src/Effects.elm`, `src/NativeOutcome.elm`, `adapter/effect_endpoint.py` | Current transaction replay and the native refusal/recovery journey |
| GTK/WebKit surfaces and leases | `native/host.c`, `native/shared-host.c` | Changed host compilation/self-tests and `qa/native-window-feedback.py` with the relevant reviewed campaign |
| Always-on-top / MAX, UX-016 | `src/MenuBridge.elm`, `src/Provider.elm`, `src/Effects.elm`, `src/GeometryProjection.elm`, `src/Surface.elm`, `native/geometry-effects.inc`, `native/core/ConfigActions.cpp` | `qa/check-search.py --pin-max`; `qa/check-pin-core.py`; `qa/check-native-authority.py`; native `qa/native-pin-max.py` takes no arguments. The planner does not map this route yet. |
| Snap and workspace transfer | `src/Snap.elm`, `src/Transfer.elm`, `src/Surface.elm`, `native/snap-placement.inc`, `native/transfer-workspace.inc` | Focused `check-snap.py` / `check-transfer-workspace.py`; compiled `check-search.py --snap-chooser` / `--transfer-workspace`; original native observations remain separate |
| Appearance, high contrast and motion | `src/Settings.elm`, `src/Motion.elm`, `src/MotionPreferences.elm`, `assets/appearance.js`, `assets/shell.css`, `adapter/shell_preferences.py`, `native/motion-profile.inc` | Focused settings/motion checks and compiled `--settings`, `--high-contrast`, `--reduced-motion`, `--live-motion` modes; mid-flight/native/AT coverage stays explicit |
| Notifications and system controls | `src/Notifications.elm`, `src/SystemMenu.elm`, their adapter authorities and `src/Surface.elm` | `qa/check-notifications.py`, `qa/check-system-menu.py`; compiled `--notifications` / `--system-menu`; service acceptance is not hardware completion |
| Files and jump lists | `src/Files.elm`, `src/JumpList.elm`, `adapter/explorer.py`, `adapter/jump_list.py` | `qa/check-files.py`, `qa/check-jump-lists.py`; compiled `--files` / `--jump-lists`; preserve installed Files semantics |
| Attention, shortcuts and drag ownership | `src/ActionProjection.elm`, `src/Shortcuts.elm`, `src/PointerOwnership.elm`, handwritten surface adapters | `qa/check-attention.py`, `qa/check-keyboard-shortcuts.py`, `qa/check-pointer-ownership.py`; native recipient/gesture observations remain separate |
| Visual tokens, preview layout, focus and semantics | `assets/shell.css`, `src/PreviewVisual.elm`, `src/SurfaceRenderer.elm`, `src/Surface.elm`, `assets/context.js` | Compiled `--high-contrast`, `--accessibility`, `--ime`, `--preview-states` modes plus the decisive original native case; browser specimens qualify their own scope only |

All abbreviated paths in the table are inside `implementation/warlock/`. Replay
modules and model results establish their stated component properties; they do
not qualify native focus, pixels, AT or IME. Read a runner's arguments before using
it. Execute builds and native campaigns through [protected execution](workflow.md).
Do not infer a current runnable core/plugin pair from filenames or historical paths.

Pin terminology: persistent taskbar application pins (UX-004), running-pin context menus and window Always on top (UX-016) are separate routes. Native Always on top needs observed checked semantics, not an optimistic taskbar preference. Additional rows identify manual check choices; they do not expand `verify-plan`'s implemented coverage.

For an Elm behavior change, follow the existing route: decode the boundary event,
update immutable policy through typed messages, emit its existing effect type,
then project the resulting state into the view. Keep native checks of current
identity, grants and effect receipts at the authority boundary. A view or host
callback must not become a second policy or synthesize a successful native result.
Connect the feature to the runnable integration root; an isolated replay or new
module alone is not delivery.

For error handling, retain the transaction context needed to distinguish Pending,
Refused and Unknown. Show the actual status and available action in the affected
surface. Retry only when the existing policy proves an effect was unsent; reconcile
Unknown through the established read-only path. Cover stale/current identity and
the relevant duplicate, timeout or dismissal case when those transitions change.

For UI changes, read the relevant `DesignLanguage/` contract, including layered
color, glow/shadow/shading, keyboard navigation, contrast and reduced motion. Keep
Omarchy vocabulary/keybindings and applicable AT/IME obligations in the selected
original scenario. A browser catalog is useful visual evidence within its scope.

Finish with an observed behavior and its remaining obligations. `claim` records
source/evidence hashes; `report --markdown` prepares a review note. Neither executes
verification or supplies a missing native observation. Failed evidence remains
available alongside the fix, without another copied application tree.
