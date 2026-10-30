# File-descriptor lease model

Development-only bounded Quint model for the intended Haskell input-inspection
owner. Numeric descriptor slots, allocation epochs, inode classes and logical
owners are separate. Independent root/proc leases can survive root retirement;
a consuming observer installs ownership before deferred cancellation.

The original negative stale-close test was vacuous: its action could never run
against a legitimately retired owner. An independent close-before-reuse positive
failed, then passed after the guard was corrected from root to closing ownership.
The original 14 test sources remain unchanged. A deliberately broken integer-only
close is excluded from the correct step and has its own counterexample test.
Typed event flags observe actions without changing their domain effects.

## Recorded bounded evidence

Protected CPU execution with Quint 0.33.0 and seed 20261030 passed four typechecks,
initialization and 16 individually selected named tests: the original 14, the
independent old-allocation positive and the broken-close counterexample. A
1,000-trace, 40-step sample observed no safety violation and reached all 16 correct
step actions; the lowest action count was 75. Five excluded/unit actions are
covered by directed tests, not random correct-step coverage.

Epoch and owner checks change together in the reuse cases; these tests do not
independently isolate both guards. Atomic borrowing, installed masking, trusted
procfs and kernel close behavior are assumptions, not results established by this
model. Raw strings remain descriptive roles. The model does not prove actual
Haskell exception handling, real descriptor reuse, pathname races, file contents,
ABI/provider closure, loader behavior, native or original-scenario acceptance.
The full dependency manifest and release requirements remain open.

`qualification.json` pins exact source and machine-local evidence, including the
failed positive control and independent review. Those references are not portable
outputs or a complete toolchain/source distribution. A fresh checkout must run
its own protected qualification. The published model/test bytes match the reviewed
and executed inputs.

## Execution and maintenance

Use the existing protected CPU launcher and authenticated AgentBus QA ownership
protocol. Typecheck all four `.qnt` files. Individually run every `run` definition
in the three test modules using an anchored `--match=^NAME$`, requiring one
positively selected passing test. Sample the main module's `safety` predicate with
the pinned project backend and seed. The `step` names in `observer-map.json` are
the correct-step witness selectors; `namedOnly` must not be represented as random
coverage. Use sampled execution, not an unsupported universal-proof claim.

Keep this model separate from the [HTTP owner model](../http-owner/README.md).
Neither accepts original delivery-003: the complete pinned dependency manifest,
altered-input rejection, real platform qualification, two clean offline builds,
SBOM/notices and all remaining native/resource/GUI obligations still require their
own source-bound evidence. Never reset stopped campaigns or carry model results
into native acceptance.
