# Exact observer call proposal

Draft only. No compiler, linker, compositor, plugin loader, GUI client or native input was invoked. No product source changes. This packet requests review of these two new source files before any build/load. Other B controller/presentation/two-output drafts are outside this packet and outside this authorization.

## Pure owning metadata entry

`pin_campaign_b.observe(address, stableId, pid)` requires exactly three Lua arguments: canonical nonzero pointer string, canonical hexadecimal stable ID string, positive integer PID. Embedded NULs, alternate types and extra arguments refuse. It selects exactly one current mapped public window both before and after the synchronous read.

| Reads | Exact owning source | Meaning |
| --- | --- | --- |
| WindowState.windows, window.getPID/validMapped/layoutTarget | desktop/state/WindowState.cpp; desktop/view/Window.hpp/.cpp | Current selected public window; shared window remains strongly retained. |
| target.space; space.algorithm/workspace; window native target/group/output | layout/target/Target.cpp; layout/space/Space.cpp; desktop/view/Window.hpp | Strong retained layout target, native target, space, algorithm, workspace, shared group and shared monitor; scope rechecked. |
| controller.getFsHandler; borrowed handler.getFullscreenModes(nativeTarget) | managers/fullscreen/FullscreenController.cpp:510; handler/FullscreenHandler.cpp:76; scrolling/ScrollingFullscreenHandler.cpp:102 | Actual raw owning handler map. Does NOT call controller.getFullscreenModes(window), whose error correction can call syncFullscreenTargets. Handler selection uses layoutManagedFS/getFullscreenHandlerName and raw handler query methods. |
| Pin.state.snapshot/ownedUnpinReady/transferOutcome | desktop/state/pin/NativePinState.cpp | Exact existing public projection and optional recorded terminal transfer. No capture/restore/rebind/retire/refresh/invalidate/begin/finish calls. |
| geometrySnapshot, floating | layout/target/Target.cpp; WindowTarget/WindowGroupTarget | Current stored logical/visual box and owning target floating state. |
| mapped/hidden/acceptsInput/noFocus/priorityFocus/pinned | desktop/view/Window.hpp/.cpp; helpers/AsyncDialogBox.cpp; window-rule getters | Existing public current flags; priorityFocus reads registered priority dialog state. |
| group.windows | desktop/view/Group.cpp | Complete current shared-owned group references, at most64, each current mapped; never invent child independent intent. |
| scrolling.dataFor(nativeTarget,true) | layout/algorithm/tiled/scrolling/ScrollingAlgorithm.cpp:1907 | Step into actual group members via their native m_target; the returned row's layout target must equal the selected current layout target. |
| column/scroller shared references, public columns/targetDatas/layoutBox | ScrollingAlgorithm.hpp | Only shared-owned weak references are locked. The unique tiled algorithm/unique tape controller are borrowed under their strong shared owning algorithm/data. No lock of a unique handler/algorithm. |
| getColumnWidth/getTargetSize; const controller.getStrip/getOffset/getDirection/stripCount | ScrollingAlgorithm.cpp:41/71; ScrollTapeController.cpp | Actual column/row fractions and actual controller offset/direction. Complete controller-to-column and controller-to-row mapping is checked first so fallback default getters cannot masquerade as current measurements. Limits64 columns/256 rows. Floating or non-scrolling target yields explicit null, never a fake empty scroll proof. |
| InputManager.getMouseCoordsInternal; FocusState.window | input/InputManager.cpp; desktop/state/FocusState.cpp | Current cursor and core focus only. Distinct actual Seat focus remains the unchanged existing probe's responsibility. |

No requestFullscreen/setFullscreenMode/syncFullscreenTargets, target geometry setter, layout mutation, focus setter, dispatch, input cancellation, event listener or window lifetime hook is called by the pure metadata entry. Plugin setup registers only the two Lua query functions. API ABI and exact core policy identity guard initialization and each query. Runtime ownership/cgroup/core-limit guard is inherited in meaning from the old QA probe. Full actual mapped-module/binary/dependency binding is still an outer collector prerequisite, not proved by the policy string.

## Separately labelled fixed native query stimulus

`pin_campaign_b.query_hit(address, stableId, pid, maskId, ignoreSelected)` adds exactly one integer0..4 and one Lua boolean. It first retains pure owning metadata, then invokes the exact existing `viewState.hitTest().windowAt(actualCursor, fixedMask, selectedOrNull)`, then retains pure metadata again. It adds no setters or hooks.

| maskId | actual uint16 mask | Scope |
| --- | --- | --- |
| 0 | 19 | RESERVED_EXTENTS + INPUT_EXTENTS + ALLOW_FLOATING |
| 1 | 27 | same + FLOATING_ONLY |
| 2 | 147 | same + FOCUS_PRIORITY |
| 3 | 83 | same + SKIP_FULLSCREEN_PRIORITY |
| 4 | 3 | RESERVED_EXTENTS + INPUT_EXTENTS, floating disallowed |

**This entry is a native query stimulus, not a blanket pure/noNativeWrites claim.** Exact unchanged ViewHitTester.windowAt calls FullscreenController.hasFullscreen/getFullscreenWindow; those functions contain inherited error-correction syncFullscreenTargets branches. The old probe also uses windowAt and is preserved byte exact. No bus event absence proves that correction did not happen. Any changed selected owning metadata or unknown/incomplete read refuses, while raw complete before/post observations remain in the refusal envelope. A correction to an unrelated object is not ruled out by selected before/post equality; a future case needs independent peer/full-scope guards. The stimulus must never be executed under a claim that stale/inconsistent state was proven read-only. There is no new core accessor or correction suppression in this proposal.

## No historical/private restoration claim

The public native projection's pointer fields are generated from CURRENT owning target/space after finding an exact stored record. They do not expose historical private record pointers. Public scrolling rows/width/offset are actual current state; the private fullscreen handler's nativeRestore rows/camera are not exposed. Transfer outcomes are optional previously recorded outcomes, not an exhaustive call log. Null transfer means no outcome observed; B24 remains pending until a genuine native partial-failure trigger is established. Ordinary workspace dispatch explicitly unsets/restores fullscreen modes and cannot prove direct owning no-mode-cycle transfer. No event hooks or presentation proof are added here.
