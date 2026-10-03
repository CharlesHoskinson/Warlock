# Helper lifetime closure before recovery

Actor renderer closure alone is insufficient: a crashed metadata/capture worker
may leave a helper writing actor captures, native exports or cache material.
Recovery must prove every registered helper group has retired before disposing
an actor directory or applying a native endpoint. Missing helper provenance or
an unfinished closure keeps API listening disabled and preserves the journal.

Every helper/renderer leader starts in a private session/group and waits behind
a launch gate. Its positive PID/start, group/session, selected environment and
selected executable material are recorded before the gate opens. A trusted
sealed launcher installs inherited restrictions preventing setpgid/setsid,
namespace creation/joining and privilege acquisition. Descendants retain the
owned group and cannot escape through those syscalls. No numeric killpg or broad
process/name search can authorize cleanup.

An isolated descriptor keeper receives the leader pidfd before exec and retains
it after leader exit and after service death. It authenticates each socket
message with kernel SCM_CREDENTIALS and accepts descriptors only from the exact
service lifetime. The service journal records keeper PID/start, launcher/script
material, exact private root inode and nonce before any job is released. Each
helper job registration is durable before its gate opens.

On service control EOF, the keeper uses PIDFD_SIGNAL_PROCESS_GROUP through the
retained descriptor to retire precisely that kernel process group, including
remaining children after leader exit. It proves every retained group is empty
before writing an fsynced, private, nonce/PID/start/root-bound terminal record.
An unexpected keeper death, unsupported group signaling or restriction policy,
nonempty group, changed keeper material, replaced root or missing terminal
record refuses recovery; it does not authorize numeric PID/group fallback.
Normal helper completion verifies its exact direct exit and empty group before
removing its ownership record. Forced orphan cleanup is never normal completion.

Restart first checks the selected compositor and complete journal, waits for
verified old keeper closure, and checks every durable outstanding job against
that complete terminal record. Only then may renderer/actor directory closure
and fresh durable endpoint preparation proceed. Native capture export callbacks
also require a proven synchronous native completion boundary; an unfinished
export without that proof quarantines the actor instead of deleting its files.

The local kernel header exposes group signaling. Upstream implementation uses
the retained struct-pid group directly, rather than a recycled numeric group:
https://github.com/torvalds/linux/blob/master/kernel/signal.c
This is design support, not identical-local-source or native acceptance proof.
Headless process-group tests must establish local behavior before integration.

Selected helper bytes are sealed before the gate. ELF helpers execute through
the sealed descriptor with their original argument vector. The explicit Python
adapter executes the sealed source with its original `__file__`, argv and import
directory. The explicit Bash adapter executes sealed source with original `$0`
and literal arguments; Bash source-path introspection is unsupported and refuses
before registration. Interpreter material is recorded. These adapters require
independent CPU regressions; no helper may silently fall back to mutable source
execution or an unowned subprocess.

Every job registry publication follows reservation-lock then keeper-lock order.
A group is registered and journaled while gated; actor renderer ownership is also
journaled before release. Recovery uses a new owned keeper for its own queries
and exact core effects after proving the old keeper's terminal closure. Failed
native export/effect returns and timeouts remain uncertain durable jobs, since
partial native work may already have occurred. They cannot become a successful
restart settlement merely because their local process group is empty.

## Confined deadline adapter

The unchanged shell IPC launcher uses GNU timeout, whose default process-group
creation conflicts with the inherited ownership policy. Owned helper jobs export
one exact Bash `timeout` function which invokes the selected immutable
`/usr/bin/timeout --foreground` with every original argument preserved. The
original deadline, `--kill-after` delay, command argv and return status are
retained. The adapter source and root-owned timeout executable material are
recorded. Any existing caller function of that name is replaced for this job.

Foreground timeout does not own a separate process group. Any surviving command
children remain in the keeper's original anchored group; they cannot authorize
normal helper completion or actor disposal. Timeouts/failures of native calls
remain uncertain and quarantined. This adapter changes ownership mechanics and
must be tested with actual CPU timeouts and the original denied-default control;
no successful IPC/native result is substituted by the adapter.
