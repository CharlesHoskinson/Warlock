# Atomic surface rejection and request recovery

This is a source review and interface requirement, not an implemented fix or
native acceptance. It applies to the singleton retirement failure preserved in
V83 and to the shared schema5 integration in V305/V308.

The recorded failure rejects an entire surface publication after native popup
retirement. Elm has already allocated observation request IDs in that publication.
Those requests never reach the backend, but subsequent notifications only set a
dirty bit while Elm waits for their responses. Recovery must align Elm's request
tracking with the host's actual admission boundary.

## Three distinct boundaries

1. `surface_preflight` validates the whole frame, lease, request batch and queue
   capacity before mutation. A rejection here proves that this invocation has
   not journaled, queued or forwarded any request from the batch.
2. `admission_batch` records operation admission before surface changes and
   backend dispatch. A failure here has a different disposition: recovery must
   follow the admission journal's actual guarantees. It cannot inherit the
   preflight-unsent guarantee merely because it reaches the same log label.
3. `popup_open` can fail after successful admission and before the request loop.
   The present function returns at this point. Durable operation records and
   frontend expectations require reconciliation even if nothing was queued.

V305 currently prints `surface-refused: commit-preflight` for both the first
boundary and failed admission. That diagnostic string cannot serve as an
authorization to cancel or repeat an operation.

## Required recovery contract

The host needs a typed disposition correlated to the exact publication, popup
lease, live output view ID/generation, and complete submitted request batch.
It must be issued to the submitting controller through the authenticated host
channel. A stale, foreign, malformed, duplicated or partially matching response
must not cancel current request slots.

For a proven preflight rejection, the controller may retire only matching
unsent observation slots, invalidate their old IDs, and obtain fresh observations
under fresh IDs after reconciling popup ownership. A delayed response using an
old ID must remain stale. Preserve notification coalescing and bounded queues.

An operation in the rejected batch needs its own exact unsent disposition before
its local Pending record can become a terminal refusal. This is not a fabricated
native effect outcome. Never replay the user's action automatically, retarget a
sent intent, or erase another operation's Pending/Unknown barrier.

Journal-admitted operations require the existing schema5 admission/recovery path.
The shared host must preserve its single Elm allocator and exact operation keys.
If receipt delivery is uncertain, fail closed and retain the unresolved record.

## Qualification obligations

- Replay the actual popup-done / publication / dismiss ordering against compiled
  Elm and actual C preflight, preserving the original failed packet.
- Reject stale publication, wrong lease, retired/replaced output owner, altered
  batch, duplicate disposition, and late old observation responses.
- Exercise rejection with observation-only, operation-only and mixed batches;
  keep unrelated operations and uncertainty barriers intact.
- Distinguish preflight rejection, admission failure and post-admission popup
  failure, including durable-record reconciliation.
- Preserve the original native target-retirement scenario, replacement identity,
  physical input route, cleanup, and absolute six-second transition deadline.
- Run the combined shared host and staged menu path on one reviewed owning
  core/plugin/Aquamarine tuple. CPU reproduction is separate from native proof.

No predecessor evidence, lease guard, production source or deadline was changed
by this review. The full S01–S16, release and deployment gates remain open.
