---
title: "Engineering lessons and architecture ideas"
created: 2026-10-29
updated: 2026-10-29
tags: [warlock, architecture, evidence]
category: concept
volatility: warm
sources: [raw/notes/2026-10-29-shortcut-draft-production-baseline.md, raw/notes/2026-10-29-knowledge-space-and-delivery-observation.md]
summary: "Separate established evidence-handling lessons from architecture proposals awaiting selection."
---

# Lessons and ideas

## Lessons supported by the current work

- Match evidence to the original verification. Bridge traces can close an obligation that explicitly permits a bridge; physical, native input, AT/IME or deployment claims still need their own observations.
- Keep diagnostics causally modest. Naming a receiver and error code narrows a boundary; it does not identify the unsupported value or explain a renderer death. Keep failure policy unchanged until a supported behavioral repair is selected.
- Capture identity at the relevant boundary. A dispatch-time global gate, payload identity and target-view identity are distinct facts. A hash-checked module or JSON buffer should be the same captured bytes consumed by the new loader.
- Preserve historical provenance. Old source/build receipts stay immutable, explicitly changed rows are versioned, and current source/assets/dependency checks are validated separately. Do not relabel an old host or ABI as current.
- Report failed outcomes precisely. Successful teardown does not make host exit normal, a private GUI launch does not complete first-use, and a build does not establish native usability.
- Make contracts executable at real boundaries. Validated opaque types and explicit errors narrow invalid states, but business, lifetime and native capability invariants still need production-route checks. Positive controls prevent reject-everything tests from passing.
- Preserve fuzz reproducibility. Keep seed, bounded case budget, compatible runner/generator/tool/source versions, event trace and minimized counterexample when supported. Do not weaken deadlines or invariants to discard a failure; sampled success is not native acceptance.
- Refactor ownership, not names. A diagram or moved folder is not a delivered simplification; a selected extraction should remove a real dependency or duplicated responsibility and preserve behavior through proportional checks.

## Proposed ideas, not adopted decisions

| Idea | Intended improvement | Required decision/evidence |
| --- | --- | --- |
| Extract a pure surface snapshot protocol from rendering | Remove policy-to-HTML dependency while keeping opaque snapshot/decoder/accessors and wire authority | Confirm actual caller graph, exact exposed API and a reversible first slice; compile relevant roots and run applicable existing replays |
| Centralize current build/package source enumeration | Reduce duplicated lists without changing provenance or produced artifacts | Map actual consumers and compiler/link order; preserve locked inputs and reproducibility checks |
| Preserve unsaved shortcut editor intent across same-revision reads | Avoid overwriting local draft during Refresh or reopen | Actual compiled baseline now reproduces five contracts with ten positive controls. Refined local model named/sampled checks pass and a correction is authored; fresh roots and original/legacy 15-check replays plus 200 seeded production sequences now pass. The latest 26–40-step run extends 100 schedules and independent source correspondence is SOURCE_READY; original native acceptance remains pending. Never auto-save or replay |
| Offer discoverable first-enable guidance without mandatory onboarding | Meet the original first-enable offer while preserving optional desktop use | Assess exact original source gap and pre-Settings usable Apps witness; no forced modal or focus theft inferred |

These proposals are not accepted behavior or instructions to start concurrent product work. Root selects ownership and one reversible implementation slice after Astra synthesis. Preserve saved data, live draft scope, current identities, Unknown/no-replay and native custody.

## Sources

- [Current observation and constraints](../../raw/notes/2026-10-29-knowledge-space-and-delivery-observation.md)
- [Standing architecture track](../../../../docs/warlock-build-loop/v2/ARCHITECTURE-REVIEW.md)

- [Standing fuzzing and Elm contracts](../../../../docs/warlock-build-loop/v2/FUZZING-CONTRACTS.md)

## Reviewed architecture study

The [Elm architecture study](../../../../docs/warlock-build-loop/v2/ELM-ARCHITECTURE-RESEARCH.md) is reviewed and available. Keep current 0.19 TEA separate from historical Signal-era papers. A pure snapshot codec can invert the direct controller-to-renderer dependency, but residual announcement rendering remains an explicit next seam. Preserve existing pending-query/local-edit behavior and raw-parser duplicate-key validation; normalized codec idempotence is not identity of every input encoding. A correlated prerequisite observation, which may be a receipt, state or retirement fact, must justify dependent effects; acknowledgement alone is not universal completion proof. No proposed extraction or reviewed study establishes native acceptance.

## A real baseline changes the debt disposition

The [draft baseline](../../raw/notes/2026-10-29-shortcut-draft-production-baseline.md) turns DEBT-05 from a source hypothesis into a reproduced local editor/reconciliation defect. Keep both the five expected RED contracts and ten positive controls; a failing test alone would not distinguish an unreachable operation. Do not turn that reproduction into a completed fix, validated abstract model or native scenario acceptance. Stored preferences, local unsaved intent and active native bindings remain separate states.

## Visible text requires a text observation

A bounding box in the viewport and a complete accessibility name do not prove that the leading action state is painted. The 320px Applications feedback trial passed both while vertically centered overflow clipped “not confirmed” above the taskbar. Use actual text-range bounds and retained screenshots for the relevant prefix; preserve the full semantic name separately. This is a concrete lesson from the [October31 observation](../../raw/notes/2026-10-31-applications-feedback.md), not native/AT acceptance.
