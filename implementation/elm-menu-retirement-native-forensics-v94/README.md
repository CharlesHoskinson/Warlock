# Retirement request starvation reproduction

This packet preserves the V83 native target-retirement failure and reproduces its request starvation with actual compiled held V69 and V87 Controller modules and the actual held V57 C host preflight. No GUI, native socket, production change, or acceptance campaign was run here.

The selected report is `qa/repro-1791109963228797961/report.json`. Both Elm profiles and both actual C preflight profiles pass. The recorded native run reached 133 checks before retirement timed out and cleaned up normally. The evidence packet pins its failure report and log and records exact producer projection51/geometry52 fields. CPU initial request IDs alone are normalized to make the recorded snapshots initialize the worker. This is a deterministic ordering reproduction, not a replay of every recorded native event.

Compiled Elm opens publication7/lease1. A notification allocates two observations in open publication8. Native popup retirement closes lease1; actual C preflight rejects that entire open publication before forwarding either observation. The logical dismiss produces closed publication9 with zero requests while Elm retains both expected correlations. Twenty-one later notifications retain publication9, allocate no replacement requests, and leave the admitted native target stale. Actual C accepts the first closed publication9 and correctly rejects its non-advancing duplicates. No effect intent, request generation, registry or outstanding operation is introduced by the reproduction.

The hypothetical positive CPU control supplies the missing observations, then synthetic empty retirement facts under new correlations. It shows existing decoders and dirty-bit drainage can recover when responses exist; these synthetic responses are explicitly not native retirement evidence. Actual logs independently show native publications94 rejected,95 closed,96 closed and no subsequent projection53/geometry54 forwarded.

The first failed compilation (worker shadowing) and second failed C control (incorrectly expecting a duplicate publication to admit) remain captured in their original report/input directories. The corrected control retains the strict publication and lease guard.

See `notes/shared-recovery-review.md` for V308's additional admission-journal boundary. A generic refusal log cannot authorize cancellation or operation replay. Full native retirement, shared menus and release gates remain open.
