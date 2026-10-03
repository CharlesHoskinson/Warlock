# Intended implementation after root source/model review

1. Keep immutable declared expected inputs and one actual started PID/start
   record. Collect fixed raw exec/argv/all-UID/parent/group/cgroup/namespace/
   selected environment and compare to the arm witness at every boundary.
2. Maintain a stack current-snapshot epoch and original monotonic deadline;
   no public caller epoch or success flag. Maximum16 discarded/accepted epochs.
   Each epoch owns its local FDs and cache; RAII closes them before another.
3. A typed MappingChanged result is possible only after an actual ENOENT/raw
   VMA difference is retained, fresh maps independently explain the difference,
   and the original exact child/source/scope still match before/after. Known
   frozen names alone cannot classify it. Other errors remain hard Refused.
4. Each fresh epoch starts with its own whole actual raw maps, backing names,
   FD/hash/mode/statx/fstatfs/flags/mount proof. Every current disk VMA must be
   covered. Do not union rows or stitch before/after from discarded epochs.
5. Current complete collection has actual root and source/VMA boundaries;
   retain them in the invocation record. A second duplicate full collection
   is unnecessary because the single collection already observes both bounds.
   Recheck declared source and all observer/context/current-owner guards before
   atomically recording the proved kernel witness for Process74 lifecycle.
6. Collector model `kernel` describes current candidate eligibility while
   the producer is live. A successful same-epoch observation is committed to
   the original Process74 model as its historical Started(kernel=true) fact
   before exit; later ordinary exit/gone does not manufacture that fact.
   Exit, EOF, receipt and gone still have their independent original gates.
7. Before acceptance/consumption, source/owner/context/receipt checks remain
   exact. A failed registration never turns a successful helper receipt into
   kernel authority. Old witness epochs/leases are inert; current duplicates
   invalidate according to Process74. No input or native actions from observer.

Actual evidence already available: untouched source helper succeeded0 with
owned private CPU peer and full EOF/durable capture receipt; actual generic
observer refused an already absent startup VMA. That evidence establishes
helper functionality, not accepted registered helper usability. The latter
still needs a fresh actual unchanged helper attempt after reviewed correction.
No installed QS/GUI or actual native Pin effect is established by CPU fixtures.
