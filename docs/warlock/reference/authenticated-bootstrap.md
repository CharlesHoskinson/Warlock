# Authenticated bounded bootstrap

Original requirement **ELM-DEL-010** requires the native service to authenticate
bridge peers by local user identity and approved session lifetime before accepting
effect requests. Its verification retains credential traces for allowed and
cross-user/replayed sessions. Original IDs, scenario oracles and deadlines remain
unchanged.

The implementation is the public `Warlock.Bootstrap.runBootstrap` route in
`implementation/warlock/haskell/runtime/`. Each frame uses the same selected
process, approved registration, scope, ingress and original absolute deadline.
Authentication checks kernel `recvmsg` credentials for fragments and checks
current authority again before calling subsequent policy. A callback and its
fixture ACK establish admission only.

The host retains a peer descriptor to check endpoint identity. Normal child exit
therefore does not by itself produce stream EOF. Completion must preserve that
identity check, the original deadline and nonreaping process custody; it must not
turn cancellation, timeout or an authentication refusal into success. EOF before
any delivered request remains refusal.

`persistent-bootstrap-controls` links the ordinary production library rather
than compiling runtime sources with admission-test macros. Root independently
pins its actual child executable. The seeded requests use distinct full-width
identities, reordered sends and fragmented writes. Negative controls retain
malformed and foreign-binding refusals, an unrelated kernel sender, buffered input
after retirement, a request sent after retirement using an ACK barrier, and empty
first EOF. The legacy normal-exit and exact-race controls remain separate.

The `common` mode does not exercise a different user. The unexecuted `full 1`
mode needs a qualified delegated mapping and actual same-PID writer UID change.
A namespace UID label, synthetic credentials or a same-user fork cannot replace
that observation. Missing `newuidmap`/`newgidmap` and a timed-out graphical
authorization attempt remain a recorded prerequisite; no package was installed.

## Current verification

The final protected run passes production `build all`, all 25 suites and 37
invocations without timeout or forced cleanup. Its 14 public-library cases admit
31 distinct positive requests and five authorized negative-control prefixes;
every refused suffix has zero callbacks. All eight positive cohorts complete
normally. Post-retirement send and buffered input refuse `ScopeClosed`; the
unrelated same-user sender refuses `ForeignProcess`. Empty first EOF has zero
credentials/callbacks and a refused operation.

Twenty-seven explicitly selected model tests pass. Separate sampled campaigns
cover 10,000 general 100-step traces and 10,000 focused 30-step conversation
traces, with no safety violation. The general campaign reaches no repeated-frame
witness; the focused campaign reaches 47. These are separate coverage results.

The first public-library baseline reproduced the one-frame defect. Initial
candidate compilation found an extra parenthesis; the next candidate exposed
the retained-peer completion defect through the unchanged legacy normal-exit
test. [The retained report and archive](../../../implementation/warlock/qa/evidence/persistent-auth-20261101/report.json)
preserve these failures, the earlier model-selection/coverage failures and final
source, plans, executable pins, logs and credential traces. The fixed owner ends
its retained peer write direction only after the same nonreaping session observer
confirms child exit; its watcher is joined before leaving the approved scope.

The [runtime README](../../../implementation/warlock/haskell/runtime/README.md)
contains the tutorial, protected-check procedure, public API and retirement
explanation. Native effects, the persistent Elm connection, native GUI, AT/IME
and release acceptance require their separate observations. Whole DEL010 stays
open until its real cross-user verification is qualified.
