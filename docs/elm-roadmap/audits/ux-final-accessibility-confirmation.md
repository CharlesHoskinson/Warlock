# Accessibility correction confirmation

Reviewed registry: `c7c80d43043f20169140a2ce968d4a75c2140a9f92c7e753283d7ce36b844146` (242 requirements / 417 scenarios).

**Verdict: confirmed at the requirements level.** All six original accessibility findings now have explicit normative corrections and matching scenario obligations. No implementation acceptance is claimed.

## UX-A11Y-001: confirmed

ELM-UI-009. Normative all-surface semantics now includes names, roles, states, values, relationships and supported actions. Nine named AT surface fixtures require semantic-oracle comparison and fail missing/unnamed controls.

## UX-A11Y-002: confirmed

ELM-UI-007, ELM-UI-010. UI-007/UI-010 make accessible outcome feedback identity-correlated, deduplicated and non-focus-stealing. Notification expectations now explicitly depend on frozen policy; named DND, irrelevant expiration and opt-in urgency cases reconcile scenarios with INTERACTION.md.

## UX-A11Y-003: confirmed

ELM-UI-011. Native and accessibility focus restoration now covers identity-bound opener, surviving parent scope and declared MRU/desktop fallback; replacement incarnations are rejected and lock overrides restoration. Named opener closure, workspace, minimize, restart and address-reuse cases are present.

## UX-A11Y-004: confirmed

ELM-UI-012. UI-012 covers native IME key consumption, field/composition identity, candidate geometry and late invalidated callbacks. Valid explicit commit now writes exactly once; cancellation/invalidation writes zero. Named explicit-valid-commit and invalidated-zero-commit cases remove the prior contradictory generic outcome.

## UX-A11Y-005: confirmed

ELM-UI-013. P0 freezes measurable contrast, focus/target geometry and text-enlargement/reflow thresholds before host qualification; non-color cues and small-output/long-label fixtures are required. Numeric values remain a properly declared future qualification gate, not claimed measured success.

## UX-A11Y-006: confirmed

ELM-UI-014, ELM-UI-018. System preference versus explicit versioned override is declared; live changes settle at the next valid presentation opportunity while preserving target/focus/deadline/ownership. Minimize, restore, switcher and Task View fixtures exist; disabling reduced motion cannot replay completed motion.

The earlier confirmation pass identified notification-policy and IME-commit scenario inconsistencies. Both were corrected and reread; the prior pass remains recorded in the JSON report.

P0 must still freeze numeric readability/reflow thresholds. Native speech, braille, IME and keyboard fixtures must actually execute on the chosen host; this confirmation does not replace those gates.
