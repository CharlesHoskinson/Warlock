# elm-security

## ADDED Requirements

### Requirement: ELM-DEL-008

The installer SHALL place shell assets and configuration in reviewed user-owned versioned paths without modifying /usr/share/omarchy.

#### Scenario: ELM-DEL-008 delivery-008

- GIVEN a prepared user installation
- WHEN installation is rehearsed
- THEN only reviewed user-owned paths change

### Requirement: ELM-DEL-010

The native service SHALL authenticate bridge peers by local user identity and approved session lifetime before accepting effect requests.

#### Scenario: ELM-DEL-010 delivery-010

- GIVEN an unrelated local peer
- WHEN it requests a window effect
- THEN the request is refused without an effect

#### Scenario: ELM-DEL-010 peer-wrong-session

- GIVEN an authenticated same-user peer from another or expired session
- WHEN it sends an effect request
- THEN session authorization rejects the request without a native effect

#### Scenario: ELM-DEL-010 peer-approved-session

- GIVEN an approved current-session same-user peer
- WHEN it sends an authorized current operation
- THEN authentication admits it for subsequent native policy validation

### Requirement: ELM-DEL-011

The native service SHALL expose an allowlisted versioned operation schema and reject arbitrary command execution, filesystem paths and unrecognized methods from web content.

#### Scenario: ELM-DEL-011 delivery-011

- GIVEN a connected renderer
- WHEN it sends a shell command or unknown method
- THEN native authority rejects it

#### Scenario: ELM-DEL-011 arbitrary-path-denied

- GIVEN a connected renderer
- WHEN it submits an arbitrary filesystem path to an operation
- THEN schema validation refuses it with no file read, write or command execution

### Requirement: ELM-DEL-012

WHEN a privileged operation requires authorization, the shell SHALL delegate to the established native authorization flow and keep credentials outside Elm and JavaScript.

#### Scenario: ELM-DEL-012 delivery-012

- GIVEN a permission-denied Files operation
- WHEN the user selects authorization
- THEN the existing native askpass route owns the credential

### Requirement: ELM-DEL-013

The host SHALL load executable assets only from the hash-verified local release and deny remote scripts, remote navigation and runtime network fetches from shell content.

#### Scenario: ELM-DEL-013 delivery-013

- GIVEN an offline release
- WHEN shell content attempts a remote fetch
- THEN the request is blocked and local shell remains usable

### Requirement: ELM-DEL-014

The host SHALL enforce a restrictive Content Security Policy that allows only required local assets and denies remote origins, eval and unapproved inline scripts.

#### Scenario: ELM-DEL-014 delivery-014

- GIVEN the packaged host
- WHEN remote, eval or inline code is injected
- THEN each unapproved execution is refused

### Requirement: ELM-DEL-015

The settings store SHALL use a versioned validated schema with atomic writes and a preserved pre-migration copy before any schema upgrade.

#### Scenario: ELM-DEL-015 delivery-015

- GIVEN old valid settings
- WHEN a schema upgrade runs
- THEN valid new settings and recoverable original settings exist

#### Scenario: ELM-DEL-015 invalid-settings

- GIVEN a valid versioned settings store
- WHEN invalid fields are submitted
- THEN the active settings remain unchanged and validation refuses the write

#### Scenario: ELM-DEL-015 interrupted-settings

- GIVEN a valid versioned settings store
- WHEN an atomic write is interrupted
- THEN either complete old or complete new valid settings are recovered, never partial bytes

#### Scenario: ELM-DEL-015 migration-failure

- GIVEN a valid versioned settings store
- WHEN a schema migration fails
- THEN the preserved pre-migration copy remains recoverable and the failed upgrade is not activated

### Requirement: ELM-DEL-017

The shell SHALL keep credentials in the existing system credential service and exclude secrets, draft contents and captured pixels from ordinary diagnostic logs.

#### Scenario: ELM-DEL-017 delivery-017

- GIVEN secret-bearing native integrations
- WHEN diagnostics are collected
- THEN logs contain references and redacted metadata only

### Requirement: ELM-REV-002

WHILE native session lock is active, the host SHALL suppress application previews and reject new application capture admission.

#### Scenario: ELM-REV-002 retained-preview-lock

- GIVEN a retained application preview is visible
- WHEN native session lock activates
- THEN no application preview pixels are exposed on lock output and new capture requests are refused

### Requirement: ELM-REV-026

The native capture broker SHALL admit preview capture only for current authenticated-session surfaces allowed by preview policy and refuse lock-screen, policy-classified credential-entry and cross-session sources.

#### Scenario: ELM-REV-026 revision-026

- GIVEN an ordinary application and protected credential surface exist
- WHEN preview capture is requested
- THEN only the authorized application can receive a lease; protected/cross-session sources are refused

### Requirement: ELM-REV-027

WHILE the frontend is unready, the native chord journal SHALL retain only declared chord control events and omit unrelated text and credential keystrokes.

#### Scenario: ELM-REV-027 revision-027

- GIVEN frontend startup overlaps password typing and an Alt chord
- WHEN the pending chord journal is inspected
- THEN only declared Alt/repeat/release/Escape metadata is present; password/text keys are absent

