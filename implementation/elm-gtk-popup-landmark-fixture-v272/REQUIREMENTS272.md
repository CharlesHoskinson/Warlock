# Controlled GTK popup landmark

Preserve held253 commands, sibling/window lifetime graph, runtime guards, standard
state APIs and input controllers. Only popup construction and its explicit marker
and button geometry observation change. No native/toolkit acceptance transfer.

P retains an actual GtkButton whose real clicked callback closes the popover. Its
child includes a controlled GtkDrawingArea: opaque background and magenta8×8 at
(4,4). Record measured drawing-area bounds and native transform using the existing
landmark fields. Record separate actual button bounds and native transform for
input placement. No theme color or DOM coordinate is a pixel/input oracle.

Drawing requires the live P widget, exact current area pointer and current GTK
popover ancestry. Clicking requires the exact current button pointer and current
popover ancestry. Retirement clears both borrowed pointers before destroying the
widget. Late callbacks from obsolete controls must produce no draw/click record.

Native GTK06 still requires exact Wayland immediate parent/grab/geometry/resource,
native popup observation, real pixels and complete input/key/negative intervals,
normal button close and opener-retirement behavior under original deadlines.
