# elm-shell-experience

## ADDED Requirements

### Requirement: ELM-UX-001

The Elm desktop SHALL maintain a scope inventory that assigns each shell surface a migration owner, acceptance scenario and rollback destination.

#### Scenario: ELM-UX-001 ux-001

- GIVEN archived QML shell
- WHEN scope is frozen
- THEN every inventoried surface has an owner, scenario and rollback route

### Requirement: ELM-UX-015

WHEN a user activates a modal family, the Elm desktop SHALL request the native eligible modal target while preserving the application’s draft content.

#### Scenario: ELM-UX-015 ux-015

- GIVEN Brave draft dialog and unrelated terminal overlap
- WHEN user selects either application
- THEN native modal target or terminal activates and draft content remains intact

### Requirement: ELM-UX-016

WHEN a user toggles always-on-top on a maximized family, the Elm desktop SHALL display pin and maximize state only after correlated native observations.

#### Scenario: ELM-UX-016 ux-016

- GIVEN maximized application overlaps floating window
- WHEN pin then unpin completes
- THEN displayed pin/MAX state agrees with native state and visible hit target

### Requirement: ELM-UX-017

WHEN Task View opens, the Elm desktop SHALL show eligible windows grouped by workspace with a keyboard-selectable active-workspace marker.

#### Scenario: ELM-UX-017 ux-017

- GIVEN two populated workspaces
- WHEN Task View opens
- THEN groups match native membership and active workspace is named

### Requirement: ELM-UX-018

WHEN a user transfers a window through Task View, the Elm desktop SHALL update workspace membership only after native transfer acceptance.

#### Scenario: ELM-UX-018 ux-018

- GIVEN window is on workspace 1
- WHEN user requests workspace 2 transfer
- THEN accepted transfer updates membership; refusal retains workspace 1

### Requirement: ELM-UX-019

WHEN a user chooses a snap region, the Elm desktop SHALL submit geometry keyed to the selected output generation and show the accepted native placement.

#### Scenario: ELM-UX-019 ux-019

- GIVEN output has a defined work area
- WHEN user chooses left half
- THEN accepted placement matches half work area within native rounding tolerance

### Requirement: ELM-UX-020

IF an output changes during snap selection, THEN the Elm desktop SHALL invalidate the old preview and require geometry derived from the new output generation before commit.

#### Scenario: ELM-UX-020 ux-020

- GIVEN snap chooser is open
- WHEN output scale changes or output disappears
- THEN old generation geometry is never committed

### Requirement: ELM-UX-021

WHEN a user drags or resizes an application window, the Elm desktop SHALL preserve native pointer ownership until release or explicit cancellation.

#### Scenario: ELM-UX-021 ux-021

- GIVEN drag crosses the taskbar and another output
- WHEN pointer releases
- THEN exactly one gesture ends and no shell surface steals the drag

### Requirement: ELM-UX-022

WHILE reduced motion is enabled, the Elm desktop SHALL use the documented reduced-motion transition profile for minimize, restore and shell overlays.

#### Scenario: ELM-UX-022 ux-022

- GIVEN reduced motion setting is enabled
- WHEN window minimizes and restores
- THEN recorded transitions match approved reduced-motion profile

### Requirement: ELM-UX-029

WHEN a user searches and launches a catalog entry, the Elm desktop SHALL issue one identity-bound launch request and show failure feedback when native launch is refused.

#### Scenario: ELM-UX-029 ux-029

- GIVEN matching catalog entry is selected
- WHEN Enter is pressed
- THEN one request occurs and refused launch displays an error

### Requirement: ELM-UX-030

WHEN a user changes shell settings, the Elm desktop SHALL persist validated preferences and restore them after host restart without applying invalid values.

#### Scenario: ELM-UX-030 ux-030

- GIVEN valid theme setting and invalid scale are submitted
- WHEN host restarts
- THEN valid preference survives and invalid scale is rejected

### Requirement: ELM-UX-031

WHEN a notification action is invoked, the Elm desktop SHALL dispatch the action to its current notification identity and remove expired action targets.

#### Scenario: ELM-UX-031 ux-031

- GIVEN notification expires while center is open
- WHEN user attempts its former action
- THEN expired action sends no request to another notification

### Requirement: ELM-UX-032

WHEN a user opens a system menu, the Elm desktop SHALL present capability-supported controls and display native outcomes for requested system changes.

#### Scenario: ELM-UX-032 ux-032

- GIVEN network adapter is unavailable
- WHEN system menu opens
- THEN network control indicates unavailable and remaining controls show observed state

### Requirement: ELM-UX-033

WHEN a user opens Files from the Elm shell, the Elm desktop SHALL invoke the installed explorer with the requested path or collection and preserve its existing operation semantics.

#### Scenario: ELM-UX-033 ux-033

- GIVEN existing Files window and collection identifier
- WHEN user opens that collection from shell
- THEN existing explorer is reused at requested collection; no ops.sh semantics change

### Requirement: ELM-UX-034

WHERE a later Elm Files replacement is approved, the Elm desktop SHALL preserve Quint-specified copy, move, collision, trash and authorization semantics before replacing the installed operation adapter.

#### Scenario: ELM-UX-034 ux-034

- GIVEN approved replacement uses captured fileops specification
- WHEN copy collision and permission denial scenarios run
- THEN collision suffix and authorization behavior match spec with no destructive deletion

### Requirement: ELM-UX-035

The Elm desktop SHALL release the defined shell scope only after original native campaigns and each migrated surface’s acceptance scenarios pass against one frozen source and ABI tuple.

#### Scenario: ELM-UX-035 ux-035

- GIVEN candidate shell and native pair are frozen
- WHEN release review runs
- THEN 38/34 restore, remaining pin, 52 drag/resize and surface scenarios have explicit results

