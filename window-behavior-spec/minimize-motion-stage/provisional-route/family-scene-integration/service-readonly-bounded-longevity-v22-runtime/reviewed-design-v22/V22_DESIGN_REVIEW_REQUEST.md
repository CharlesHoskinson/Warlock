# V22 design review before implementation

Scope: bounded current-owner read-only operation checks, retaining full
historical validation at startup/before recovery effects/audit/normal closure.
The immutable V21 sources remain exact. No V22 runtime is copied or changed.

Please review `BOUNDED_AUTHORITY_CONTRACT.md`, `bounded_read_authority.qnt`,
`bounded_read_authority_test.qnt`, and `formal-design-before-runtime.json`.
Final52 named + mixed/valid-path2×2000×100 pass before implementation. Exact
owner/FD/fullflags/role/seals/material/tip/publication tokens are preserved;
connection and owner refusal stay terminal. Durable diskTip precedes row
reclamation and FD adoption, with explicit crash guards. Publication blocks
new queries until adoption. Current FD bounds include the preparing pair.

The explicit `olderAncestorDamageIsNotSilentlyClaimedCurrentTest` requires review:
fresh current data carries no all-history-current-integrity assertion. Changed
unborrowed older files are refused by full audit/restart, not looked up on each
unrelated fresh query. No implementation has weakened V21. A complete-chain
claim remains full verification; old proof/data never grants replay/native or
cancellation authority.

Unchanged V21 CPU measurement:1031 actual peer queries, seven repeated samples
at0/64/128/256/512/768/1024 archived rows, active7. Median23.480→463.012ms,
max621.009ms, original1s per-query bound, all534 source bytes/modes exact.
Rotation measurements use separate proactive maintenance, not an assertion of
its original absolute deadline. No arbitrary lifetime or native-baseline claim.

`kernel-anchor-feasibility-v2.json` persists actual raw before/after metadata and
positive individually-valid/identical-byte sealed-FD replacement before any
assertion. Actual47 seals, write/truncate/chmodExecute EPERM; no claim that seals
alone prevent PROT_EXEC mapping. Source must refuse executable aliases too.
Initial parse/Map.set errors, intermediate42/48 proofs and first feasibility
probe remain retained. `MEASUREMENT_AND_COUNTEREXAMPLES.md` explains limits.

Remaining after design review: fresh derivative runtime integration, actual
constant-history query cost/borrowed-FD concurrency faults, complete inherited
proof/offline/closure, independent review/freeze, root-only baseline/restart and
fault campaign. Native baseline38, actor-ledger512, current cancel/reduction
integration and production deployment remain independently open.
