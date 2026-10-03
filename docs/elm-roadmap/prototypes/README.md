# Architecture experiments and limits

These CPU-only experiments debug the designed boundaries without touching the live desktop. All commands run under protected QA. Sources, failures, pinned versions, seeds, logs and counterexamples are retained.

| Experiment | Executed evidence | Scope |
| --- | --- | --- |
| [Quint scene](quint/scene_README.md) | 11 named tests; six invariants, 1,000 sampled traces of up to 40 transitions; three deliberately faulty derivatives produce counterexamples | Eligibility before ranking, MAX/pin/fullscreen candidate policy, native focus, inert proxy handoff, lock and GPU lease revocation |
| [Quint bridge](quint/bridge/README.md) | 18 named tests; 2,000 sampled traces of up to 40 transitions; nine deliberately faulty derivatives fail targeted tests | Epoch/incarnation/revision checks, gap barrier, cancellation linearization, dependency receipts, deduplication, deadlines and Unknown |
| [Compiled Elm worker](elm/README.md) | Compiler0.19.2 and eight named deterministic reducer checks | Typed immutable model, pure update, lossless identities and receipt-driven effect descriptions |

The bridge experiment found a real weakness in the test design: changing incarnation and revision together allowed one guard to mask the absence of the other. The initial failed mutation campaign is preserved; independent changes now expose each missing guard. Scene mutants expose three architecture failures that ordinary happy-path animation tests can miss.

This is bounded sampling plus exact transition tests, not exhaustive verification or liveness proof. The two Quint models are separate abstractions; their composition, cross-language reducer equivalence, full modal/output topology, queue mechanics and cache-eviction policy still need formal and native coverage. The Elm worker tests fixtures without a DOM, host, GPU or state-derived subscriptions. It is not a compositor and performs no native effects.

P0/P1 must extend the executable architecture model to production schemas and complete policy oracles. P2 must replay retained ITF failures as typed Elm message fixtures and compare effect descriptions with the native protocol model. P3/P4 native acceptance measures actual pixels, focus, buffers and presentation. The GPU inventory only discovers hardware; actual accelerated webview/WebGPU workloads remain unqualified.
