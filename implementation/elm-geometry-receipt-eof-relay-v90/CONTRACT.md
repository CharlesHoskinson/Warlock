# Fixed-profile receipt EOF relay

This QA-only derivative preserves V92's actual pump, controls, bounded pipe queues,
three-second EOF deadline, normal-exit proof and failure cleanup. No production
broker or menu source changes. CPU qualification is separate from native scenario09.

The entrypoint is `qa/relay.py ABS_PRIVATE_CONFIG`, executed in protected QA.
The config is a canonical UID-owned 0600 regular single-link file with exactly one
of these closed schemas:

```
{"profile":"broker","authorityConfig":"ABS_PRIVATE_AUTHORITY_CONFIG","controlDirectory":"ABS_PRIVATE_RELAY_DIRECTORY"}
{"profile":"receipt","receiptConfig":"ABS_PRIVATE_V82_CONFIG","controlDirectory":"ABS_PRIVATE_RELAY_DIRECTORY"}
```

The relay directory is canonical UID-owned 0700 and initially empty. Arbitrary
commands, backends, mixed-profile fields and unprofiled legacy configs are refused.
The broker profile executes only V74's owning captured V64 daemon after its exact
component manifest and captured adapter source hashes are verified. The receipt
profile verifies all regular files, modes, sizes and preserved symlink targets
against the exact held V82 manifest, then executes its fixed broker-entrypoint in
fresh `/usr/bin/python3 -B`. The actual V82 entrypoint parses the private receipt
configuration; the relay does not import cached receipt modules or infer native
identity, capabilities or outcome. A bad receipt configuration makes that child
refuse and cannot produce normal exit proof. This relay never creates protocol
frames or retries effects.

Public APIs remain `actor_status(controlDirectory)`, `close_stdin(controlDirectory)`
and `exit_status(controlDirectory)`. Consumers must compare the exact original
relay and child PID/start markers, require `childExit == 0`, `stdinClosed is True`
and actual relay exit0, and verify both original processes retired. Gate closure
captures unread bytes accepted at the relay's observed cutoff using FIONREAD,
drains that snapshot and the bounded userspace input queue before child EOF,
and flushes the bounded output queue before normal completion. Output backpressure
cannot postpone the absolute deadline. Signals are confined to failure cleanup.

For scenario09, actorA's private V82 receiptConfig chooses selectorOrdinal2 and
forwards the first RestoreGeometry06 receipt. Reconnect08 must gracefully close
and retire that exact actor. Only then may the runner archive that configuration
and atomically publish a new private config/new inode for fresh actorB with
selectorOrdinal1. The host's physical reconnect creates actorB; its first matching
RestoreGeometry09 receipt is held. Record both config hashes/inodes, the forwarded
06 packet, exact EOF/retirement evidence and actual matching09 hold/release.
No live actor or pending request may be retargeted. Ordinal counters are process
local. Native full09 remains unqualified until the real frozen tuple passes.

CPU evidence retains all 33 V92 identities (baseline19, queue/deadline7, strict
late-completion7) plus 24 closed-profile/parser/pinning oracles. The first new
profile failure was a test adversary trying to write a copied read-only manifest;
that source/report remains preserved. The corrected fixture explicitly permits
writing its own isolated copy. All V92 failures and inventories remain unchanged
and referenced through `parent.json`.
