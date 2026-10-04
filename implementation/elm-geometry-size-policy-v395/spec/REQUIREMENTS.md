# Size-bound contract proposal for ELM-RC-006

This additive implementation contract preserves the frozen baseline242 requirements and the failed native152 representative GTK case. The current authority90/strict geometry projection broadly defines constrainedSize as any bound; changing that contract requires a fresh negotiated wire version or an explicit synchronized producer/consumer amendment. This helper alone grants no native capability or release acceptance.

- SB-001 (ubiquitous): The geometry authority shall intersect client and layout/rule size bounds independently for both axes.
- SB-002 (ubiquitous): The authority shall interpret zero raw client maximum as unbounded and absent/effective DBL_MAX layout maximum as unbounded.
- SB-003 (unwanted): If a bound is negative, nonfinite, contradictory or has a zero effective maximum, then the authority shall refuse geometry operations without changing a window or saved original.
- SB-004 (state driven): While either axis is fixed by positive equal effective minimum/maximum, the authority shall refuse ordinary maximize/restore resizing.
- SB-005 (event driven): When an ordinary maximize intent is prepared, the authority shall check the exact chosen workarea target against both effective axes; a feasible minimum-only bound shall not disable maximize.
- SB-006 (event driven): When exact restoration is prepared, the authority shall check the exact saved logical and visual sizes against live bounds without substituting a new original.
- SB-007 (event driven): When a native callback changes bounds or actual size, the authority shall revalidate the operation's exact target and postconditions before reporting Committed.
- SB-008 (ubiquitous): The authority shall retain stale/full-key/Unknown/ownership/input-block/no-replay barriers and refuse every original scope or mode mismatch.

## OpenSpec scenarios

Given a resizable GTK window with client minimum128x64 and no maximum, when the workarea target is800x552, then maximize may pass the size gate. Given minimum900x64, the same target is refused. Given finite maximum below the target, it is refused; equality and larger finite maximum are admitted when neither axis is fixed. Given layout maximum400 and raw maximum900, the effective upper bound is400. Given contradictory raw minimum500/layout maximum400, geometry is refused. Given a fixed width and resizable height, geometry resizing is refused. Given an original320x180 followed by a live minimum400x64, exact restoration is refused even if maximize remains feasible. Given a malformed bound, the prior saved original is retained. Given stale or Unknown authority context, passing this pure size gate shall not authorize a mutation.

## Integration obligations

Expose validated effective bounds and per-operation feasibility in a fresh strict negotiated projection; version the Python/Elm decoders together. Keep maximize-target feasibility distinct from exact-original restoration feasibility. Native logical and visual target dimensions can differ because of decoration/layout geometry; inspect the real constraint coordinate space before using this helper for each. Recheck after callbacks and test real GTK minima, fixed/maximum-size clients, configure/ACK/RGB, peers, original08/09/10 and exact ABI. No activation or baseline completion from pure tests.
