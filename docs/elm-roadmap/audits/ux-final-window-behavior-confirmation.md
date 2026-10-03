# Window behavior correction confirmation

Verdict: **confirmed for planning contracts**. The original review remains unchanged.

Requirements: 242; SHA-256 `c7c80d43043f20169140a2ce968d4a75c2140a9f92c7e753283d7ce36b844146`.

INTERACTION.md SHA-256: `2a947a3aa56d7b7b9e7d2f5c1ceb100ac7b8c345a73fd7616c0c4c567d0e01c4`.

All three original medium findings are resolved by ELM-UI-001, ELM-UI-002 and ELM-UI-003 with explicit policy and acceptance fixtures. The additional partial-navigation and minimized-family/modal clarifications remove ambiguity without weakening native eligibility or identity checks.

- UX-WIN-001: Explicit committed-MRU eligible focus succession and desktop fallback, same-revision commitment, plus focused/unfocused/last-family fixtures.
- UX-WIN-002: Explicit workspace/output navigation with preserved membership, visible target pixels/focus and refusal fixtures. Partial committed navigation followed by restore refusal has eligible destination fallback or separately validated compensation.
- UX-WIN-003: Frozen committed-MRU and incarnation tie-break ordering, all-session workspace/output scope, family identity representation, initial forward/reverse selection, wraparound, cancel/recency, zero/one and retired/late-arrival fixtures. Minimized families resolve eligible modal only after restore.

Implementation acceptance remains **pending**. This confirms the specified UX behavior and its proposed validation; it is not proof of live compositor behavior, repaired Heroic layering, GPU execution or user-tested usability. Native scenarios and their independent observations must still pass.
