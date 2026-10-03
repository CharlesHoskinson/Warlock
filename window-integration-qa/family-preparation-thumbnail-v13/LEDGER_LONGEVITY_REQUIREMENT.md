# Durable read-only ledger longevity remains open

V20 MAX_HISTORY512 retains complete history and refuses admission BEFORE connection
when full. This is fail-closed bounded QA capacity, not steady-state production
parity. Repeated housekeeping/read-only queries can exhaust it. This packet must
not describe a bounded baseline as sustained production acceptance.

A later formal-first derivative needs durable authenticated epoch reclamation or
rotation. It may reclaim only exact closed and durably published terminal rows,
after immutable receipt/actor/owner consumers are discharged and the replacement
checkpoint/archive is durably confirmed. Preserve unclosed/refused-unpublished/
uncertain or referenced rows; never truncate them to admit new work. Bind old and
new epoch hashes, root/lease/service lifetime, full count/range and retained source/
request identities; make crash/restart between archive, replacement and publication
recover conservatively without duplicate IDs, missing rows or stale observations.

Admission must be blocked while an epoch transition is uncertain or durability
fails. Old batches cannot become usable after reclamation, and live actor drain
must still authenticate its exact jobs. Whole Keeper/native uncertainty/resource
and current receipt guards remain. Native long-run workload/capacity/restart faults
are required later. V4 preserves the512 limit and tests/refuses bounded capacity;
it does not implement, waive or claim durable rotation.
