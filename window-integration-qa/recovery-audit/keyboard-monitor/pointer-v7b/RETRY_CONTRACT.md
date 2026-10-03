# Pointer trial retry contract before fixture repair

Attempt 1 remains failed and immutable. It passed native one-shot consumption
but incorrectly required fractional values from a compositor IPC that explicitly
floors before returning integers. This is an IPC oracle precision error; it does
not prove official callback rearming or later pointer/reader correctness.

## Actual early motion oracle

The first two real private Wayland pointer motions target integer logical
coordinates (12,12) then (14,14). Before the probe pumps its GLib context, require
exact actual IPC cursor coordinates and pointerPending zero. Only then pump the
official libatspi GDBus callback and require pointerPending one. The device has
no GObject observer and no MouseReviewer; this establishes the official callback
chain before those later consumers connect. Later fractional a{sv}dd, CSD,
popup, actual accessibility and reader item gates remain unchanged.

## Failure cleanup and maintenance

Record the process-list checkpoint immediately before scenario execution. On
failure first close stdin and allow natural paired keyboard EOF releases, then
stop only scenario-created processes. The session Bus, accessibility launcher,
Registry, Foot receiver and compositor remain alive through PrepareUnload.
PrepareUnload false must preserve loaded plugin subscriptions and must never
invoke raw plugin unload. PrepareUnload true permits normal plugin unload before
infrastructure termination. Every remaining owned private process is terminated
only afterward, with exact private runtime/UID/PID-start guards. The report
records the quiescence outcome and unload result rather than hiding an error.
No main plugin load, physical input, original reader change or retry execution
is authorized by this fixture repair. The SO/product bytes stay unchanged.
