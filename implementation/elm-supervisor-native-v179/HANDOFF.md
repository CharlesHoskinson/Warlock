# Supervised native shell restart and cancellation

V174 implements an external supervisor for the frozen V169 native shell. A runtime
capsule is materialized from V171's accepted source/build inventory, including
actual compiled Main/Bar/Popup assets and all adapter inputs. The launcher verifies
all18 runtime files, owner-controlled regular paths, no symlink files/ancestors,
exact asset/adapter directory membership, private authority configuration and the
recorded core hash before every generation. Duplicate metadata is refused. It
constructs a fixed argv list and never runs a shell or compositor command.

Only native host exit3 requests another generation; ordinary exit/failure is not
retried. SIGTERM/INT cancel generation creation, forward stop to the owned host and
wait for normal teardown. After5 seconds an unresponsive host is killed and the
supervisor reports failure. Forced-stop child-helper cleanup is not fully qualified;
production service/cgroup ownership remains a release obligation. No unlimited
automatic retry or recurring restart timer is introduced.

V176 adds private O_EXCL generation logs for QA so old/new controller traces cannot
be joined by matching publication numbers. V178 replaces its20ms polling loop with
Linux pidfd readiness and a nonblocking signal wakeup pipe under DefaultSelector.
Native/CPU tests run the actual program, not mocked process return codes. Sources:
https://man7.org/linux/man-pages/man2/pidfd_open.2.html
https://docs.python.org/3/library/signal.html#signal.set_wakeup_fd
https://docs.python.org/3/library/selectors.html

V174/V176/V178 each pass15 actual synthetic subprocess/capsule checks: native-only
restart, failure refusal, changed-next-generation/binary/unsealed-adapter/duplicate/
public-authority/symlink refusal, graceful stop, cancellation of an exit3 race and
forced unresponsive-host failure. These establish supervisor lifecycle and validation,
not native GUI behavior. All predecessors and their packets remain preserved.

V177 passes37 protected native checks. V179 runs the event-driven V178 supervisor
and passes38. The same supervisor actually owns both host generations; the fixture
never launches a replacement host. A real renderer SIGKILL with an open popup reaches
native recovery bars retaining48px reservation, identical window geometry/minimize/
incarnations and actual application keyboard input. A real native Restart click
produces exit3 and a fresh supervised host/backend binding. Coherent snapshot precedes
new effects; explicit fresh activation reaches the expected keyboard recipient.

A second renderer failure reaches recovery; stopping the supervisor forwards native
stop, exits without force and creates no third generation. Native/backend teardown
and protected ordered cleanup pass. All original check/wait/click/choose/key helper
ASTs and their deadlines are retained for this selected workload. V171's full137/
original91 native regression, compiled37+58+12 Elm and recovery Quint6/1000 are retained
separately, not newly repeated or relabeled as this38-check campaign. V179 independently
observes five ep_poll snapshots over2s with unchanged voluntary/involuntary context
switch counts; this proves bounded idle behavior, not complete CPU/wakeup budgets.

The runtime source is exactly V169, including its renderer-sharing and native GTK
fallback. Native layer PIDs are actual sealed ELF children rather than the Python
supervisor PID. Geometry is asserted at failure and after restart, not atomically
across the reservation gap. Old packet refusal uses an independent QA connection;
former authenticated connection/pending Unknown persistence remain stronger open
gates. The existing abstract recovery Quint contract is retained, not automated
supervisor/native refinement.

Production service/forced-helper ownership, pending-operation reconciliation,
atomic reservation handoff, recovery hotplug/zero outputs and keyboard-only/AT,
coherent GPU/menu/corrected-core tuple, full scene/window operations, IME, physical
hardware/usability/budgets/long soak, C00 and release remain open. No requirement or
complete sprint is closed. No installed desktop/configuration is changed.
