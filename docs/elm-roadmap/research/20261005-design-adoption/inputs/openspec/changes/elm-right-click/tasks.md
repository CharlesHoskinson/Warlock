# Delivery tasks

- [ ] RC-P0: Review the additive contract, map all RC scenarios to existing
  obligations or new gaps, record owners/verifiers and amendment lineage; keep
  frozen baseline counts unchanged until the amendment is incorporated explicitly.
- [ ] RC-P0: Freeze gesture/button mapping, input provenance, timing/tolerance,
  resource bounds, focus fallback and per-output placement fixture oracles.
- [ ] RC-P1: Implement typed context/action/menu lifecycle and capability tables;
  replay every scenario against compiled Elm and retain negative counterexamples.
- [ ] RC-P1: Model open/select/dismiss, stale identities, mixed-button sequences,
  duplicate intents and pending/unknown outcomes in Quint; execute explicitly
  selected named scenarios and replay sampled journals against Elm.
- [ ] RC-P2: Build an isolated native taskbar/preview menu with real right-button,
  Shift+F10/Menu-key navigation, source/ABI hashes, delivery and cleanup receipts.
- [ ] RC-P2: Implement supported native window-menu actions; independently prove
  state enablement, no activation on open, modal/fullscreen/grab refusal, graceful
  close and cancellable Move/Size before advertising those capabilities.
- [ ] RC-P3: Add app pin persistence, frozen group close outcomes, explicit jump
  providers and stale provider/catalog rejection; retain unsaved-document prompts.
- [ ] RC-P3: Add declared desktop, Files and system adapters; preserve Files
  no-overwrite/trash semantics and existing privileged-operation workflow.
- [ ] RC-P4: Run serial protected native mixed-button, outside-click, application
  delegation, retirement/rebind and compositor/broker recovery campaigns.
- [ ] RC-P4: Qualify output removal, mixed DPI, transformed outputs, high contrast,
  enlarged text, native accessibility, speech/braille and IME interaction.
- [ ] RC-P5: Review coherent acceptance receipts, integrate traceability and UI/UX
  coverage, prepare deployment/rollback and verify the complete integrated flow.

## Requirement mapping

All rows are planned work, not executed acceptance. P0/P1 verification covers every
requirement; native/UI/AT rows provide the additional applicable acceptance gates.

| Requirement | Delivery stages |
| --- | --- |
| ELM-RC-001 | RC-P0, RC-P1, RC-P2, RC-P4 |
| ELM-RC-002 | RC-P0, RC-P1, RC-P3 |
| ELM-RC-003 | RC-P0, RC-P1, RC-P2, RC-P4 |
| ELM-RC-004 | RC-P0, RC-P1, RC-P2 |
| ELM-RC-005 | RC-P0, RC-P1, RC-P2, RC-P4 |
| ELM-RC-006 | RC-P0, RC-P1, RC-P2 |
| ELM-RC-007 | RC-P0, RC-P1, RC-P2, RC-P4 |
| ELM-RC-008 | RC-P0, RC-P1, RC-P2, RC-P3 |
| ELM-RC-009 | RC-P0, RC-P1, RC-P3 |
| ELM-RC-010 | RC-P0, RC-P1, RC-P3 |
| ELM-RC-011 | RC-P0, RC-P1, RC-P2, RC-P4 |
| ELM-RC-012 | RC-P0, RC-P1, RC-P3 |
| ELM-RC-013 | RC-P0, RC-P1, RC-P3 |
| ELM-RC-014 | RC-P0, RC-P1, RC-P3 |
| ELM-RC-015 | RC-P0, RC-P1, RC-P3 |
| ELM-RC-016 | RC-P0, RC-P1, RC-P2, RC-P4 |
| ELM-RC-017 | RC-P0, RC-P1, RC-P2, RC-P4 |
| ELM-RC-018 | RC-P0, RC-P1, RC-P4 |
| ELM-RC-019 | RC-P0, RC-P1, RC-P4 |
| ELM-RC-020 | RC-P0, RC-P1, RC-P2, RC-P4 |
| ELM-RC-021 | RC-P0, RC-P1, RC-P2, RC-P3, RC-P4 |
| ELM-RC-022 | RC-P0, RC-P1, RC-P2, RC-P4 |
| ELM-RC-023 | RC-P0, RC-P1, RC-P3, RC-P4 |
| ELM-RC-024 | RC-P0, RC-P1, RC-P3, RC-P4 |
