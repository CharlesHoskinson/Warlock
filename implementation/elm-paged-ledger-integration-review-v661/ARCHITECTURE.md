# Concrete V7 integration plan

Status: proposed architecture and independent CPU review. Existing 64-history
limits remain enforced. V647 alone is not a deployable authority store.

## Origin and event mapping

Use V630 `durable_ledger.key(record)` semantics: canonical exact JSON of
`effectProtocol`, entire binding (`lifetime`, `session`, `frontend`) and entire
validated intent. Status is an event fact rather than part of origin identity.
Schema numbers, original raw bytes and source digests are conserved separately.
Do not reuse the V647 fixture key with its approximate protocol/request field
names as the production schema. C and Elm must share strict canonical UInt64
string decoding and complete target incarnation semantics with Python.

Use full origin bytes as the primary equality key. SHA-256 routes and checks
content; its first 16 hexadecimal digits are V647's 64-bit route, not a unique
ArchiveUInt64 origin ID. Thirty-two distinct full digest keys can occupy a route
bucket; the 33rd currently refuses. Full-digest collision currently poisons and
refuses rather than returning another origin. Never truncate digest to a UInt64
foreign key or use archive generation as an origin, request ID or proof sequence.
If internal UInt64 event IDs are introduced, allocate them monotonically in the
same atomic root transaction, store an immutable bijective ID→full-origin/event
mapping, reject exhaustion and collision, and preserve both directions through
migration/compaction. Such IDs are references, not equality/replay authority.

Immutable event identity comprises namespace, exact origin or scope, fact kind
and fact-specific discriminator. Admission/Unknown/terminal each retain original
payload; Prepared and Released retain the original proof/join/anchor; each
DeliveryAttestation has its own exact ID/current proof/join and original anchor.
The materialized per-origin index points to these facts without relabeling
Unknown. Latest delivery index points to one certificate while every published
certificate remains retained. Independent scope indexes contain request maxima,
generation maxima, proof-sequence maxima and authenticated retired facts; an
increase in one domain never compensates for a decrease in another.

## Proposed API and atomic root

A future `AuthorityStore` wraps a refined archive, not direct multiple `append`
calls. Its authenticated, typed API is:

- `openValidated(authority, pairedSchema)`: verify exact ownership, source/root
  closure, migration marker, locks and fresh root barrier before any positive
  lookup or absence. Return opaque validated handle and immutable generation.
- `lookupOrigin(fullOrigin)`, `lookupScope(fullBinding)`: return immutable facts
  and independently validated maxima/retirement, with bounded path reads.
- `admit(fullPendingRecord, producerContext)`: atomically commit Admission, live
  root, both allocation maxima and worst-case completion reservation. Return a
  durable token required by the native invoker; refusal returns no token.
- `recordReceipt(token, exactReceipt)`: preserve exact Admission; atomically
  publish Unknown or definitive receipt plus indexes, consume reservation and
  retain a conserved disposition. No receipt means Unknown, never Committed.
- `prepareRelease(authenticatedJoin)`: validate native Retired proof and separate
  action/geometry accepted IDs in the same output; atomically publish exact
  Prepared and retirement/proof maxima before exact C admission unlink.
- `finishRelease(preparedToken)`: unlink only the exact full-key admission,
  fsync its directory, then atomically publish Released and live removal. Restart
  completes Prepared only after a fresh root barrier; no effect is replayed.
- `attestDelivery(originalAnchor, freshJoin)`: atomically publish immutable
  certificate and latest-delivery index before emitting unchanged strict wire
  `{id,proof,observation}`. Original anchor/proof/Unknown cannot be rewritten.
- `beginCohort(generation, cursor, livePriority)`, `ackCohort(exactReceipt)`:
  bounded authenticated generation-pinned discovery/progress, separate from
  origin disposition and native proof. Ack is not a successful send.
- `importPredecessor(validatedSource)` and `activatePairedMigration(...)`:
  source-specific exact conservation and paired transition below.

The refined manifest atomically references event index, origin disposition index,
live root (≤64), per-scope independent maxima/retirement index, delivery index,
reservation accounting and migration/progress roots. Every updated root/page is
in the bounded transaction closure. V647's one-event append cannot atomically
update these independent structures. Either publish a bounded single semantic
transaction envelope with authoritative validated projection, or extend COW root
publication to a bounded multi-event transaction. Select and model one before
implementation. Never run Admission append followed by a separate watermark
append and call it atomic: V661 demonstrates the intervening restart state.

Page/root file fsync → page directory fsync → manifest fsync/rename/directory
fsync → CURRENT fsync/rename/root fsync precedes token/ack exposure. Quota reserves
physical logical completion budget before effect, conservatively charged on
abandonment. No fsync promises physical preallocation or malicious same-UID
rollback resistance; those limitations require explicit acceptance scope.

## C integration and shared ownership

