# Toolkit gesture interruption and family consistency

This follow-on closes specific evidence gaps, not the accepted Qt19/GTK13 baseline again. It is confined to owned private Weston/Hyprland sessions, core1 QA scope, source-frozen native candidate, captured main read-only preservation and clients-first cleanup. No main actions or native launches are currently authorized.

## Existing evidence and missing cases

The accepted QtV9 Wayland and X11V2 campaigns prove public same-QApplication WindowModal owner/child/nested/independent-peer callbacks, caption refusal and family minimize/restore. Their19 gates contain no active caption drag, border resize, held-button Escape or plugin reload. Earlier GTK modal probes create the independent peer in a separate process. Generic caption14 and410 replay states prove native behavior primarily through different fixture clients; they do not establish GTK4/QtWidgets lifecycle consistency for these exact combinations. Requirements entries drag/resize, window identity, pin/minimize, previews and recovery supply this contract.

## New private matrix

Run serial explicit QtWidgets-Wayland, QtWidgets-owned-authenticated-X11, GTK4-Wayland and GTK4-owned-authenticated-X11 variants after review. Each application creates an owner, child, nested dialog and independent peer in one process using public native transient/modal APIs. X11 enabled only explicit X11 variants; exact owned server/display/authority and actual platform/module mapping required. No main DISPLAY fallback. Pin snapshots compare every member separately, and peer identity/geometry/workspace/pin/callbacks remain independent.

Use exact address/stableID/PID/start/native parent relationships. Capture public button client geometry, native surface extent, real callbacks, native float pointer readiness and read-only core/plugin input state. Never replace hit tests, focus, identity, target coordinates or native gesture methods in the observer. Every passed action must be supported by actual private virtual-pointer/button/key events and native/public results; command ACKs are counted separately. This does not prove physical hardware input.

## New scenarios

1. GTK4 same-process peer remains actionable during its sibling modal chain. This supplements the separate-process GTK evidence.
2. Deepest modal caption moves and border/corner resizes its exact identity, including crossing a same-process peer and a private focus change while held. No other member/peer changes geometry or pin. A blocked ancestor caption must route to deepest without starting a drag; this is only a precondition, not another baseline callback campaign.
3. Escape before movement and after movement retires the gesture, restores its press rectangle, clears snap staging, and preserves per-member pin state. The real button remains held until release; no second press gains authority. Release, then real peer click and a fresh gesture, must work.
4. Reload the exact private native candidate during a held move/resize. Retire the old gesture/callback generation and restore its captured press geometry. No old release or delayed motion can mutate geometry. Keep the same application/window identities and pins; public buttons and a fresh gesture must work after release. No main plugin reload.
5. Minimize the captured family during a held gesture. Preserve the latest valid native geometry and per-member pins as the destination, cancel capture/snap staging, retain actual taskbar identity/preview, then release. Restore the same current family and deepest surviving modal focus; the independent peer stays unchanged. Do not reinterpret this as smooth-motion or cadence proof.
6. Close the captured dialog while held, verify its actual native lifetime is absent, create a new public dialog, then deliver old motion/release/retained identity action. New stableID must differ and no stale action may mutate/focus the new identity. After release, new public callbacks and gestures must work. There is no address/PID-only match.
7. Capture mixed member pin flags through native read-only state; minimize/restore must preserve that exact map. Explicit family Pin is a separate user command and can normalize pins, but interruption cannot roll back a newer pin choice. Scope is native pin retention, not app launcher pinning.

## Model and proof limits

The model tracks individual native-lifetime epochs, capture generation, physical held state, move/resize geometry, modal target, per-member pin snapshots and minimized preview authority. Adversarial current/stale events are generated directly, including blocked ancestors and reused lifetimes; the generator does not filter invalid actions out. Abstract models are requirement proofs, not native acceptance. Toolkit/protocol differences must be established by actual mapped modules and public observations.

Retain any counterexample and create a fresh product revision only if actual input/source evidence proves a product gap. Current production, candidate and all accepted packets remain unchanged. Native runner freeze must include platform/loader/source closure, actual matrix command, no portal helpers, complete owned IPC, normal client shutdown, unload-before-compositor, exact server/runtime cleanup, all main preservation and before/after executed hashes. Any capture/grab remaining after release, wrong identity mutation, pin/focus mismatch, stale action, missing actual preview, helper activation or forced cleanup is a failure.

## Source-confirmed cancellation drop and focus authority

The exact installed core `CDragStateController::dragEnd` calls another window's decoration `INPUT_TYPE_DRAG_END` and then `CGroup::add(draggedWindow)` on any move end, including Escape/config reload/minimize retirement; no release reason is passed. It subsequently calls fullWindowFocus on the dragged window. These are concrete missing cancellation guards. A nonrelease end must not invoke a drop callback, mutate group membership or overwrite a newer independent user focus. Genuine release retains existing drop and core focus semantics. Minimize's subsequent explicit policy focus remains a separate action.

Stage only a synchronous cancellation context for the captured exact weak target/window/stable ID, while delegating real core dragEnd for cursor, target, resizing and geometry cleanup. Narrow hooks may suppress only decoration drag-end/drop for that captured window and its group add. Full focus suppression is limited to DESKTOP_STATE_CHANGE for that exact captured owner when another current focus is selected. Other reasons, unrelated windows, native releases and all modal target selection delegate unchanged. No global group setting, private controller field edit, fake release or synthetic corrective focus.

Formal invariants cover nonrelease group preservation and Escape/reload focus preservation; true release can group. The retained mutation witness enables the missing cancellation drop and must fail. Actual grouped-window cancellation and genuine-release positive controls remain mandatory. This revision is not deployment approval.
