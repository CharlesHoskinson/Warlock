# Integrated bounded recovery store contract

This contract governs V291's broker store; V70's copied SPEC.md remains historical.

- ledger-v4.json is a single atomic schema4 collection: lifetime, up to64 unresolved
  normalized schema2 entries, up to128 full-binding allocation watermarks,
  bootstrapHashes for both legacy singleton files, optional latest schema2 record,
  and predecessorSHA256 for any prototype ledger-v3.json.
- The namespace, positive canonical UInt64 values, binding/context relations,
  protocol/operation partition, exact JSON fields, private single-link files,
  no-follow descriptors and nonblocking ownership rules remain strict.
- Semantic full keys use canonical sorted-key JSON. Member ordering does not
  affect equality; any changed binding/protocol/intent/context does.
- A newly admitted begin returns True only after durable Pending. Exact duplicate
  returns False and cannot authorize a second submission. Any unresolved target
  blocks a different operation/binding on that native incarnation. Neither entry
  nor allocation-scope capacity exhaustion evicts existing evidence.
- Exact terminal Committed/Refused removes one unresolved key; Unknown retains it.
  Latest preserves the most recently submitted key and its outcome; a delayed
  older receipt cannot replace a newer latest record. Watermarks survive settling
  all entries and never regress across effect protocols within a binding.
- Schema1/2 legacy migration retains existing owner-qualified behavior. A strict
  prototype schema3 collection migrates into schema4 without modifying its source;
  later changes to that source or either legacy singleton cause refusal.
- File writes handle EINTR and partial progress and reject zero progress. File
  fsync and successful descriptor close precede rename; directory fsync follows.
  Any write/fsync/rename/data-close failure poisons the current object until
  explicit close, correction and reopen. Post-rename visibility is not successful
  durability when directory fsync fails.
- Recovery returns no executable command. The broker publishes protocol3
  host-recovery-watermarks with current binding and exact request/generation
  strings, then one host-uncertain per unresolved original intent. Protocol1 uses
  its existing wire shape; protocol2 explicitly includes effectProtocol=2.
- Elm accepts allocation metadata only for its current binding during reconciliation,
  merges maxima with its existing allocator, and recovers entries as Unknown without
  changing observed native geometry or inventing settlement. Original full-key
  action guards remain. Fresh independent snapshots establish visible state.
- RecoveryStore's minimal internal settle-record adapter preserves legacy Journal
  fixture/API compatibility. It is not a frontend/native command route; production
  daemon outcomes must pass the actual strict endpoint decoder and full ledger
  receipt validator. read() returns the stored latest record, not invented state.
- Native host admission currently cannot use this collection. No deployment or
  coherent native release claim is allowed until the live host handoff is implemented
  and tested. The128 allocation-scope budget remains an availability gate.
