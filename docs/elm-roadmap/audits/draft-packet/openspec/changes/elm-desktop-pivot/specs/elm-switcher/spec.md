# elm-switcher

## ADDED Requirements

### Requirement: ELM-UX-011

WHEN native Alt-Tab chord events arrive, the Elm desktop SHALL advance selection in the frozen eligible-window order for that chord generation.

#### Scenario: ELM-UX-011 ux-011

- GIVEN three eligible windows
- WHEN Alt-Tab then Shift-Alt-Tab occur
- THEN selection advances then returns within the same frozen order

### Requirement: ELM-UX-012

WHEN Alt release precedes switcher readiness, the Elm desktop SHALL resolve the native chord once without leaving an open switcher or issuing a second activation.

#### Scenario: ELM-UX-012 ux-012

- GIVEN host is starting
- WHEN Alt press, Tab and release precede readiness
- THEN one resolution occurs and no switcher remains open

### Requirement: ELM-UX-013

WHEN Escape cancels a switcher chord before native commit, the Elm desktop SHALL close the switcher and preserve the previously focused window.

#### Scenario: ELM-UX-013 ux-013

- GIVEN switcher selection differs from focused window
- WHEN Escape arrives before commit
- THEN switcher closes and focus is unchanged

### Requirement: ELM-UX-014

IF the selected switcher window closes or its identity becomes stale, THEN the Elm desktop SHALL reselect a surviving eligible member or dismiss an empty chord without activating a replacement incarnation.

#### Scenario: ELM-UX-014 ux-014

- GIVEN selected window closes and address is reused
- WHEN release attempts selection commit
- THEN reused address is never activated as the closed window

