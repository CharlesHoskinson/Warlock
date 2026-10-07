# elm-verification — design adoption draft

## Purpose

Draft refinements for the existing in-flight `elm-verification` capability. This change contains ADDED research contracts only; it does not create or archive a main spec, replace existing pivot/right-click deltas, or establish release acceptance.

Consensus research drafts ready for internal specification integration and implementation. A reviewed baseline amendment remains a separate integration step. These artifacts do not change the canonical 242 requirements/417 scenarios, S01–S16, right-click24, original13 native preview cases, restore38/recovery34/drag-resize52 or original deadlines. Native authority and no automatic replay of Unknown remain mandatory. C00–C06 compositor replacement remains conditional.

No new native, hardware, IME, AT or full-release evidence is supplied by this packet. Frozen component/model/CPU/compiled replay evidence is not production-provider or full GUI ownership/drain/fidelity acceptance. GUI814 and toolkit391 retain separate owning ABI pairs. Implementation and qualification tasks remain unchecked.

## ADDED Requirements

### Requirement: ELM-ADOPT-001 — Versioned complete replay inputs with effect isolation

WHEN a reducer replay is evaluated, the verifier SHALL reproduce state and ordered effect descriptions from versioned initial state and complete recorded inputs, reject invalid input explicitly, report selected and processed coverage, and execute no native mutations.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P0.

Baseline mapping: ELM-TEA-002, ELM-TEA-003, ELM-QA-006, ELM-QA-007, ELM-REV-007, ELM-REV-012.

Existing work mapping: W03, W04, W05.

Source proposals: IMM-01, OPUS01-IMM-2, OPUS01-IMM-4.

Owner: Verification lead. Verifier: Independent acceptance reviewer.

Guardrails: Sanitized replay needs an explicit semantics-preserving mapping. Refused dummy events are counted explicitly; a nonempty selected corpus cannot pass by processing zero inputs.

Tradeoffs: Fixture/schema upkeep and log bytes; preserve existing reducer rather than build another. Recorded timer inputs do not qualify native deadlines.

Primary sources:

- <https://apalache-mc.org/docs/adr/015adr-trace.html>
- <https://arxiv.org/abs/2006.00915>
- <https://arxiv.org/abs/2104.01146>
- <https://arxiv.org/abs/2404.16075>
- <https://doc.akka.io/libraries/akka-core/current/typed/persistence.html>
- <https://guide.elm-lang.org/architecture/>
- <https://immerjs.github.io/immer/patches/>
- <https://kafka.apache.org/43/design/design/>
- <https://lamport.azurewebsites.net/pubs/abadi-existence.pdf>
- <https://people.seas.harvard.edu/~chong/pubs/pldi13-elm.pdf>
- <https://quint.sh/docs/checking-properties>
- <https://raw.githubusercontent.com/avh4/elm-program-test/main/src/ProgramTest.elm>
- <https://raw.githubusercontent.com/elm/browser/master/src/Debugger/History.elm>
- <https://raw.githubusercontent.com/elm/core/1.0.5/src/Array.elm>
- <https://raw.githubusercontent.com/elm/core/1.0.5/src/Dict.elm>
- <https://redux.js.org/style-guide/>
- <https://redux.js.org/usage/structuring-reducers/prerequisite-concepts>
- <https://www.cs.cmu.edu/~rwh/students/okasaki.pdf>

#### Scenario: ELM-ADOPT-001 Deterministic history

- **GIVEN** A valid checkpoint and ordered native observations including deadlines
- **WHEN** The compiled reducer processes them twice
- **THEN** All state/effect rows match and no effect endpoint is invoked

#### Scenario: ELM-ADOPT-001 Malformed racing clock input

- **GIVEN** A pending request and envelope missing clock-domain metadata
- **WHEN** A late receipt is supplied through the envelope
- **THEN** Validation fails explicitly; valid inputs retain original deadline and recorded order

### Requirement: ELM-ADOPT-005 — Explicit concrete state and command refinement mapping

WHEN coupled replay is reported as conformance evidence, the verifier SHALL compare concrete state and ordered commands through a documented abstraction map and disclose stuttering, equivalence and environmental assumptions without substituting that evidence for native acceptance.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P1.

Baseline mapping: ELM-QA-004, ELM-QA-005, ELM-QA-006, ELM-TEA-002, ELM-REV-009.

Existing work mapping: W03, W04, W10.

Source proposals: IMM-05, OPUS01-IMM-1.

Owner: Verification lead. Verifier: Independent acceptance reviewer.

Guardrails: Explicit partial-observation/stuttering abstraction; compare actual commands and resources as well as model state. Bounded sampling/trace validation is not an exhaustive proof. Every concrete state and command field is listed as mapped or explicitly reviewed quotient/stutter/ghost-only; an unlisted field fails coverage. Quotients preserve authentication/binding identity, clock/deadline and outcome meaning; reviewed opaque-nonce renaming is allowed without erasing those relations.

Tradeoffs: Mapping/comparator reviewer upkeep; full mechanized proof deferred; sampled exploration remains bounded evidence.

Primary sources:

- <https://apalache-mc.org/docs/adr/015adr-trace.html>
- <https://arxiv.org/abs/2006.00915>
- <https://arxiv.org/abs/2104.01146>
- <https://arxiv.org/abs/2404.16075>
- <https://immerjs.github.io/immer/patches/>
- <https://kafka.apache.org/43/design/design/>
- <https://lamport.azurewebsites.net/pubs/abadi-existence.pdf>
- <https://people.seas.harvard.edu/~chong/pubs/pldi13-elm.pdf>
- <https://quint.sh/docs/checking-properties>
- <https://raw.githubusercontent.com/avh4/elm-program-test/main/src/ProgramTest.elm>
- <https://raw.githubusercontent.com/elm/browser/master/src/Debugger/History.elm>
- <https://raw.githubusercontent.com/elm/core/1.0.5/src/Array.elm>
- <https://raw.githubusercontent.com/elm/core/1.0.5/src/Dict.elm>
- <https://redux.js.org/style-guide/>
- <https://redux.js.org/usage/structuring-reducers/prerequisite-concepts>
- <https://www.cs.cmu.edu/~rwh/students/okasaki.pdf>
- <https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/abadi-existence.pdf>

#### Scenario: ELM-ADOPT-005 Backend stuttering

- **GIVEN** Broker housekeeping without observable frontend change
- **WHEN** Coupled replay applies declared abstraction map
- **THEN** Frontend stutters while native accounting and eligible queued receipts remain checked

#### Scenario: ELM-ADOPT-005 Equal final state with incorrect effect order

- **GIVEN** Executions with equal final visible model
- **WHEN** One reorders Cancel/Ack or retires before consumer completion
- **THEN** Transition/command/resource comparison fails at first relevant mismatch

#### Scenario: ELM-ADOPT-005 unlisted-field-mutation

- **GIVEN** a runtime mutant drops an Unknown reservation or changes an undeclared field
- **WHEN** abstraction coverage and coupled replay run
- **THEN** verification fails at that field rather than silently observing only the visible model
