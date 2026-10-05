# Synchronized applied-state correction

The real child-native-v1 campaign failed: a synchronized child applied blue
pixels and advanced its context without a parent commit. Preserve that evidence.
The installed Wayland protocol says that synchronized state is cached, mode is
inherited recursively, initial mode is synchronized, and destruction is immediate.

- SYNC-01: WHILE a child is effectively synchronized, committed state SHALL
  remain cached without changing its current texture or applied revision.
- SYNC-02: WHEN its parent applies state, synchronized descendant cached state
  SHALL apply before native commit observers see the resulting subtree.
- SYNC-03: WHEN mode changes make a cached child effectively desynchronized,
  the cached state SHALL apply without requiring an artificial root commit.
- SYNC-04: WHEN cached state is replaced or its resource retires, presentation
  feedback and buffer ownership SHALL drain without resource address retargeting.

Implement display-owned caching with existing SSurfaceState ownership and merge
semantics. Preserve existing class layouts and exported ancestor interfaces;
compile actual Compositor.cpp and Subcompositor.cpp on their owning headers.
No production eligibility or full native/release claim follows from this fix.
Double-buffered position/stack/membership, async acquire/fifo/timing coherence,
full presentation and measured resources still need their original qualification.
