# Broker release delivery recovery v630

This derivative uses the v626 startup staging and the exact v624 DeliveryLedger.
Its production changes are the RecoveryStore ledger selection and reconciliation
announcement/delivery logic. No original v608 release archive or effect outcome
is changed, and no native effect is replayed.

After synchronization, the coordinator combines live Unknown entries with exact
historical Released Unknown records. The combined census must fit 64 records
before the first announcement or native proof request. Every full record precedes
proof publication. Historical records retain their original binding, intent,
protocol and Unknown status. Distinct scopes still have serial proof-ready and
current read barriers; queued pre-ready replies cannot release reservations.

For each accepted current action/geometry pair, the coordinator ensures an
existing durable Released disposition through the inherited `release(join)`,
then calls `attest(join)`. Only the fresh certificate can provide the subsequent
wire identity, proof and observation. Its immutable original `anchorId` stays in
the durable sidecar; the frontend wire remains exactly `{id, proof, observation}`
inside the existing host-reservation-released frame. The coordinator never
relabels original archived proof/read IDs with a new binding.

The v619 ReconciliationFrame decoder is byte identical to v626. It requires a
64-lowercase-hex delivery ID and exact proof/read correlation, without computing
its hash or requiring an original archive ID. The fresh certificate ID is thus
compatible. Adding anchorId to the strict wire trio is forbidden. The tests
demonstrate acceptance of the actual certificate trio and refusal of that extra
field using the compiled public controller.

The main regression feeds one compiled controller trajectory across broker
disconnect/reconnect, preserving the old UI Unknown reservation after the first
release output is deliberately lost. The reopened real store has no live old
reservation, yet reannounces its archived Unknown, obtains a fresh typed proof
and current reads and persists a new certificate before publication. The
controller clears the retained UI reservation while history/transaction remain
Unknown. The original V6 bytes and first proof are unchanged.

An unrelated new live reservation for the same target remains live. A real
sidecar file-fsync fault in the coordinator path prevents any release frame,
poisons the writer and preserves original history plus that live reservation
after reopen. The combined-65 census control is explicitly synthetic, with
distinct valid-shaped live keys; it refuses before partial announcements.

Actual C admission writes, real private stores and the actual Python coordinator
are exercised. Proof transport, captured read payload adaptations and frontend
transport delivery remain synthetic. The controller is compiled from held v619
sources, independently of the copied v626 GUI files: Desktop.elm differs between
those frontend revisions. No complete v630 GUI build or native authentication,
power-loss, desktop deployment or native acceptance is claimed. A later coherent
GUI derivative must merge the reviewed frontend and backend and qualify it.

Both combined recovery and the inherited archive/definitive history remain
bounded. The v608 64-history effects lifetime problem and scalable archival remain
later S15 obligations. Reconciliation is not an unlimited archive or an eviction
policy.
