# Proposed field mapping; no runtime guard change

| Contract fact | Actual observation | Refusal |
|---|---|---|
| Selected VMA | Raw initial `/proc/PID/maps` line and exact same line in fresh maps | Missing, malformed or altered range/perms/offset/device/inode/path |
| Actual kernel mapping name | Bounded `readlink` of exact `map_files/start-end` before/after | Error, deleted marker, noncanonical or differing name |
| Current named disk image | O_NOFOLLOW FD + lstat/fstat/statx + bounded pread SHA | Nonregular, special/mismatched mode, identity/hash/read change |
| FD provenance | Actual FD symlink, fdinfo full flags/inode/mount before/after | O_PATH, write access, mismatch, replacement or unavailable evidence |
| Subvolume device | Named/fstat/statx exact matching major/minor | Any mismatch; never compare merely inode and bytes |
| Filesystem device | Actual selected FD mount ID's parsed mountinfo device | Wrong/missing/duplicate ID, changed selected line, wrong filesystem |
| Btrfs branch | Actual fstatfs magic + mountinfo type + statx SUBVOL + selected subvolid | No other filesystem fallback, absent statx capability, ambiguous subvolid |
| Same scope | Registered child PID/start/UID/parent/group/exe/argv/cgroup + all namespace guards | Refused read, mismatched UID, reused PID, changed lifetime/namespace |
| Frozen source authority | Existing immutable input SHA/full-mode/link closure | Missing/deleted/new/unreadable code remains refused |

`MappingDiagnostic.cpp` is attribution code only. It does not implement this
table's acceptance predicate. `ProcessKernel.cpp` still executes its original
device/inode refusal after saving the diagnostic. The current failure artifact
has mappingAuthority=false and strictOriginalPredicateUnchanged=true.

The temporal model uses opaque allocation/field tokens for exact equality
across observations; semantic wrong-device/subvolume/hash/flags facts are
separate faults. The numeric relation model directly compares the two device
domains and requires all currently observed metadata relationships. These
models do not grant GUI or input authority. Their obligation is to invalidate
a bounded candidate witness on replacement, unavailable mandatory facts or
mismatched device-domain translation.

map_files follow stat/statx/open EPERM is retained as an unavailable stronger
proof. The proposed bounded named-image agreement property does not claim
actual opened mapped-target identity. Root review must decide whether that
property meets the intended disk-code authority before any new guard executes.
