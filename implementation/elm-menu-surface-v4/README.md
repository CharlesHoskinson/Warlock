# Visible window action menu candidate

This is a fresh derivative of the V98 shared surface controller and the V3 menu
adapter. Main owns the interaction model; Popup renders its bounded presentation
DTO. A current context event chooses an explicit native ownership root, builds
Restore/Minimize rows from admitted facts, and opens `mode=menu` with a new lease.
The existing Shell/Effects engine allocates the native intent. One atomic surface
commit publishes the closed menu before the native host forwards the command.

Menu receipts retain their original full native tuple independently of the
engine's latest transaction. An Unknown menu operation blocks another action on
that same native root, including taskbar routes and frontend rebinds. Observation
does not resolve uncertainty. Target retirement and changed capabilities close a
stale menu; an admitted revision with an unchanged action table refreshes a Ready
menu with a new provider binding, menu identity and lease. The current provider
scope is registered for the isolated single-output experiment; it does not
qualify general output identity or positioning.

The native host checks manager origin, protocol, publication and lease, captures
physical secondary-button or keyboard evidence, and performs a bounded async DOM
hit test for context invocation. These checks supplement the existing authenticated
broker channel; JSON shape checks do not supply authentication. Popup keyboard
navigation and native gesture handling are new integration work with separate
native qualification gates. Bar keyboard context invocation remains outside the
qualified scope.

Protected compiled checks exercise 48 menu/controller scenarios. The full build
also preserves V98's 20 replay, 27 Shell and 55 surface checks, including the choice
expiry behavior, and compiles actual Main/Popup, the native host and header
selftests. These are component and compatibility results. Native attempts have
exposed focus and GTK key-delivery faults; their failed reports and normal cleanup
receipts remain in `qa/`. No complete native context-menu scenario, full feature,
mandatory requirement or release is accepted by this document.

Run CPU checks through the protected launcher:

```sh
python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- python3 -B qa/replay.py
python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- python3 -B qa/build.py
```

After reviewing the native scenario and its frozen build, run exactly one native
lane through `python3 -B qa/run_native.py native` or `... regression`. This wrapper
uses the shared global native lease and protected launcher. The preserved V93
regression changes only candidate and fixture/backend paths; its scenarios and
six-second observation deadlines remain intact. The menu lane adds real grouped
picker context invocation, exact root keyboard focus, disabled rows, popup closure,
Minimize/Restore observations and target retirement.

`qa/freeze.py` is prepared but must run only after fresh passed build/replay reports
capture its current source. Native reports are optional explicit arguments; each
selected report must have passed, have normal cleanup, and match current tested
production inputs. Omitted or failed native lanes supply no qualification. The
one-shot manifest preserves all attempts and keeps every completion flag false.

The frozen `qa/scenario-oracle.json` binds the accepted V93 report, original
fixture and source hashes, and its exact 91+1 check-name multiset. The freezer
also compares the whole normalized regression AST and original check/wait call
arguments, allowing only reviewed candidate paths and provenance metadata. It
requires the correct source-script identity for each selected native lane; a
passed report from another scenario cannot qualify it.
