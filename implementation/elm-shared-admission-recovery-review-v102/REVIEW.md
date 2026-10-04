# Shared host admission recovery follow-up

This read-only source review extends V99. It changes no production behavior and
does not establish native acceptance.

The inspected V305 `admission_batch` selects at most one window operation. A
second operation rejects the batch before `admission_write` runs. This narrows
the failure analysis: the current code does not journal a prefix of multiple
operations from one batch.

However, `admission_write` can successfully rename the admission record to its
final filename and then fail the directory `fsync`. Its return value is false
while the final file remains present. The failure cleanup unlinks the temporary
filename, not the renamed target. A false return therefore cannot prove that no
admission record exists. Preserve the exact record and existing recovery path;
do not issue an unsent certificate based on that return value alone.

The shared host calls the inherited void `surface_receive` after its own
preflight. It prints `view-commit` afterward regardless of whether the inherited
function rejected admission or returned on popup creation failure. That log line
is not a successful admission or dispatch receipt.

The shared controller has one primary native manager; per-output bar managers
are presentation/input peers. A new disposition must return through the trusted
controller channel and retain the exact submitted topology revision, relevant
output scope, publication, lease and batch identities. Closed frames may have
no popup owner: retain the submission's scope rather than deriving it from the
host's subsequently current popup owner. Output retirement/replacement must not
let a delayed response cancel another scope's observations or operations.

Required fault evidence must distinguish: preflight refusal before admission;
duplicate-operation rejection before writes; rename success followed by failed
directory synchronization; popup failure after durable admission; and actual
backend queue/receipt delivery. Preserve the original operation keys, source
hashes, deadlines and recovery journal. A textual success log is insufficient.

The present findings are requirements for the combined shared-host recovery
implementation and tests. No operation is automatically replayed, no uncertainty
barrier is cleared, and no full roadmap gate is closed by this review.
