## ADDED Requirements

### Requirement: Apply the owned shader program
The system SHALL render claimed family shader pixels with the actual owning applied program and its qualified input dependencies.

EARS WRLK-SHADER-RENDER-001: WHEN capturing an authorized family under a supported applied program, the renderer SHALL apply that program to owned family pixels, retain exact native context and original clocks/deadlines, and refuse any changed-source result before publication.

#### Scenario: Applied tint fidelity
- **GIVEN** a current family whose root is opaque red
- **WHEN** a real applied shader changes red to204 without buffer commits
- **THEN** the claimed corresponding captured root pixels match independently observed native output and old source contexts allocate no producer

### Requirement: Independent framebuffer ownership
The system SHALL prevent source/destination aliasing and retain issued GPU source ownership until completion.

EARS WRLK-SHADER-RENDER-002: WHILE a shader pass is pending or issued, its independent source storage SHALL remain owned; WHEN completion is confirmed, source/pass references SHALL retire in order and the final image SHALL remain independently owned under existing producer/export/consumer receipts.

#### Scenario: Second cropped framebuffer
- **WHEN** applying a shader to captured family storage
- **THEN** source and destination are distinct bounded framebuffers, the pass cannot be optimized away, and actual completion precedes source retirement

### Requirement: Preserve capture authority and original budgets
The system SHALL preserve the existing family source/privacy, typed ownership and original resource/deadline obligations.

EARS WRLK-SHADER-RENDER-003: WHEN a shader capture is accepted, it SHALL retain the original native issued scope and two-second deadline, unchanged typed FD3 identity, exact physical mapping/FD/export/producer drain, and the single immutable Elm policy; measured resource acceptance SHALL include all extra GPU/driver allocations under frozen S02 budgets.

#### Scenario: No authority expansion
- **WHEN** qualification uses an independent compositor screenshot as an oracle
- **THEN** that QA artifact grants no new product monitor plane, foreign-content permission, lifetime renewal or physical ownership shortcut

### Requirement: Complete shader semantics and evidence
The system SHALL distinguish bounded shader execution evidence from complete native shader fidelity.

EARS WRLK-SHADER-RENDER-004: WHEN claiming complete shader fidelity, the system SHALL independently qualify whole-image global UV/neighborhood, contextual/time/pointer/output, color/HDR/transform and hardware dependencies under original privacy, clocks and ownership; otherwise full shader and GUI release acceptance SHALL remain open.

#### Scenario: Two root samples
- **WHEN** identity and tint root samples match while broader dependencies lack evidence
- **THEN** only those sampled behaviors are qualified, with production eligibility and full release unchanged
