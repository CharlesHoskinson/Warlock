# Public pointer signal signed coordinate contract

## Proven failure
The immutable PointerPrivateV3 attempt3 report SHA a3e8c1b92cee64e17107a812ff33b0e71907f0d573d03d9380544d43bbfe6736 retains the failure. Actual native cursor276,106 and parent origin96,120 imply relative180,-14. Private wire QueryPointer replies carry double180 and double-14. The official public pointer-moved callback records y4294967282, then Orca AXComponent.get_object_at_point raises OverflowError before the signed gint WINDOW query.

The installed trusted libatspi signal metadata is [AtspiAccessible,guint,guint]. Official2.60.6/2.60.7 atspi-device.c declares unsigned coordinate GTypes although its marshaller is OBJECT_INT_INT; the official Manager emits coordinates cast to gint. This compatibility defect is at the C/GObject/Python boundary. Native popup allocation, independent Gtk.pick, toolkit actual input hit and AX parent mapping passed. No evidence yet proves the popup child AX hit after correcting this boundary.

## Required boundary semantics
Only the actual MouseReviewer._on_mouse_moved public signal callback decodes coordinates before any AX query. For each exact Python int in [-2^31,2^32-1], preserve values <=2^31-1 and subtract2^32 from larger values. Thus signed negative input from a corrected upstream signal is preserved, and unsigned representation of a signed gint is restored. Refuse bool, floats, strings, None and values outside the defined interval before querying AX. Both coordinates must be valid. No clamp, origin shift, popup-specific case, manual pick, synthetic reader event or native bridge change is permitted.

This is Omarchy Orca compat v3, private source packaging. The original signed Orca prefix, system libatspi, original v2 compat and frozen V3 campaign remain unchanged. Only mouse_review.py changes from compatv2, retaining lifecycle/intent repairs. It remains connected to the same official public pointer-moved signal. Fractional coordinates remain the official libatspi integer conversion boundary; native dd precision is tested separately.

## Native acceptance still required
The existing full negative popup case must observe the actual official public signal with unsigned raw value, the actual AX descendant query with restored signed values, actual current item named Actual popup target A and normal Orca speech. No failure is converted to a pass by these offline tests. Full pointer outage/restart, keyboard policy/lifecycle and normal process teardown remain required. Invalid coordinates must not reach an AX query; positive coordinates and old lifecycle intent behavior must be unchanged.
