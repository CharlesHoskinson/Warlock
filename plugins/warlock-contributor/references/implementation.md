# Find the implementation before adding code

Use this map when selecting source paths for a slice. Inspect the current exports
and call sites; paths identify responsibilities, not permission to edit every row.
The original requirement and OpenSpec determine which behavior belongs in the change.

| Work | Start here | Decisive component evidence |
| --- | --- | --- |
| Shell policy and typed transitions | `implementation/warlock/src/Desktop.elm`; integration ports in `src/Main.elm` | `src/DesktopReplay.elm` and the replay for the affected subsystem |
| Taskbar/popup presentation and feedback | `src/SurfaceRenderer.elm`, `src/Bar.elm`, `src/ActionProjection.elm` | `qa/check-feedback.py`; native presentation/input when required |
| Single-family taskbar primary actions/state labels | `src/Taskbar.elm`, `src/TaskbarShell.elm`, `src/Surface.elm` | `qa/check-search.py --taskbar-primary`; native `qa/native-window-feedback.py --taskbar-primary` for exact receipt, MRU/desktop focus and window pixels; primary keyboard/AT remains separate |
| Catalog search and launch | `src/Catalog.elm`, `src/Launch.elm`, `adapter/catalog_authority.py` | `qa/check-search.py`, `src/CatalogReplay.elm`, `src/LaunchReplay.elm` |
| Persistent pins | `src/Desktop.elm`, `adapter/taskbar_preferences.py`, `adapter/taskbar_projection.py` | `qa/check-pin-storage.py`, `qa/pins.qnt` |
| Task View/workspace navigation | `src/Desktop.elm` and the current native authority | `qa/check-navigation-projection.py`, `qa/task-view.qnt`, `qa/workspace-navigation.qnt` |
| Pending/Refused/Unknown outcomes | `src/Effects.elm`, `src/NativeOutcome.elm`, `adapter/effect_endpoint.py` | Current transaction replay and the native refusal/recovery journey |
| GTK/WebKit surfaces and leases | `native/host.c`, `native/shared-host.c` | Changed host compilation/self-tests and `qa/native-window-feedback.py` with the relevant reviewed campaign |

All abbreviated paths in the table are inside `implementation/warlock/`. Replay
modules and model results establish their stated component properties; they do
not qualify native focus, pixels, AT or IME. Read a runner's arguments before using
it. Execute builds and native campaigns through [protected execution](workflow.md).
Do not infer a current runnable core/plugin pair from filenames or historical paths.

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
