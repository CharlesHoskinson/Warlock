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

### Requirement: ELM-DEL-011

The native service SHALL expose an allowlisted versioned operation schema and reject arbitrary command execution, filesystem paths and unrecognized methods from web content.

#### Scenario: ELM-DEL-011 delivery-011

- GIVEN a connected renderer
- WHEN it sends a shell command or unknown method
- THEN native authority rejects it

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

### Requirement: ELM-DEL-017

The shell SHALL keep credentials in the existing system credential service and exclude secrets, draft contents and captured pixels from ordinary diagnostic logs.

#### Scenario: ELM-DEL-017 delivery-017

- GIVEN secret-bearing native integrations
- WHEN diagnostics are collected
- THEN logs contain references and redacted metadata only

