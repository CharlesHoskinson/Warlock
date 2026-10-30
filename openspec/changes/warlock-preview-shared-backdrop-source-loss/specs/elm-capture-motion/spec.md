## ADDED Requirements

> Current production-language decision (2026-10-30): Warlock-authored production uses Elm and Haskell only; all GUI elements are Elm. Haskell owns native/runtime capabilities, Haskell supplies pure policy where selected, and Elm owns GUI presentation with one authoritative policy owner per domain. Only Elm and Haskell authored production components may ship, including behind an allowed-language wrapper. Development/formal tooling and separately inventoried third-party libraries are distinct. Preserve original IDs, scenarios, behavior, deadlines and historical evidence; old passes do not accept replacements. Implementation remains paused pending readiness and root/Muse authorization. See `warlock-production-language-migration`.

### Requirement: Declared source loss decoding
The system SHALL enforce the generated source loss boundary.

EARS WRLK-BACKDROP-LOSS-001: WHEN the authenticated native generated source reports preview-family-backdrop-source-unavailable, the shared provider SHALL map that exact reason to SourceUnavailable only for the generated plane; shared declared style-source/layout denials SHALL preserve their typed meaning and undeclared transport/error aliases SHALL remain unknown.

#### Scenario: Unknown or cross-plane refusal
- **WHEN** an unknown transport error or a generated refusal for a transparent plane is received
- **THEN** the decoder grants no source-denial settlement or automatic replay

### Requirement: Original URI and physical ownership
The system SHALL enforce the generated source loss boundary.

EARS WRLK-BACKDROP-LOSS-002: WHEN a known original generated source loses availability, native URI authority SHALL revoke before Elm consumes the typed original-job source denial; mapping/FD/export/producer ownership and terminal receipts SHALL remain until physical completion and exact original ACK, with no fabricated scope/clock or recapture/deadline renewal.

#### Scenario: Actual generated source becomes nonopaque
- **WHEN** native generated color becomes nonopaque with unchanged root commits while the shared GUI owns a frame
- **THEN** the same original frame/job is released and actual physical retirement precedes its exact terminal ACK

### Requirement: Bounded qualification and release
The system SHALL enforce the generated source loss boundary.

EARS WRLK-BACKDROP-LOSS-003: WHEN publishing source-loss qualification, the verifier SHALL retain native87 and all original1783 identities/deadlines, normal owned exits and ordered clean teardown, and SHALL distinguish actual GUI/FD cleanup from synthetic held-read controls and keep independently stalled frontend/hardware/all original release gates open.

#### Scenario: Native source-loss campaign passes
- **WHEN** the bounded actual source-loss campaign passes
- **THEN** only that bounded result is qualified; previewEligible and fullReleaseAccepted remain false

