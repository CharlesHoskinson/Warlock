# Browser V13 runtime data source handoff

Frozen V12 sources/proofs and the actual V12 failure remain immutable. V12
failed after four original gates, before input, because the BrowserMetrics
parent was absent in both actual samples. Exact root/FD/VMA/mount metadata and
live runtime/profile0700 anchors remained stable. The V12 failure is a retained
failure, never accepted retroactively.

## Evidence and authority

Actual V12 FD7 is regular0600 uid1000 nlink0 exact4MiB, fullflags32770 O_RDWR,
mount346/device84/inode330537, with canonical PID-encoded deleted target and
rw-s fullrange offset0 VMA. Raw before/after root maps were identical and showed
no executable alias in fresh root/compositor maps. Both parent observations
were FileNotFoundError errno2. Runtime330465/profile330525 matched prelaunch
mode0700 anchors; no historical parent inode/mode or actual deletion actor was
observed. LocalMemory argv is recorded only as a request. Additional official
Brave v1.96.59 package source context matches the recorded version family,
without claiming compiled branch or unlink attribution.

## Formal-first refinement

V12's models and proof plus actual failure are copied into retained source and
failure directories. The V13 contract distinguishes present exact owned
mode0700 parent from stable exact component ENOENT under a pinned live profile.
Independent review required a separate runtimeToken and descriptor-relative
lookup, both incorporated before runtime.70 named cases and2000x100 traces
passed before helper changes in `metrics-formal-detached-before-implementation`.
Review is external `browser-v13-independent-review/model-review.json`.

## Narrow runtime change

Only `owned_metrics_data.py` changes the existing parent observation/projection.
The actual profile is opened O_DIRECTORY|O_NOFOLLOW; fstat before/after and
canonical named profile identity before/after must equal its prelaunch anchor.
Two follow_symlinks=False `BrowserMetrics` lookups use that descriptor. Raw
actual errno/filename/singlecomponent/fullrequestedpath and profileFD metadata
are attached to evidence before predicates. An absent state requires actual
FileNotFoundError ENOENT of the exact child, with no invented inode or mode.
A present directory is opened relative to the same FD and must match both
slot observations, exact owned fullmode0700, and directory device/inode.

Both parent states must match full before/after and post strict-disk samples.
The confirmed parent state remains anchored across successive phases. State
changes, replacement, symlink/dangling/specialfile, nonENOENT/unreadable error,
or named/pinned profile rebinding refuse. Other FD/VMA/source/ownership/mount/
noexec predicates and exact captured root hash/line/row binding remain unchanged.
The V12 classifier/extras/private session bytes are inherited exactly, including
explicit accepted+confirmed+usable gate before mapped_inputs returns.
Mutable timestamps/content/position remain excluded from stable equality.

## Kernel/offline proof

41 CPU-only actual tmpfs/procfs tests include all31 V12 faults and10 new cases:
real unlink+rmdir with surviving one-FD mmap; exact descriptor-relative ENOENT;
present/absent changes between samples and during disk validation; retained
absence changed in a later phase; real dangling symlink and regular-file parent;
nonENOENT and wrongfilename errors; and actual profile rename/replacement during
pinned descriptor lookup. No GUI processes run in these fixtures. Full original
seven models plus metrics model and all Python tests are required before freeze.

Root owns source review, freeze, preflight and the original15 native browser
campaign. This packet grants no native focus/input or installed deployment
acceptance from offline tests. No main GUI/config/sudo/native operations occurred.
