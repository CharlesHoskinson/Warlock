# elm-host

## ADDED Requirements

### Requirement: ELM-ARC-001

The Elm desktop SHALL record the deployed compositor, plugin, shell, compiler and host versions and source hashes before a comparative native run.

#### Scenario: ELM-ARC-001 architecture-001

- GIVEN a taskbar-v3 desktop
- WHEN a comparison is prepared
- THEN the report identifies every participating artifact

### Requirement: ELM-ARC-002

The Elm desktop SHALL assign DOM presentation to Elm, Wayland surface lifetime to the native host, and application-window effects to native authority.

#### Scenario: ELM-ARC-002 architecture-002

- GIVEN an Elm shell view
- WHEN an application-window action is requested
- THEN only native authority mutates the application window

### Requirement: ELM-ARC-021

The Elm desktop SHALL compare GTK/WebKitGTK and a dedicated Qt/WebEngine host using the same Elm assets, compositor tuple, workload and measurement definitions.

#### Scenario: ELM-ARC-021 architecture-021

- GIVEN two candidate hosts
- WHEN the same vertical slice is tested
- THEN separate native results and resource measurements are retained

### Requirement: ELM-ARC-022

The Elm desktop SHALL create native layer and popup roles, input regions and keyboard-interactivity settings before exposing their Elm views.

#### Scenario: ELM-ARC-022 architecture-022

- GIVEN a taskbar and popup
- WHEN their native surfaces are created
- THEN roles and input masks precede frontend readiness

### Requirement: ELM-ARC-023

The Elm desktop SHALL pass native host tests for IME preedit, keyboard navigation, Orca and braille, clipboard, file drag-and-drop, fractional scale and negative output coordinates.

#### Scenario: ELM-ARC-023 architecture-023

- GIVEN a selected host
- WHEN the compatibility campaign runs
- THEN each named route has native evidence or blocks release

### Requirement: ELM-ARC-024

The Elm desktop SHALL load packaged shell assets from an allowlisted local origin and deny remote navigation, arbitrary native method invocation and unapproved resource URLs.

#### Scenario: ELM-ARC-024 architecture-024

- GIVEN an untrusted navigation or message
- WHEN it targets the privileged bridge
- THEN navigation or capability access is denied

### Requirement: ELM-ARC-026

WHEN the frontend or renderer restarts, the Elm desktop SHALL invalidate its old epoch, revoke its owned resources and reconcile a fresh snapshot before admitting new effects.

#### Scenario: ELM-ARC-026 architecture-026

- GIVEN a renderer with pending work
- WHEN it crashes and restarts
- THEN old work is refused and effects await snapshot reconciliation

### Requirement: ELM-ARC-027

WHEN Elm shell activation fails its release checks, the Elm desktop SHALL restore the recorded accepted shell configuration without restarting the compositor or closing application windows.

#### Scenario: ELM-ARC-027 architecture-027

- GIVEN the accepted shell configuration is saved
- WHEN a candidate activation fails
- THEN the accepted shell returns and drafts remain connected

