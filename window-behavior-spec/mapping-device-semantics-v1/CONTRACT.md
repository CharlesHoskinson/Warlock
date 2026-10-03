# Owned Btrfs mapping device comparison proposal

Status: source/formal proposal for root review. No acceptance predicate has been
changed. Both actual registered QProcess attempts still fail the original
`maps.device == lstat.device` guard. No GUI or installed Process acceptance.

## Observed field meanings

The retained Linux v6.19 primary sources report three distinct facts:

- `fs/proc/task_mmu.c:show_map_vma` obtains the mapping device from
  `file_user_inode(vma->vm_file)->i_sb->s_dev` and the mapping inode from
  `inode->i_ino`.
- `fs/btrfs/inode.c:btrfs_getattr` replaces `stat->dev` with the Btrfs root's
  `anon_dev` and exposes the actual root identifier as `STATX_SUBVOL`.
- `fs/proc_namespace.c:show_mountinfo` obtains the selected mount's device from
  its superblock's `s_dev`.

This is source attribution, not proof that the installed 7.2.7 Omarchy kernel
is byte identical to that reference. The actual kernel witness is independent:
the owned child mapping says device 0:30, while the same canonical named image's
opened FD says device 0:32, mount 33, subvolume 256; the actual selected mount
line says Btrfs and device 0:30. The frozen image hash and inode match.

## Proposed narrowly bounded Btrfs branch

Retain exact current child UID/PID/start/parent/group/final exe/argv/cgroup and
all declared namespace/environment/source guards. Read all candidate raw maps
before validation. Preserve the complete selected row: bounds, permissions,
offset, device, inode and canonical path. Malformed, deleted, unreadable,
missing, anonymous executable and unfrozen code remain refusal.

Only when the current opened canonical frozen regular source's actual
`fstatfs` reports BTRFS_SUPER_MAGIC, require the following conjunction:

1. The source is opened O_RDONLY|O_NOFOLLOW|O_CLOEXEC. Named lstat, actual FD
   fstat, and FD statx match exact subvolume device, inode, full mode, UID/GID,
   nlink, size, and mtime before and after a bounded pread hash. Match frozen
   bytes and full mode. Require statx INO/MODE/UID/GID/NLINK/SIZE/MTIME,
   MNT_ID and SUBVOL result bits; mount/subvolume identifiers are positive.
2. The descriptor's kernel fdinfo identifies the exact inode and mount ID and
   exact read-only flags/access mode. Its actual fd symlink remains the exact
   canonical source. No O_PATH or pathname-only metadata authority.
3. Observer and consumer mount namespaces are the same actual declared
   namespace. Their bounded mountinfo snapshots identify exactly one selected
   FD mount ID. Both actual selected lines are identical before and after;
   the line is parsed completely, its filesystem is exactly Btrfs and its
   device is exactly the original maps row's device. Require its actual
   subvolid option to equal the FD statx subvolume and reject missing/duplicate
   mount or subvolume fields. Do not substitute the block-device filename.
4. The maps inode equals the named/FD/statx inode. Before/after kernel
   `map_files/<start>-<end>` readlink is the canonical frozen source path;
   the original exact VMA row remains present in both captured maps. Preserve
   offset, range and protection, never compare just pathname or hash.
5. Recheck the same registered child identity and declared namespace after
   metadata/hash collection. Any missing, refused, ambiguous or changed
   required fact invalidates the entire witness and all completion authority.

The direct-device non-Btrfs branch stays mandatory for other filesystems. No
fallback merely because that direct branch failed. This proposal is a precise
translation between two kernel-reported device domains, not removal of device
comparison. Cache only within one bounded checked kernel read; never across
leases, source identities, mount snapshots, or VMA changes.

## Explicit observation limits and review question

Actual map_files readlink succeeds. Actual follow stat/statx/open return EPERM,
as retained in both snapshots. Reference `fs/proc/base.c` permits readlink but
requires initial-user-namespace checkpoint/admin capability for follow.
No permission retry, privilege escalation, ptrace, process memory read, or
invented direct mapped-file FD is proposed. The actual descriptor is an opened
current named image, not an FD opened through map_files. This contract proves
agreement of a current immutable named disk image, current kernel mapping name,
inode and superblock-device witness within the captured process/mount scope.
It does not prove mapped memory bytes, historical backing mount ownership, or
absence of changes between observations; predecessor named-file hash guards
also did not read process memory. Root must review whether this bounded
property supplies the intended frozen disk-code authority. If direct backing
FD identity is required instead, the observed EPERM remains a blocker.

Initial diagnostic consumed its own FD read position and therefore reported
full FDInfo inequality. The fresh diagnostic uses pread and captures selected
mount lines before/after; both retained attempts are strict failures. Raw
errors are recorded before any refusal, never interpreted as successful proof.

## Temporal and failure semantics

The model separates a before snapshot, after snapshot and explicit verify.
Replace producer/consumer identity, FD allocation, named inode/device, mount,
subvolume, hash, raw row, path, namespace or protection at either boundary:
acceptance is cleared and must be refused. An observation from an old epoch
cannot confirm a new one. Diagnostic reports confer zero mapping authority.
No native writes, retries, delayed sleeps, or relaxed original feature oracle.
