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

## Hand off at the sprint gate

Record the following before integration:

- Original requirement/scenario and the existing boundary assessed.
- Source revision, owners and contract preserved or changed.
- Actual verification evidence and independent review disposition.
- Documentation updated and its links/commands checked.
- Remaining native/release obligations, open debt and next bounded migration.

Close a debt item only when its stated obligations have evidence and independent review. If only part is resolved, record that part and carry the remainder forward. Keep the original acceptance ledger authoritative. Documentation updates and debt accounting do not reset an investigation stop or establish original scenario acceptance.
