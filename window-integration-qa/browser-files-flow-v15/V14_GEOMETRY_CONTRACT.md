# Exact Browser viewport to private compositor coordinate witness

Formal/source checkpoint first. Frozen V13's failure is retained. Its 105 stable
samples show outer/native client dimensions930×700 and inner890×563 at ratio1;
they establish a width/height difference, not where browser chrome lies.
Wayland DOM screenX/screenY[0,0] provide no global placement authority. The old
zero horizontal inset and bottom-aligned content assumptions are unproved.

The proposed new witness observes genuine serial pointer motion without any
button or keyboard action, after all original sandbox/closure/data confirmations.
This calibration is explicit native input in the root-owned run; import, model,
source review and preflight do not perform it. It provides no application click,
focus, draft, caret or Files callback outcome by itself.

Before each move, capture the exact owned Browser PID/start/address/stableId,
exact CDP target/session/local frozen URL, current native surface box, DOM
outer/inner/textarea rect/device ratio and visual viewport state, bounded event
sequence, draft/caret/active element and native focus/grab/held state. Require
one untransformed logical output and ratio1, visual viewport scale1/offset0,
zero document scroll, positive finite client dimensions and a contained finite
positive textarea rect. A stable surface/DOM pair must occur twice. No invented
offset is permitted from dimension differences or screenX/screenY.

Select two bounded distinct points inside the currently observed Browser
surface, separated in both axes. They are candidate motion locations only:
being inside that surface does not prove that either hits web content. If no
new trusted web pointer event arrives, refuse without pressing. Move serially
using the original private virtual pointer. Retain actual float cursor snapshots
and exact native Browser hit-owner. Require no button/grab/capture and unchanged
native focus, exact app lifetime, draft/caret/DOM active element and layout.
The frozen local fixture records bounded read-only pointermove evidence;
CDP retains only its fixed allowlisted query, never dispatches input or writes.

Bind each move to newly sequenced trusted primary mouse pointermove events with
buttons0, no modifiers and finite CSS client coordinates. Retain every observed
event's actual browser timeStamp and performance.now handling timestamp; require
both no earlier than the browser performance.now sampled immediately before
the selected move. This refuses an older queued event by its original timestamp.
The same known private fixture, page lifetime, performance.timeOrigin and
monotonic clock basis are
mandatory; a timestamp mismatch refuses rather than rebases a clock.
event, native cursor and layout snapshot before validation. Require the native
cursor stable before/after the DOM event observation, one distinct final event
coordinate for that move, and exact translation equality between both moves.
The translation uses observed native coordinates in their surface-local
Wayland24.8 representation minus observed CSS client coordinates; screen
coordinates and requested motion acknowledgement are not authority. Frozen
Hyprland input source derives local position from native cursor minus exact
surface-box origin. Its v0.56.2 Seat source sends wl_fixed_from_double(local);
the installed wayland-util.h implements round(local*256), half away from zero.
Require both local axes at least1px inside the surface, avoiding the separate
Seat right/bottom edge adjustment. Calculate that same bounded binary64
subtraction and multiplication, then exact half-away integer rounding of that
observed double and divide by256. Add the exact surface origin to obtain the
wire-representable global basis. The observed CSS/native translation must agree
exactly across both moves after this named conversion. Different conversion,
clipping, zoom/scroll/scale or a missing final event refuses. The conversion is
representation at the actual protocol boundary, never a fitted tolerance or
inferred browser inset. Primary Chromium reference remains current upstream,
with requested installed revision retrieval failures retained; no installed
Chromium equivalence claim is needed to require the actual matching witness.
There is no arbitrary epsilon, guessed40/137px inset or readiness bypass.

The derived viewport box must be fully inside the exact native surface and its
size equal the DOM inner dimensions. Define all four nonnegative chrome insets
from this box and the surface. They are observed results, not fixed constants.
Two matching before/after surface/layout keys and unchanged exact lifetime,
session, output and coordinate basis bind the witness. Changes, missing events,
untrusted/synthetic events, old sequence, mixed targets, zero movement, wrong
translation, ratio/scroll/viewport changes, nonfinite/out-of-bounds rectangles,
capture, focus or draft/caret changes invalidate authority.

Only then map a DOM textarea interior point using the witnessed translation.
The inherited virtual-pointer command parser accepts integer move coordinates.
Choose an exact integer point strictly inside the translated textarea interior,
and verify containment; never send its fractional DOM rectangle as a textual
move coordinate. Original Files points also require explicit integer syntax and
actual intended-button containment before any button input.
Every actual move must be generated from exactly two Python integer values
(booleans excluded), within the1600×1000 private output. Serialize the whole
fixed grammar `move DIGITS DIGITS\n`; missing/extra/fractional/nonfinite/signed
or out-of-range tokens are refused before writing. Point selection takes exact
binary64-observed rectangle values as rational numbers and floors its exact
center, then proves strict integer containment within the requested interior
margin. The margin selects an interior region; it is no coordinate tolerance.
Recheck the exact layout/lifetime/session/native hit and input state before the
original genuine press+release. The existing actual textarea-focus observation,
trusted draft typing/interior caret, exposed real Files callbacks/raise, retained
draft/caret on refocus, private reload/continuation, no submission/extra targets,
post-operation strict mappings, main18 preservation and normal cleanup remain
the original15 feature gates. Existing data/code guards remain mandatory.

Observation scope is bounded selected moves and snapshots, not global or
continuous input routing proof. The packet remains source-stage/nonrunnable
until the concrete coordinate representation rule and runtime source are
reviewed and a fresh exact byte/mode/link closure is frozen by the root owner.
