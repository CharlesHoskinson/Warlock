## ADDED Requirements

### Requirement: Native renderer input identity
The system SHALL use value-owned native renderer facts in the content revision of a style-cropped family source.

EARS WRLK-RENDER-001: WHEN a tracked native rendering input changes, the system SHALL advance the native content revision before accepting a capture of the changed source.

#### Scenario: Shadow falloff changes without a client commit
- **GIVEN** unchanged client buffers, family geometry, current style channels and gradients
- **WHEN** the owning native shadow falloff changes actual rendered pixels
- **THEN** the native content revision advances and the previous capture context is stale

#### Scenario: Native window opacity override
- **GIVEN** a mapped native window with half-alpha channels
- **WHEN** its native opaque override changes the pixels produced by the owning renderer
- **THEN** the source revision accounts for that rule independently of those alpha channels

### Requirement: Stable and unavailable native snapshots
The system SHALL preserve stable content identity and canonical unavailable state for native renderer snapshots.

EARS WRLK-RENDER-002: WHILE all source identity, family inputs and tracked rendering facts are unchanged, the system SHALL retain the native style content revision.

EARS WRLK-RENDER-003: IF required native facts are incomplete or malformed, the system SHALL expose an unavailable source; recovery SHALL use a later revision and exhausted identity SHALL remain unavailable.

#### Scenario: Repeated unavailable configuration
- **WHEN** the same unavailable native snapshot is observed repeatedly
- **THEN** it grants no valid capture context and cannot reset an exhausted revision counter

### Requirement: Old contexts cannot allocate capture ownership
The system SHALL validate the exact current native source context before creating capture storage ownership.

EARS WRLK-RENDER-004: WHEN a capture request carries a superseded native rendering context, the system SHALL refuse it before allocating a producer image or export.

#### Scenario: Glow falloff context is superseded
- **WHEN** native glow falloff advances the source revision
- **THEN** a request using the preceding context is refused and producer ownership remains empty

### Requirement: Live source with historical pixels
The system SHALL distinguish current source liveness from a retained frame's captured revision.

EARS WRLK-RENDER-005: WHILE an authorized retained frame has an older scene or content revision than the current source, the shared Elm policy SHALL present it as historical even if the source is live.

#### Scenario: Reopen after a live configuration change
- **GIVEN** a retained family image under its original native job, URI and expiry
- **WHEN** rendering configuration advances the live source revision and a new picker lease opens
- **THEN** the image is labeled historical without recapture, resume or renewal; original expiry causes physical retirement before the exact retained acknowledgment

### Requirement: Pixel evidence for renderer fidelity
The system SHALL establish claimed renderer coverage through actual native pixel evidence on the owning core/plugin tuple.

EARS WRLK-RENDER-006: WHEN qualification claims fidelity for a rendering effect, it SHALL compare actual captured pixels with independent native output and retain failures, physical ownership evidence and original deadline outcomes.

#### Scenario: Glow corner contour
- **WHEN** glow falloff is qualified
- **THEN** actual root pixels match independent output at both falloffs, changed pixels agree and pixels outside the owning shader's glow contour remain unchanged
