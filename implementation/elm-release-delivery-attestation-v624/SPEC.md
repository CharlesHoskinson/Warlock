# Release delivery attestation v624

`DeliveryLedger` extends the unchanged v608 `RetirementLedger`. A certificate is
local delivery evidence for an existing historical Released Unknown. It neither
reclassifies an effect as Committed/Refused nor releases a live reservation.

When `attest(ObservationJoin)` receives a complete trusted join, it requires an
exact full record match to an existing Released archive entry. The certificate
contains `id`, `anchorId`, `record`, `proof` and `observation`; `id` is SHA-256 of
the canonical payload excluding `id`. `anchorId` always identifies the original
immutable release, while the proof and accepted read contexts describe the
current delivery attempt. No original proof is rebound to a new frontend.

Each record has at most one latest certificate in `release-deliveries-v1.json`.
The sidecar is explicitly a mutable bounded cache, limited to 64 records and
1 MiB. Its schema is `{schema: 1, lifetime, certificates}`. Replacement requires
a strictly greater native proof sequence; exact payload retries are idempotent.
The first certificate must not predate its original retirement proof. Sequence
freshness is scoped to the same native lifetime, not compared with action or
geometry revisions/read IDs. A typed599 proof and accepted post-proof reads are
caller assumptions, with structural correlation checked again locally.

Both inherited writer ownership and the short host lock cover sidecar operations.
Files require current UID, 0600, regular nonsymlink, single-link ownership. JSON
duplicates, extra fields, invalid counters, foreign anchors, wrong records and
unsafe/missing storage fail closed. Sidecar initialization writes an empty file
before its strict initialization marker. An interrupted empty initialization may
complete on reopening; a populated sidecar without its marker is refused.

Persistence loops over partial writes, fsyncs the new file, closes it, renames it
and fsyncs the root directory before returning a positive certificate. Startup
and reads reestablish a root directory barrier before exposing a visible rename
whose previous fsync may have been interrupted. Storage write, fsync, close and
cleanup failures poison the object; inherited and delivery operations then refuse
until explicit reopen/correction. Ordinary invalid input and stale proof refusal
do not poison otherwise sound storage.

The sidecar does not write V6. Its operations may run the inherited V6 sync,
which can perform its existing exact admission cleanup/import/recovery. Tests
bind parent bytes where no inherited sync mutation is due, and prove that a new
live reservation for the same target remains untouched by attestation.

`delivery_snapshot()` returns a detached durable sidecar copy. `attest()` returns
a detached certificate only after the persistence barrier. The backend/frontend
integration, authenticated current binding selection, read acceptance, and
reannouncement of historical records are future work. A failed delivery cannot
alter the historical Unknown or original release archive.

The existing v608 64-entry definitive history and historical release capacities
remain unchanged. Later S15 needs a scalable archive and a practical effects
lifetime/retention policy that preserves outcome truth, monotonic allocation and
recovery anchors. This packet does not solve that limit or authorize eviction.

CPU evidence uses real private filesystems and the unchanged compiled C admission
producer. Constructable typed proofs and accepted contexts are synthetic trusted
coordinator inputs. Crash tests inspect process-crash visibility and pre/post-call
fault ordering; they do not simulate power loss, authenticate a native peer, load
a compositor ABI, or prove frontend/full GUI acceptance.
