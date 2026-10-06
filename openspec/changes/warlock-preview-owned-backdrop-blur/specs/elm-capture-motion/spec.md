## ADDED Requirements

### Requirement: Generated backdrop is an explicit source
The system SHALL enforce the explicit generated-backdrop boundary.

EARS WRLK-BACKDROP-001: WHEN a generated-backdrop capture is requested, the system SHALL derive opaque native color on the compositor owner thread, include its copied value or absence in the existing immutable source identity and SHALL NOT accept a caller-supplied color or native pixel attestation.

#### Scenario: Changed actual generated color
- **WHEN** actual native generated color changes or becomes unavailable
- **THEN** the source epoch advances or generated capture refuses before allocation; copied earlier facts remain immutable

### Requirement: Private blur resources and contributors
The system SHALL enforce the explicit generated-backdrop boundary.

EARS WRLK-BACKDROP-002: WHILE generated-backdrop capture is active, native live blur SHALL read only the complete owned generated-color/family source and two private initialized scratch buffers; monitor images, foreign windows, shared work-buffer pools and precomputed monitor blur caches SHALL NOT become capture inputs.

#### Scenario: Monitor cache contains foreign pixels
- **WHEN** the normal monitor blur cache contains another window
- **THEN** the capture disables that cache path and renders only its declared generated/family contributors

### Requirement: Admission and physical phase ownership
The system SHALL enforce the explicit generated-backdrop boundary.

EARS WRLK-BACKDROP-003: WHEN admitting generated-backdrop capture, the producer SHALL reserve the conservative three-output-plane/readback/encoded peak under unchanged capacity before EGL/FBO allocation, recheck the original plan/context/deadline and retire scratch after GPU completion before screen destination allocation.

#### Scenario: One byte below complete phase
- **WHEN** the available reservation is one byte below required peak
- **THEN** admission refuses without allocation; exact-capacity reservation releases after physical retirement

### Requirement: Typed source transport and grants
The system SHALL enforce the explicit generated-backdrop boundary.

EARS WRLK-BACKDROP-004: WHEN transferring generated-backdrop pixels, the producer SHALL use authenticated typed scope/capture/state/retire operations and FD4 plane256/crop/scale/native-color metadata bound to the exact original child grant/context; legacy planes SHALL NOT import or retire this source.

#### Scenario: Legacy alias is refused
- **WHEN** a legacy FD3 import or transparent-plane retirement names the new capture
- **THEN** the request refuses without granting pixel authority or retiring its producer

### Requirement: Native regression and independent pixels
The system SHALL enforce the explicit generated-backdrop boundary.

EARS WRLK-BACKDROP-005: WHEN qualifying native blur, the verifier SHALL retain all original1783 assertions/deadlines/normal exits and compare every76800 body pixel in both brightness states against independent native output, require the unchanged RGB-delta predicate and stronger exact RGBA equality, and retain failed84 evidence.

#### Scenario: Tracked configuration omitted pixels
- **WHEN** configuration changes native brightness but family pixels remain unchanged
- **THEN** terminal fidelity refuses after original assertions/normal cleanup; new implementation must pass the same original delta predicate

### Requirement: Ownership through every refusal
The system SHALL enforce the explicit generated-backdrop boundary.

EARS WRLK-BACKDROP-006: WHEN decoding or retiring a generated FD, the system SHALL take physical ownership before validation, reject malformed version/flags/color/context/CRC/seals, close mappings/FDs before capacity releases and require exact export/producer retirement before terminal acceptance.

#### Scenario: Malformed metadata owns transferred FD
- **WHEN** metadata is malformed after ownership transfers
- **THEN** typed refusal closes the physical FD and grants no frame or lease authority

### Requirement: Complete backdrop and release remain mandatory
The system SHALL enforce the explicit generated-backdrop boundary.

EARS WRLK-BACKDROP-007: WHEN publishing a generated-color fixture result, the verifier SHALL retain arbitrary authorized backdrop/privacy/dependency, general shader/color/HDR/transform/output/GPU-driver/hardware, original preview/restore/recovery/input/AT/IME/journey and coherent deployment obligations until independently accepted on the release tuple.

#### Scenario: Controlled generated white matches
- **WHEN** the bounded generated-white experiment passes
- **THEN** previewEligible and fullReleaseAccepted remain false until their original broader gates pass
