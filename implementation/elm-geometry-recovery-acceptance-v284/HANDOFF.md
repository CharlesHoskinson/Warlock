# Geometry broker and Elm recovery integration, with cold-restart defect

V280 derives from hash-verified held V64 geometry broker sources and V275 durable
journal. One actual broker dispatches both protocols through guarded begin before
native submission, guarded settle before frontend publication, and the existing
inert-by-default protected-QA after-submit hook. The hook now uses the outcome's
actual protocol for the retired-binding replay probe; no new native hook run is
claimed. Startup opens the instance/lifetime journal before attached publication,
then emits informational uncertainty and geometry negotiation. Recovery failures
produce the typed storage reason followed by disconnect. Bounded stream framing,
geometry negotiation, strict endpoint decoders and no automatic retry remain.

V280 executes 193 checks across 25 real daemon subprocess cases plus informational
startup recovery. These use real stdio, selectors and durable files, with an
explicitly synthetic native transport: all five operations and all three outcomes,
transport interruption, mismatched receipt, actual public settlement record,
ENOSPC and directory-fsync EIO injection for both protocols. Pending is read from
the actual file at submission; settlement is read after publication. Normal/failure
exit codes are recorded and remaining children are retired. There is no native
process authentication, configure ACK, actual window mutation, pixels or Elm port
integration acceptance. The unchanged inherited framing suite passes 1,011 checks,
including 1,000 seeded segmentations. Errno injection is CPU evidence, not native
full/read-only storage qualification.

V281 ports typed storage feedback, stale-action ordering and strict geometry
host-uncertain decoding into the reviewed V58 Elm shared controller. It preserves
coalesced dual-observer refresh. The first real compile fails because V58 Binding
lacks the classic recovery lifetime helper. V282 is a fresh derivative adding that
helper while retaining authorityIdentity. Actual optimized Main, Popup and
MenuSurfaceReplay compile. The original menu78/geometry53/refresh21 checks pass,
and 34 new compiled shared-controller checks verify informational Unknown,
operation/protocol/binding/lifetime rejection, duplicate recovery, monotonic
request/generation allocation, no snapshot-as-settlement, same-window action
blocking, unrelated shared IDs, storage notice preservation and explicit reconnect.
No DOM/AT, native menu, geometry pointer or GPU acceptance is implied.

A release-critical issue is now reproduced in V283: durable A=Unknown, unrelated
B=Committed, close writer, open a cold writer. The current single-latest journal
returns no A uncertainty. Three setup assertions pass and the fourth preservation
assertion fails. This is preserved evidence, not accepted behavior. The Elm model
can retain multiple unresolved transactions and permit unrelated actions; the
journal must preserve every unresolved admitted/submitted operation rather than
lose A when B settles. This packet is bounded implementation progress only.

Immediate next work: implement a bounded durable multi-intent ledger with strict
legacy schema1/schema2 migration, exact host/broker correlation, terminal receipt
handling and informational recovery for every unresolved operation; preserve shared
counter monotonicity and refuse capacity exhaustion before native submission.
Replay V283's original identity unchanged against the fresh implementation. Qualify
all cold-restart, interrupted-write and cross-window cases before composing the
native recovery host with the geometry/context carrier. Then freeze and test one
actual host/broker/core/plugin/Elm tuple with original and fault/pixel/input gates.
No completed requirement, sprint or release is asserted. No installed/live desktop
change occurred. Broader storage/provisioning/global old-broker revocation, original
restore timing, GPU/WebGPU, AT/IME, physical/human, budgets, C00 and rollback remain.
