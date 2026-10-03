# elm-shell-experience

## ADDED Requirements

### Requirement: ELM-UI-002

WHEN a listed target outside the effective workspace set is activated, the native authority SHALL navigate to its preserved workspace on its owning output before visible activation without implicit transfer, and SHALL maintain an eligible visible fallback or separately validated compensation if a later restore is refused.

#### Scenario: ELM-UI-002 activate-other-workspace

- GIVEN a target on workspace 2 and activation from workspace 1
- WHEN taskbar restore commits
- THEN workspace 2 becomes visible on its owning output and target pixels and focus are observed with membership unchanged

#### Scenario: ELM-UI-002 activate-other-output

- GIVEN a target on workspace 2 and activation from workspace 1
- WHEN a target on another output is selected
- THEN that output presents its preserved workspace and target focus without moving the window

#### Scenario: ELM-UI-002 activation-refused

- GIVEN a target on workspace 2 and activation from workspace 1
- WHEN workspace navigation or restore is refused
- THEN current visible focus remains, no hidden target gets focus and correlated refusal appears

#### Scenario: ELM-UI-002 navigation-partial-refusal

- GIVEN workspace navigation committed and prior focus is no longer visible
- WHEN the subsequent restore is refused
- THEN eligible visible destination fallback or separately generation-validated compensation restores usable focus; no stale target or uncertain replay occurs

### Requirement: ELM-UI-005

The launcher SHALL bind results and selection to the current query and catalog generation, apply the frozen matching/ranking policy, expose initial, loading, no-match and unavailable states, and preserve the query with reachable recovery on refusal.

#### Scenario: ELM-UI-005 search-no-match

- GIVEN a query and catalog fixture
- WHEN no entries match
- THEN no-match message and query remain reachable without launch

#### Scenario: ELM-UI-005 search-unavailable

- GIVEN a query and catalog fixture
- WHEN catalog provider fails
- THEN unavailable state exposes keyboard retry without automatic launch

#### Scenario: ELM-UI-005 search-race

- GIVEN a query and catalog fixture
- WHEN query changes while old refresh completes
- THEN only current-generation results and selection can dispatch

#### Scenario: ELM-UI-005 search-removed

- GIVEN a query and catalog fixture
- WHEN selected identity disappears before Enter
- THEN no replacement entry launches and selection reconciles

#### Scenario: ELM-UI-005 search-refused

- GIVEN a query and catalog fixture
- WHEN launch is refused
- THEN query and focus remain with accessible refusal and retry

### Requirement: ELM-UI-006

The Task View SHALL provide keyboard and pointer selection of windows and workspaces, identity-correlated visible activation and transfer outcomes, usable empty states and dismissal with focus return, according to the frozen workspace-management scope.

#### Scenario: ELM-UI-006 overview-select

- GIVEN an open overview
- WHEN a minimized cross-workspace entry is selected
- THEN matching restore/navigation commits and the target becomes visible

#### Scenario: ELM-UI-006 overview-refusal

- GIVEN an open overview
- WHEN native activation is refused
- THEN overview remains usable with feedback and retained selection context

#### Scenario: ELM-UI-006 overview-empty

- GIVEN an open overview
- WHEN an empty workspace is selected
- THEN empty destination is navigable and dismissal remains available

#### Scenario: ELM-UI-006 overview-cancel

- GIVEN an open overview
- WHEN overview is dismissed without action
- THEN no native mutation occurs and eligible opener focus returns

#### Scenario: ELM-UI-006 overview-retire

- GIVEN an open overview
- WHEN selected member disappears
- THEN selection safely falls back without activating a replacement incarnation

### Requirement: ELM-UI-007

The shell SHALL expose correlated pending, committed, refused, cancelled and unknown/reconciling action states, suppress duplicate dispatch during pending work, and provide reachable recovery after native reconciliation without replaying uncertain mutations or discarding user context.

#### Scenario: ELM-UI-007 restore-pending

