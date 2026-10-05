# Extended synchronized child cache qualification

Additive to CHILD-01..05 and original S09 preview13; no baseline changes.
- CACHE-01: WHILE a newly created default-synchronized child has a committed buffer without a parent commit, capture SHALL exclude the queued buffer; WHEN its parent commits, capture SHALL include that buffer.
- CACHE-02: WHILE a synchronized child queues several buffers followed by a bufferless commit, context and pixels SHALL retain the applied state; WHEN the parent commits, the last buffered state SHALL apply.
- CACHE-03: WHEN a child becomes effectively desynchronized, pending state SHALL apply without a new root commit; a locally desynchronized grandchild SHALL remain queued while its ancestor is synchronized.
- CACHE-04: WHILE a synchronized NULL attachment is queued, applied child pixels and context SHALL remain; WHEN the parent commits, the child and descendants SHALL disappear from capture.
- CACHE-05: WHEN a child is destroyed with cached state outstanding, a later parent commit SHALL never resurrect that state or retarget a replacement resource.

Retain the entire native-v2 campaign and exact core-subsurface-cache-v1/source-revisions-v2/AQ155 tuple. Original two-second captures, three-second IPC, six-second fixture observation and physical consumer/export/producer retirement remain unchanged. Use independent libpng point/count decoding with an overlapping unrelated peer. Select explicit Quint scenarios and compare projected pixels from actual native captures with their exported traces. This qualification covers bounded SHM state application, not acquire fences, FIFO/presentation, layout double buffering, ordinary desktop rendering, provider/WebKit, production eligibility, measured budgets or full release. Omarchy command/keybinding obligations remain unchanged.
