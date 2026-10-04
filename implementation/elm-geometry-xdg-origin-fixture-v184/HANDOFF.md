# Controlled XDG origin fixture: CPU held, native qualification pending

Final source native/xdg-origin-client.c SHA fee17bd9680bd2c236a624fddc80acfff25d83f275180e4db22b4fa5f04de626. The exact compiled client is selected by client-build-report.json; verify its selected build report, binary, artifacts, inputs, tools, dependencies and linkedLibraries before launching. This executable has not been connected to a compositor in this packet.

Final protected CPU build: qa/client-build-1791128443207969331/report.json. Actual source-included helper/callback50 and actual CLI25 pass: qa/test-1791128474911399590/report.json. A link wrapper records zero wl_display_connect calls in helper/main-validation tests. Three unsafe compiled sources (lost scale, lost origin, accepted foreign pointer recipient) fail2/7/5 checks respectively. First mutation campaign's Werror failure from an unused parameter is retained at qa/test-1791128172404075843; it is not counted as a killed behavioral control. Earlier compiled snapshots and passing predecessor47/50-check reports remain captured.

Invocation profile examples (execute only through the reviewed serialized native runner):

```
xdg-origin-client --origin-x 0 --origin-y 0 --right-pad 0 --bottom-pad 0 --scale 1
xdg-origin-client --origin-x 16 --origin-y 24 --right-pad 16 --bottom-pad 24 --scale 1
xdg-origin-client --origin-x 16 --origin-y 24 --right-pad 16 --bottom-pad 24 --scale 2
```

Add --validate to check a profile without connection. Default ordinary geometry320x180; --width/--height choose another supported initial geometry32..4096. Raw hints --min-width/--min-height/--max-width/--max-height are0..4096, zero unspecified; the initial and server-configured extents must honor declared limits. Tiny extents under32 cannot preserve distinct landmarks and are explicitly refused; this fixture cannot qualify those profiles. One surface cannot prove negative geometry against negative subsurface bounds; negative origins are unsupported here.

The stdin commands are maximize, unmaximize, sync, inspect and quit, each newline terminated. A complete stdinEOF performs normal local teardown. Barrier events correlate exact requestSequence/requestSerial and command. A processing barrier, queued buffercommit and local normalexit are not configure/pixel/presentation/server-retirement receipts. Keep stdout drained and normal cleanup bounded externally; this fixture does not supply its own journal backpressure deadline. Final EAGAIN flush is not a promise that every destructor reached the server; require independent native empty census, client/process/socket retirement and host cleanup.

The event journal uses JSON lines, monotonic sequence/time and PID. ready reports exact PID-qualified title ELM-XDG-ORIGIN-PROBE-PID and appId elm-xdg-origin-probe. configure reports selected width/height, actual configuredWidth/Height, serial, prior ackedSerial and MAX/fullscreen states; ack-configure follows and records ackedSerial; buffercommit follows with bufferSerial==ackedSerial, geometry[originX,originY,width,height], surfaceSize(logical), bufferSize(physical), scale, inflight/allocatedBytes and landmarks. Requested geometry is not a receipt for the compositor-intersected effective geometry.

Landmarks are four distinct corner colors and an interior ACK-serial color. Each point is wl_surface-local logical coordinates; scale2 paints matching2x2 physical pixel blocks. Interior color encodes the low18 bits of ACK serial, so a runner must verify selected serial colors are unique among tested buffers. Outside geometry is opaque dark gray, edge white; corner landmarks override the edge. Use an unobstructed interior point and all four corners away from layer/menu overlays. Bind screenshots to the exact selected committed ACK buffer; do not trust title or a queued-commit log as presentation evidence.

Pointer enter/motion/button/leave events only journal after wl_pointer.enter identifies the exact owned wl_surface proxy. localFixed preserves native fixed-point coordinates; local reports logical double coordinates. button serial/time/state are actual pointer protocol values. The fixture does not claim a default all-surface input region matches XDG geometry/CSD boundaries: physical probes must establish the actual recipient and local coordinates at painted landmark pixels.

REQUIREMENTS.md and the frozen V175 contract define native MAX/ordinary-restore, scale1/2, decoration/workarea, ACK/adopted-buffer/pixel and physical-parent-input obligations. Use exact native lifetime/incarnation, owning core/plugin/AQ mapped tuple and kernel peer identity. Preserve3s native/5s receipt/6s whole-scenario absolute budgets and all original outcomes. This controlled-client profile is not broad GTK/CSD, viewport or negative-origin acceptance. It changes no native compositor, effect eligibility, formal model or installed desktop.
