# Owned read-only history longevity V21

Fresh formal-first derivative of frozen V20 d3d836eda0e2a25681df4ca80740ca94f8d2084ea1c48f8834293b740122c068.
No native launch/deployment/acceptance. Root's actor Keeper branch and collectorV5
are separate. This policy applies to fixed read-only data rows only, never
native/effect/export jobs or unresolved semantic results. Original request,
peer/FD/root/lease/source/executable/shape/EOF/deadline guards remain required.

The active ledger remains bounded at512. Before connecting at capacity, archive
an immutable batch of closed, durably published rows for which no live query
retains a confirmation reference. Pending, unclosed, unpublished refusal and
referenced rows cannot be reclaimed. Failure may refuse before connection, never
truncate history or extend the original caller's absolute deadline.

A separate rotation mutex serializes archive planning. Only brief snapshots and
final journal publication use manager-reservation then ledger lock. Archive file
creation/readback and peer/source checks occur outside these publication locks.
Concurrent unrelated reservations and query confirmations remain possible. Final
commit rechecks the same issuer, epoch/previous digest and exact candidate rows
with no current references. New disjoint rows may be retained during writing.
A stale plan or any unknown/error/corruption latches refusal; it cannot authorize
bytes or new connections. No bounded software trace proves physical cadence.

Each immutable0600 regular segment under an anchored0700 root-owned directory
contains schema, exact issuer digest, monotonic epoch, previous pointer, exact
closed row bytes and serial interval. Names are canonical single components with
issuer/epoch/content digest; source/helper hashes and expected namespace are
validated. Actual descriptor/named identity/mode/UID/size, full bounded bytes and
SHA must agree before/after read. Symlink, alias, special/unsafe/changed material,
duplicate/reordered/cyclic/missing chain and still-valid issuer/epoch/digest
replacement refuse. No timestamps imply authority.

Durable sequence: plan → O_EXCL file write/fsync → parent fsync → exact readback →
original journal writer publishes compact rows+new authenticated tip → memory
reclamation. Failed archive durability keeps the old durable ledger. Failed or
uncertain tip publication faults the service; no bytes may escape. A crash before
tip publication leaves an unusable orphan and the old full ledger. A crash after
publication must validate the entire referenced chain and retained current rows
before any new API authority; valid disk state reconstructs without data replay.
Reclamation follows confirmed durable tip publication; closed process groups
supply no substitute data/native receipt. All native quarantine remains exact.

References are acquired with durable registration before connection and released
only in a query-finally path after the existing complete/refused closed outcome.
The reference is local ownership, not a claim bytes reached a caller. Archived
complete data supplies provenance only; it is never returned again by restart.
Current row IDs use a durable monotonically increasing per-issuer serial and
cannot reuse archived IDs. An old service's entire bounded current dataset,
including pending/unpublished rows, is preserved in an immutable predecessor
record before a new issuer overwrites the journal. This is retention, not closed
row reclamation or normalization. Predecessor and segment chains have validated
issuer/epoch/digest bindings and grant no current query/native authority.

Recovery validates the old dataset/chain under the new exact runtime lease before
journal replacement. It never substitutes old data for new queries or settles
native jobs. Source/root/socket changes, malformed/unknown state, corrupt/missing
archives, durability faults and unfinished native effects remain refusal or
quarantine. Historical row retention is separate from current query capacity.
V20 and failed collectors remain immutable; old-schema/source migration is not
implicitly authorized. Native baseline/fault acceptance follows separate review.

Required proof/tests: capacity before connection; genuine >512 actual Unix-peer
queries and immutable archived rows; pending/refused-unpublished/current reference
retention; writer blocked while reservation stays available; valid concurrent
rows; exact source/namespace/issuer/epoch/hash changes; archive/write/fsync/readback/
journal-publication/reclamation crash points; restart chain validation/no replay;
corrupted and valid-replacement chains; original five requests/effect refusal and
full inherited source/model closure. Actor-ledger512 needs its own semantic
eligibility adapter after root's actor ownership integration; no implicit reuse.

Before-publication orphan refinement: a successful predecessor seal can outlive
a crashed owner without a journal pointer. A new exact lease may explicitly
re-seal the SAME full current old journal dataset into the canonical checksum
name. O_EXCL is attempted first. On EEXIST only this chosen predecessor may be
read through the anchored directory, with new FD/named identity, complete exact
body/hash/schema validation, file and directory fsync and matching post-disk
readback. The new owner must confirm and publish its pointer before authority.
No directory scan discovers authority, no partial/unsafe/replaced referenced
file is accepted, and no prior identity or unlink actor is inferred. Segments
remain O_EXCL-only. Volatile seal ownership resets on process crash in the
refined model; failure remains latched for a running bound instance.
Proactive guarded closed-row rotation uses the same plan/write/publish guards
and permits real disjoint rows while sufficient active capacity remains.

Startup lineage publication: Keeper creation can persist before ReadonlyIPC
construction. Every fresh snapshot therefore carries readonlyPredecessor
independently of readonlyOwnership. If a crash leaves no current reader ledger,
the exact pointer and full sealed dataset must be verified under the selected
new lease before any inherited recovery effect. They remain historical data
only. The eventual current reader must bind that same pointer and begin empty.
An active reader's predecessor and the independent startup pointer must agree.
All ordinary Keeper/job/native closure gates are still independently required;
absence of a reader grants neither data nor native authority.
