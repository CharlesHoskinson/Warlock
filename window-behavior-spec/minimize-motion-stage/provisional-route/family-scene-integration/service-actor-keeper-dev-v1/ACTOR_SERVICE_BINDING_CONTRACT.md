# Actor Keeper integration into the current service

Fresh source derivative only. Base is frozen service-readonly-ipc-v20,
manifest SHA d3d836eda0e2a25681df4ca80740ca94f8d2084ea1c48f8834293b740122c068.
Existing V16 runtime already implements the authenticated sealed Keeper actor
ledger and RPCs. Preserve that implementation and its meaningful kernel tests;
do not reimplement or claim those primitives constitute completed cancellation.

First wire NativeFactory's actor_record callback into the real RuntimeService
journal. Preserve helperOwnership's existing complete schema and readonlyOwnership.
Publish actorOwnership separately, with complete jobs/freezes/revisions/fault.
The manager reservation lock precedes the Keeper lock. Failed publication faults
the actor ledger and must retain existing unresolved jobs and owned captures.
Factory snapshots are observations, not cancellation or native-effect authority.

Successful native-effect/export process exit and physical group disappearance
cannot complete a native job. Port V16's exact unresolved-job behavior. A future
guarded caller must validate its actual returned result and bind exact job,
source, PID/start, actor, current receipt/token/full scope to a durable semantic
journal entry before Keeper.native_returned. Missing/stale/partial/uncertain or
unpublished result remains quarantine. No fabricated result, zero-exit shortcut,
Boolean quiet flag, whole-Keeper stop or dropped history supplies this proof.

This first derivative must refuse normal factory closure when the actor ledger
faults or has unknown/unreturned jobs. Whole-Keeper crash cleanup remains the
existing exact descriptor mechanism; source disposal and user completion cannot
be inferred from that cleanup. Pending cancellation cannot settle the endpoint.

Semantic caller wiring, authenticated current-receipt ingress, controller
non-settlement retirement, recovery ledger validation, normal renderer/worker
drain and final source disposal are mandatory subsequent integration steps.
The first derivative is not native-ready until they are complete. Existing V20
baseline/fault oracles, deadlines, V16 cancellation contract, V18 reduction and
all Windows parity requirements remain in force. Both 512-history bounds need
durable reclamation before production longevity acceptance.

Run this binding model before copying/changing runtime. Then reuse actual V16
kernel tests against the fresh service integration and add only meaningful
factory/journal/fault boundary coverage. No GUI, main desktop or deployment is
authorized by this source checkpoint.
