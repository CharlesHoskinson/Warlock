# elm-window-policy

## ADDED Requirements

### Requirement: ELM-REN-015

The native window authority SHALL make painted ordering, hit testing and committed focus agree for overlapping floating maximized windows.

#### Scenario: ELM-REN-015 ren-015

- GIVEN MAX and floating windows overlap
- WHEN the visible top window is clicked
- THEN that eligible top window receives focus

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

