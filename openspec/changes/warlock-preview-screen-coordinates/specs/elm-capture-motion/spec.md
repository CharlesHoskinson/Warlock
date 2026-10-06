## ADDED Requirements

### Requirement: Native shader coordinate domain
The system SHALL preserve the owning screen program's native coordinate and texture domain for claimed output-coordinate captures.

EARS WRLK-SHADER-COORD-001: WHEN applying a supported output shader to an authorized family, the renderer SHALL use the actual native output coordinate domain, texture dimensions and framebuffer fragment coordinates; any changed applied source SHALL refuse publication under the original context and deadline.

#### Scenario: Static coordinate program
- **GIVEN** a static program emitting native interpolated screen coordinates
- **WHEN** an owned family crop is captured
- **THEN** its qualified pixels match independent native output at the same positions, while every original GUI identity/deadline remains unchanged

### Requirement: Isolated source and physical crop ownership
The system SHALL retain only authorized contributor pixels and independently own the exported crop.

EARS WRLK-SHADER-COORD-002: WHILE shader work is pending, the source SHALL remain independently owned; WHEN completion is confirmed, the source SHALL retire before new crop allocation, and destination retirement SHALL follow confirmed crop-copy completion without publishing a monitor or foreign-window image.

#### Scenario: Full plane with isolated contributors
- **WHEN** a native shader needs output-sized input
- **THEN** only validated family contributors are rendered into the private plane, and the final export contains exactly its authorized native crop under existing producer/export/consumer receipts

### Requirement: Storage admission before allocation
The system SHALL account every nominal framebuffer phase before allocating capture storage.

EARS WRLK-SHADER-COORD-003: WHEN a producer admits a shader capture, it SHALL reserve at least the maximum nominal source/destination/crop/readback/PNG allocation phase under unchanged capacity and recheck the native plan/source/original deadline before allocation; measured GPU acceptance SHALL additionally include actual driver/compositor allocations.

#### Scenario: Crop budget alone is insufficient
- **GIVEN** crop-only storage fits but two native output planes exceed the remaining capacity
- **WHEN** admission is attempted
- **THEN** allocation is refused with no producer/export authority and no capacity or deadline extension

### Requirement: Bounded coordinate proof and remaining fidelity
The system SHALL keep coordinate qualification separate from complete shader and GUI release acceptance.

EARS WRLK-SHADER-COORD-004: WHEN publishing a bounded coordinate result, the release verifier SHALL retain off-output, whole-family/alpha/decorations, neighborhood/backdrop/privacy, contextual/time/pointer/output, color/HDR/transform, driver/resource and hardware obligations until independently qualified on the coherent release tuple.

#### Scenario: Coordinate sample does not close release
- **WHEN** a coordinate sample and bounded nominal storage model pass
- **THEN** full shader/family fidelity and every unmet original preview/restore/recovery/drag/input/AT/IME/resource/hardware/journey/deployment release gate remain open
