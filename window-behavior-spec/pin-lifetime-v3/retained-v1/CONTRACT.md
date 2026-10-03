# Window pin lifetime and command ordering

This fresh stage preserves installed pin.lua, hypr-pin-toggle, windowctl and the
frozen V22 native candidate. It is not a deployment or a native acceptance.

## Confirmed source gaps

Installed titlebar commands substitute only %WINDOW_ADDRESS% and execute
asynchronously. Installed pin.lua resolves that address later, and timers and
reload cleanup write opacity by address without a lifetime check. An address
can identify a different window after closure. This source gap does not establish
the cause of the user's particular failed click.

The existing V22 candidate already exposes public native window lifetime
through hl.plugin.hyprbars.window_lifetime(w): address, stableID and PID. Its
native titlebar retains a weak owning window. Config::Actions provides explicit
owning-window floatWindow, pinWindow and alterZOrder actions. Core pinWindow
requires a floating window and rejects fullscreen modes; maximized pin parity
therefore needs separate work and must not be claimed from the floating fix.

## Required behavior

1. A titlebar pin click changes the captured owning window synchronously before
   a subsequent minimize can capture its pin state. A focus change cannot
   redirect the operation. Two real clicks toggle twice.
2. External delayed commands require the captured address, stableID, PID and
   current compositor session. Missing identity is never repaired by selecting
   the active window. Closed/reused/replaced identities receive no write.
3. Only the requested member's pin changes. Other independently pinned family
   members retain their state; the existing deepest modal focus policy remains.
4. Float/pin backend errors remain visible refusals. Unsupported fullscreen or
   maximized states do not silently report successful pinning or destroy saved
   geometry. Their full parity remains open until an actual supported policy is
   implemented and checked.
5. Each fade binds to the same actual native window lifetime and current fade
   generation. An older callback cannot override a newer effect. Closure,
   minimize, reload and reduced motion retire the effect; cleanup writes only
   to that same live eligible window. Timers for other windows are independent.
6. A pin followed by minimize and restore retains the last pin intent through
   an identity-proven minimize record. Older two-field records provide no
   lifetime proof. Migration must preserve actual user state and be audited
   separately; this model does not invent historical ownership of those records.
7. No scratchpad move is part of pinning. Pinning must not send applications to
   a hidden workspace or change an unrelated draft/focus/input state.

## Acceptance and limits

The formal model below addresses owner identity, stale commands/effects,
independent family pin bits, and ordering with identity-proven minimize state.
Implement the native synchronous action and lifetime-bound feedback only after
the model passes. Then check the actual staged native implementation against
the model and run real titlebar/keyboard/taskbar actions across existing and new
windows in the private compositor. Preserve existing drag/family/oracle sources.
Main deployment, maximized pinning, legacy record migration and full Windows
parity remain unaccepted until their own concrete implementation and QA.
