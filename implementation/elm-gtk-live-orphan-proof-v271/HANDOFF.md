# Actual live adopted-child control

This protected CPU control snapshots the mutable268 supervisor and runs eight
real fork trees. Each primary exits while eight children remain alive; half of
the children create separate sessions. Every orphan must complete normally and
appear in the actual terminal wait-status ledger before the supervisor returns.
The control checks real PID/start lifetime records and completion markers, not
process-group membership. Source changes during testing are reported explicitly.

This is bounded actual process evidence. It does not prove every scheduling
interleaving, absence of all adoption races, GTK/private-bus native acceptance,
or complete desktop qualification. Final source review must also check the
termination decision against current kernel children after irreversible reap.
No GUI, installed configuration, or frozen predecessor is changed.
