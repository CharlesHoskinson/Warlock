# Browser V12 independent contract/model review

The contract's narrow class of owned writable nonexecutable tmpfs data is
reasonable. It preserves strict executable/disk-code authority and scopes the
observation to captured owned snapshots. Retained V11 attribution explicitly
does not establish after-FD metadata or executable-alias absence. It cannot be
used as an actual accepted witness for V12.

## Formal refinement gap before implementation

`runtime_metrics.qnt` carries `inode`, `profile`, `mount`, and
`currentSnapshot` as Boolean predicates. The exact FD number, device/inode,
mount ID, profile and parent inode, target, raw root maps hash, and exact VMA
line are absent. Equality of two valid Witness records therefore does not
represent equality of these concrete objects. Replacing one valid object with
another remains `true == true` in the model. Only root `lifetime` has an
explicit temporal identity counterexample. Existing 21 named tests and 2,000
random traces establish the current abstract invariant, not these replacements.

`review_model.py` checks the exact current schema and persists ten concrete
identity changes whose projections are equal under that schema. This is a
refinement counterexample, not a claimed failing Quint allProps trace.

Before classifier edits, add concrete equality tokens for root identity,
selected FD, device/inode/mount, profile/parent, canonical target, and captured
root maps hash plus selected VMA line. Carry access mode and O_PATH separately
from complete FD flags, and preserve complete flags between observations.
Use named valid replacement tests at both verify and post-disk confirmation;
each must remove input authority. Add successful writable-data timestamp
variation without dropping immutable metadata identity.

`fdAccess == 2` must mean the O_ACCMODE result, not full fdinfo flags. The
retained actual FD may have other flag bits. Runtime should require
`flags & O_ACCMODE == O_RDWR`, no O_PATH, and exact full flags across snapshots.
File-position and mtime/ctime/data are mutable; equality should deliberately
exclude these and document the selected immutable projection.

## Minimum runtime refinement

- Validate the exact root PID/start/UID/private scope and frozen executable
  before and after each bounded observation; preserve existing private
  Wayland/bus/socket guards rather than deriving ownership from a filename.
- Capture raw stat/fdinfo/target/mount errors before predicates. In both FD
  inventories require exactly one matching FD and the same number, full
  mode0600 (including special bits), UID, regular type, nlink0, exact4MiB,
  target, device/inode, mount ID and full flags.
- Profile, BrowserMetrics parent and runtime directory must resolve to the
  selected owned private objects, with exact inode/device and appropriate
  directory modes before/after; reject symlink or ambiguous mount routes.
- Require canonical PID-encoded name, selected raw root maps SHA and exact
  parsed/raw mapping line. Only that root row can consume the proof; reject
  descendant/Files/other-batch proof reuse.
- Exact rw-s, offset0, page-aligned full4MiB VMA must match the FD. Compare
  device/inode for executable aliases in all captured owned maps and fresh
  root/compositor maps. Keep the bounded observation claim explicit.
- Post strict-disk confirmation must repeat FD inventory/metadata, root and
  directory identities, mount and fresh VMA/alias checks. Any read error,
  replacement, duplicate or changed selected immutable projection clears
  acceptance before input. A before-only diagnostic never authorizes input.

All browser focus/caret/Files callback/reload, strict new/missing/deleted code,
sandbox/network namespace, main preservation and normal teardown gates remain
mandatory. No native or main operations were performed by this review.
