# Browser / copied Files V8 diagnostic

Fresh derivative of frozen V7. No native execution by this agent.

The root V7 run found one exact compositor producer FD for the copied Files read-only deleted tmpfs VMA, then failed the combined metadata predicate before retaining raw stat. The failed field remains unknown. All 18 main preservation gates and normal owned cleanup passed; no input was reached.

V8 attaches a caller-owned evidence dictionary before metadata collection. It retains full kernel stat fields, full mode and type, target, bounded raw fdinfo and mountinfo with byte length/SHA/base64, selected parsed fields, individual predicate results, and typed/errno read failures before the original checks. Producer-FD before/after comparisons and post-disk-validation confirmation remain required. Any collection error refuses acceptance. No shared-memory contents are read.

The full-mode 0600 predicate is unchanged. runtime_inputs.py, private_session.py, browser_exec.py, network_guard.py, bus_authority.py and cdp_readonly.py are byte-identical to V7. This run is expected to remain a diagnostic failure if mode differs.

Tagged v0.56.2 primary source calls fchmod(fd,0). Bounded disassembly of the exact installed Hyprland binary independently shows mode argument zero at the exported allocateSHMFilePair fchmod call and original requested size at ftruncate. These facts support reviewing a mode-zero contract only after actual metadata is available; they do not establish this actual inode's fields or prove exact tagged-source/build equality.

Offline: 29 owned-data Python tests including mode-zero failure persistence, special mode bits, target/fdinfo read refusal and raw parse failure; all inherited suites and strict failure policies are retained. Frozen closure and root review precede root-only actual execution. No deployment or main writes.

## Potential follow-up contract, not implemented

If actual owned stat confirms mode zero with every other conjunct true, propose replacing exact fullMode==0600 with exact fullMode==0000 in a fresh derivative. Keep regular-file type, UID, unlink count, exact device/inode, mount ID/device, positive bounded file size, RO access flags, exact VMA bounds/offset, no executable alias in captured owned scope, same producer/consumer lifetimes, private kernel peer, FD inventory, before/after snapshots and post-disk-validation confirmation. Do not permit a set of modes or infer acceptance from a name/source alone. Refuse all special bits and all ordinary missing/deleted code. Root review is required before implementing this proposal.