- GIVEN a restore action with retained user context
- WHEN its outcome becomes pending
- THEN visible and accessible correlated feedback appears, focus/context persist, no false success or duplicate effect occurs, and recovery follows native truth

#### Scenario: ELM-UI-007 restore-refused

- GIVEN a restore action with retained user context
- WHEN its outcome becomes refused
- THEN visible and accessible correlated feedback appears, focus/context persist, no false success or duplicate effect occurs, and recovery follows native truth

#### Scenario: ELM-UI-007 restore-unknown

- GIVEN a restore action with retained user context
- WHEN its outcome becomes unknown
- THEN visible and accessible correlated feedback appears, focus/context persist, no false success or duplicate effect occurs, and recovery follows native truth

#### Scenario: ELM-UI-007 pin-pending

- GIVEN a pin action with retained user context
- WHEN its outcome becomes pending
- THEN visible and accessible correlated feedback appears, focus/context persist, no false success or duplicate effect occurs, and recovery follows native truth

#### Scenario: ELM-UI-007 pin-refused

- GIVEN a pin action with retained user context
- WHEN its outcome becomes refused
- THEN visible and accessible correlated feedback appears, focus/context persist, no false success or duplicate effect occurs, and recovery follows native truth

#### Scenario: ELM-UI-007 pin-unknown

- GIVEN a pin action with retained user context
- WHEN its outcome becomes unknown
- THEN visible and accessible correlated feedback appears, focus/context persist, no false success or duplicate effect occurs, and recovery follows native truth

#### Scenario: ELM-UI-007 snap-pending

- GIVEN a snap action with retained user context
- WHEN its outcome becomes pending
- THEN visible and accessible correlated feedback appears, focus/context persist, no false success or duplicate effect occurs, and recovery follows native truth

#### Scenario: ELM-UI-007 snap-refused

- GIVEN a snap action with retained user context
- WHEN its outcome becomes refused
- THEN visible and accessible correlated feedback appears, focus/context persist, no false success or duplicate effect occurs, and recovery follows native truth

#### Scenario: ELM-UI-007 snap-unknown

- GIVEN a snap action with retained user context
- WHEN its outcome becomes unknown
- THEN visible and accessible correlated feedback appears, focus/context persist, no false success or duplicate effect occurs, and recovery follows native truth

#### Scenario: ELM-UI-007 jump-list-pending

- GIVEN a jump-list action with retained user context
- WHEN its outcome becomes pending
- THEN visible and accessible correlated feedback appears, focus/context persist, no false success or duplicate effect occurs, and recovery follows native truth

#### Scenario: ELM-UI-007 jump-list-refused

- GIVEN a jump-list action with retained user context
- WHEN its outcome becomes refused
- THEN visible and accessible correlated feedback appears, focus/context persist, no false success or duplicate effect occurs, and recovery follows native truth

#### Scenario: ELM-UI-007 jump-list-unknown

- GIVEN a jump-list action with retained user context
- WHEN its outcome becomes unknown
- THEN visible and accessible correlated feedback appears, focus/context persist, no false success or duplicate effect occurs, and recovery follows native truth

#### Scenario: ELM-UI-007 settings-pending

- GIVEN a settings action with retained user context
- WHEN its outcome becomes pending
- THEN visible and accessible correlated feedback appears, focus/context persist, no false success or duplicate effect occurs, and recovery follows native truth

#### Scenario: ELM-UI-007 settings-refused

- GIVEN a settings action with retained user context
- WHEN its outcome becomes refused
- THEN visible and accessible correlated feedback appears, focus/context persist, no false success or duplicate effect occurs, and recovery follows native truth

#### Scenario: ELM-UI-007 settings-unknown

- GIVEN a settings action with retained user context
- WHEN its outcome becomes unknown
- THEN visible and accessible correlated feedback appears, focus/context persist, no false success or duplicate effect occurs, and recovery follows native truth

### Requirement: ELM-UI-015

WHEN an operation exceeds its frozen feedback threshold, the shell SHALL expose accessible pending or reconciling feedback, keep cancellation and independent controls usable and show success only after matching native confirmation.

