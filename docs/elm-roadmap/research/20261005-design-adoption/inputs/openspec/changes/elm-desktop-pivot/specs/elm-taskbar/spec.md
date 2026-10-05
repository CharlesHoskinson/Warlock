# elm-taskbar

## ADDED Requirements

### Requirement: ELM-UI-004

The taskbar SHALL follow the INTERACTION.md primary-action table for zero, single and multiple family entries, distinguish application pin from always-on-top, and expose explicit new-instance actions without launching duplicates on ordinary activation.

#### Scenario: ELM-UI-004 taskbar-zero

- GIVEN a pinned app with zero windows
- WHEN primary pointer or keyboard activation occurs
- THEN one launch request is issued

#### Scenario: ELM-UI-004 taskbar-inactive

- GIVEN one inactive member
- WHEN primary pointer or keyboard activation occurs
- THEN the member visibly activates

#### Scenario: ELM-UI-004 taskbar-minimized

- GIVEN one minimized member
- WHEN primary pointer or keyboard activation occurs
- THEN the member restores and visibly activates

#### Scenario: ELM-UI-004 taskbar-active

- GIVEN one active eligible member
- WHEN primary pointer or keyboard activation occurs
- THEN the family minimizes with declared focus succession

#### Scenario: ELM-UI-004 taskbar-group

- GIVEN multiple family entries
- WHEN primary pointer or keyboard activation occurs
- THEN a group picker opens without new launch and selecting a member visibly activates it

#### Scenario: ELM-UI-004 taskbar-refusal

- GIVEN native authority refuses the requested action
- WHEN primary pointer or keyboard activation occurs
- THEN observed state remains authoritative with feedback

### Requirement: ELM-UI-008

The shell SHALL keep every configured icon, group member and action reachable through bounded scrolling or overflow, reveal keyboard selection, preserve identity/order across resizing, and expose labeled menu and window-operation affordances through pointer and keyboard.

#### Scenario: ELM-UI-008 overflow-first-last

- GIVEN small output, enlarged text and more icons than fit
- WHEN first and last entries and their menus are visited
- THEN all entries are reachable, focus is revealed and labels identify operations

#### Scenario: ELM-UI-008 overflow-resize

- GIVEN small output, enlarged text and more icons than fit
- WHEN output size changes
- THEN identity and configured order persist with reachable active selection

#### Scenario: ELM-UI-008 menu-invocation

- GIVEN small output, enlarged text and more icons than fit
- WHEN context menu or jump list is invoked
- THEN secondary click and Menu/Shift-F10 expose labeled operations and Escape returns focus

### Requirement: ELM-UX-002

The Elm desktop SHALL place taskbar application icons at the left edge of each configured taskbar output.

#### Scenario: ELM-UX-002 ux-002

- GIVEN two outputs at different scales
- WHEN taskbar opens
- THEN first icon begins at the configured left inset on each output

### Requirement: ELM-UX-003

WHEN the desktop catalog changes, the Elm desktop SHALL refresh application entries using desktop-file visibility and launch semantics.

#### Scenario: ELM-UX-003 ux-003

- GIVEN visible and hidden desktop entries
- WHEN catalog revision arrives
- THEN only eligible entries appear and launches preserve recorded arguments

### Requirement: ELM-UX-004

WHEN a user reorders or pins an application icon, the Elm desktop SHALL persist its desktop identity and relative order across shell restart.

#### Scenario: ELM-UX-004 ux-004

- GIVEN two pinned applications
- WHEN user reorders and restarts shell
- THEN both identities retain the chosen relative order

### Requirement: ELM-UX-005

WHEN a taskbar group is opened, the Elm desktop SHALL list each eligible window incarnation once and route selection to that incarnation.

#### Scenario: ELM-UX-005 ux-005

- GIVEN application has three windows
- WHEN group is opened and one member selected
- THEN three entries appear and only selected incarnation receives activation

### Requirement: ELM-UX-006

WHILE a window is minimized, the Elm desktop SHALL retain its taskbar identity and label its retained preview as historical.

#### Scenario: ELM-UX-006 ux-006

- GIVEN window has a retained frame
- WHEN window minimizes
- THEN entry remains present with historical preview label

### Requirement: ELM-UX-007

WHEN a retained preview is unavailable, the Elm desktop SHALL display the application icon and window title without substituting another incarnation’s pixels.

#### Scenario: ELM-UX-007 ux-007

- GIVEN preview lease has expired
- WHEN preview opens
- THEN fallback shows correct title and icon with no unrelated pixels

### Requirement: ELM-UX-008

WHEN an eligible taskbar window is selected, the Elm desktop SHALL request activation or restore through native authority without moving it to a scratchpad.

#### Scenario: ELM-UX-008 ux-008

- GIVEN minimized window belongs to workspace 2
- WHEN user selects its icon
- THEN native receipt confirms restore and workspace membership has not become scratchpad

### Requirement: ELM-UX-009

WHILE native observations mark a window active or attention-requesting, the Elm desktop SHALL expose distinct active and attention indicators.

#### Scenario: ELM-UX-009 ux-009

- GIVEN inactive window requests attention
- WHEN attention observation arrives
- THEN attention indicator differs from active indicator in pixels and accessible state

### Requirement: ELM-UX-010

WHEN a user invokes an application jump list, the Elm desktop SHALL show only catalog-declared actions and supported recent-item actions for that application identity.

#### Scenario: ELM-UX-010 ux-010

- GIVEN catalog declares two actions
- WHEN jump list opens
- THEN two declared actions appear and unsupported actions are absent

#### Scenario: ELM-UX-010 jump-list-recent-identity

- GIVEN an application with supported recent-item provider and a foreign item
- WHEN its jump list opens and an item is selected
- THEN only identity-bound supported recent actions appear and dispatch; foreign items never dispatch

