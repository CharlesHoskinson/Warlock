# Shared-host performance calibration

V160 runs the frozen V150 optimized Elm/native host and V89 owning core/plugin
pair unchanged in a protected private session. This is a new calibration workload,
not a repeat of the original 91-case native campaign. V151 functional and V157
hardware-rendering packets are retained as separately hashed evidence.

The workload contains one 800x600 output and two controlled application windows.
After five seconds of warm idle, actual protocol pointer input opens/closes the
window picker 20 times; another five seconds of idle follows. The sampler records
31 host-descendant snapshots, stable PID/start identities, process names, threads,
CPU ticks, context-switch counters, RSS, PSS and private memory. Normal client exit,
plugin unload and protected ordered cleanup pass. All 26 workload checks pass.

Warm idle uses about 0.39% of one CPU core for identities surviving the sample
interval. Each snapshot contains 21 processes: one host, one network process,
three WebKit renderer processes, one Python authority broker, and 15 sandbox/
D-Bus proxy processes. One controller/backend does not imply one renderer process.
PPID ancestry can miss detached workers; endpoint identity equality cannot exclude
short-lived children. This is not complete process-group CPU acceptance. Summed
RSS counts shared pages more than once; PSS/private are also recorded independently.

Helper-start to exact-publication focused DOM receipt is p50 92.62ms, p95 107.67ms,
p99 108.80ms (20 samples, nearest rank). It includes helper spawn, observation
polling and full protocol-log parsing, with DOM/Wayland tracing enabled. There is
no measured instrumentation correction and no native presentation latency claim.

PSS increases from 305238 to 332913 KiB; private memory from 228600 to 245756 KiB.
Initial popup/JIT/cache allocation may contribute; this short run cannot distinguish
bounded warm-up from a leak. Next isolate warm-up and run longer repeated workloads
with sampled cgroup/process-group membership, actual presentation receipts and
production/instrumented comparison before setting or accepting budgets.

V158 failed before launching a GUI because the derivative selected a nested
finally block. V159 omitted Wayland tracing and timed out: the unchanged collector
needs xdg_popup.configure geometry to join DOM observations. Its popup was rendered
and focused in native logs; cleanup passed. Both failures remain frozen. V160
restores tracing and records its unmeasured overhead. Original check/wait/click
helper ASTs and deadlines are preserved; the selected workload changes deliberately.

Current-shell comparative baseline, cold start, dense workloads, full process-group
coverage, actual input-to-present/cadence, uploads/wakeups/VRAM, long soak and numeric
budget approval remain open. No requirement or sprint is closed. No installed
configuration or live desktop is changed.
