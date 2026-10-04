# XDG pointer alignment: native campaign requirements

This is a source-only plan. No native runner, desktop change, policy change or
model function is introduced. It does not qualify physical hardware or GTK.

## Selected scope and prerequisites

P01. Qualify zero-window-geometry-origin controlled197 client, buffer scales1/2,
monitor scale1 separately, through ordinary, MAX and ordinary restore. Use the
current435 core89/plugin409/AQ155 mapped tuple and its owning private parent,
not the earlier AQ105 host. Require full immutable upstream manifests, actual
mapped libraries/module and the final screenshot runner's held bytes before
assembling executable QA. Original212 native failure1791133183538677576 is
retained: zero1 ordinary/MAX/restore45 pixel samples passed; nonzero1 ordinary
corners failed despite matching center serial. Zero2 remains independently open
until217 provides actual evidence. Full four-profile pixel acceptance stays false.

P02. Choose V82 private Weston fake-seat protocol, injected through actual exported
notify_motion_absolute/notify_button APIs, whose owning module/report435 already
pins. It exercises parent Wayland pointer → AQ155 → child compositor → owned197
wl_pointer callbacks. This is synthetic native seat input, not a physical device.
V436 child virtual-pointer route is a different, narrower path and cannot replace
this route without a separate explicitly named result. Parent admission alone
is not target delivery, geometry alignment or pixel proof.

## Ownership, coordinates and journal

P03. Before every gesture bind owned Weston PID/start, SO_PEERCRED PID/UID, socket
inode/path identity, module hash and exact fake-seat parent launch. Bind target
PID/start/incarnation/native address and live wl_surface-owned journal identity.
Retain the actual parent request and receipts. Verify the focused parent client
is the owned nested compositor. Refused, duplicate, malformed or extra receipts
fail; never automatically repeat a gesture.

P04. Establish observed current child monitor origin/logical size/scale and parent
fullscreen surface destination/offset before interpreting parent global points.
AQ155 emitWarp normalizes parent surface-local coordinates by its current
surfaceSize. Parent coordinates must be derived from observed parent surface
placement and destination, not assumed equal to child global coordinates.
Initial supported setup requires exact identity geometry800×600, monitor scale1,
parent destination800×600 and verified parent surface origin0,0. If these facts
cannot be evidenced, stop with an unqualified mapping; do not calibrate from
an expected recipient callback. No fractional parent-global rounding policy is
introduced. Buffer scale1/2 changes SHM density only, never logical pointer units.

P05. Before each injected pair, establish a full197 journal boundary through held194
parser and an actual sync barrier. Inspect ALL pointer-button records after that
owned boundary, for every button and serial, not a preselected matching pair.
Require exactly one272 press and one272 release, ordered, with no other button
records in the interval. Pass that entire interval to held213.validate_pair.
Require exact owned PID, increasing sequences and expected logical surface-local
coordinates on the1/256 lattice, consistent localFixed values, ownedSurface=true
and canonical serial/time fields. Preserve pointer-enter/motion/leave records
and raw full journal for independent review. A two-record subset that conceals
extra presses/releases cannot pass. Source callbacks plus journal decoder do not
prove hardware origin or that another process received no input.

P06. Test center and four actual landmark interior points in separate gestures for
each stage. Derive each global point from admitted native real rectangle and
pixel-proven landmark position; expected local = global−native real position
for qualified zero-origin setup. Require complete colored3×3 landmark proof,
selected configure/ACK/commit serial and distinct palette history through210.
Reject clipping, popup/layer occlusion, aliasing, invalid serial histories and
unexpected coordinate conversion. Do not infer target coordinates from CLI
preferred size or XDG proposal. Ordinary restore must match captured actual
ordinary placement/configure geometry.

## Deadline and postinterval coherence

P07. Each stage uses one original absolute6s deadline encompassing transition,
receipt, settle, pre-input facts/ACK/pixels, all five gestures, delivery, final
sync/commit/facts/output/pixel readbacks and decode. Native transport retains
its original3s bound, clipped to remaining stage time. No fresh deadline per
click, capture, helper receipt or final read. If five gestures cannot fit, retain
failure and redesign stages explicitly before a fresh campaign; do not silently
extend this requirement. V82 InteractiveClient._wait currently starts a new6s
and cannot be used unchanged. Prefer the actual bounded one-shot V82 client
motion/press/release/quit invocation pattern in77, with min(3,remaining) timeout
and postreturn deadline gate, plus fresh peer checks. Any new persistent wrapper
must accept the same absolute deadline for write/receipt/cleanup.

P08. After each pair and after final screenshot, require same owned target,
incarnation, output/workarea/scale, placement/mode, geometry extent/origin,
selected configure/ACK/buffer serial and buffer scale/generation. Require fresh
facts and sync results beyond the boundary, not stale cached snapshots. A focus
change caused by the admitted click may be legitimate: record before/after
focus/revisions and use fresh exact context for subsequent effects, without
relaxing native dependency guards. Unexpected geometry/commit/presentation
changes invalidate that pair's coherent alignment claim. Capture final raw
facts, monitor/native readbacks and image bytes before deadline.

## Diagnostics, cleanup and release gates

P09. Nonzero-origin pointer comparison is diagnostic only, after separate actual
landmark rendering aligns or with the existing pixel counterexample preserved.
Compare actual observed visible pixels and actual local callbacks; no guessed
origin transform or capability enablement. A matching pointer-local hypothesis
cannot erase incorrect rendering or qualify MAX/restore support.

P10. Failure cleanup attempts release of any actually held button and normal owned
helper/client shutdown without treating cleanup-generated releases as successful
probe events. Retain all extra journal events. Preserve bounded normal quit,
server empty-client census, plugin unload ordering, mapped tuple and runtime
retirement. Parent release_all on helper resource destruction is a fallback,
not evidence that the explicit intended release reached197. Root alone launches
through the serial native lock. Full pointer/native/GTK acceptance remains false
until the owned campaign reports all stated stages, pixels and recipients.
