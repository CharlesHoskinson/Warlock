# elm-accessibility

## ADDED Requirements

### Requirement: ELM-UX-023

The Elm desktop SHALL provide keyboard routes for launcher, taskbar groups, switcher, Task View, snap chooser, menus and settings without requiring pointer input.

#### Scenario: ELM-UX-023 ux-023

- GIVEN pointer is unused
- WHEN keyboard-only acceptance script visits all migrated surfaces
- THEN each surface can be opened, operated and dismissed without pointer events

### Requirement: ELM-UX-024

WHILE a shell popup owns keyboard focus, the Elm desktop SHALL constrain traversal to its documented focus order and restore the previous eligible focus target on dismissal.

#### Scenario: ELM-UX-024 ux-024

- GIVEN taskbar menu has focus
- WHEN Tab traversal then Escape occurs
- THEN focus follows menu order and returns to original eligible target

### Requirement: ELM-UX-025

The Elm desktop SHALL expose names, roles, states and focus changes for taskbar and switcher controls through the chosen host’s native accessibility bridge.

#### Scenario: ELM-UX-025 ux-025

- GIVEN Orca and accessibility inspector are attached
- WHEN taskbar and switcher are operated
- THEN inspector and Orca observe matching name, role, selection and focus

### Requirement: ELM-UX-026

WHEN a shell control gains focus or changes selection, the Elm desktop SHALL expose that state to configured speech and braille consumers without duplicate announcements from parallel shell hosts.

#### Scenario: ELM-UX-026 ux-026

- GIVEN Orca speech and braille output are configured
- WHEN user changes switcher selection
- THEN speech and braille identify the same selected window once per transition

### Requirement: ELM-UX-027

The Elm desktop SHALL preserve readable labels and visible focus indicators in normal, high-contrast and enlarged-text theme fixtures without clipping actionable controls.

#### Scenario: ELM-UX-027 ux-027

- GIVEN supported theme and text-scale fixtures
- WHEN all shell surfaces render
- THEN labels and focus remain visible and every action retains a hit target

### Requirement: ELM-UX-028

WHEN an input method composes text in a shell field, the Elm desktop SHALL retain preedit and candidate interaction until explicit commit or cancellation.

#### Scenario: ELM-UX-028 ux-028

- GIVEN launcher search has focus with configured IME
- WHEN user composes, selects candidate and commits
- THEN one committed query appears and preedit is not dispatched as a launch

