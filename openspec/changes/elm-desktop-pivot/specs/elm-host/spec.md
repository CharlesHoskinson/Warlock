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

#### Scenario: ELM-ARC-002 ownership-presentation

- GIVEN a pinned Elm/native host
- WHEN a view and its Wayland surface are created and retired
- THEN Elm owns DOM state, native host owns surface lifetime and native authority alone owns application effects

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

#### Scenario: ELM-ARC-023 host-ime

- GIVEN the selected host and an active preedit string
- WHEN the ime compatibility route executes
- THEN composition commits or cancels without duplicate/missing characters and restores the documented focus

#### Scenario: ELM-ARC-023 host-keyboard

- GIVEN the selected host and a keyboard-only user
- WHEN the keyboard compatibility route executes
- THEN taskbar, switcher, menus and settings are reachable and escapable with visible focus

#### Scenario: ELM-ARC-023 host-orca

- GIVEN the selected host and Orca with supported speech output
- WHEN the orca compatibility route executes
- THEN current control name/state and focus transitions are announced correctly

#### Scenario: ELM-ARC-023 host-braille

- GIVEN the selected host and a supported braille device
- WHEN the braille compatibility route executes
- THEN selected control name/state and focus changes appear on the braille display

#### Scenario: ELM-ARC-023 host-clipboard

- GIVEN the selected host and two supported native applications and shell input
- WHEN the clipboard compatibility route executes
- THEN copied content transfers to the intended selection without stale ownership

#### Scenario: ELM-ARC-023 host-file-dnd

- GIVEN the selected host and a valid filesystem payload and native destination
- WHEN the file-dnd compatibility route executes
- THEN the accepted payload reaches the intended destination once and cancelled drags cause no action

#### Scenario: ELM-ARC-023 host-scale

- GIVEN the selected host and a supported fractional-scale output
- WHEN the scale compatibility route executes
- THEN rendered and hit-tested control bounds correspond in the target scale

#### Scenario: ELM-ARC-023 host-negative-output

- GIVEN the selected host and an output positioned at negative native coordinates
- WHEN the negative-output compatibility route executes
- THEN popups and hit coordinates remain inside the correct output bounds

### Requirement: ELM-ARC-024

The Elm desktop SHALL load packaged shell assets from an allowlisted local origin and deny remote navigation, arbitrary native method invocation and unapproved resource URLs.

#### Scenario: ELM-ARC-024 architecture-024

- GIVEN an untrusted navigation or message
- WHEN it targets the privileged bridge
- THEN navigation or capability access is denied

### Requirement: ELM-ARC-026

WHEN the frontend, renderer or native authority restarts, the native authority SHALL invalidate old epochs and resources and install a fresh coherent snapshot before admitting effects.

#### Scenario: ELM-ARC-026 architecture-026

- GIVEN a renderer with pending work
- WHEN it crashes and restarts
- THEN old work is refused and effects await snapshot reconciliation

#### Scenario: ELM-ARC-026 authority-restart

- GIVEN pending old-epoch work exists
- WHEN the authority restarts
- THEN old work is rejected even when target geometry is unchanged and a fresh snapshot precedes new effect admission

### Requirement: ELM-ARC-027

WHEN Elm shell activation fails its release checks, the Elm desktop SHALL restore the recorded accepted shell configuration without restarting the compositor or closing application windows.

#### Scenario: ELM-ARC-027 architecture-027

- GIVEN the accepted shell configuration is saved
- WHEN a candidate activation fails
- THEN the accepted shell returns and drafts remain connected

### Requirement: ELM-TEA-001

The Elm frontend SHALL represent lifecycle, receipt and operation state with custom types, keep native observations separate from desired UI state and derive projections from one authoritative snapshot without duplicated native authority.

#### Scenario: ELM-TEA-001 tea-typed-model

- GIVEN a pinned Elm model and named domain fixture
- WHEN the typed-model boundary and replay campaign execute
- THEN the declared contract holds, exact models and effect descriptions match the fixture and no native acceptance is inferred

### Requirement: ELM-TEA-002

The Elm frontend SHALL implement state transitions as pure Model and Msg reducers with typed effect descriptions, and SHALL reproduce identical models and effects for identical sanitized message histories.

#### Scenario: ELM-TEA-002 tea-pure-update

- GIVEN a pinned Elm model and named domain fixture
- WHEN the pure-update boundary and replay campaign execute
- THEN the declared contract holds, exact models and effect descriptions match the fixture and no native acceptance is inferred

### Requirement: ELM-TEA-003

The Elm frontend SHALL sequence dependent native effects through matching committed receipts, reserve Cmd.batch for independent effects and validate observations at typed decoders before model mutation.

#### Scenario: ELM-TEA-003 tea-effects

- GIVEN a pinned Elm model and named domain fixture
- WHEN the effects boundary and replay campaign execute
- THEN the declared contract holds, exact models and effect descriptions match the fixture and no native acceptance is inferred

### Requirement: ELM-TEA-004

The Elm frontend SHALL derive recurring subscriptions from visible consumers and active transactions while preserving ordered native control and revocation delivery independently of overlay visibility.

#### Scenario: ELM-TEA-004 tea-subscriptions

- GIVEN a pinned Elm model and named domain fixture
- WHEN the subscriptions boundary and replay campaign execute
- THEN the declared contract holds, exact models and effect descriptions match the fixture and no native acceptance is inferred

### Requirement: ELM-TEA-005

The Elm host adapter SHALL keep JavaScript limited to validated transport and approved host integrations, keep GPU resources and per-frame work outside Elm messages and use current commands and subscriptions rather than historical Signal APIs.

#### Scenario: ELM-TEA-005 tea-narrow-interop

- GIVEN a pinned Elm model and named domain fixture
- WHEN the narrow-interop boundary and replay campaign execute
- THEN the declared contract holds, exact models and effect descriptions match the fixture and no native acceptance is inferred

