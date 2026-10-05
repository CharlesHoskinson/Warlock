# Controlled native child fixture

The real Wayland/xdg-shell/subsurface SHM client compiles with strict warnings
and retained compiler/protocol/header/library identities. Buffer and callback
ownership derives from the reviewed xdg-origin-fixture-v184; bounded control
commands report root/child commit counters and native server barriers.

Child-native-v1 confirmed a real synchronized-state defect: queued child blue
pixels appeared without a parent commit. Its failure and eight normal exits
remain retained. The same fixture and independent PNG oracle then passed the
140-check child-native-v2 campaign on the actual cache-corrected owning tuple,
with sixteen normal exits and clean teardown. Root-native-v2 separately retained
all 73 original root color/orientation/context/FD checks and seven normal exits.

These are bounded producer experiments. Cached multi-commit merging, inherited
initial synchronization, pending destruction, asynchronous fences/FIFO/timers,
position/stack double buffering, whole desktop rendering and production provider
integration still need their own qualification. No full preview or release gate
is closed by this fixture.
