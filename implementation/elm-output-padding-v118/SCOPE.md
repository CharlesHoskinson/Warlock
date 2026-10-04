# Native monitor ownership and bounded popup viewport

This component explicitly pins its layer surface to a retained GdkMonitor native
object. Trusted --monitor-index selects an initial enumeration entry once;
default selection pins the primary/first monitor. An unavailable explicit entry
refuses startup before WebKit/backend construction. The index is not a persistent
connector identity and is never followed when enumeration changes. The retained
native monitor object is the owner for this process lifetime.

Removal of the owned monitor retires the host, suppresses renderer callbacks,
clears queued requests, cancels asynchronous writes, closes popup/grab and hides
the bar before normal client-first teardown. Removing another monitor leaves
the host alive. Already forwarded requests are not claimed cancelled; durable
all-origin Unknown/journal recovery remains a separate incomplete obligation.

Popup dimensions use the selected monitor's logical geometry, the current 48px
bar reservation and the owning compositor's four-pixel positioner constraint
inset (native-core-v2/src/protocols/XDGShell.cpp getPosition). Defaults remain
700x420 where space permits. A 640x480 output requests 632x420, allowing native
positioning to keep the complete rectangle inside the output. The default bar
policy still needs general external workareas, margins and live resize handling.

Failed V113 requested 700px on a 640px display. V114 bounded the width but V115
configured x=4,w=640 and still exceeded the output. V116 attempted undecorated,
shadowless wrapper geometry; V117 still configured x=4,w=640. That attempt is
retained but omitted from V118. The exact compositor positioner insets its
constraint box by four pixels; V118 accounts for its admitted logical rectangle.
GTK documents decoration and automatic shadow geometry here:
https://docs.gtk.org/gtk3/method.Window.set_decorated.html
https://docs.gtk.org/gdk3/method.Window.set_shadow_width.html
These explain the investigated wrapper API, not the eventual compositor fix.

V118 builds actual optimized Elm Main/Popup and owning native host. Elm production
modules match V106/V107: retained compiled67 controller and12 presenter evidence
is checked by source equality. Native C has eight test groups including strict
startup-index boundaries and logical popup dimension refusals. V112 independently
executes four named monitor ownership/removal scenarios and 1,000 sampled traces;
V111's initial Quint set-exclusion type failure is preserved. No automatic
model-to-C refinement is asserted.

V119 preserves all original91 window oracles/deadlines, recovery/grab/topology
checks, and adds actual asymmetric nested outputs. Two private host processes
qualify the native ownership component: they are not the final shared-controller
multi-output desktop. Native layers must show bars on WAYLAND-1(800x600) and
QA-SECOND(640x480), each reserving top48. Real pointer opens the secondary popup;
its entire configured rectangle must fit. Removing QA-SECOND with the popup open
must retire only its host, with normal exits and ordered cleanup.

Remaining: one Elm controller routing presentation across all output views,
persistent connector/output incarnation policy, window filtering, output changes
with active resize/scale/transform, fullscreen/lock, queued/delayed fault cases,
actual physical multi-display/AT/IME/human UX/performance, WebGPU, C00 and release.
