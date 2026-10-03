# Fresh native recovery contract

This fresh source design inherits the frozen Service V12 runtime semantics. It
does not change V12, launch a daemon, or authorize native actions. Recovery never
reuses a previous visual scene's readiness, presentation, validation, or source
path as authority.

Before listening, restart holds the same private runtime lease and reads one
checksum-validated exact compositor-session journal. Old V12 journals lacking
the provenance below continue to refuse unresolved restart. Journal recovery
requires both the accepted symbolic direction ledger and every old actor's
resource ownership record; the latest operation field alone is insufficient.

## Accepted intent

The recovery snapshot records all unresolved pending requests, complete family
receipt ownership, compressed direction anchors, and remaining intent events.
Each receipt is a positive typed integer no greater than the durable serial.
Each identity contains a canonical address, stable ID and positive typed PID.
Constant intent remains constant across partially committed native endpoints.
Anchored toggle/activate is resolved only from fresh exact native state. Direction
composition follows the same Direction implementation as ordinary receipt flow.

Recovery planning receives a fresh complete exact family from a trusted observer.
It combines direction anchors and events only for that family's exact members.
Multiple different anchor receipts in a merged family refuse; no receipt wins
through PID, address alone, timestamp, or journal iteration order. A newer event
outside the family does not supersede that family. Every recovered member must
belong to the latest family receipt scope and to this fresh complete family.

An absent identity or incompatible family cannot authorize any endpoint write.
An explicit cancellation outcome may discharge such work, but must be durable
and is not a successful endpoint settlement. The original journal stays intact
if planning, resource cleanup, durable recovery preparation, or observation fails.

## Old resource ownership

Every live/retiring actor is recorded even if it has no current scene. Provenance
must include renderer PID/start, selected session and executable material, actor
directory device/inode and source ownership. Restart must first prove old owned
renderers cannot present or emit callbacks. Missing/replaced identity never
authorizes signaling a different process or deleting a replacement directory.
No broad process search, basename match, inherited journal image deletion, or
old callback replay is allowed. Normal shutdown and crash cleanup remain distinct.

## Settlement boundary

A pure plan carries receipt and exact identities, without native authority.
Before each write, the runtime requires a durable recovery preparation, fresh
selected compositor PID/start/socket proof, fresh complete family/geometry and
workspace/output proof, unchanged latest receipt scope, and retired old renderer
authority. The guarded pinned core handles one exact endpoint at a time.
Restore orders owner before descendants and focuses the exact captured focus
member only after surviving members are visible. A crash during recovery may
repeat a guarded idempotent endpoint, never reinterpret a constant accepted
direction from the partially committed visibility.

The journal is cleared only after all outcomes and old-resource closure are
durable. API listening and new actor construction occur afterwards. Full native
recovery acceptance requires crash/restart during initial pending metadata,
presented reversal, partial family commit, output replacement, member closure,
and another recovery crash, with exact main preservation and no orphan resources.

## Current artifact scope

`native_recovery.qnt` models the settlement authority boundary. The pure
`recovery_intent.py` component validates and reconstructs family direction from
durable anchors/events using the existing exact Direction semantics. It cannot
write native state. Native journal provenance emission and runtime resource/
endpoint integration remain required before this design can become Service V13.
