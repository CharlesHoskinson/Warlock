# elm-native-compositor

## ADDED Requirements

### Requirement: ELM-REN-023

WHERE a compositor replacement is selected, the project SHALL document a native Rust or C++ execution boundary and an Elm policy interface before implementation.

#### Scenario: ELM-REN-023 ren-023

- GIVEN replacement remains an optional product goal
- WHEN feasibility is reviewed
- THEN the plan names native ownership rather than promising pure Elm

### Requirement: ELM-REN-024

WHERE compositor replacement is selected, the native compositor SHALL implement a versioned Wayland and Xwayland compatibility matrix with explicit unsupported cases.

#### Scenario: ELM-REN-024 ren-024

- GIVEN Wayland and X11 clients share the session
- WHEN configure or modal transitions occur
- THEN supported semantics pass and unsupported cases are reported

### Requirement: ELM-REN-025

WHERE compositor replacement is selected, the native compositor SHALL own DRM/KMS outputs, seat input and session transitions independently of Elm responsiveness.

#### Scenario: ELM-REN-025 ren-025

- GIVEN the Elm host is stalled
- WHEN input or output hotplug occurs
- THEN native seat and output handling remain responsive

### Requirement: ELM-REN-026

WHERE compositor replacement is selected, the native compositor SHALL provide tested IME, preedit and text-input integration for its supported application matrix.

#### Scenario: ELM-REN-026 ren-026

- GIVEN a supported app has an active preedit
- WHEN focus changes then returns
- THEN text and focus follow the documented IME lifecycle

### Requirement: ELM-REN-027

WHERE compositor replacement is selected, the native compositor SHALL gate capture and remote-control access through documented portal and permission boundaries.

#### Scenario: ELM-REN-027 ren-027

- GIVEN a capture session is authorized
- WHEN permission is revoked
- THEN new capture and remote-input access stop

### Requirement: ELM-REN-028

WHERE compositor replacement is selected, the native compositor SHALL validate client requests and isolate privileged protocols from untrusted shell content.

#### Scenario: ELM-REN-028 ren-028

- GIVEN an untrusted client sends malformed protocol traffic
- WHEN the server processes it
- THEN privileged operations remain denied and other clients remain isolated

### Requirement: ELM-REN-029

WHERE compositor replacement is selected, the native compositor SHALL retain frame scheduling, fences, hit testing and buffer retirement in native loops without awaiting Elm port replies.

#### Scenario: ELM-REN-029 ren-029

- GIVEN Elm is paused or its webview crashes
- WHEN pointer and frame events arrive
- THEN native loops continue under the documented fallback policy

### Requirement: ELM-REN-030

WHERE compositor replacement is selected, the deployment plan SHALL provide tested session fallback and recovery instructions that disclose loss of application connections on compositor failure.

#### Scenario: ELM-REN-030 ren-030

- GIVEN the optional compositor fails in a sacrificial session
- WHEN recovery executes
- THEN a working fallback session starts with connection-loss limits documented

