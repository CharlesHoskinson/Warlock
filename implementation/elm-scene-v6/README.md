Pure Elm scene admission experiment

`Scene.elm` admits an entire candidate or returns a refusal. Its opaque `Admitted`
type exposes paint order, an input-region probe candidate and focused recipient
only after validation. It rejects unknown owners, cycles, duplicate incarnations,
partial or duplicated order, excluded sources, child-before-owner order and focus
on an ineligible or modal-blocked parent. Dependent children inherit owner
exclusion; a minimized source stays in the supplied window inventory while
disappearing from the admitted live order. Keyboard focus does not depend on the
probe point being inside the focused window's pointer region.

This is an experimental decoded scene projection, not a versioned production wire
schema. `member` represents current effective native workspace/output membership;
`inputAtProbe` represents the result of native geometry/region evaluation at one
declared probe point. Neither field grants Elm authority to determine compositor
membership, coordinates or hit dispatch. Unknown minimized state is refused.
Incarnations and scene revisions are separate opaque canonical uint64 strings.
Prototype bounds are 256 windows and 32 ancestor traversals. They are not frozen
product workload budgets. Ancestor validation completes before recursive live
eligibility is evaluated, so cyclic inputs cannot recurse indefinitely.

The native compositor still owns canonical solving, painting, hit dispatch and
focus. This module validates observations; it does not publish an independent
stack or execute effects. Production integration still requires authenticated
lifetime/session binding, observer correlation and atomic revisions, complete
output/sticky/security/role semantics, native layer/family constraints and
presentation evidence. Pin/MAX/fullscreen precedence and stable unrelated order
remain native-policy gates. Bounded envelopes and duplicate JSON-key refusal are
host/adapter obligations as in V3. Admission cannot repair a native renderer that
already painted an excluded window.

Protected verification:

```
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B /home/hoskinson/omarchy-windows-parity/implementation/elm-scene-v6/qa/run.py
```

Accepted CPU packet: `qa/run-1791052752897124970/report.json`. It contains compiled
Elm evidence for 4,117 fixture cases, six actual named Quint scenarios and 1,000
sampled invariant runs of at most 40 steps, seed 610602. The conformance report
replays all retained named/sample states into compiled Elm. Two independently
compiled unsafe derivatives remove owner exclusion or modal-focus protection;
both produce the expected assertion failures. Full source copies, versions,
logs, traces and artifact hashes are retained. The earlier Quint type failure
and pre-conformance passing packet remain separate historical evidence.

The fixed three-window Quint abstraction covers a modal owner/child plus an
independent peer. It does not model arbitrary ancestry, coordinates, host/GPU
behavior, bridge ordering or every product layer. The compiled Elm fixture cases
cover malformed ancestry and bounds independently. These are partial connections
to ELM-LAY-001 and scene/family/focus requirements, not complete requirement or
native acceptance. No live desktop configuration or running window is changed.
