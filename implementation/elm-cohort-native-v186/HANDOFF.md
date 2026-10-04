# Owned shell cohort and forced teardown

V184 wraps the sealed V178 supervisor and actual V169 native host in one unique,
transient systemd user scope. The wrapper proves the scope ID, cgroup, KillMode,
stop timeout and its unreaped direct child's PID/start/cgroup before admitting
scope cleanup. KillMode=control-group owns detached shell helpers as well as the
main host. Shutdown uses the exact owned unit, never ancestry guessing, desktop
process names or another application's process group. No persistent unit or
installed desktop configuration is changed.

The manager control transport uses the real /run/user/<UID>/bus; the managed
supervisor and GUI receive their original private display/runtime/bus environment.
V182/V183 preserve the initial failure from using the private QA bus for manager
control. Protected launcher, core limit1 and native serial lock are unchanged.

V181 passes7 actual CPU/cohort checks: a SIGTERM-ignoring helper creates a new
session/process group yet remains inside the owned scope; stopping that scope
removes it and its parent after the5-second stop timeout. A separate peer remains
alive and then exits normally. This is actual systemd behavior, not a mocked
process-group model.

V185 passes40 protected native checks: real renderer failure, native recovery
reservation, actual Restart exit3 and supervised replacement, fresh binding and
actual application keyboard input. Cooperative root stop cancels recovery and
creates no third generation. The shell scope excludes the private compositor and
controlled application fixture and has no remaining members at completion.

V186 passes42 protected native checks. It repeats the real first failure/restart,
then verifies and SIGSTOPs the second native host and its related renderer.
Root stop makes the inner supervisor kill its hung native child after5 seconds
and report forced failure (native exit-9, supervisor/wrapper exit1). The wrapper
stops the exact owned scope, removing3 residual helpers, including the renderer.
Observed stop time is5.050s; this is one workload observation, not a release budget.
External application identities and compositor PID/start survive, and actual
keyboard input reaches the expected application after shell teardown. The14-second
outer observation bound is specific to this new forced-stop workload; inherited
check/wait/click/choose/key helpers and original native deadlines are unchanged.
Intentional whole-GUI teardown releases reservations; atomic restart geometry is
not asserted. Forced descendants are recorded as fault cleanup, not normal exits.

The runtime capsule remains18 sealed files from V169 and the V89 owning core/plugin
pair. V171's full137/original91 native checks,37+58+12 typed Elm cases and recovery
Quint6 named/1000 samples are retained, not rerun by these selected campaigns.
No new Quint/native refinement claim is made by using systemd scope semantics.

Application launch is not implemented by this runtime. Before admitting real
launch actions, LaunchService must put applications in independently owned scopes
outside the shell cohort; shell lifetime must never terminate user applications.
The external fixture proves exclusion only for independently launched applications.
Wrapper death/startup-failure ownership races, former authenticated connection and
pending Unknown reconciliation, recovery hotplug/zero outputs, keyboard/AT/IME,
atomic reservation handoff, integrated corrected-core/menu/GPU tuple, full native
window operations, representative devices/user studies/budgets/soak, C00 and release
remain open. No complete requirement, sprint or goal is closed.
