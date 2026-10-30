# Optional cancellation coordinator and daemon

The coordinator attaches the selected strict client's current binding to the
actual V7 store and serializes native calls after durable attempts. A complete
terminal response is stored, exact admission is retired and ACK permission is
persisted before native ACK; the exact ACK is stored afterward. Native RPCs run
outside host_guard. Duplicate operations return retained exact responses or
refuse; they never grant a second commit attempt. Startup historical records do
not create native execution or ACK rights for a restarted grant.

Actual protected repository test groups pass: 140 lifecycle/ordering checks,
52 daemon-selection/unwind checks and 110 historical-startup/dispatch checks.
Counts include positive lock-depth assertions; they are not feature counts.
Tests use real V6/V7 files and production validators, strict native-schema
response doubles and inert service/event objects. Final outputs and hashes are
in checks/report.json. Default omitted/false mode never imports the coordinator
and selects V6 only in legacy-compatible namespaces. Any V7 ledger or marker
refuses before legacy migration; switching the flag off cannot downgrade custody. Explicit internal Boolean cancellationOptIn=true
selects V7 and the coordinator; non-Boolean config refuses before connection.
Normal context unwinding detaches before closing storage. The tests stop main
at its actual startup-publication boundary; no full event-loop/EOF/native session
journey is implied. Direct dispatch reaches prepare/commit/ACK once only in the
explicit coordinator mode and rejects new kinds without fallback in default mode.

Tests also exercise stored attempt failure before RPC, binding drift before/after
RPC, old/new grant separation, interrupted post-certificate finish, late duplicate
controls, and an adversarial correlated Prepared reply after Unknown. That reply
sequence is a defense-in-depth control, not claimed to be valid native ordering.
A poisoned standalone coordinator must be closed by its caller; daemon ExitStack
owns that cleanup. Poison already refuses further calls before detach completes.

The unchanged persistence model and prior actual 24 named/nine bounded samples are
referenced by manifest hash, not newly run here. Source correspondence is bounded:
that model does not prove wire parsing, RPC authentication, event I/O, dynamic
connections, physical input or C/Elm routing. The existing store fault/capacity
results remain separate evidence. No new original ARC007/008/012/013 verdict.

The production host still does not emit/accept these lifecycle messages or
consume host-cancellation-recovery; Elm issued/prepared/Cancelled routing remains
unimplemented. Host-issued original deadlines and companion Pending admission
are next-stage work; canonical request values in these tests do not establish
frontend clock authority. Physical Escape, native generation resources, live
transport, main-session deployment and release acceptance remain open.

Diataxis: coordinator test how-to and protocol/status reference updated; ownership
explanation covers current-grant attachment and cleanup; source-navigation tutorial
unaffected because its safe read-only path/commands remain unchanged.

The final coordinator report uses the isolation-corrected store94dc/helpera119,
reconciliation6cd8 and journalba709. See the adjacent cancellation-isolation packet
for both retained RED defects, current store checks and the reduced isolation
model. Earlier model-correspondence.md reviews its recorded older source tuple;
it is historical correspondence, not approval of these additional guards.
