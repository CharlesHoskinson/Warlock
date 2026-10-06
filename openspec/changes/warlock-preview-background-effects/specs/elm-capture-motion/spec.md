## ADDED Requirements

### Requirement: Applied background-effect input identity
The system SHALL include actual native background-effect preferences and applied regions in the content identity of every participating render surface covered by a claimed family source.

EARS WRLK-BACKDROP-001: WHEN a native background-effect preference changes before a buffer commit, the system SHALL advance content identity before accepting a capture under that changed preference.

#### Scenario: Create effect before buffer commit
- **GIVEN** stable native family buffers, geometry, current style channels and gradients
- **WHEN** the native protocol processes creation and changes the renderer preference without a buffer commit
- **THEN** the current content revision changes and the preceding capture context cannot allocate ownership

### Requirement: Pending and applied protocol effects
The system SHALL distinguish pending requests from the applied native background-effect state.

EARS WRLK-BACKDROP-002: WHILE a region change or effect removal remains pending under the owning protocol, the system SHALL retain content identity for unchanged applied facts; WHEN the native commit applies the change, the system SHALL observe that applied state.

#### Scenario: Pending region and removal
- **WHEN** an actual pending region request or destroy is processed without the applying surface commit
- **THEN** the snapshot retains the applied region and preference until that commit, without inventing a buffer commit

### Requirement: Value-owned bounded regions
The system SHALL retain exact bounded normalized blur rectangles as immutable values.

EARS WRLK-BACKDROP-003: IF region facts are malformed, orphaned or exceed the aggregate budget, the system SHALL expose an unavailable source with stable canonical invalid state, later recovery identity and permanent exhaustion.

#### Scenario: Exact copied region
- **WHEN** the owning native region changes after a snapshot is retained
- **THEN** the retained snapshot remains unchanged; the next complete observation records the exact new rectangles

### Requirement: Actual background-dependent fidelity
The system SHALL establish background-dependent blur fidelity through actual owning native rendering and approved backdrop/source/privacy provenance.

EARS WRLK-BACKDROP-004: WHEN background-dependent blur fidelity is claimed, qualification SHALL preserve the original family privacy/foreign-pixel invariants and compare actual capture with independent native rendering under the exact backdrop, source context, transforms, clocks and physical ownership.

#### Scenario: Blur remains enabled
- **GIVEN** a backdrop that produces a measurable native blur effect
- **WHEN** the family capture path is qualified for that effect
- **THEN** actual native blur remains enabled and its pixels agree; a no_blur or snapshot-suppressed path cannot establish that claim
