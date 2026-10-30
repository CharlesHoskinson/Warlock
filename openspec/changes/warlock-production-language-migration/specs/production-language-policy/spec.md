## ADDED Requirements
### Requirement: WARLOCK-LANG-001 — Allowed authored production languages

Warlock-authored production SHALL use Elm and Haskell only. All GUI elements SHALL use Elm. Haskell SHALL own native/runtime capabilities, with Haskell pure policy where selected and one authoritative policy owner per domain. All authored shipped implementations SHALL use the allowed languages, including implementations behind wrappers. Development QA/formal tooling and separately inventoried third-party dependencies remain distinct.

#### Scenario: Replacement retains original behavioral contract

- GIVEN an original requirement/scenario and its historical source/evidence
- WHEN an allowed-language implementation replaces the historical component
- THEN original identities, behavioral oracle, deadlines and applicable native gates remain unchanged
- AND retained historical passes do not accept the replacement

### Requirement: WARLOCK-LANG-002 — Functional frontend and typed effects

All GUI elements SHALL use Elm with typed models, validated decoders, pure reducers and explicit typed effects. Typed ports/IPC SHALL preserve lossless protocol identities, committed-receipt sequencing and only independent effect batching. Native authority, cleanup and no-replay semantics SHALL remain unchanged. Design/spec preparation SHALL NOT arm implementation or autonomous continuation before readiness and root/Muse authorization.

#### Scenario: Replacement effect boundary

- GIVEN a replacement frontend and its selected policy owner
- WHEN a dependent native effect or external observation is processed
- THEN validated identities and matching committed receipts govern progress without duplicated native authority
- AND compiler, lint and property checks do not substitute for required original native observations
