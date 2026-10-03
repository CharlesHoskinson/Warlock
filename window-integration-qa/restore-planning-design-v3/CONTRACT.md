# Bounded concurrent destination observations

This source proposal changes only the scheduling of independent destination
plans. It retains the six original monitor/workspace focus operations in member
order, their individual owned native-effect jobs, and the three sequential
motionRefresh calls. It does not group or parallelize native writes. It does not
change the hidden capture path, source-count acceptance, original2s receipt,
query timeouts, fallback, renderer or exact family/context validation.

## Evidence and chosen scope

Frozen V26 `NativeDesktop.plan_destination` performs only stored state/metadata
reads and the five-request adapter's fixed monitors/workspaces/clients queries.
Its independent production module performs no assignments on that path.
ReadonlyIPC has separate owned descriptors and exact peer/EOF/durable completion
for each request; its shared lock serializes only publication and confirmation.
Plans can complete in different order. Results must remain in original member
slots. NativeDesktop.apply_destination still rereads stored fields/metadata and
fresh exact live client identity before each member's two effects.

Primary HyprCtl.cpp matches the frozen selected source byte for byte. Its exact
dispatchBatch body continues after an individual error. Actual installed
hyprctl's batchRequest discards request's failure status. The CPU replay observed
exit0 with a middle error and existing OwnedCommands classified batch as helper.
An authenticated batch would require a new semantic completion/ownership API and
additional per-operation guard mapping. This proposal chooses readonly planning
scheduling to retain existing native ownership semantics.

## Scheduling and authority

For 1..64 selected hidden members, at most3 workers call the unchanged
plan_destination function. No lifecycle/receipt/Keeper lock is held during plan
IO, future waits or worker shutdown. Before each plan and after its complete
result, briefly acquire the existing receipt lock and check exact current Scene
object plus receivedNs+2000000000. A stale/expired/error plan cannot publish a
usable slot. The deadline never restarts. Pending not-yet-started plans cancel
when any failure/current change is observed; already registered readonly calls
still own their normal close/EOF/durable terminal obligations under their
unchanged individual timeout. Drain every worker before returning or raising.

The controller receives a complete ordered list only after all workers drained,
then rechecks ownership and the unchanged receipt deadline with its existing effect lock before the first focus operation. No partial list enters
focus, refresh, metadata validation, capture or seed. On error, the unchanged
controller reject/fallback path remains responsible for native settlement.

## Existing effect and deadline semantics, explicitly retained

The complete-family receipt lock excludes replacement during the existing
six-effect focus loop. Existing per-member stored/lifetime rereads and the
individual sealed OwnedLaunch native-effect classifications remain unchanged.
Each native call retains its original2s timeout. A nonzero/timeout can follow
partial work: later operations stop and the exact unfinished native job remains
uncertain. A completed job must not be inferred from process disappearance.

The original focus loop can cross the original scene deadline after it starts;
this proposal does not redefine that loop or infer a deadline-triggered undo.
Actual positive return and owned normal completion still matter, and seed is
strictly prohibited at/after the original receipt deadline. Native deadline
fallback and reduction continue to use all original guards; ready does not skip
them. This model represents effect dispatch/returned completion separately and
does not claim native presentation acceptance.

Context or current Scene replacement before/after a plan prevents its slot from
conferring current authority. Source/stored lifetime changes still refuse at
the original per-member recheck. A monitor's configured name is resolved by the
unchanged native focus handler, not assumed to pin its old object generation.
Missing/replaced monitor dispatch errors retain native uncertainty. Fresh final
family, geometry, source/order, outputs and original2s before-seed gates remain.

## CPU scope and requirements

The frozen-controller CPU replay uses real OwnedCommands/OwnedLaunch/Keeper,
ReadonlyIPC/NativeSession/RuntimeLease/JournalStore and genuine private Unix
peer/EOF. The peer imposes explicit350ms monitor/workspace reply delays. All
six focus calls and three refresh calls run; original2s before-seed refuses.
The family/pixels/settlement and shell refresh are explicit nongraphical fixture
boundaries. This proves reachable preparation cost; it does not identify the
historical native slow call or prove PNG/renderer/native parity.

Before source application, root reviews the exact intended two-file diff and
formal source map. Required actual CPU tests cover ordered positive slots,
cancel/error/timeout workers with no effects,64 capacity/3 worker bound, source
and lifetime changes at existing apply rechecks, exact six native jobs/order,
unchanged3 refresh, and deadline crossing/partial native uncertainty. Original38
and fault34 remain unchanged and require later root-owned native acceptance.