#### Scenario: ELM-UI-015 slow-native

- GIVEN a pending restore with original deadline
- WHEN feedback threshold is reached
- THEN pending feedback appears, controls remain usable and no success is claimed

#### Scenario: ELM-UI-015 unknown-native

- GIVEN a submitted operation becomes Unknown
- WHEN reconciliation runs
- THEN feedback describes uncertainty and no blind retry occurs

#### Scenario: ELM-UI-015 feedback-threshold

- GIVEN P0 feedback matrix
- WHEN host qualification begins
- THEN a missing numeric threshold blocks qualification

### Requirement: ELM-UI-019

WHEN an output disappears, the host SHALL recover shell controls and displaced popup focus on a declared surviving output, preserve workspace identity and reachable application recovery, and reject removed-generation effects until available outputs reconcile.

#### Scenario: ELM-UI-019 output-remove

- GIVEN focused popup and recovery control on external output
- WHEN output unplugs
- THEN popup dismisses to eligible focus or rehosts and recovery stays keyboard reachable

#### Scenario: ELM-UI-019 outputs-return

- GIVEN all outputs disappear
- WHEN one returns
- THEN controls reconcile on available output without old-generation effects

### Requirement: ELM-UI-020

WHEN a migrated component is first enabled, the shell SHALL offer dismissible keyboard-accessible guidance, preserve approved preference mappings, require explicit shortcut-conflict decisions and expose offline recovery without mandatory onboarding.

#### Scenario: ELM-UI-020 first-use

- GIVEN customized shortcuts and qualified component
- WHEN component enables and guidance dismisses
- THEN mapping or explicit conflict choice persists, help remains available and component works

#### Scenario: ELM-UI-020 offline-recovery

- GIVEN guidance dismissed and host later fails
- WHEN documented offline rollback runs
- THEN predecessor and compatible preferences recover without the failed host

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

#### Scenario: ELM-UX-015 modal-draft-retained

- GIVEN a parent with unsaved text and its eligible modal
- WHEN the family is activated then focus switches to an unrelated terminal
- THEN native modal targeting and terminal activation succeed separately and exact parent and modal draft bytes remain intact

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

#### Scenario: ELM-UX-018 transfer-refused

- GIVEN a window on workspace 1
- WHEN native authority refuses transfer to workspace 2
- THEN membership remains workspace 1 and refusal feedback appears

#### Scenario: ELM-UX-018 transfer-accepted

- GIVEN a window on workspace 1
- WHEN native authority commits transfer to workspace 2
- THEN membership changes only with the matching committed receipt

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

#### Scenario: ELM-UX-029 launcher-accepted

- GIVEN a current catalog entry is selected
- WHEN Enter causes a native accepted launch
- THEN one identity-bound launch request is accepted and success is shown without refusal feedback

#### Scenario: ELM-UX-029 launcher-refused

- GIVEN a current catalog entry is selected but native launch is denied
- WHEN Enter submits the request
- THEN one request is refused and the UI shows that refusal without a duplicate launch

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

#### Scenario: ELM-UX-031 notification-valid

- GIVEN a current live notification with action identity A
- WHEN A is invoked
- THEN the current producer receives exactly that action once and another notification is unaffected

#### Scenario: ELM-UX-031 notification-reused

- GIVEN an expired notification id has been reused by a new native incarnation
- WHEN an old queued action arrives
- THEN the old action is rejected and the new incarnation receives no unintended action

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

#### Scenario: ELM-UX-035 release-all-pass

- GIVEN one frozen coherent candidate tuple has all required native campaigns and migrated-surface scenarios executed
- WHEN release review evaluates the complete gate ledger
- THEN each mapped original38/34, pin/input, dragresize52, reliability and surface gate is pass on that tuple before admission

#### Scenario: ELM-UX-035 release-failed-case

- GIVEN one required original case or migrated surface has failed or lacks evidence
- WHEN release review runs
- THEN release is blocked and the missing/failed case identity is recorded

