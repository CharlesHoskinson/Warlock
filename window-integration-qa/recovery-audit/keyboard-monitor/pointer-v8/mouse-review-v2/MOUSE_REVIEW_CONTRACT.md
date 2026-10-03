# Omarchy Orca compat: mouse-review lifecycle

This contract precedes a private source patch to the actual Orca 50.2
`MouseReviewer`. It does not describe unchanged official Orca behavior. The
Atspi device and PointerLocator backend remain the installed public library.
The original signed prefix and accepted v6a dependencies remain immutable.

## Required semantics

1. Mouse review defaults to disabled. `get_is_enabled()` is the explicit
   settings request; temporary backend loss must not erase that request.
   Explicit true/false requests remain mutable while incapable. Returning a
   backend must honor a disable requested during an outage.
2. An enabled, capable AT-SPI reviewer has exactly one handler on its current
   actual device and reports itself active. Repeated activation is idempotent.
3. Disabling disconnects the handler, clears queued work and the old current
   item, and makes `get_current_item()` return None. Toggle alternates the
   requested intent, including while capability is unavailable. A temporarily
   inactive reviewer with a true request must accept an explicit false request.
   Active implies both the requested setting and real backend capability.
4. The new public `refresh_device(device)` operates on this same reviewer
   object, preserving existing command references. It snapshots the public
   enabled request; deactivates/disconnects/invalidates old work; selects the
   supplied actual device; negotiates POINTER_MONITOR through its public API;
   and activates only if the saved request and new capability permit it.
   None or a device without pointer capability leaves the reviewer inactive
   while preserving the request for a later capable replacement.
5. The class owns its fields internally. Reconnect adapters must not assign
   private reader fields, replace the singleton, or replace command handlers.
6. Retired device signals and queued timeout callbacks cannot append work,
   consume a replacement device's queue, or restore a retired current item.
   A class-owned epoch invalidates old timeouts; actual sender identity and
   active state reject retired-device signals.
7. Capability negotiation must use the same fresh device. Manager registration
   release/reclaim is a separate, quiescent public-API protocol operation:
   factory claims the name first, then release, set capabilities, reclaim,
   Watch and replay explicitly requested policies. No held-key state may be
   dropped to make the probe succeed. Until this separate gate is proved,
   the patch does not claim end-to-end restart recovery.

## Evidence boundaries

The model covers the lifecycle, not actual AX hit testing, library signals or
native pointer input. Source-extracted method tests exercise the patched
methods with controlled collaborators; they are not native reader evidence.
Required later native gates: false/true/toggle, actual official pointer-moved,
current-item None to actual accessible, device/service restart while enabled,
no retired events, preserved command configuration, and all main-session
preservation checks. No main reader enable/load/autostart is authorized here.

## Primary source defect

Original `mouse_review.py` activates the AT-SPI handler at lines 526–527 but
sets `_active = True` only in the Wnck branch at line 550. Its public disable,
toggle and current-item methods rely on `_active`. The minimal patch corrects
that branch and adds the public refresh lifecycle without changing the
navigation algorithm, bindings or Atspi implementation.

## Retained first-candidate counterexample

The immutable v1 candidate incorrectly kept the official capability early return
and active-state shortcut: enable → refresh(None) → set_is_enabled(False) left
the request true and backend return reenabled. Root retained the actual source
reproduction in `window-integration-qa/mouse-review-disable-loss-counterexample.json`.
This fresh v2 changes the contract/model before implementation to accept explicit
intent regardless of backend state. Toggle follows that intent, not active state.
