# Actual source and intended inverse

Selected frozen runtime: `service-housekeeping-admission-v26`, manifest
e98809f3cee21c3fc8a0447c98c76915cc3083df2ac1090f1531c7fa3b25a1b2.
The intended patch changes two files only; whole-file inverse is generated and
asserted. No runtime source is applied by this proposal.

`NativeDesktop.plan_destinations` is a new bounded scheduler around the unchanged
`plan_destination`. The captured exact member list is copied before workers run.
checked_identity supplies the original typed tuple and duplicate guard. Three
workers maximum;64 submitted slots maximum. Each worker uses original stored
fields/metadata and monitors/workspaces/clients; no native dispatcher or refresh
is invoked by a worker. Independent ReadonlyIPC owns each query descriptor and
registration/EOF/closed/published ledger row; original per-query deadlines stay.
New pre/post/collected guards read the current Scene and received deadline under
the actual shared receipt RLock; no IO/future wait/shutdown holds that lock.

`SceneController.prepare` selects the new capability only for the original
hidden restore members. It receives the complete list in member order, retains
the old generic sequential branch exactly, and checks original receipt expiry
again while holding the existing atomic focus lock before starting effects.
The original per-member apply loop, three refresh loop, metadata/fresh/source
capture/geometry/order/output/seed guards remain unchanged.

The model's running/done/valid plan sets represent3 selected member slots, not
query jobs or the whole64-member population. Each `Done` means the actual
unchanged complete planner returned and its current/deadline guard passed.
`Collect` represents worker drain, complete ordered result extraction and final
guard; no pending worker can authorize effects. Actual64-cap/3-concurrency tests
remain required before application acceptance.

`AdmitMember` represents the unchanged apply_destination's identity/material and
fresh live-client guard. The first admission also represents the added receipt
deadline guard under the existing shared lock. `Dispatch` and `Return` represent
the original OwnedLaunch native-effect dispatch/normal returned completion,
separately; false completion retains unknown native ownership. Six slots remain
monitor0/workspace0/monitor1/workspace1/monitor2/workspace2, no dedup or parallel
writes. The lock excludes new receipt/context authority during the sequence.
Group disappearance cannot replace returned native completion. Once the existing
atomic sequence begins it may cross the scene deadline; the original strict
before-seed deadline remains separate. No new partial sequence or seed authority
is inferred from that inherited behavior.

Source/lifetime/material differences are represented as failed existing member
guards; native monitor lookup/refusal is represented as an unsuccessful returned
effect. Context/successor changes before the atomic focus lock are represented
by current=false. The model does not introduce new native monitor-generation
claims. NativeDispatcher resolution and all original postcapture validation
still matter in the later native baseline.

The exact selected HyprCtl.cpp parser SHA798b7c6c4c1684557842463d46ac99c96629be4179e0e461dca77670247b91fa
matches frozen `qt-modal-private-v9/primary-cursor/HyprCtl.cpp`. Primary
dispatchBatch at1309 continues after errors; client batchRequest at339 discards
request return status. The exact primary parser body is extracted into the CPU
recording harness with format enum/static_cast/ASCII trim stubs explicitly
identified. This only establishes parsing/order/error continuation. Genuine
installed CLI/OwnedCommands CPU execution separately proves exit0 on a middle
error and helper classification. The batch route is rejected for this patch;
no batch ACK or native effect protocol is newly accepted.

The frozen-controller replay's350ms monitor/workspace reply delays demonstrate
reachable original receipt exhaustion, while exact6 focus and3 refresh return
normally. v1 replay fixture accidentally routed batch through a generic dispatch
branch and failed its diagnostic assertion; it remains retained. v2 corrected
only the fixture order and passes. An initial C++ recording stub omitted the
unused output-format enum then static_cast alias; retained compilation epochs
are fixture failures. No product or native failure was rewritten.

## Concrete empty-plan refinement

The actual old/current late all-visible comparison at QA/restore-planning-empty-plan-counterexample-v1 confirms the extra expiry guard incorrectly changed the original nativeEndpointAlreadySatisfied path when no focus was planned. The new guard applies only when plans is nonempty, exactly before the first actual focus effect. The original all-visible no-op path retains its old deadline semantics and exact family/current/native settlement checks. No expired hidden plan receives effect authority. Initial V27 code/14-kernel proof/counterexample source epoch are preserved. NoHidden models the zero-worker/zero-focus branch, not acceptance of an incomplete planned family.