Resolve the final common lock hierarchy before coding: `archive-writer-v7.lock`
then `host-writer.lock`, both nonblocking and inode/UID/mode checked. V647's current
`WRITER` is storage-only. C and Python must use the same protocol; no native bind,
request, proof acquisition or output wait under either lock. V626's staged startup
remains: collect short-lock state, release locks, attach then flush coherent frames.

C admission must consult full origin, retired-scope facts and both allocation
maxima at the same validated root used to grant admission. Preserve Pending files
as exact late-write evidence during transition; do not grant before durable token.
Exact already Released/terminal late admission is unlinked and directory-synced
after root barrier. A different origin, even on the same target or retired scope,
is imported as Unknown until its own authenticated disposition. Absence alone
never permits reuse of a request/generation below conserved maxima. Native grant
history/proof sequence storage must itself scale or explicitly refuse; merely
paging Python history cannot lift the native history bound.

## Recovery delivery and frontend slots

V630 currently combines all live Unknown plus all historical Released in a list
and rejects length >64 before any frames. V642 retains released slots forever up
to64; its informational scope correctly drains already-delivered history, but
does not implement eviction or a paging protocol. V624 latest-certificates array
has its own64 cap. V608 has independent64 release and definitive history caps,
and its older watermark scope list is128. All require coordinated replacements.

Keep live Unknown census ≤64; freeze and validate the complete census before any
partial announcement. Discovery is bounded streaming, but do not omit live
records to make room for history. Send live recovery first. Historical cohort
size is at most remaining frontend tracking capacity, with one active announced
proof scope and existing native request queue bound16. If live census fills64,
history waits until genuine release frees capacity; no history eviction frees a
live reservation. Records in each cohort precede its proof; proof-ready must
precede fresh read requests in FIFO. Only actually accepted newer replies
supersede accepted stamps; merely emitted next requests do not invalidate a
queued old-pair release. Preserve V619/V642 exact same-output joins and no effect.

A proposed cohort identity binds current frontend, pinned archive root/generation,
cohort ordinal and digest of the complete full-origin membership/certificate set.
Explicit frontend acceptance ack permits releasing informational slots, never
unresolved live slots. Backend receipt is durably anchored before cursor advance.
Wrong/partial/future/old ack does not advance. Lost ack replays the same cohort
idempotently with fresh native proof/read certificates; already-released slot
behavior retains V642 informational drain semantics. New frontend state/session
starts a new bounded discovery checkpoint, not an assumption that previous view
accepted output. Temporary informational slots are safely retired only under
reviewed new protocol; archived evidence/replay indexes remain permanent.

This keeps hot state bounded but does not bound total startup time for arbitrarily
large history. Do not stretch existing behavior deadlines to conceal replay cost.
Define measured per-cohort deadlines and total cancellation/resumption gates;
live readiness has priority, and historical browsing is cancellable. Cross-process
cursor pin lifetime, resumable delivery acknowledgements and stale view revocation
need actual tests before claiming efficient recovery.

## Migration stages

1. Freeze/read schemas3–6 plus sidecar1 under common ownership; reject any old
   producer still able to publish. Pin each exact source file, marker and identity.
2. Stream-validate every original record, latest/settled receipt, live admission,
   Prepared/Released proof/join/ID, bootstrap/predecessor hash and available
   sidecar certificate. V624 contains latest certificate per origin; do not invent
   earlier overwritten certificates. Retain original source bytes in bounded
   chunks with exact reassembly hashes (old files may exceed16KiB envelopes).
3. Build new immutable events and indexes in an inactive V7 generation. Map each
   old exact key to its conserved facts; independently prove request/generation
   maxima never decrease and import authenticated retirement/proof maxima from
   their actual source, not invented archived metadata. Detect conflicts, orphan
   certificates and unknown native evidence before activation; fail closed.
4. Compare streaming source/destination conservation commitments plus per-record
   witnesses; preserve source files. Fsync all pages/roots, then a paired migration
   marker/activation root. Interrupted migration restarts inactive or fully
   validated active; visible activation still needs fresh restart root barriers.
5. Switch matching C/Python/coordinator/compiled Elm together. Old writers reject
   active V7 and cannot downgrade. Rollback is a new explicitly reviewed forward
   migration, never selecting a stale predecessor root. Resume Prepared without
   replay and preserve exact C late admission distinctions.
6. Remove global history limits only after authority, migration, cohort delivery,
   native grant and frontend slot controls pass together. Keep hot64/cohort64,
   cache64, native16 and every overflow/refusal guard. Archive compression/orphan
   reconciliation needs separate conserved-index specification; no primary event
   or predecessor evidence garbage collection is authorized by this proposal.

## Smallest next executable slice

First model and implement a storage-only typed `commitAdmission` plus exact
origin/scope indexes and completion reservation in a fresh derivative. Two origins
with same target, independent stale request/generation, route collisions, quota
exhaustion and crash between every boundary must establish one atomic admission
root. No C/native effect yet. Next implement source-exact frozen V6/sidecar import
with streaming conservation. Paired C lookup/lock integration and compiled cohort
protocol follow only after those gates. Full S15 remains open throughout these
partial slices.
