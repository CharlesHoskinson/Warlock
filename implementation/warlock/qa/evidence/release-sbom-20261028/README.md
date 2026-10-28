# Release component gate and review binding

ELM-DEL-005 / `delivery-005` is **partial**, with original independent acceptance
blocked. Packaging now rejects unaccounted/unreviewed contents and binds final
archive bytes to the original reviewed inventory and generated metadata. A
rewritten matching manifest/archive cannot bless post-review changes.

The [manifest](manifest.json) pins the actual changed source/model bytes, exact
original oracle, scoped observations, reviewer disposition and missing evidence.
The [protected observations](protected-checks.json) are direct lead checks of the
final builder integration, independent negatives and available candidate files.
The [before-fix observation](before-fix.txt) preserves the actual stale-review
schedule that the Quint companion found; corrected production regression requires
refusal. Original failed and accepted packets remain unchanged.

Five bounded models and their explicit tests/correspondence are in candidate
`qa/release-*.qnt`, `qa/release-*_test.qnt` and `qa/release-*-model.md`. Their
sampled checks establish conditional model consistency. Several accepted-snapshot
invariants repeat decision predicates; atomic observation and filesystem races
inside a function are outside scope. Neither those models nor Graphify retrieval
prove the Python implementation or full desktop.

The available-byte projection verifies current catalog evidence and authored
payload identities, then deliberately refuses the missing recorded native tuple
and unknown review dispositions. It is not a complete candidate package. Root's
new native rebuild is separate work and does not silently replace historical
hashes. Complete provenance/grants, a real package cross-check, independent
original acceptance and remaining release/native gates stay open.

Run the candidate API, integration and independent checks through the unchanged
`window-integration-qa/qa_run.py` with `PYTHONDONTWRITEBYTECODE=1` and the reviewed
QA `PYTHONPATH`. Exact observed commands and scope are retained in the report.
Source and manifests—not graph labels or test counts—remain authoritative.
