# Exact owned browser runtime data with a detached parent

Frozen BrowserV12 and its actual failed campaign remain immutable. The actual
V12 samples preserve one exact live root FD7 regular0600 uid1000 nlink0 4MiB
O_RDWR file, exact target/device/inode/tmpfs mount, fullsize rw-s offset0 VMA,
exact fresh runtime/profile0700 anchors, and root/compositor lifetimes. Both
samples independently record ENOENT for BrowserMetrics. No deletion syscall or
historical BrowserMetrics inode/mode was observed; no unlink actor, histogram
contents, or installed source-branch equivalence is claimed. The actual
LocalMemory command-line request is a request, not proof of executed allocator
branch or directory lifetime.

## Parent state

A fresh bounded data witness permits exactly two observed states for the
canonical single `BrowserMetrics` component directly under the selected fresh
mode0700 profile:

- Present: current nonsymlink canonical owned full mode0700 directory with exact
  path/device/inode/UID/fullmode token.
- Absent: actual lstat of that exact component returns FileNotFoundError with
  errno ENOENT and the exact requested filename, while the selected current
  profile and runtime remain the same pre-launch owned mode0700 objects. The
  lookup uses an O_DIRECTORY|O_NOFOLLOW descriptor whose fstat and before/after
  named profile identity match that anchor; follow_symlinks=False lookup of the
  single component is relative to that descriptor. Preserve actual ENOENT
  filename and the full canonical requested path.
  This records present namespace absence, not historical directory provenance.

The same parent state must persist through before, after and fresh post-disk
samples. Present/absent changes, directory replacement, symlink (including
 dangling), special file, malformed/unknown/error/nonENOENT observation, or
changed live profile/runtime anchors revoke authority. A confirmed parent
state is retained across successive mapping phases. Absent carries no invented
historical parent inode or mode. Permission and source ownership remain
properties of the actual producer FD and selected live runtime/profile anchors.

## All original predicates

Exact root PID/start/UID/private scope/frozen executable and selected compositor
lifetime, one producer FD number, device/inode/target, fullflags O_RDWR without
O_PATH, regular fullmode0600 uid-owned nlink0 exact4MiB file, exact runtime tmpfs
mount, canonical PID-encoded filename, rw-s fullsize aligned offset0 VMA and
complete observed-batch/fresh root/compositor executable-alias refusal remain
mandatory. Before/after stable FD metadata and fresh post ordinary strict disk
confirmation remain mandatory; timestamps/content/FD position remain mutable.

Only the exact original captured root rawmaps hash and mapping line, supplied
with the actual captured root row identity, can consume a proof. Unreadable,
partial, replaced, disappeared or stale proof revokes input usability. Empty
candidate snapshots must still refuse newly appearing metrics mappings before
input. All ordinary/deleted disk-code guards, original15 browser draft/caret/
Files callback/focus/reload, sandbox/network, lifecycle and desktop-preservation
oracles remain mandatory. Native acceptance belongs to root after source review.

The parent state refinement must pass explicit identity/temporal models before
runtime changes, including detached-parent successful cases and state-change,
replacement, unknown/error, symlink/special and stale-partial adversaries.
