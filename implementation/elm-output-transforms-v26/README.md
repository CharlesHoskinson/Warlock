# Actual output changes and all eight transforms

The private native campaign passed 168 checks with cleanup, preserving the earlier
regressions and testing all eight Wayland output transforms at 125% scale. Fresh
frames captured changed output geometry, scale and transform with higher core
configuration generations; retained frames stayed unchanged. Each transform
qualified actual normalized capture pixels and pointer press/release plus keyboard
delivery inside and outside the peer input hole. Odd transforms used swapped
logical dimensions and the helper's fixed 800x600 protocol coordinate extents.

V25 separately passed 111 checks for output movement, fractional scale and 180°
transform. The preserved V24 failure probed a normalized grim image with raw
framebuffer coordinates; its corrected derivative retained intended assertions
and original deadlines. The frozen compiled V21 decoder accepted all 109 packets
from V25 and V26, with canonical scene, current-scene evidence, correlation and
presentation explicitly false. No new compiler or Quint run is claimed here.
Exact evidence, source closure and inherited core/plugin ABI are frozen in
`qa/slice-manifest.json`.

Capture orientation and virtual-pointer logical mapping do not establish raw
scanout orientation, presentation feedback or physical-device calibration. The
monitor receipt's historical `before` field was sampled after command submission;
use the retained baseline and fresh frame assertions for configuration ordering.
Some floating content extends beyond odd-transform monitor bounds; the qualified
probe points are inside the visible overlap. Complete clipping, viewport/buffer
mapping, multi-output hotplug/hardware, roles/devices, performance, human UX,
accessibility/IME and release remain open. Nothing is installed on the desktop.

Next: bind coherent scene dependencies and native policy to the typed Elm shell,
then implement the integrated taskbar and switcher. Continue the complete UI/UX
strategy, including actual end-to-end journeys and accessibility/device matrices.
