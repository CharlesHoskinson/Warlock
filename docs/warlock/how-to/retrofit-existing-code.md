# Retrofit an existing Warlock boundary

Use this guide when an existing production boundary needs the adopted architecture, contracts or QA practices applied retroactively. Work in one selected original-requirement slice; use the [debt register](../../warlock-build-loop/v2/RETROFIT.md) to carry unfinished work across sprints.

## Establish the baseline

Identify the actual current source and consumers before editing. Use Graphify to find the route, then verify its source pointers. Record the original requirement/scenario, current evidence, and the specific coupling, failure or missing coverage. Distinguish an observed product defect from an untested boundary or a broken fixture. Preserve the failing trace and relevant accepted evidence.

Map the boundary's state owner, incoming events, admitted effects, subscriptions and resource lifetime. For native resources, include creation, cancellation, retirement and normal cleanup. For persisted preferences, include dirty drafts, read failure, conflicting refresh and restart. State the smallest change that improves this boundary and the behavior it must preserve.

## Declare and verify the contract

Write the preconditions, postconditions and invariants in reviewable terms tied to the original behavior. Use validated opaque values where they prevent invalid construction, and explicit errors at untrusted boundaries. A valid decoded value can still have expired native authority; check identity, incarnation, publication and lease where the effect is admitted.

Select proportional checks using [the verification guide](verify-selected-change.md) and [fuzzing/contracts policy](../../warlock-build-loop/v2/FUZZING-CONTRACTS.md). Exercise the real production route with a reachable positive control and a meaningful invalid, stale, duplicate or lifecycle case. For changed reducer/authority/concurrency invariants, include reproducible sequence fuzzing and applicable Quint correspondence. Record seeds, budgets, source/tool identities and counterexamples. Compile changed roots or units and relink as required.

Root owns protected execution. Preserve original deadlines, ABI pairing and the user's drafts. Native, keyboard, AT/IME and resource obligations need their applicable observations; a pure extraction or passing model does not establish them. Keep failed qualification records even when the fixture is later corrected.

## Update the documentation with the change

Choose the page by the reader's need:

| Change affects | Documentation to maintain |
| --- | --- |
| A guided learning path | Tutorial with a safe, bounded exercise |
| A contributor or operator task | How-to guide with checked prerequisites and commands |
| An interface, command, status or evidence boundary | Reference with exact current behavior and limits |
| Ownership, authority or a design decision | Explanation with rationale and tradeoffs |

Link between quadrants when necessary. Document delivered behavior separately from proposals and unverified behavior. Keep durable instructions in these versioned docs and lessons, failures and ideas in the LLM wiki.

## Follow a completed bounded example

Use the settings migration repair as a reference for the shape of a retrofit,
not as evidence for another component:

1. Read the [settings storage reference](../reference/settings-storage.md) to
   identify the actual schema transition and persistence contract. The original
   schema-1 bytes must survive before the active schema-2 file is replaced.
2. Follow the [retained migration evidence](../../../implementation/warlock/qa/evidence/settings-migration-20261030/LIMITS.md).
   The baseline reproduced a save that lost the original copy; the correction
   added durable backup ordering and explicit refusal/Unknown outcomes.
3. Inspect the [verification and original acceptance record](../../../implementation/warlock/qa/evidence/settings-migration-verification-20261030/acceptance.json).
   It separates existing checks, migration checks, abrupt process-exit cases,
   model results and independent review. Process exits do not prove hardware
   power-loss behavior.
4. Compare your selected boundary with the same questions: what concrete failure
   was observed, which owner enforces the contract, which production transitions
   were exercised, and which original obligations remain separate?

For your own sprint, give each documentation quadrant an updated page or a
specific unaffected reason in the sprint record. A storage fix may update a
reference and ownership explanation while leaving a source-navigation tutorial
unchanged. State that reason; do not copy one procedure into four pages.

## Hand off at the sprint gate

Use the [sprint retrofit template](../../warlock-build-loop/v2/SPRINT-RETROFIT-TEMPLATE.md)
in the selected sprint's owned handoff so unfinished obligations survive the next
iteration.

Record the following before integration:

- Original requirement/scenario and the existing boundary assessed.
- Source revision, owners and contract preserved or changed.
- Actual verification evidence and independent review disposition.
- Documentation updated and its links/commands checked.
- Remaining native/release obligations, open debt and next bounded migration.

Close a debt item only when its stated obligations have evidence and independent review. If only part is resolved, record that part and carry the remainder forward. Keep the original acceptance ledger authoritative. Documentation updates and debt accounting do not reset an investigation stop or establish original scenario acceptance.
