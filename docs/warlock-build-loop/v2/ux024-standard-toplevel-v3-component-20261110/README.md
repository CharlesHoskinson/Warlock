# Standard foreign-toplevel observation state

The new Haskell module collects standard version3 window callbacks.
Title, application, states, output membership and parent changes remain pending until the handle receives Done.
Opaque owner, handle and output tokens reject stale callbacks and reused identifiers.
Closed handles retire. Invalid parent graphs refuse publication.
The module bounds rows, outputs, text and state arrays.
It does not invent workspace, hidden or effect-capability facts.

| Protected observation | API baseline | First implementation | Corrected implementation |
| --- | --- | --- | --- |
| Builder controls | 11 passed | 11 passed | 11 passed |
| Compiler result | New public module absent | Strict unreachable-pattern error | Both targets compiled and linked |
| Allocation-only program | Not executed | Not executed | PASS |
| GUI owner executed | No | No | No |
| Outer group absence | Refused | Passed | Passed |

The API baseline also retains its outer process-group absence refusal.
Its later inactive scope does not convert that failed check to a clean result.
The first implementation fails strict GHC because an inner ManagerFinished case is unreachable.
The correction removes that one case. Compiler flags and the test fixture remain unchanged.
Independent source and actual-result reviews bind the correction and complete result.

The unchanged fixture contains34 fixed controls and32 seeded sequences with two checks each.
The allocation-only program reaches its final PASS after these controls and the existing parser regressions.
No separate per-control output telemetry is claimed.
The final run binds258 Haskell files,11 support files and271 managed inputs including metadata.
Both actual ELF identities and current source hashes match the retained report.

This is a compiled state-model component for the actual planned standard Wayland client.
A per-handle Done is not a global atomic compositor snapshot.
ManagerFinished in this model does not prove callback quiescence or runtime resource retirement.
No display connection, authenticated provider, physical GUI behavior or original UX024 acceptance is established.
The owned runtime client and truthful Backend/Shell integration remain required.
All original242 requirements,417 scenarios and native acceptance limits remain unchanged.
