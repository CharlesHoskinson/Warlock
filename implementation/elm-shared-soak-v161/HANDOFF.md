# Post-warmup repeated popup resource measurement

The unchanged V150 shared host and owning V89 core/plugin pair complete 5 warm-up
popup cycles, 3 idle seconds, 100 measured cycles and 5 final idle seconds. The
protected workload passes111 checks,115 resource snapshots and normal exit/cleanup.
Original functional native91 is retained in V151 and not repeated by this workload.

The post-warmup interval lasts55.35s. All sampled process identity sets contain
the same21 processes. PSS grows10122KiB and private memory10116KiB. Private growth
is mostly in the three WebKit renderer processes (1172,2904,4860KiB); host1336KiB,
broker24KiB. A stable count is not proof of bounded memory or no transient children.

This weakens a claim that all growth is initial popup allocation; it does not
establish a leak without a longer production/instrumented comparison and plateau
analysis. DOM and Wayland tracing remain enabled, collector parsing is included
in timing, and PPID ancestry excludes reparented children. Complete process-group,
true input-to-present, long-soak, current-shell comparison and numeric budgets stay
open. Raw per-process snapshots, ten batch summaries and failures remain preserved.

Next test the V162 related-view renderer-sharing prototype through full original
native cases before claiming process/memory reduction. Existing control policies,
manager scopes and authority authentication remain unchanged. No live desktop change.
