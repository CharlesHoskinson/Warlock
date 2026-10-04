# Exact runtime closure guard

Before launch validate exact321 descriptor SHA, captured loader cache/tools, all
171 freshly resolved library hashes and actual307/319/315/AQ155 artifact hashes.
After both plugins load, require current same-UID/non-zombie expected child
PID/start, same mount namespace, mapped exact artifacts and every lookup library,
current hash and device/inode identity, and exact executable identity. Reject
alternate/deleted required artifact and lookup-library mappings. Parse exactly
the bounded metadata bytes that were hashed from one fd. Bracket all reads with live
identity and unchanged mount topology. All hashing respects the supplied original
absolute deadline; this module never extends a phase or IPC deadline.
Open pinned files O_NONBLOCK/O_NOFOLLOW/O_CLOEXEC and validate regular fd before
stream creation. Refusals close the fd. FIFO/symlink/directory replacements never
wait for a writer or reach stream hashing. Frozen326 remains the failed predecessor.

First actual self-process test discovered Btrfs path stat device differs from
procfs mapping device on this machine (0:33 vs0:30). Kernel source explains the
different fields: [Btrfs getattr](https://github.com/torvalds/linux/blob/master/fs/btrfs/inode.c)
uses root anon_dev; [proc maps](https://github.com/torvalds/linux/blob/master/fs/proc/task_mmu.c)
uses inode superblock s_dev. Bounded owning mountinfo supplies the latter only
for Btrfs, with exact mount-point stat-device agreement. Ambiguous mounts or an
unmounted nested subvolume refuse qualification. Do not drop device checks.

This is a bracketed diagnostic, not an atomic proof that memory remains
immutable. Additional mapped libraries may exist. This guard does not authenticate
the shell Wayland connection, bind menu/target/controller state, authorize an
operation, verify native callbacks or establish full native acceptance.
