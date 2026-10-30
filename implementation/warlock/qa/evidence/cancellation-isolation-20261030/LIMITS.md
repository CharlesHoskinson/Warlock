# Cancellation custody isolation

Two actual storage defects were reproduced and repaired. The crosslane RED
uses real V7 storage and Reconciliation with a strict native retirement-response
double: the old legacy path unlinked typed Pending before its later save refused.
Typed full keys are now excluded from legacy projection, release and unlink;
restart validation also rejects conflicting legacy Prepared/Released records.
Genuine legacy records retain their previous path, including another full key
with the same incarnation. Typed certificate retirement remains distinct.

The downgrade RED reopens V7 custody with omitted/false cancellation mode and
observes frozen V6 mutation followed by V7 refusal. Journal now checks for either
V7 ledger or marker under the writer lock before migration. Legacy constructors
refuse without changing data, including partial, dangling-symlink, directory and
FIFO presence. Clean legacy namespaces and a different lifetime remain usable.
This is fail-closed namespace ownership, not automatic recovery or downgrade.

The final protected store report has nine passing groups, including 33 checks
each for legacy isolation and namespace ownership. Other groups retain their
individual counts/observations; do not add heterogeneous observations into a
feature count. Coordinator ordering/config/history checks are in the adjacent
coordinator packet and use this same corrected store. Native response doubles
do not prove a real native producer bug, authenticated transport or C/Elm routing.

The first isolation model typecheck failed because `keys` collides with a Quint
builtin; its source and failed report remain in model-red. The only correction
was renaming that identifier to KEYS. The corrected source passes 13 named tests
and four sampled properties (1000 traces, 30 steps, seed 20261030). typedCustody
and ackAfterRetirement address safety; noReplay and projectedLegacyOnly are
bookkeeping properties, not transport proofs. Three opaque keys abstract full
identities and proof association. Namespace downgrade is not modeled; its evidence
is the actual filesystem suite. The earlier durability model remains separate.

No original scenario, physical Escape, generation resource, all-slot, hardware
power-loss, release or deployment acceptance follows. Host-owned application
acceptance/deadline admission, strict C/Elm consumers and end-to-end native
interleavings remain next implementation work. Frozen earlier packets are
historical evidence and were not rewritten to imply these guards existed then.
