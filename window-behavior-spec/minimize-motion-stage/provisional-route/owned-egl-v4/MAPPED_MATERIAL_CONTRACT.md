# Same-domain mapped Mesa material guard (before implementation)

V3 rejects the actual supported Arch Mesa/Intel backend because fstat and proc
maps use different device domains on Btrfs. Linux7.2.7 btrfs_getattr substitutes
root->anon_dev for stat.dev; proc maps and PROCMAP_QUERY use inode->i_sb->s_dev.
The exact v3 failure and all83 inputs remain unchanged. map_files readlink is
accessible, but stat/open return EPERM even for our own ordinary mappings.

V4 keeps device comparison. Before creating a probe it records existing named
mappings (bounded4096 lines/64 matching segments). It hashes the opened immutable
file descriptor, then creates a temporary read-only mapping of that same fd.
PROCMAP_QUERY supplies file-backed device/inode/path/buildID for both the probe
and every candidate existing segment in the same kernel device domain. The
probe may never be treated as a preexisting loaded library. Existing mapping
path/inode/device and pinned actual ELF buildID must match the hashed fd proof.
Unknown ioctl, missing/partial/mismatched ELF buildID, changed/replaced/deleted
mapping or query range, wrong digest and unmapped material fail closed. The
kernel holds vm_file while parsing buildID. No root or new GUI connection is
needed. Temporary mapping and descriptors have RAII cleanup.

Each source library emits independent canonical path, file/stat identity, hash,
probe identity, existing map/query identity, buildID and exact rejection reason.
Only complete material proofs plus the reviewed hardware/version predicate can
allow source upload/readiness. Generic non-ELF primitive tests have no backend
authority; the production material predicate requires exact pinned nonempty
ELF buildIDs as well as its full SHA256. Real tmpfs and Btrfs mappings, identical
bytes/path replacement with new inode, deleted/unmapped/wronghash and changed
buildID must be tested offline.

The idle producer must commit its transparent initialization once per output,
then await a route or output generation change. Existing route/start/readiness,
actual feedback binding and cleanup semantics remain unchanged. GPU context and
material proof initialize once; snapshots upload once per accepted seed.
