# elm-window-policy

## ADDED Requirements

### Requirement: ELM-REN-015

The native window authority SHALL derive MAX overlap painting and hit traversal from one committed constrained scene, applying explicit input-region and transform rules and committing the documented modal recipient after a qualifying activation.

#### Scenario: ELM-REN-015 ren-015

- GIVEN MAX and floating windows overlap
- WHEN the visible top window is clicked
- THEN that eligible top window receives focus

#### Scenario: ELM-REN-015 max-input-region

- GIVEN two overlapping MAX surfaces with the upper input region excluding the point
- WHEN the excluded point is clicked
- THEN paint retains the upper pixels, native hit chooses the eligible lower input surface, and the scene revision agrees

#### Scenario: ELM-REN-015 max-modal-focus

- GIVEN the clicked eligible MAX owner has a mapped blocking modal
- WHEN the owner is activated
- THEN native authority focuses the accepted modal recipient without corrupting constrained paint order

#### Scenario: ELM-REN-015 max-focus-not-top

- GIVEN the current focus remains on another window and no activation occurs
- WHEN a new eligible surface is merely painted
- THEN painting alone does not force focus to equal the top painted surface

### Requirement: ELM-REN-016

WHEN pin state changes, the native authority SHALL preserve documented MAX return geometry and evaluate painted and input order under the new pin state.

#### Scenario: ELM-REN-016 ren-016

- GIVEN a maximized floating window
- WHEN pin then unpin is committed
- THEN return geometry and painted/hit order match the policy

### Requirement: ELM-REN-017

WHILE true fullscreen is active, the native authority SHALL apply an explicit fullscreen and pinned-surface policy without treating fullscreen as floating MAX.

#### Scenario: ELM-REN-017 ren-017

- GIVEN true fullscreen and a pinned window coexist
- WHEN a menu or focus action occurs
- THEN the documented fullscreen policy governs each surface

### Requirement: ELM-REN-018

WHEN focusing a modal family, the native authority SHALL resolve eligible recipients from current native family and input state before committing focus.

#### Scenario: ELM-REN-018 ren-018

- GIVEN a draft modal and overlapping unrelated window exist
- WHEN the user clicks the unrelated eligible window
- THEN native policy focuses the intended eligible recipient without closing drafts

### Requirement: ELM-REN-020

WHEN a window transfers between outputs, the canonical authority SHALL commit placement, snap membership and frame ownership using current output generations.

#### Scenario: ELM-REN-020 ren-020

- GIVEN a transfer is pending
- WHEN the target output disappears
- THEN the stale target is refused and ownership reconciles

### Requirement: ELM-REV-031

The native focus policy SHALL distinguish genuine input blockers from allows_input=false and SHALL refuse no-focus only when an independently verified native blocking predicate applies.

#### Scenario: ELM-REV-031 revision-031

- GIVEN allows_input=false has no separate native blocker
- WHEN focus eligibility is tested
- THEN that flag alone does not establish no-focus; a real blocker independently prevents the effect

### Requirement: ELM-UI-001

WHEN the focused family minimizes, the native authority SHALL focus the most recently committed eligible successor or the desktop no-application-focus state in the same scene revision, and SHALL preserve current focus when an unfocused family minimizes.

#### Scenario: ELM-UI-001 focus-successor

- GIVEN focused A, eligible B and C with B most recently active
- WHEN the selected family minimizes
- THEN B receives focus and A receives no keyboard input

#### Scenario: ELM-UI-001 focus-last

- GIVEN one active family
- WHEN the selected family minimizes
- THEN no minimized surface retains focus and the desktop focus state is observed

#### Scenario: ELM-UI-001 focus-unfocused

- GIVEN B focused and A unfocused
- WHEN the selected family minimizes
- THEN B retains focus

