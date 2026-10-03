# V21 source review request: owned read-only history longevity

UNFROZEN source packet. No native campaign, installed/main/config writes, or
production acceptance. Frozen V20 and failed V5 sources/evidence are retained.

## Implementation

`readonly_archive.py` owns anchored private immutable segment/predecessor files:
canonical single-component checksum names, O_EXCL, file/directory fsync, exact
FD/named identity and bounded full readback, issuer/epoch/previous bindings.
`readonly_ipc.py` keeps at most512 active rows; only closed, durably published,
unreferenced rows can leave memory, after the original journal writer confirms
the compact ledger tip. Local live references span the original query's final
confirmation and are released in finally. Pending and unpublished refusal rows
are preserved without completion normalization. Archived rows never supply
returned data or native authority. Registration uses monotonic per-issuer IDs.

NativeFactory validates retained history before inherited recovery effects,
seals the complete prior current dataset, and passes its pointer to a fresh
empty reader. Every RuntimeService snapshot also carries readonlyPredecessor
independently of readonlyOwnership: Keeper can persist before reader creation.
A crash at that boundary cannot lose the pointer. Pending pointer validation
precedes recovery; every native/Keeper/job/resource guard remains independent.

An explicitly selected identical predecessor orphan may be re-sealed after
crash only by exact body/hash/FD/namespace validation, renewed fsync/readback and
new owner confirmation. No directory scan grants authority. Segments remain
O_EXCL-only. Partial files, unknown state, source/namespace/owner changes and
publication faults refuse. Normal close requires no live confirmation references.

## Proof and regression

- Initial51 named /2×2000×100 proof completed before runtime files existed.
- Orphan19-case refinement completed before its runtime delta; model and actual
  kernel counterexamples retained. Exact historical source bindings recorded.
- Startup12-case proof completed before startup correction. The earlier passed
  source/full356-test checkpoint is preserved, not represented as final code.
- FINAL357 Python;308 named;30 models×2000×100 PASS, exact source unchanged.
-29 new CPU/kernel tests include genuine640 Unix-peer queries,512 immutable rows
  plus128 current rows, real child crash after durable tip/new PID+nonce restart,
  archive write/fsync/readback/tip/crash faults, real pending/held connections,
  lease/file/directory replacements, raw unpublished refusal retention, and
  actual NativeFactory→RuntimeService→sealed Keeper startup publication/closure.
-327 inherited tests unchanged. One inherited capacity test is the formal
  feature inverse: eligible completed rows archive instead of the old hard stop.
  Original test bytes, five exact requests, original retained-row validator AST,
  controller/query deadlines and ordinary helper/native/receipt guards retained.
- Actual inventory tests include a nested descriptor with this manifest's own
  basename and refusal of a declared ancestral mode mismatch.

## Review and remaining acceptance

Full-chain verification currently runs at every authority check; work grows with
retained history.640 genuine operations pass original per-query bounds. No
unbounded steady-state latency or physical cadence claim. A bounded current-owner
validation policy would require separate formal/source review; no guard relaxed.

Actual original38 baseline/restart/fault acceptance remains open. Failed V5 has
three captures but no renderer seeds/uploads and controller-deadline fallback;
no individual helper/export latency cause is asserted here. Root owns native
pairing and campaigns. Collector must use version2 ledger/startup pointers and
actual current V21 module/source attestation while preserving every original gate.

Root actor-Keeper integration, current-receipt/user cancellation, reduced-motion
V18 integration, actor-ledger512 longevity, C1/native integration and deployment
are separate open requirements. No data archival adapter may reclaim native or
semantic jobs without their own exact eligibility proof.

Review `source-handoff-v21.json`, `longevity-final-offline-checkpoint.json`,
`formal-and-runtime-history-bindings.json`, `source-inverse-v21.json`,
`closure-tools-regression.json`, and the contract/models. Use
`python -B closure_tools/freeze_longevity.py` for inventory; only root should
freeze/run after independent review. Its --freeze uses O_EXCL+fsync0600 for exact
root descriptors, omits only those descriptors, and preserves ancestral modes.
