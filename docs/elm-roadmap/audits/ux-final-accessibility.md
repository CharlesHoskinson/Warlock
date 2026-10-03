# Final UI/UX review: accessibility and inclusive interaction

Verdict: **changes required**. Reviewed requirements SHA-256: `04fee8c928a929915f676baae39730754786fca921c7673a3d8cbd5e395d20fe` (216 requirements).

This is a requirements review, not implementation acceptance. No native GUI or desktop configuration was changed.

The plan gives keyboard routes, IME, native accessibility, audible/braille evidence and reduced motion serious gates. Six contracts still need clarification before an inclusive-interaction confirmation.

## UX-A11Y-001: Complete native accessibility semantics for every migrated surface

Severity: high. Requirements: ELM-UX-023, ELM-UX-025, ELM-UX-026, ELM-QA-019.

Counterexample: Taskbar and switcher export correct accessible controls, but launcher results, Task View workspace transfer, snap chooser, notifications, jump lists and settings are keyboard operable without exposing roles, labels, values or supported actions. UX-025 passes while a speech/braille user cannot identify or operate those controls reliably.

Contract correction: The Elm desktop SHALL expose names, roles, states, values, relationships and supported actions for every interactive control on every migrated shell surface through the selected host native accessibility bridge. Treat decorative preview pixels as noninteractive; expose the separately identified restore control.

Scenario correction: For each UX-023 surface, enumerate all interactive controls and exercise native AT discovery and action invocation, with speech/braille traces verifying labels, checked/expanded/disabled/value states and action results. A missing control or unnamed action blocks that surface gate.

## UX-A11Y-002: Announce asynchronous outcomes and notification changes without stealing focus

Severity: high. Requirements: ELM-ARC-007, ELM-UX-018, ELM-UX-029, ELM-UX-030, ELM-UX-031, ELM-UX-032, ELM-UX-026.

Counterexample: A keyboard user submits a launch that is refused. A red visual error satisfies UX-029, but keyboard focus remains on the search field and no speech/braille change occurs. Similarly an expired notification action disappears silently, and a refusal of workspace transfer looks like inactivity to a blind user.

Contract correction: WHEN a shell action produces a refusal, validation error, unavailable state or completion requiring user attention, the Elm desktop SHALL expose a concise accessible status associated with the originating control without moving focus, and SHALL avoid duplicate announcements for repeated receipts. Notification arrivals, expiration and action failures need an explicit announcement and interruption policy.

Scenario correction: With speech and braille active and input focus unchanged, inject launch refusal, transfer refusal, settings validation failure, unavailable system adapter, notification arrival and expired-action rejection. Verify one identity-correlated message per transition, reachable detail or recovery action and no forced focus relocation. Verify a repeated receipt causes no repeated announcement.

## UX-A11Y-003: Define focus fallback and nested-popup restoration

Severity: medium. Requirements: ELM-UX-024, ELM-UX-014, ELM-ARC-018.

Counterexample: A taskbar menu opens from an application that closes while the menu is open. Escape cannot restore the previous eligible focus target because it no longer exists. Another application reuses an address, or a nested submenu closes, leaving no specified fallback and potentially restoring the wrong scope. Native identity checks prevent unsafe activation but do not ensure usable keyboard focus.

Contract correction: WHEN a shell focus scope closes, the host SHALL restore its eligible identity-bound opener, or a documented current eligible fallback if that opener has died or become ineligible; nested scope dismissal SHALL restore the surviving parent scope, and SHALL never restore a replacement incarnation.

Scenario correction: Test nested menu dismissal, opener closure, workspace change, minimized opener, renderer restart and address reuse. Record native focus and accessibility focus, require a usable fallback, and prove no dead/replacement target receives activation. Lock supersedes all ordinary fallback behavior.

## UX-A11Y-004: Cover IME interaction conflicts, candidate geometry and late callbacks

Severity: medium. Requirements: ELM-UX-028, ELM-ARC-023, ELM-QA-019, ELM-REN-019.

Counterexample: An IME candidate-selection Enter bubbles to the launcher submit handler while preedit is active. The minimal commit test can still produce one string and pass while a production launcher issues an unintended launch. After focus moves to another field, a late composition callback could commit into that field; a candidate popup can remain on the old scaled output.

Contract correction: WHILE composition owns a shell field, shell shortcuts and submit handlers SHALL respect the native input-method consumption decision; composition events SHALL be bound to field identity and composition generation, and candidate geometry SHALL follow the current caret/output transform. Focus loss, field destruction and host restart SHALL have an explicit cancellation policy that rejects late old-generation commits.

Scenario correction: On actual launcher/settings fields, use Enter/Escape/arrows during candidate selection and prove no launch, shortcut or dismissal occurs unless the input method releases that key. Test field-to-field focus, destruction/recreation, output transfer/scale change and late commit callbacks; prove exactly one current-field commit or cancellation and correct candidate placement.

## UX-A11Y-005: Make readability and focus visibility objectively testable

Severity: medium. Requirements: ELM-UX-027, ELM-QA-020, ELM-UX-009.

Counterexample: A one-pixel low-contrast focus ring is technically visible; enlarged text uses an unspecified tiny scale; active and attention indications differ only by similar colors. All named theme fixtures could pass while important controls remain difficult to identify.

Contract correction: The P0 accessibility fixture matrix SHALL freeze measurable text/nontext contrast, focus-indicator visibility, minimum effective target geometry and supported text-enlargement/reflow levels before host qualification. Active, attention, disabled and error states SHALL retain a discernible non-color cue. Long labels and small outputs SHALL preserve reachable actions through documented wrapping, scrolling or overflow.

Scenario correction: Test high contrast, largest supported text scale, narrow/small output, long localized labels and color-independent state recognition. Measure against frozen thresholds; navigate every control and prove focused content is not obscured or unreachable. Avoid selecting convenient fixture limits after results are known.

## UX-A11Y-006: Define reduced-motion preference changes during active transitions

Severity: medium. Requirements: ELM-UX-022, ELM-REN-011, ELM-QA-019, ELM-UX-030.

Counterexample: Reduced motion is enabled in settings while a minimize animation is already running. Existing WHILE requirements do not say when the preference is read, which preference source wins, or how current motion is retired. A cached preference may leave the animation running until restart.

Contract correction: WHEN the effective reduced-motion preference changes, the shell SHALL apply the documented preference source/override policy without restart and settle active decorative transitions without changing the acknowledged target state, focus, deadline or resource ownership.

Scenario correction: Toggle reduced motion both before and during minimize, restore, switcher and Task View transitions. Verify prompt removal of optional motion, the same final state/focus, no duplicate native effect, no orphan actor/lease, and correct persistence/override behavior after host restart.

Confirmation requires explicit normative contracts and scenarios for these six gaps, or a documented narrower supported scope. The GPU, native layering and original acceptance campaigns remain implementation gates.
