# Extended real Wayland child fixture

Strict C11 build passed on the frozen installed Wayland client/xdg-shell tuple.
Preserves all original commands and buffer/control/barrier/teardown bounds.
Adds default-synchronized creation without a parent commit, a bufferless child
commit, grandchild yellow pixels and local desync for native cache qualification.
This private fixture emits native commit counters and server barriers; neither
is a pixel or presentation receipt. No production policy or eligibility changes.
See [SPEC.md](SPEC.md) for CACHE-01..05 and unchanged deadlines.
