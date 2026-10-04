# Instance and lifetime recovery isolation

V238 stores host admission and broker settlement under the private runtime at
`elm-window-recovery/<compositor-instance>/<authenticated-lifetime>/`. The broker
opens its journal after authenticating the native lifetime and completes migration
before sending its attached frame. The host binds its admission directory to that
same trusted attached lifetime. Locks belong to each namespace; a live host rejects
a change of bound lifetime. Existing journal records are informational, never a
retry queue.

Legacy records do not identify their instance. Matching-lifetime imports require
a private `legacy-owner.json` containing exactly `schema: 1`, `instance`, and
`lifetime`. Missing or contradictory ownership refuses migration before attachment;
another instance's records and foreign lifetimes are excluded. This implementation
does not infer or provision that ownership record for an existing installation.
The legacy records remain unchanged. Both legacy writer locks must quiesce while
the broker snapshots them. A durable migration plan precedes record copies; after
an interrupted copy, the same plan resumes rather than reading mutable legacy
records again. The completion marker hashes the plan and prevents subsequent
startup from resurrecting a legacy pending action after a new settlement.

V236 preserves the failed C compilation (local variable collision), its admission
failure, and its passing journal checks. V237 fixes compilation but is superseded
by V238's explicit legacy ownership rule and stricter marker type checks. V238
passes 42 filesystem isolation/migration checks, 19 abrupt-writer/correlation
checks, 22 compiled C admission/filesystem checks, the actual host build and its
self-tests, and compiled Elm replay suites of 20, 27, and 30 checks. V241 executes
eight explicitly named Quint scenarios and 1,000 invariant samples of up to 40
steps. Its ownership, stable-plan and isolation contract is abstract; this is not
an automated refinement proof of the native implementation.

V239 seals the V238 native ELF, compiled assets and broker into a 20-file runtime
capsule, retaining the exact V89 core/plugin ABI pair and V229 supervisor behavior.
V240 passes 59 native checks: an actual primary minimize is durably admitted but
held before broker write; the broker dies; existing and replacement Elm views show
Unknown without automatic replay; explicit current-state action gets advanced
identity and commits. Six real screenshot/body-pixel stages and keyboard recipient
checks preserve the actual visible/minimized state across failure and recovery.
The replacement broker uses the same instance/lifetime directory. Owned cohort,
application and compositor teardown pass with recorded exits. Original helper
ASTs and deadlines are preserved. No installed desktop or user drafts were changed.

V242, V243 and V244 prepare restore-unread, minimize-lost-receipt and
restore-lost-receipt scripts on that same tuple. They have not executed in this
packet: the native coordinator conservatively refused while another protected
build was active. Their source preparation is not acceptance. Old V235 four-case
native acceptance remains retained on its original tuple and does not qualify
this changed host/broker build.

Next: execute those three prepared cases through the serialized native wrapper;
qualify normally settled recovery on V238; implement visible storage/migration
failure UX and qualify explicit legacy ownership provisioning. Global old-live-
broker revocation, original restore38/recovery34/case34 timing, coherent updated
geometry/menu/GPU/native91/137 regression, AT/IME, hotplug/zero-output recovery,
physical-device and human UX checks, budgets/soak, C00 and release remain open.
No requirement or work package is marked complete.
