# Browser V10 local-memory metrics fixture

The strict V9 actual flow fails before native input because an owned browser
retains a writable shared 4 MiB deleted BrowserMetrics profile allocation, even
with PersistentHistograms disabled. Retain that result. No new deleted mapping
authority is introduced. All mapping, source, native input, draft/caret, Files
callback, reload, lifecycle and preservation oracles remain unchanged.

The pinned Chromium persistent_histograms.cc defines storage=LocalMemory for
PersistentHistograms and constructs a local-memory allocator on that branch.
Request that precise feature parameter explicitly in a fresh fixture instead of
disabling the feature. Other feature disables and metrics-recording-only stay
exact. This is a source-backed configuration request; the installed Chrome
154 implementation has not been proven equivalent to that current source.
Actual raw mappings must establish absence of any deleted BrowserMetrics
allocation before input. If it still occurs the existing strict gate fails, and
a fresh diagnostic is required. Never make a failure pass by adding an exception.

All original seven Quint models remain applicable because no authority or window
semantics change. Their complete run is required before freeze. This candidate
is private, with owned runtime/profile/network/private bus and all five crash
handoff guards; no installed browser flags, main GUI or restoration changes.
