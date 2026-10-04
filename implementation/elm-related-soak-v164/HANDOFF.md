# Related-view renderer sharing and repeated resources

V162 changes only native WebKit child-view construction: popup and output bars
use the primary view as related-view, with distinct user-content managers and
shared existing settings. Checked getters verify manager/context/settings before
use. Constructor convenience API is not used because it inherits the manager.
Navigation policy, scope/capability checks, one Elm controller/backend, parser
and authority semantics are unchanged; all29 Elm modules match frozen V145.

V163 passes137 native checks: all original91 and inherited shared-output135 plus
actual renderer-process observations on one and two outputs. Each has one renderer
and nine descendant processes. Popup focus, output scale/rotation/reflow, remove/
replug and broker interruption/recovery pass. The exact build, original helpers,
assertion calls and deadlines are reviewed/frozen in V163. Retained compiled
37+58+12 checks and Quint10 named/1000 invariant samples are not newly rerun.

V164 repeats the V161 workload unchanged except GUI source: five warm-up popup
cycles, three idle seconds,100 measured cycles and five final idle seconds.
It passes111 checks/115 snapshots with normal exits and protected ordered cleanup.
This selected resource workload does not repeat original91 functional scenarios.

The three-renderer V161 and single-renderer V164 use21 and9 descendant processes.
Final PSS is293830 versus258498KiB, a35332KiB difference in these two traced runs.
Final private memory is202412 versus210676KiB; private memory is not lower here.
Post-warmup private growth is10116 versus10332KiB, so renderer sharing does not
resolve the resource-growth question. Timings include helper spawn, DOM tracing,
Wayland logs and increasing collector parse work; reported distributions are
not production/native-presentation latency. comparison.json retains the raw values.

A shared renderer creates a correlated failure domain. V163 inherits fail-closed
host shutdown on renderer termination; actual renderer-failure/restart recovery
and accelerated shader/display qualification on V162 remain required next gates.
V157 hardware diagnostics apply to the earlier host and are retained separately,
not relabeled graphics qualification of V162. Complete process-group accounting,
cold/dense/current-shell comparisons, instrumentation overhead, long soak, approved
numeric budgets, AT/IME, menu integration, scene and release remain open.

This is bounded implementation/evidence progress. No requirement or sprint closes,
and the installed desktop/configuration is unchanged.
