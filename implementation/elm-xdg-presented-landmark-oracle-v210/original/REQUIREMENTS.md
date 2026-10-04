# Presented landmark oracle

Before implementation: qualify actual screenshot samples against the197 committed
XDG fixture's four colored corners and current ACK-serial-dependent center.
Use monitor logical origin and actual integer monitor scale separately from
buffer scale. Accept exact screenshot dimensions and bounded RGB data only.
Source197 already draws markers; no client/core/plugin changes are required.
For zero-origin profiles, compare the real native rectangle and committed
geometry extent before projecting points into an output screenshot. Nonzero
origin rendering is unqualified: an explicit diagnostic hypothesis may inspect
surface-local origin alignment but must not enable capability or assert support.
Reject stale center pixels, missing/clipped markers, wrong transforms and
identity/serial ambiguity. CPU synthetic image checks do not prove presentation.
Native use must bind owned PID/incarnation, current configure/ACK/commit,
output origin/scale, actual screenshot and original6s transition deadline.

The18-bit center palette aliases every2^18 serials. Reject distinct observed
serials sharing the selected color; caller must supply complete bounded observed
commit history. Serial wrap/repeated numeric serial still requires caller-owned
configure generation and fresh capture binding; pixels alone cannot prove it.
