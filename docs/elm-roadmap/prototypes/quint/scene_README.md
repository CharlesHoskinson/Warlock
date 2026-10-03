# Canonical scene and frame-lease experiment

`scene_model.qnt` is an executable two-window, one-overlap-point architecture prototype. Eleven explicitly selected named scenarios pass. Six invariants hold across a bounded 1,000-sample simulation with at most 40 transitions per sample, seed 610104, Quint 0.33.0 TypeScript backend. This is sampled CPU model evidence, not exhaustive verification or actual renderer, Wayland, GPU, accessibility or application acceptance.

The model derives paint and input candidates from the same current eligibility predicate. Ordinary maximization does not add a band; minimized/inactive windows remain excluded even if pinned/fullscreen. Input-transparent regions can select a different recipient from the top painted window. Focus changes only on activation and is cleared when its target becomes ineligible. An inert restore proxy leaves the application minimized until accepted live content allows a single state transition that retires the proxy and restores live eligibility. Lock revokes publication/input and GPU device loss revokes the simulated GPU-backed lease.

Pinned-above-fullscreen is a declared candidate band rule in this experiment. Its presence makes the test oracle explicit; it does not establish the final product's complete fullscreen, transient or security-surface policy. Inactive membership abstracts workspace/output identity, and the two fixed window identities omit incarnation reuse, modal ancestry, real coordinates and scene-revision races. Other architecture models and native acceptance must cover those domains.

The typed `Event` union maps to an Elm `Msg`; `Scene` maps to a typed immutable `Model`. The match expression in `fire` computes the candidate model from current state and event, equivalent to a pure reducer computation. `step` supplies nondeterministic external events rather than allowing uncontrolled callbacks to mutate derived presentation. Native observations, effect receipts and frame-ready notifications become explicit messages in an eventual Elm implementation; actual effects and per-frame sampling remain native. This prototype contains no Elm ports or implemented FRP runtime and does not infer browser feasibility from pure-state simulation.

Three deliberate derivatives are retained under `scene-receipts/`:

| Mutation | Named scenario that fails | Violated invariant | Captured counterexample |
| --- | --- | --- | --- |
| Remove minimized exclusion | `minimizedFullscreenExcludedTest` | `noExcludedPaint` | Both windows minimized yet a minimized fullscreen window remains paint candidate |
| Make proxy interactive | `inertRestoreProxyTest` | `proxyInert` | Accepted lease and minimized owner have an interactive restore proxy |
| Keep lease on device loss | `gpuLossRevokesLeaseTest` | `leaseValid` | `gpuReady=false` while `lease=true` |

Every mutation produces an actual assertion failure and a separate invariant counterexample, retained as logs and ITF invariant traces. Test mode does not emit ITF for failing assertions in this tool version; named failure traces remain in console logs. The correct model and passing evidence are not replaced by buggy derivatives. An initial reserved-name parsing failure and an evidence-checker assumption about failed-test ITF output are also retained.

Run through the protected launcher:

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B /home/hoskinson/omarchy-windows-parity/docs/elm-roadmap/prototypes/quint/run_scene_proofs.py
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B /home/hoskinson/omarchy-windows-parity/docs/elm-roadmap/prototypes/quint/verify_scene_evidence.py
```

The first runner preserves commands, exit expectations, seeds, model/test/runner hashes, tool version and logs in `scene-proof-receipt.json`. The second verifies the eleven actual executed identities, evidence hashes and specific mutation failures in `scene-evidence-verification.json`. It does not accept a selector or generic nonzero exit as proof of scenario execution or of an invariant counterexample. Preserve an existing receipt directory before re-running a changed derivative.

Requirement connections: ELM-LAY-001, ELM-REN-015/017, ELM-REV-013/014/015/016/017 for eligibility and native authority; ELM-REN-007 and ELM-REV-033 for inert/live handoff; ELM-REV-002/003/004/018 for lock; ELM-GPU-007, ELM-QA-025 and ELM-REV-019 for GPU-backed lease invalidation. These are partial architecture connections, not full coverage claims for the requirements.
