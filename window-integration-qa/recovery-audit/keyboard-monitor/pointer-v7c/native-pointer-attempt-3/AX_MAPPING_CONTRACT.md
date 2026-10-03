# Guarded actual accessibility mapping

No GTK window identity protocol is available in this installed Hyprland ABI.
The v7 resolver must therefore prove a unique correspondence at query time.
It must never guess a title, choose the active sibling, fabricate an AX path,
or return PID-only metadata for an ambiguous application.

Required before a successful PointerLocator reply:

- The fresh hover target is a mapped, visible native client surface. The same
  actual native window object/PID/process-start identity remains under the
  pointer when the asynchronous resolver completes.
- Exactly one mapped native toplevel has that PID. Multiple windows are an
  explicit UnknownToplevel boundary, even if only one exports accessibility.
- The actual private accessibility Registry.GetChildren supplies the AX peer.
  Its unique bus owner is checked by that bus daemon's GetConnectionUnixProcessID
  and equals the native PID. Exactly one matching application reference exists.
- Accessible.GetChildren on that real application yields exactly one toplevel
  reference belonging to the verified unique application bus owner. Its real
  GetRole is FRAME, DIALOG or WINDOW. Empty/multiple/foreign/malformed objects
  are UnknownToplevel. The application reference's own root path is not reused
  as a fabricated window path.
- All replies use finite logical pointer-minus-client-origin double coordinates,
  rechecked after lookup. Final replies require the caller's same authorized
  registration epoch and a nonretired service. Async operations have bounded
  counts/deadlines and safe cancellation on retirement/disconnect/unload.
  Completed accessibility replies wait while a bounded session dispatch tick
  still has queued control messages, so pending owner changes are processed
  before an asynchronous result is finalized. Session-bus loss retires pending
  pointer work and notifications.

Metadata contains the actual verified `app-dbus-name` string and actual
`toplevel-object-path` object path. PID alone is never a success fallback here.
This strict singleton policy provides a useful exact mapping and an explicit
same-PID multiwindow refusal. It does not claim general multiwindow support.

For authorized UnknownToplevel the service still sends the truthful error and
arms the reviewed one-query/one-later-motion state only after reply delivery.
Unauthorized/retired calls are never armed. Actual app bus disappearance,
hover/window/process change and stale epochs must not return prior metadata.
