## ADDED Requirements

### Requirement: Applied screen program identity
The system SHALL identify the actually applied screen shader using exact value-owned successful linked inputs.

EARS WRLK-SHADER-001: WHEN successfully applied vertex or fragment source changes, the system SHALL advance source content before admitting a changed-source capture and SHALL refuse the preceding context before allocating a producer/export.

#### Scenario: Same path different program
- **GIVEN** an applied shader at a stable configured path
- **WHEN** new bytes are successfully linked from that same path
- **THEN** content identity advances independently of root/child buffer commits and old capture contexts allocate no resource

### Requirement: Disk state and program state
The system SHALL distinguish later filesystem content from applied program inputs.

EARS WRLK-SHADER-002: WHILE the linked program inputs remain unchanged, the system SHALL keep their source content identity stable, including a disk edit without reload or an identical static reload.

#### Scenario: File edited without reload
- **WHEN** shader file bytes change without an actual successful program reload
- **THEN** the applied facts retain the earlier exact source bytes and source identity

### Requirement: Shader lifetime and unavailable recovery
The system SHALL preserve applied shader owner lifetime, exact bounded source ownership and canonical unavailable recovery.

EARS WRLK-SHADER-003: IF the owner is absent or facts are incomplete, malformed, over budget or use unqualified contextual uniforms, the system SHALL refuse current capture without allocation; WHEN complete supported facts recover, it SHALL require a later content identity.

#### Scenario: Contextual program
- **WHEN** an actual applied program consumes time, output or pointer uniforms without qualified dependencies
- **THEN** the source is unavailable and cannot allocate capture; later static recovery advances beyond the preceding valid source identity

#### Scenario: Failed replacement
- **WHEN** the owning renderer destroys the old program and replacement compilation fails or configuration disables the program
- **THEN** exact observed facts retire the preceding inputs to the effective off state

### Requirement: Complete shader rendering remains required
The system SHALL qualify source identity separately from actual shader pixel fidelity.

EARS WRLK-SHADER-004: WHEN claiming complete native shader fidelity, the system SHALL verify actual applied shader rendering with its full output/time/pointer/color/transform dependencies under original privacy, lifetime, clocks and physical ownership.

#### Scenario: Fact observer only
- **WHEN** qualification proves applied inputs without proving their displayed family pixels
- **THEN** shader pixel fidelity, production preview eligibility and complete GUI release remain unqualified
