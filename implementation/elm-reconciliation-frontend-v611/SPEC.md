# Reconciliation frontend v611 — preserved intermediate

Derived from frozen GUI592 plus the frozen601 typed decoder. The copied601 module
adds only proofDecoder to its export list; frozen601 itself is unchanged. The
controller owns full historical Unknown records and exact current announced proof,
with per-domain frontend requested IDs and accepted contexts. Existing Shell,
Effects, MenuBridge, ReceiptRouter and Menu remain the authoritative window/menu
reducers. No native window policy is duplicated.

A full host-reservation-unknown retains old binding, effect protocol, complete
intent and Unknown status. Validated recovery uses existing Effects allocation
and capacity policy; a typed helper marks an already admitted Pending exact key
Unknown from that actual full record, without creating a fake receipt. Historical
record capacity is64 with no eviction and a persistent fail-closed window mutation
flag when exhausted. Unsupported legacy origins remain blocked.

The exact nine-field native binding-retirement Retired proof is announced before
post-proof reads. Each ready acknowledgement has exactly protocolVersion3,
kind reconciliation-ready, current binding, proofRequestId and queriedBinding.
It precedes existing Shell refresh requests. The same acknowledgement is repeated
before fresh read batches for idempotent refusal recovery; only one old scope is
active. The backend must treat already completed known proof acknowledgements as
informational no-ops, never reset a later active scope. Unknown or foreign IDs refuse.

Only the copied601 decoder, stored full Unknown/proof and admitted public Shell
reads permit release. The exact announced proof must match the release proof.
Effects release removes only a matching Unknown live reservation, keeps transaction
history and counters, and sends no effects. Full origin collisions retain a shared
Effects reservation until every matching stored origin releases. Exact menu
mappings are marked Unknown and retired by typed helpers, never fabricated terminal
receipts; bounded historical uncertain menu entries remain. Prepared/queued local
choices are retired before proof refresh and again on release. Only a new explicit
user intent can submit a subsequent native mutation.

## Known liveness gap: superseded by fresh v619

The original v611 contract invalidates accepted stamps when new reads are requested,
requires requested IDs still equal accepted IDs at release, and requires Ready
phase when detecting accepted action replies. A valid second reply can immediately
drain a queued refresh into another read batch/Reconciling and consequently reject
an already durable release for the completed pair. The original43 checks and9
mutation controls are retained as intermediate evidence, including the obsolete
retry-pending rejection assertion. They do not establish final reconciliation
liveness. Fresh v619 must preserve accepted post-proof stamps until a newer reply
is actually accepted, qualify original releases during a pending next batch and
reject obsolete pairs only after actual newer accepted replies.

## Evidence and limits

Optimized compiled public controller/worker ports passed43 checks,9 deliberate
compiled mutations were detected, and actual Main/Bar/Popup plus unchanged native
CPU host/helpers compiled and passed self-tests. Source, commands, source hashes,
failed attempts, counterexamples and original573 observations are retained.
Fixtures are synthetic typed frontend trajectories derived from those preserved
observations; none is an authenticated native/durable recovery campaign.

The copied592 native carrier does not admit reconciliation-ready. A combined
candidate must use the owning612+ successor carrier/coordinator and qualify their
actual source tuple. No daemon wiring, native launch, activation, fsync/backend
acceptance, keyboard/AT/IME acceptance or frozen shared evidence changes are claimed.
