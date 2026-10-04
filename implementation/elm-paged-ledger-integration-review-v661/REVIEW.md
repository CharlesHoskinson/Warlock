# Independent V661 review of V647 and V7 integration

Verdict: **V647 confirmed within its declared storage-only CPU scope; V7 authority,
integration, native and S15 acceptance remain changes-required/open.** No new
implementation defect was established against the declared primitive contract.

Reviewed frozen V647 manifest SHA256:
`30eaeeada4ff5fcd60c67378d682a74e162eb57721e01d7269909cc3bfa560ac`.
The new protected V661 run passed62 assertions: parent/ancestry inventory checks
and isolated actual-primitive controls. The historical362 checks,1,026 records,
64-page cache maximum and48 fault-boundary cases are reviewed historical evidence,
not newly executed campaigns. The authoritative V647 model packet has three named
runs,500 sampled50-step traces and three detected typed mutants; none is a proof
of actual filesystem power loss, C or complete authority conservation.

| V629 requirement | V647 refinement evidence | Remaining acceptance |
| --- | --- | --- |
| ARC-001 immutable evidence | Actual exact opaque bytes and distinct event keys, retained predecessor roots, conflicting key refusal | Typed full-origin/status conservation, authentic native proof/anchors, every migration disposition and certificate |
| ARC-002 independent bounds | Pages16KiB, event payload16KiB, depth16, cache64, batches32 and bounded DFS;1,026 fixture records | Live64/cohort64/native16 integration, memory measurement, sustained history, compressed index cost |
| ARC-003 admission/replay | Opaque Admission bytes only | Independent request/generation/proof indexes, authenticated retired scopes, atomic admission and reserved completion capacity |
| ARC-004 publication ordering | Actual file/directory fsync order,48 injected before/after failures, five process exits | Paired ledger/C transactions, hardware filesystem qualification |
| ARC-005 restart barrier | Fresh root fsync before usable handle, visible CURRENT validation with no fallback | Prepared unlink, Released wire, admission/native gating under common paired ownership |
| ARC-006 power loss | Symbolic visible/durable separation | Actual power-loss durability, independent maxima and admission removal under filesystem/C integration |
| ARC-007 release ordering | Opaque Prepared/Released facts can coexist | Authenticated typed join and Prepared→exact unlink+dirsync→Released→cert barriers |
| ARC-008 late C admission | None | Exact old terminal/Released cleanup vs different retired origin Unknown, actual C controls |
| ARC-009 migration | Byte-exact frozen629 ancestry only | Streaming complete schemas3–6/sidecar1 import and paired activation |
| ARC-010 compaction | No primary evidence deletion, no compaction | Replacement indexes, conserved maxima, cross-process reader pins, safe orphan reconciliation |
| ARC-011 fail closed | UID/mode/type/link/hash/schema/size/typed metadata/quota/lock/I/O tests | Completion reservation, C lock semantics, auth counters, migration refusals and physical capacity guarantees |
| ARC-012 paged delivery | Generation-pinned bounded iterator, byte conservation | Cohort protocol, fresh authentic proof/read certs, bounded frontend slots and durable accepted-progress |
| ARC-013 locks | One verified nonblocking private WRITER | Common archive/host lock hierarchy, native grant ownership and no lock-held bind/output waits |
| ARC-014 full S15 | Explicitly unaccepted | Actual sustained≥10,000 same-lifetime cycles, paired filesystem/C/frontend/native and resource/provenance/power-loss gates |

Important findings are integration requirements, not retroactive failures of V647:

- **V7-REVIEW-001, high:** `Archive.append` commits one opaque event, not admission
  plus all authority indexes. A new witness deliberately appends Admission then
  faults before a separate watermark append; restart finds Admission without
  watermark. Require the V7-002 atomic transaction before any effect token.
- **V7-REVIEW-002, high:** archived JSON is intentionally not native authority.
  New actual control preserves overflowing request/Boolean generation/negative
  sequence as opaque evidence. Typed authority must refuse these values before
  treating a record as replay permission. Generation/count of archive are event
  publication metadata, not domain maxima.
- **V7-REVIEW-003, high:** global history limits occur in V608 release/definitive
  arrays, V624 certificate array, V630 combined recovery list and V642 retained
  frontend slots. Increasing only one cap cannot establish scalable recovery.
  The proposed coordinated cohort/accepted-progress protocol requires a fresh
  spec and compiled FIFO controls, preserving V642's informational drain.
- **V7-REVIEW-004, medium:**16-nibble radix routing is64-bit, while entries retain
  full256-bit digest and exact canonical key. New synthetic hash-routing controls
  establish distinct32-key bucket behavior and fail-closed33rd insertion; full
  digest collision refuses and poisons. This is not natural cryptographic
  collision evidence. An ArchiveUInt64 routing prefix cannot identify origins.
- **V7-REVIEW-005, medium:** final V647 source is pinned to its held report, and
  ancestry matches629. This establishes source closure, not a reproducible full
  Python/stdlib/Quint toolchain inventory or sustained production resource bound.
  Fixture temporary filesystem states were removed; power loss remains symbolic.
  Retained19,499 regular files/12,965,222 bytes and conservative22,577 inode charge
  at1,026 records expose index amplification, not efficient final S15 economics.

The storage model abstracts keys as integers and durable/visible sets with quota4.
Its invariant `exposed ⊆ durable ∧ |durable| ≤ charge ≤ 4` does not independently
prove monotone request/generation/proof domains, full-origin conservation,
certificate anchoring, lock ordering or migration correctness. Named conservation
and restart tests are bounded witnesses. The frozen629 model is also symbolic;
retain its limits when citing refinement, rather than adding together separate
model/CPU/native claims as end-to-end acceptance.

`SPEC-AMENDMENT.md` defines ten proposed EARS/OpenSpec integration gates before
semantics. `ARCHITECTURE.md` specifies exact APIs, roots, mapping, paired locks,
lossless migration stages, bounded delivery and the smallest independent slice.
No existing store, coordinator, Elm source, C, native runner, ledger or git state
was changed. No new native campaign was run.

Reproduction (only writes V661 report and isolated temporary fixtures):

```
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B /home/hoskinson/omarchy-windows-parity/implementation/elm-paged-ledger-integration-review-v661/qa/review.py
```
