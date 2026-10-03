# Exact recorded source aliases in collector closure

Fresh V9 full CPU epoch1 ran144 actual tests:143 passed, one original unchanged
freezer test failed because collector_v9_closure.add_file requires lstat regular
and refuses byte-input/link overlap. Frozen V24 legitimately records /usr/bin/cc
as a byte/mode input AND symlink cc -> gcc. Its target is a regular source file;
input hash/mode refer to target bytes. This is a closure collector defect, not a
product renderer failure. The failed suite and approved seven-file epoch remain.

Before any correction, specify exactly these existing frozen packet semantics:

1. Every byte input requires its exact declared mode and complete file hash.
   An ordinary regular path is allowed only if no link declaration conflicts.
2. A named symlink byte input is allowed only with an exact selected symlink
   declaration from the packet, or the already pinned union. Both must agree
   when present. The resolved backing path must itself be an explicitly captured byte/mode
   input, with the same expected digest/mode. Named target, regular type, full hash and target
   mode must match. No unknown symlink source is accepted from matching bytes.
3. Verify all selected link identities before resolving bytes, record the selected
   link and verify all selected links and named target again after hashing and
   target stat. A changed target with identical bytes is a failure. A target
   directory, socket, missing material or changed target mode is a failure.
4. Overlap between byte/mode and link maps is permitted only for such exact
   named aliases. Conflicting hashes/modes/targets across packets refuse.
   Prior byte/link pairs remain recorded together; neither erases the other.
5. Full frozen V24/V7/V8 inputs and all actual failure evidence remain mandatory.
   Every original144 test/outcome assertion, all baseline38/fault34 gates and
   deadlines remain unchanged. Only closure interpretation changes; no product
   runtime, native helper, callback role, receipt or effect authority changes.

The finite model checks exact recorded source alias/material/mode agreement and
cross-packet conflicts. It does not claim an atomic global filesystem snapshot.
Actual CPU/kernel tests must exercise real regular files/symlinks, same-byte
wrong targets, absent declarations and modes. The complete freezer source
verification is still necessary before and after adding evidence.

The proposed external root freezer must apply this same recorded-alias rule to
all inputs/modes/links while adding source-ready/design/proof/review evidence.
No candidate or proposed freezer changes are applied until root source review.
