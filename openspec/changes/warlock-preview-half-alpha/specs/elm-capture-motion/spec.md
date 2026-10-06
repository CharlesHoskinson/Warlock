## ADDED Requirements

### Requirement: Declared partially transparent body composition
The system SHALL prove native client alpha independently of decoration transparency.

EARS WRLK-HALF-001: WHEN qualifying half-alpha under an applied tint screen program, the verifier SHALL compare all76800 body pixels, require73728 root alpha128/nativeRGB102/0/0 and3072 child alpha192/encodedRGB68/0/170/nativeRGB51/0/128, and refuse every composited mismatch or unexpected pixel.

#### Scenario: Opaque evidence cannot close half-alpha
- **WHEN** opaque native80 images have equal composited RGB
- **THEN** the half-alpha oracle still refuses them with76800 unexpected body pixels

### Requirement: Independent pointer preparation and restoration
The system SHALL preserve original cursor behavior while controlling pointer contamination in its private composition experiment.

EARS WRLK-HALF-002: WHEN preparing the private half-alpha measurement, the fixture SHALL save compositor-reported cursor coordinates, move and observe the cursor outside the entire body before issuing the scoped job, and restore and observe those original coordinates before remaining original GUI assertions.

#### Scenario: Focus warped pointer into body
- **GIVEN** native81 independent output includes the pointer and253 mismatches
- **WHEN** a corrected derivative runs
- **THEN** all pixels remain compared without masking, failed81 evidence remains immutable and original cursor checks remain mandatory

### Requirement: Explicit blur condition
The system SHALL distinguish a controlled no-blur experiment from complete backdrop fidelity.

EARS WRLK-HALF-003: WHILE no_blur=1 is used for half-alpha qualification, reports SHALL state that condition and SHALL NOT close arbitrary-backdrop blur provenance/privacy; the fixture SHALL restore no_blur=0 and active/inactive opacity1 before original remaining cases.

#### Scenario: Controlled composition passes
- **WHEN** the actual black backdrop and every body pixel match
- **THEN** background blur and general shader/color/output/hardware obligations remain open

### Requirement: Original native authority and retirement
The system SHALL retain original scope and physical ownership during added composition qualification.

EARS WRLK-HALF-004: WHEN capturing the half-alpha family, the system SHALL preserve the original native-issued two-second scope/deadline, exact owning core/plugin tuple, sealed FD3 context/crop/CRC and physical mapping/FD/export/producer retirement before terminal acceptance after all1783 original assertions and normal owned exits.

#### Scenario: Measurement disagreement after cleanup
- **WHEN** valid decoded facts have passed:false
- **THEN** terminal fidelity fails after original assertions and normal cleanup; exit0 measurement completion grants no acceptance

### Requirement: Coherent release remains mandatory
The system SHALL keep bounded half-alpha evidence separate from production eligibility and full GUI release.

EARS WRLK-HALF-005: WHEN publishing bounded half-alpha qualification, the verifier SHALL retain arbitrary blur/backdrop privacy, general neighbor/contextual shaders, CM/HDR/transforms/output, measured GPU-driver resources/hardware and original preview13/restore38/recovery34/case34/cursor/receipt/drag52/input/AT/IME/journey/reversible deployment obligations until independently accepted.

#### Scenario: Component passes do not qualify release
- **WHEN** the private experiment passes on one tuple
- **THEN** previewEligible and fullReleaseAccepted remain false until their original broader gates pass
