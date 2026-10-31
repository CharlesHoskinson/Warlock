# Desktop integration contract

`host/index.js` exports `createHost({frames, onSnapshot, onDiagnostic})`. It returns `registerService(kind, handler)`, `registerPreview(provider)`, `start()`, `reset(seed)`, `getSnapshot()`, `subscribe(listener)`, `invoke(entryIntent)`, `dispatchInput(input)`, `setFault(policy)` and `destroy()`.

For a titlebar window menu, `invoke('window-menu', {windowId, incarnation, trigger, anchor})` captures the focused, visible window and a viewport-coordinate anchor. `trigger` is `pointer` or `keyboard`; `anchor` contains finite `x` and `y` coordinates. The host checks the captured identity again while preparing the menu and retains the anchor through the picker. An omitted context uses the focused window and the default anchor.

`stage/index.js` exports `mountStage({root, host})`, returning `render(snapshot)`, `getAnchors()` and `destroy()`. The stage does not mutate the world directly.

`input/index.js` exports `installInput({host, stage, frames, legendRoot})`, returning a disposer. `previews/index.js` exports `createPreviewProvider(context)`. `services/index.js` exports `registerServices(host)`. `scenarios/index.js` exports `loadScenario(id, host)`, returning a readiness promise. `tour/index.js` exports `mountTour({host, stage, root})`, returning start, stop and destroy.

The host owns the external world. Snapshots are immutable presentation data; decimal identifier strings retain UInt64 precision. A service handler receives `readWorld`, `transact`, `reply`, `publishObservation`, a clock and an epoch cancellation signal. Receipts and observations are separate; a receipt is not proof of a state change. Reset retires the epoch and cancels outstanding work. Unknown outcomes do not retry mutations.

Frame messages use `{bridgeVersion, epoch, frameId, kind, payload}`. The host verifies origin, source, registered frame ID, kind and epoch. Controller commit strings are preserved verbatim. The WebKit shim runs before each native adapter. Each renderer has its own document and global scope.

The snapshot's `appearance` holds committed Settings values (`theme`, `textScale`, `effectsOff`, and `reducedTransparency`). `motion.applied` is the acknowledged `full` or `reduced` profile, and is absent while application is unacknowledged. Service contexts include the current fault policy as `fault`; `signal` retires all work from an old epoch.

Compositor input uses `dispatchInput({kind:'popup-dismiss', epoch, scope, lease})` for an outside press. It only dismisses the current open scope and lease. After a pointer `start`, the compositor can commit an edge placement with `dispatchInput({kind:'placement', epoch, windowId, incarnation, placementMode, geometry})`; placement mode is `snapped` or `maximized`, and geometry is an in-work-area rectangle. T08 also sends `outside-press` with the current `publication` and `lease`, and sends placement with `zone` after canceling the drag; those inputs are accepted with the same identity checks. A stale epoch, changed incarnation, minimized window, or invalid geometry is rejected. Pointer cancellation restores the pre-drag geometry and mode.

Compositor window focus, close, minimize and pointer inputs carry the captured `epoch`, `windowId` and `incarnation`. Every pointer event also carries the same `pointerId`, `mode` and starting coordinates as its start; reset retires the gesture. Dragging a maximized or snapped window restores its saved ordinary geometry and clears its maximized and restore state. Cancellation restores the complete pre-drag placement.
