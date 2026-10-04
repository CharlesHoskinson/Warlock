# V647 isolated paged immutable archive

Status: **prototype CPU accepted; no ledger integration, native acceptance or S15
acceptance**. Frozen V629 architecture, all 14 EARS, OpenSpec and Quint source are
copied byte-exact in `ancestry/`. The storage-only refinement in
`spec/REFINEMENT.md` and its initial passing Quint packet were created before the
Python primitive. Existing V608/V624/V630 and the C/frontend remain unchanged.

Authoritative executable evidence:

- `qa/tests-1791154696119822432/report.json`: **362 checks passed**, actual temporary
  files, 1,026 retained records, 19,499 regular archive files, 12,965,222 actual
  bytes, 64 maximum cache pages, depth 16, batch size at most 32. Conservative
  charged capacity: 17,171,299 bytes / 22,577 files. These are one CPU fixture's
  measurements, not sustained production scaling acceptance.
- `qa/model-1791154554659366036/report.json`: three actual named Quint runs,
  500 sampled 50-step traces, three typechecking negative mutations with detected
  counterexamples (early exposure, lost history on restart, missing quota charge).
- `qa/model-1791153992899934836/report.json`: initial pre-implementation passing
  model. Initial parse/type errors are retained. The subsequent failed model QA
  packet preserves a sampled mutant that was missed; the authoritative packet
  uses a deterministic witness for that mutation.

The earlier failed filesystem packet preserves a QA fixture error: record 501
was queried as Released instead of its actual DeliveryAttestation key. Earlier
intermediate passing runs are superseded by the final report above. Some source
edits overlapped intermediate runs, so their closing source digest is not claimed
as an independently held execution closure. The final run was held unchanged;
the freezer verifies its hashes against actual final source.

`Archive.append(fullKey, kind, exactJsonBytes)` creates a new immutable event and
17 fixed-depth COW index pages, then a small predecessor-linked root. Exact full
canonical JSON keys authorize equality; SHA-256 only routes/indexes/verifies
content. Existing keys accept only byte-identical envelopes. Historical Unknown,
terminal, Prepared, Released, certificate and predecessor facts use distinct
full event identities. The primitive preserves caller bytes and checks JSON;
it **does not authenticate the caller's native proof or interpret an outcome**.

The protected writer holds one nonblocking verified writer lock. Runtime files
must be regular, owner UID, 0600, single-link; directory/path must be UID-owned
0700 without symlink components. Reads validate schema, duplicate keys, counter
types, bounded size and referenced hashes, including cache hits. CURRENT cannot
change under a live writer. Fixed exclusive publication temporary slots prevent
repeated uncharged quota-temporary accumulation; a leftover slot blocks future
mutation and is retained for separately reviewed recovery.

Configured byte/inode quota is conservatively charged and synchronized before
page creation. Publication calls run in this order:

1. QUOTA temporary fsync/rename/root-directory fsync.
2. Event/index temporary writes, file fsyncs, renames, root-directory fsync.
3. Immutable root temporary write/fsync/rename/root-directory fsync.
4. CURRENT temporary write/fsync/rename/root-directory fsync.
5. Return the new root identifier.

Restart validates CURRENT, its root, direct predecessor and at most 18 newly
published event/index pages, then calls root fsync **before** returning a usable
handle. Historical paths are validated as they are traversed. Invalid visible
roots never silently fall back. Storage errors poison the handle; invalid caller
input, exact-key conflict and pre-write quota refusal retain the old usable root.
All immutable events and predecessor roots remain; there is no cleanup or
compaction of primary evidence. Batches pin an immutable root and use a bounded
DFS stack. Cancelling a read cursor does not poison a healthy writer.

The 362 checks include 48 before/after syscall-boundary faults, five actual
abrupt child-process exits, fresh root barriers, byte conservation, bounded
lookups/batches/cache, immutable same-key conflicts, quota refusal, short syscall
writes, injected ENOSPC, failed cleanup poisoning, fixed orphan-slot refusal,
directory/file/link/schema/hash/size/duplicate JSON and typed decoder controls.
Fixtures are temporary and intentionally removed after reporting. Abrupt process
exit preserves visible filesystem names; **it is not a device power-loss test**.
The v647 model and frozen v629 model separate symbolic visible and durable roots.

Unclosed integration gates: authentic independent native request/generation and
proof-sequence maxima, retired scope indexes, Admission-before-effect/completion
reservation, exact C late readmission, host lock order, live-reservation schema,
authenticated proof/anchors, lossless paired migration, efficient compressed
index/streaming compaction, orphan reconciliation, sustained 10,000 cycles,
reader pin lifecycle across processes, native/frontend history limits and actual
power-loss qualification. Physical free space is not preallocated; ENOSPC fails
closed. Malicious same-UID hash-consistent rollback is not prevented. Fixed-depth
index cost is deliberately high; do not deploy this primitive as a final S15
store or treat opaque archived counters as trusted replay authority.

Reproduce through the protected CPU launcher:

```
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B /home/hoskinson/omarchy-windows-parity/implementation/elm-paged-history-storage-v647/qa/test.py
```
