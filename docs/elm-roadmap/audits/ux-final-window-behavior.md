# Final UI/UX review: desktop window behavior

Verdict: **changes required** (three medium contract/scenario gaps; no critical or high finding).

Requirements SHA-256: `caff7b206582e4966315af5bcaf6031441b73e0bb7bac7a6f642745a8d2c0050`.
Reviewed 216 proposed requirements. Implementation acceptance remains **pending**. This review does not establish a repaired desktop or native acceptance.

The native layering design is coherent: eligibility precedes precedence; MAX, pin and true fullscreen are separate; modal redirects cannot synthesize application clicks; inert proxies retire atomically; and Heroic is an explicit adversarial fixture without overstated root-cause claims. The remaining gaps concern predictable outcomes after minimize and navigation, rather than the canonical scene design.

## UX-WIN-001 — medium

Requirements: ELM-REN-006, ELM-LAY-002, ELM-REV-017.

Minimization excludes the live window and its dependent family, but the registry does not state which eligible recipient takes keyboard focus when the currently focused family is minimized, or the safe result when no application remains. Paint/input consistency alone does not select a successor. A candidate could satisfy surface exclusion while keyboard focus remains on an ineligible owner or jumps unpredictably.

Add a native minimize-focus contract: WHEN the focused family becomes minimized, the native authority SHALL commit an eligible successor according to a frozen focus-return policy, or a documented desktop/no-application-focus state when no eligible application remains, in the same committed scene revision. Preserve focus when minimizing an unfocused family.

Recommended acceptance fixtures:

- Focused A minimizes with eligible B and C: the predeclared successor receives focus and A/family receive no keyboard events.
- Last eligible application minimizes: no minimized live surface retains focus and the declared desktop/no-app-focus state is observed.
- Unfocused A minimizes while B is active: B retains focus.

## UX-WIN-002 — medium

Requirements: ELM-UX-008, ELM-UX-017, ELM-UX-018, ELM-REV-016.

The taskbar restore scenario starts with a minimized window on workspace 2 and checks only that membership does not become scratchpad. It does not specify what the user sees when selection originates on workspace 1: switch to the preserved workspace, transfer the window, or refuse with feedback. The normal-workspace-preservation rule constrains the choice but does not make visible activation explicit. A restored window can remain on an inactive workspace while the scenario still passes.

Freeze a product policy for activating an enumerated target outside the effective workspace/output set before implementing taskbar/Task View/switcher activation. Require successful activation to reconcile workspace visibility and current source eligibility, then show/focus the selected incarnation without an implicit membership transfer; any explicit transfer must remain a separate accepted operation. Refusal must retain current visible focus and explain the outcome.

Recommended acceptance fixtures:

- Select minimized workspace-2 target from workspace 1: apply the frozen workspace-navigation rule, preserve its membership, and independently observe target pixels/focus after restore.
- Select target on another output: selected output/workspace behavior matches the frozen rule rather than restoring invisibly.
- Workspace navigation or restore is refused: current visible focus is retained, no hidden target receives direct focus, and correlated refusal feedback appears.

## UX-WIN-003 — medium

Requirements: ELM-UX-011, ELM-UX-013, ELM-UX-014, ELM-REV-016.

The switcher freezes an eligible-window order per chord, but the product rule that produces that order is not defined in the registry: MRU versus stack order, modal-family representation, workspace/output scope, initial selection and wraparound. The current three-window forward/back scenario can pass with multiple incompatible interaction models. Surface eligibility and enumeration are correctly separated elsewhere, making these product decisions especially necessary for minimized and cross-workspace entries.

Add a P0 switcher-policy freeze requirement with named ordered fixtures covering initial selection, committed activation recency, modal-family representation, minimized entries, workspace/output scope, wraparound and cancelled chords. Define the initial order algorithm explicitly in that artifact and gate P3 qualification on its concrete expected sequence; do not infer the algorithm from native z order.

Recommended acceptance fixtures:

- Known committed activation history A then B then C: first forward step and full wraparound match the frozen expected incarnation sequence.
- Cancel a chord before commit: original focus is preserved and the next chord starts from the declared unchanged activation-history policy.
- Parent with modal, minimized peer and other-workspace peer: entry inclusion/representation and exact selection order match the frozen policy with no duplicate family activation.

## Review boundary

Read-only review of the requirement registry, roadmap, layering design and relevant window-policy/switcher OpenSpec. No native GUI campaign, desktop changes or implementation proof was performed. The proposed product-policy freezes may be decided in P0, but need explicit normative requirements and concrete sequence/focus/visibility fixtures before implementation acceptance.
