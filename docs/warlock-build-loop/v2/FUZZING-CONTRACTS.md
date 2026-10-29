# Fuzzing and contracts for Warlock

Standing user requirement, October 29, 2026. Apply this policy to implementation and refactoring within the original scenario slice. It complements protected CPU/native QA and Quint correspondence; it does not grant acceptance from generated tests alone.

## Elm contracts

Elm has no built-in Eiffel-style design-by-contract facility. Express contracts through types, explicit validation and executable properties:

- Use custom types for meaningful exclusive states and opaque types with hidden constructors for validated identities, snapshots, leases and capabilities. Expose smart constructors or decoders returning `Result`/decoder errors. A public type alias alone does not hide construction.
- Name preconditions, postconditions and preserved invariants for each changed public domain transition. Link them to original requirement IDs and the owning Quint action/invariant where one exists. A contract must preserve the original requirement, rather than encode the current bug as intended behavior.
- Treat JSON, ports, native messages, disk data and async completions as untrusted inputs. Validate identity, generation, bounds and shape at the actual authority boundary. A well-typed frontend value is not proof that a native capability remains current.
- Preserve operational state and admit no effect for invalid/stale inputs according to the applicable original contract. State explicitly which bounded diagnostic fields may change; do not silently normalize away policy or authority differences in a test.
- Separate a pure transition's proposed effects from their runtime execution. Verify effect admission and result correlation, not just final model equality. Ordered effects require explicit acknowledgement/state transitions; `Cmd.batch` is not an ordering contract.
- Keep production refusal and recovery explicit. Do not use `Debug.todo`, `Debug.log`, deliberate crashes, disabled optimization or unchecked assertions as the production contract mechanism. Static typing does not prove business invariants, native lifetime, effect delivery or physical presentation.

For a snapshot extraction, contracts include validated construction, unchanged protocol/encoding and accessors, rejection of invalid identity/bounds, and unchanged action/effect admission for the same input sequence. Views may project validated snapshots but must not create policy authority.

## Property-based and sequence fuzzing

For changed decoders, reducers, protocols, identity/lifetime logic and persistence behavior, use applicable Elm property fuzzing (`elm-explorations/test` with a compatible pinned `elm-test` runner) or the existing protected production replay harness. Verify actual toolchain/dependencies first; this document does not assert that the package or runner is already installed in the product. Add declared test dependencies only when implementing a selected meaningful test. Avoid a new generic testing framework when the existing one exercises the production boundary.

Include valid generators and positive reachability controls so rejection tests cannot pass merely because everything is rejected. Generate malformed and boundary values, duplicate/out-of-order/stale completions and state/event sequences where applicable. Preserve large identity values as their actual protocol representation; cover empty, maximum, overflow and version cases. For persistence, include unsaved drafts, unchanged revisions, changed revisions, failed saves, and authority restart without accidental replay. For preview lifetimes, cover revoke/retire, incarnation/output changes, hidden consumers and unavailable content with correct fallback.

Write properties against original behavior, such as identity-correct selection, stale-result refusal, no duplicate admitted effect, unchanged unrelated state, resource retirement and round-trip preservation for valid values. Do not fuzz only a copied toy reducer or a mirror of the implementation. State the abstraction when a fixture cannot execute real native resources. Model tests should link the abstract action and actual implementation route; Quint sampling is distinct from proof and from native acceptance.

Use a reproducible seed and bounded run/case budget. Save failures immediately, including the minimized counterexample if the tool supports shrinking, event trace, generator constraints, exact invocation, seed, tool versions and source hashes. Add a focused regression for each demonstrated production bug. A seed without the compatible runner/generator/source version is insufficient for reproduction. Keep previous failures and do not discard inconvenient inputs, change original deadlines, or weaken an invariant to make a run pass.

## Execution and integration

Root serializes CPU/native campaigns through the existing protected launchers and AgentBus HOLD/RELEASE workflow. Fuzzing does not justify unbounded CPU/memory, parallel native campaigns, relaxed core limits, software-renderer fallback or touching the user's session/drafts. Workers prepare source and test proposals under assigned ownership; root runs reviewed commands.

At each implementation/refactor gate, record the changed contract, properties and positive/negative controls, actual tests run with seeds/case counts, failures and remaining native/AT/IME/resource obligations. Run checks proportionate to the change. Pure documentation or cosmetic changes do not require unrelated fuzz suites; explicitly identify when fuzzing is inapplicable. Failure investigation still follows the loop's bounded-qualification rule.

## Primary references

- [Elm custom types](https://guide.elm-lang.org/types/custom_types) and [module boundaries](https://guide.elm-lang.org/webapps/modules).
- [Elm test package and fuzzing documentation](https://github.com/elm-explorations/test).
- [elm-test runner documentation](https://github.com/rtfeldman/node-test-runner).
- [Pinned Elm core command semantics](https://github.com/elm/core/blob/1.0.5/src/Platform/Cmd.elm).

Web research and downloads use Scrapling, per the user's standing instruction. Keep retrieved metadata/links and concise original summaries; do not commit full copyrighted papers or full chat transcripts.
