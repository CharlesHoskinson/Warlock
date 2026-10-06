## ADDED Requirements

### Requirement: Every owned surface renderer fact
The system SHALL include renderer background-effect facts of every participating owned native surface in a claimed family source's content identity.

EARS WRLK-SURFACE-001: WHEN a root, subsurface or popup's applied native preference, region or surface incarnation changes, the system SHALL advance content identity before accepting a changed-source capture and SHALL refuse the old context before allocation.

#### Scenario: Child and popup creation before commits
- **GIVEN** existing owned native child and popup surfaces
- **WHEN** processing effect creation changes their native renderer preference without a buffer commit
- **THEN** exact fact projection observes the preference with a later source content revision and the preceding context allocates no producer/export

### Requirement: Incarnation and immutable region values
The system SHALL use native lifetime/window-scoped surface incarnations and exact value-owned regions rather than object addresses or lossy hashes.

EARS WRLK-SURFACE-002: WHILE native tree identities and applied facts are unchanged, the system SHALL retain content identity; IF identities/regions are malformed, duplicated, orphaned or over budget, it SHALL expose canonical unavailable state with later recovery identity and permanent exhaustion.

#### Scenario: Pending versus applied nested region
- **WHEN** region/change/clear/removal requests remain pending under the owning protocol
- **THEN** the exact applied fact snapshot remains stable until the selected surface's applying commit; prior copied rectangle values remain unchanged

#### Scenario: Popup identity retirement
- **WHEN** an owned popup is actually destroyed
- **THEN** its native identity retires from the observed tree without being reused for a later unrelated surface

### Requirement: Native qualification projection is observational
The system SHALL keep QA fact projection authenticated, bounded and observational.

EARS WRLK-SURFACE-003: WHEN native qualification inspects effect facts, the projection SHALL enforce the existing native session/PID/start binding, schema, lock/output guards and byte bounds, and SHALL grant no producer/export/effect authority or capture lifetime extension.

#### Scenario: Unknown QA field
- **WHEN** a fact request carries an unexpected field
- **THEN** native validation refuses the exact schema before it can allocate capture ownership

### Requirement: Fact coverage does not establish pixel fidelity
The system SHALL qualify actual backdrop-dependent rendering separately from immutable fact coverage.

EARS WRLK-SURFACE-004: WHEN qualification claims native background blur fidelity, actual blur and approved backdrop provenance SHALL remain active under the original family source/privacy, context, clocks, transform and physical ownership invariants.

#### Scenario: Snapshot suppression remains open
- **WHEN** the family snapshot renderer suppresses background blur
- **THEN** source-fact/model/native metadata passes cannot establish background pixel fidelity or production preview eligibility
