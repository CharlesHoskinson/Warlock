# V647 storage refinement, recorded before implementation

This primitive refines ARC-001/002/004/005/011/012 of frozen V629. It neither
implements admission authority nor accepts S15. A fixed-depth immutable radix
index has fanout 16, depth at most 16, leaves at most 32 exact event references,
pages at most 16 KiB, and an LRU at most 64 pages. Event envelopes preserve exact
caller JSON bytes; key digests route searches, while full canonical keys authorize
equality. A collision bucket exhausted at depth 16 refuses insertion.

The first implementation uses 16 routing levels: at most 17 new index pages
per insertion, deliberately trading extra fsync and disk cost for a simple bounded
publication closure. Compressed paths and streaming compaction are later work.

CURRENT selects one small immutable root with a predecessor reference and at
most 18 newly created event/index references. All predecessor roots and all
immutable events remain. Root count is historical record count, never a live
reservation count. Independent native request/generation/proof watermarks require
future secondary indexes and paired authority integration; arbitrary archived
payloads are evidence, not trusted replay maxima.

The additional QUOTA counter reserves conservative bytes/inodes durably before
publication. Abandoned transactions retain their charge, so repeated crashes
cannot silently evade capacity. There is no cleanup or compaction of immutable
files. Temporary cleanup errors poison the writer. Reopening validates visible
CURRENT, its root, direct predecessor and bounded new-page closure, then fsyncs
the root before exposing even absence. A malformed visible root never falls back
to a predecessor. All traversed historical pages are verified lazily.

File and directory fsync ordering is enforced by actual calls and injectable
before/after-call boundaries. Process death tests retain real filesystem names;
they are not power-loss tests. The symbolic model has separate durable/visible
state, conservative quota and positive exposure; it does not prove POSIX or
hardware behavior. No fsync establishes rollback resistance against malicious
same-UID replacement. This prototype takes only its own nonblocking writer lock.

Mutable publication temporary names use fixed exclusive slots, so failed QUOTA
updates cannot leak arbitrarily many uncharged temporary inodes. A leftover slot
refuses future writes; reading the validated old root can continue after restart.
Automatic orphan reclamation is deliberately outside this prototype.

OpenSpec: a 1,025-event history crosses the 64-page cache bound without evicting
old Unknown, terminal, proof anchor or predecessor bytes; a pinned iterator
continues at its immutable generation; identical keys are idempotent only for
byte-identical envelopes. Quota refusal preserves all history. Failed publication
poisons its handle; a restart may observe either predecessor or published root
depending on CURRENT rename, and must pass a fresh root barrier. Symlink,
hardlink, owner/mode/type/size/hash/schema/duplicate-key failure refuses exposure.
