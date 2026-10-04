# Resumed UI/UX review

Three existing reviewers resumed read-only review of motion/graphics, keyboard/navigation, and window behavior. This records recommendations, not executed acceptance or five newly commissioned experts. Existing strategy: docs/elm-roadmap/UI-UX-TEST-STRATEGY.md. All242 baseline requirements and417 scenario statuses remain unchanged.

## Next executable gates

1. Requalify joint161/reconnect57/bounds604 on the changed shared Elm source and owning core470/plugin471/AQ155. Keep original identities, deadlines and normal cleanup. Integrate independently held Escape and pointer evidence only after exact source review. V231 records corrected controlled pointer acceptance; old219 helper objections cannot be applied indiscriminately to that corrected tuple.
2. Add real GTK owner/modal/popup and unrelated-peer fixtures. Preserve architecture-018, owner-modal-activation, modal-no-click, unrelated-activation, qa-unrelated-window, ren-018, architecture-022, ren-015, max-modal-focus, max-input-region, focus-successor/focus-last/focus-unfocused, restore-overlay-handoff and proxy-retirement. Observe pixels, actual pointer recipient and application keyboard receipts independently. Retire a modal between blocked-parent press and release: no release may leak to any parent/peer/replacement. Preserve unsaved draft bytes.
3. Run connected keyboard journeys mapped to ELM-UX-023 keyboard-taskbar-groups/keyboard-launcher/keyboard-menus, ELM-UX-024 ux-024, ELM-UI-011 focus-scope-nested dismissal/opener closure/address reuse/renderer restart, and ELM-UI-007 restore-pending/refused/unknown. Retired or hidden incarnations receive zero keys; Unknown reconciles before a new validated effect. Compare DOM, seat, actual application and exported AT-SPI focus.
4. Qualify actual accessibility: ELM-UX-025 actual-surface-at, ELM-UX-026 ux-026, ELM-UI-010 announce-launch refusal. Inspect native AT-SPI and use real Orca and required braille; announcements occur once without focus theft. DOM semantics are only component evidence.
5. Qualify native composing IME: ELM-UX-028 ime-spike-commit/cancel, ELM-UI-012 ime-Enter Escape arrows/ime-explicit-valid-commit/ime-invalidated-zero-commit/ime-host restart/ime-output scale transfer. Consumed keys cause zero shell effects, valid commit writes once, invalidated callbacks write zero times.
6. Qualify workspace/output failure: ELM-UI-002 navigation-partial-refusal, ELM-UI-019 output-remove/outputs-return. Maintain visible eligible fallback after partial navigation/restore refusal; reject retired generations and keep recovery keyboard reachable.

## Motion, graphics and efficiency

Existing pointer/menu fixtures disable animations and use fixed800x600@60; their passes cannot close interrupted/reversed motion, retained-to-live handoff, mid-flight reduced motion or physical cadence. Fresh derivatives of GPU157 and measurement160 must replace their old GUI/core89 bindings with the current tuple. Confirm actual rendering backend for displayed workload separately from GPU inventory and WebGPU exposure. Keep WebGPU, import/acquire synchronization, lease revocation and device/context loss as separate gates.

budgets.json remains calibration-only. Freeze measured baseline and numeric feedback, input-to-present, whole-process CPU/GPU/memory/power and quiescence thresholds before comparative acceptance. Helper-to-DOM receipts are not presentation timestamps. Physical fractional-scale/high-refresh/hotplug/zero-output tests and human task participation remain required.

No native test, participant study or device qualification was performed by these reviewers. Overall release remains open; bounded native fixtures cannot substitute for complete journeys.
