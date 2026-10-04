# Actual parent pointer and GTK recipient

Fresh derivative of V11, preserving its passed native campaign and failed
malformed-coordinate CPU check. V12 rejects nonfinite delivered coordinates,
nonfinite expected coordinates/tolerance, and unsupported expected-point shapes.

The native test injects through the exact private Weston 15 fake seat. It does
not use the child virtual-pointer protocol, force pointer focus, or synthesize
GTK events. An initial ordinary parent motion establishes movement from the
initial location. Every targeted point requires independently received GTK
button press/release, typed signal/event widget equality, a live owned GDK event
window, quantization-adjusted coordinates and exactly one count increment.
GTK EventBox legitimately has a separate input-only child window; its drawing
window address is not used as the sole recipient identity.

The parent stays 800x600. Original child modes are 800x600@1, 640x480@1,
960x640@2, and 800x600@1. Each has center and two opposite inset points. The
six-second observation deadline is unchanged. Parent socket PID/UID/start and
socket identity, actual core/AQ/module mappings, source hashes, private runtime,
normal client exit and ordered descendant cleanup remain checked.

The final manifest identifies selected reports and all captured files. Native
input delivery does not prove pixel presentation, cursor fallback, rotation,
multi-output routing, staged/ACK callback fencing, accessibility/IME, release
budgets, complete window operations or full S01–S16 acceptance. No main desktop
installation or activation occurs.
