# PointerLocator integration contract

This stage precedes native implementation. It does not modify the compositor or
reader. The keyboard bridge currently lacks this interface, so the official
AT-SPI device disables pointer monitoring after its UnknownInterface warning.

The manager exports `org.freedesktop.a11y.PointerLocator` at
`/org/freedesktop/a11y/Manager`, on the existing session bus manager name.
`QueryPointer()` returns `(a{sv}dd)`: application metadata and two relative
logical coordinates. `PointerPositionChanged()` has no arguments and is directed
to the requesting unique owner. The [KWin interface description](https://invent.kde.org/plasma/kwin/-/blob/master/src/org.freedesktop.a11y.Manager.xml)
defines the ABI and one-query/one-motion notification throttle. Local reviewed
schema: `../recovery-audit/keyboard-monitor/sources/kwin-interface.xml`.

## Required behavior

1. Resolve the currently hovered surface/toplevel from current compositor input
   state. Keyboard focus is independent. Obtain a fresh valid mapped identity and
   client/window origin in the same compositor-loop transaction as the pointer.
   Relative coordinates retain fractional and negative values and are independent
   of output scale/rotation after conversion to global logical coordinates.
2. Metadata uses `app-dbus-name` (string) with `toplevel-object-path` (object path)
   when a fresh exact accessibility mapping exists. The protocol also permits
   `pid` (signed int32). Never invent a window object path, reuse an old PID/path
   mapping, or select an inaccessible sibling merely because it has the same PID.
   If no usable identity is available, return
   `org.freedesktop.a11y.UnknownToplevel`. An explicitly recognized desktop surface
   may return empty metadata and desktop-relative coordinates.
3. Validate the actual unique caller's current registration/owner epoch through
   the bridge's existing authorization. Owning a name does not enable monitoring.
   An unauthorized query does not arm a notification. Successful authorized
   replies and authorized UnknownToplevel replies arm one notification, matching
   [Mutter's query handler](https://github.com/GNOME/mutter/blob/main/src/backends/meta-a11y-manager.c).
4. Arm after the method reply has been sent. A later real coordinate change sends
   one directed signal and clears that caller's pending request. Refocus at the
   same position and further motion without another query send nothing. Multiple
   queries coalesce to one pending notification per current owner. One caller's
   request/reply does not rearm another caller.
5. Disconnect/name replacement clears the old owner's pending request. A retiring
   service rejects new queries and emits no pending signals. It cannot reactivate
   through a late query or owner callback. All state is compositor-session scoped.
6. Official libatspi 2.60.6 consumes the returned tuple, then emits pointer-moved
   with an exact accessible toplevel when given bus/path or an application root
   when given only PID. Orca 50.2's PID fallback can choose an active sibling when
   several windows contain the same relative point. PID-only tests cannot prove
   correct multi-window targeting. Exact toplevel mapping or a guarded explicit
   ambiguity failure is required for that gate.

## Native acceptance

Use the next frozen private keyboard bridge, actual official AT-SPI device and
copied GTK/Qt clients. Verify introspection, tuple types, fractional coordinates,
inactive hovered client versus keyboard focus, moved windows, client geometry
offsets, popup/subsurface origin, multiple windows in one process, unknown target,
directed one-shot/coalesced signals, disconnected/replaced owners, retirement,
and owner restart. Observe actual pointer-moved events and reader navigation;
matching pure arithmetic is insufficient. Record all main preservation gates.

Exact installed ABI headers provide `CWLSurface::getSurfaceBoxGlobal()` and
view lookup, but native adapter selection remains unimplemented here. The
Hyprland mouse-move event occurs before pointer-focus updating; a query must not
read a stale hit from inside that callback. Send the notification after the event
or resolve current hit independently when handling the subsequent method call.

The model intentionally covers notification/authority semantics. Actual
compositor hit testing, AT-SPI mapping and pixel-coordinate agreement require
native evidence and are not inferred from its pass.
