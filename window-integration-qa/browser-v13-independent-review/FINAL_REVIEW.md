# Browser V13 independent runtime review

Source refinement and CPU tests **PASS**. `runtime-review.json` records the
independent 41-test replay in an isolated QA scope, 73 input hashes unchanged
before/after, all original 31 test ASTs unchanged, and byte-exact reconstruction
of the inherited helper after removing only the reviewed parent additions.
The three classifier/session wiring files remain exact frozen V12. The final
70-case model and contract still match the recorded proof before implementation.
The full 162 Python / 139 named / eight model report's source hashes were also
verified; that full suite was recorded by the implementation owner, whereas
this runtime review independently reran the focused 41 tests.

The added observer opens the exact profile with `O_DIRECTORY|O_NOFOLLOW`,
checks its descriptor and named path against the prelaunch anchor before/after,
and performs two nofollow `BrowserMetrics` component lookups relative to that
descriptor. Present state requires owned full mode0700 and agreement with an
opened child descriptor. Absent state requires actual errno2 and the exact
component filename, retaining the full requested path. Dangling symlinks,
special files, permission errors, a wrong ENOENT filename, rebinding and state
changes fail. Real kernel fixtures cover detached absence and revocation across
the initial samples, disk confirmation and later phases. Both complete samples
retain diagnostics before metadata validation.

The observation proves the selected current namespace state at the bounded
samples. It makes no historical parent inode/mode, source-branch equivalence,
deletion actor or continuous observation claim. Identity-preserving changes
which happen and revert entirely between samples are outside that bounded
scope. Mutable data/timestamps/FD position remain outside authority as in V12.

All inherited exact FD/full flags/0600/UID/unlink/4MiB/mount/device/inode/target,
raw root hash and line, VMA bounds/no executable alias, producer/compositor
lifetime, invalidation and post-disk input confirmation predicates are retained.
No general deleted mapping or executable code exception was added. Frozen V12
and its actual failure remain unchanged. Original sandbox/network, browser
draft/caret, Files callback/focus/reload, main preservation and normal cleanup
requirements remain gates for the root-owned actual run.

No native process or input was launched by this review. Actual Browser/Files
behavior remains unaccepted until that run completes. This external review
directory is stable for inclusion in the new frozen packet.
