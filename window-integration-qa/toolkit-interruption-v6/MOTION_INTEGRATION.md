# Gesture retirement before minimize source capture

Required contract: the motion transaction retires any matching captured family gesture **before** it reads geometry for source capture or allocates visual actors. The destination is current valid geometry and current per-member pin state. Native retirement is not a physical button release. No main or service V11/V12 integration has been applied here.

Fresh candidate Lua API:

`local ok, retired = hl.plugin.hyprbars.retire_gesture_current(address, stableIdHex)`

Both arguments are exact lowercase strings from `window_families`: address `0x…`, stable ID hex without prefix. Current mapped, non-hidden native window must match both. A stale, absent, hidden or malformed request returns `false,false`. A valid current window with no matching active or pending caption gesture returns `true,false` without ending another target. A matching unstarted caption intent is cleared with its swallowed genuine release still reserved. A matching captured weak native target/window/stable ID is ended once through the real core controller, returning success only if that controller target cleared; `retired` also reports a matching pending caption intent. Requery identities and geometry after retirement. Failure must abort before capture; do not retry by address/PID, infer a release, or continue using pre-retirement cached geometry.

Call for each freshly queried family member before final capture/snapshot; the active target might be a nested child rather than requested root. Actual family authority still comes from the motion transaction's existing exact relation/identity checks. The API does not infer a family from PID and does not reserve a future native lifetime.

For move, native emits separate synchronous `hyprbars.drag_retire_current(window)` event. The staged `installed-snap.lua` subscribes and clears matching drag source/normal/shake/Snap Bar staging without calling snap, restoring press geometry or modifying pin state. Core resize skips rollback only during this explicit retirement. Escape/config reload/normal unload use rollback. Existing `drag_finish(window,released)` signature and release semantics remain unchanged.

Required packaging pair: the new native candidate and updated snap Lua must ship together in the private campaign; source closure includes both. Configuration rebind registers the new event alongside existing start/finish. Motion should probe this API as a required capability for interrupted transactions, rather than silently falling back to old cancellation. Public API ACK is not feature acceptance: actual held button→retire→fresh geometry snapshot→native minimize/actual preview/restore→real release→fresh public input gates are still mandatory.

Review concern: core dragEnd performs its existing focus/group checks before return. No synthetic focus or custom group suppression is staged here; an actual private grouped-window interruption test remains needed before claiming broader grouping parity. Full plugin unload also removes listeners; fresh input/release callback refusal must be observed, not inferred from target absence.
