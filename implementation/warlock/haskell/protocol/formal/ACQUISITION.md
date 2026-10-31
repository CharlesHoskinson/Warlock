# Acquisition model qualification

This source-bound model supports ELM-TEA-005 / tea-narrow-interop and the resource
substep of ELM-DEL-021 / delivery-021. It accepts neither complete original
scenario. Logical resources 1 and 2 are identities, not raw descriptors or native
capabilities. The source assumes one caller-retained shell and an exclusive offer
caller. It models custody, setup use, retirement requests and once-only closure.

Root executed Quint 0.33.0 typechecks, executable initialization, all 26 individually
anchored tests, and 1,000 sampled traces of 30 steps with seed 20261031. No safety
counterexample was observed in those runs. Aggregate witness counts were Pending
500, Live 31, setup failure 178, Uncertain 331, Confirmed 169 and deferred retirement
137. These six witnesses are not complete per-action coverage or an exhaustive
proof. No fairness, liveness, heap, kernel-close or native behavior was established.

The previous model used one result slot: transfer return disabled later activation
failure delivery. Separate transfer/activation outcomes fix that model defect.
A second source review found that a later retirement failure could steal a
successful activation outcome. `SelectedBranch` now records the actual source
branch selected when setup finishes. A directed positive executes that ordering;
a separately excluded mutation makes the new invariant fail. All 24 earlier
controls remain alongside those two regressions. The normal `step` excludes
intentionally broken actions.

Correspondence uses actual `Ingress.Internal.activateIngressWithHook`,
`transferSocketWithHooks`, `retireIngress`, `closeShared` and `closeIfUnclaimed`.
The pre-retained shell precedes transfer; finite owner-only publication ends the
setup lease; close uses its own once-claim cell and never retries Uncertain.
Atomic publication remains a model premise, checked separately by real Haskell
interruption controls. `noAbandonedSetup` is a mutant-sensitive observer, not
independent scheduler instrumentation. A successful branch retains its outcome
across another retirement's failure, but modeled delivery timing can still wait
for closure. Cleanup-branch labels project one setup/cleanup call; attribution
among multiple concurrent cleanup callers is incomplete. This is not a full
concurrent return API, exception-identity or OS proof.

The actual public Haskell composition separately passed 20 boundary controls,
23 owner controls and 256 sequences of 24 actions, including 132 live positives.
The initial constructor-arity failure and sequence-fixture parse failure remain
preserved. Native peer authentication, effect authority, GUI/input/AT/IME,
whole-session teardown, resource budgets and release qualification remain open.
Exact reports, tools and source hashes are in
[transport-qualification.json](../transport-qualification.json).
