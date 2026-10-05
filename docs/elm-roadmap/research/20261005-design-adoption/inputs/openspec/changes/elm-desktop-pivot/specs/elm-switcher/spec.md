# elm-switcher

## ADDED Requirements

### Requirement: ELM-UI-003

The product owner SHALL freeze the INTERACTION.md switcher scope, committed-MRU order, modal-family representation, initial forward/reverse selection, wraparound, zero/one-entry behavior and candidate-retirement fallback before P3 qualification.

#### Scenario: ELM-UI-003 switcher-order

- GIVEN known committed history A then B then C with C focused
- WHEN forward and reverse cycles traverse the frozen candidates
- THEN first forward chooses B, forward sequence B A C wraps and reverse starts A; family entries are unique

#### Scenario: ELM-UI-003 switcher-cancel

- GIVEN known committed history A then B then C with C focused
- WHEN a chord is cancelled
- THEN C focus and committed MRU remain unchanged

#### Scenario: ELM-UI-003 switcher-membership

- GIVEN known committed history A then B then C with C focused
- WHEN a modal family, minimized peer and other-workspace peer are enumerated
- THEN all ordinary user-session workspace candidates are represented once per family and lock/protected exclusions hold

#### Scenario: ELM-UI-003 switcher-zero-one

- GIVEN known committed history A then B then C with C focused
- WHEN zero or one candidate is enumerated
- THEN zero is a no-op; one keeps or activates the sole eligible family without accidental minimization

#### Scenario: ELM-UI-003 switcher-retire-arrive

- GIVEN known committed history A then B then C with C focused
- WHEN selected candidate dies and a new one arrives during chord
- THEN dead identity retires, next surviving entry is selected, and the new arrival waits for the next chord

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

