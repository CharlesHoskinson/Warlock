# elm-accessibility

## ADDED Requirements

### Requirement: ELM-UI-009

The Elm desktop SHALL expose names, roles, states, values, relationships and supported actions for every interactive control on every migrated surface through the native accessibility bridge, with decorative pixels inert and restore controls separately identified.

#### Scenario: ELM-UI-009 at-launcher

- GIVEN the launcher surface
- WHEN native assistive technology enumerates and invokes each control
- THEN speech/braille labels, states, values and action results match the semantic oracle; missing or unnamed controls fail

#### Scenario: ELM-UI-009 at-taskbar-groups

- GIVEN the taskbar groups surface
- WHEN native assistive technology enumerates and invokes each control
- THEN speech/braille labels, states, values and action results match the semantic oracle; missing or unnamed controls fail

#### Scenario: ELM-UI-009 at-switcher

- GIVEN the switcher surface
- WHEN native assistive technology enumerates and invokes each control
- THEN speech/braille labels, states, values and action results match the semantic oracle; missing or unnamed controls fail

#### Scenario: ELM-UI-009 at-Task-View

- GIVEN the Task View surface
- WHEN native assistive technology enumerates and invokes each control
- THEN speech/braille labels, states, values and action results match the semantic oracle; missing or unnamed controls fail

#### Scenario: ELM-UI-009 at-snap-chooser

- GIVEN the snap chooser surface
- WHEN native assistive technology enumerates and invokes each control
- THEN speech/braille labels, states, values and action results match the semantic oracle; missing or unnamed controls fail

#### Scenario: ELM-UI-009 at-menus

- GIVEN the menus surface
- WHEN native assistive technology enumerates and invokes each control
- THEN speech/braille labels, states, values and action results match the semantic oracle; missing or unnamed controls fail

#### Scenario: ELM-UI-009 at-settings

- GIVEN the settings surface
- WHEN native assistive technology enumerates and invokes each control
- THEN speech/braille labels, states, values and action results match the semantic oracle; missing or unnamed controls fail

#### Scenario: ELM-UI-009 at-notifications

- GIVEN the notifications surface
- WHEN native assistive technology enumerates and invokes each control
- THEN speech/braille labels, states, values and action results match the semantic oracle; missing or unnamed controls fail

#### Scenario: ELM-UI-009 at-jump-lists

- GIVEN the jump lists surface
- WHEN native assistive technology enumerates and invokes each control
- THEN speech/braille labels, states, values and action results match the semantic oracle; missing or unnamed controls fail

### Requirement: ELM-UI-010

WHEN an action needs user attention or a notification changes, the shell SHALL publish concise identity-correlated accessible status without moving focus, deduplicate repeated receipts and apply the frozen notification announcement/interruption policy.

#### Scenario: ELM-UI-010 announce-launch refusal

- GIVEN speech and braille active with stable input focus
- WHEN launch refusal occurs
- THEN one correlated message appears with reachable detail/recovery and no focus relocation; repeated receipts do not reannounce

#### Scenario: ELM-UI-010 announce-transfer refusal

- GIVEN speech and braille active with stable input focus
- WHEN transfer refusal occurs
- THEN one correlated message appears with reachable detail/recovery and no focus relocation; repeated receipts do not reannounce

#### Scenario: ELM-UI-010 announce-settings validation failure

- GIVEN speech and braille active with stable input focus
- WHEN settings validation failure occurs
- THEN one correlated message appears with reachable detail/recovery and no focus relocation; repeated receipts do not reannounce

#### Scenario: ELM-UI-010 announce-adapter unavailable

- GIVEN speech and braille active with stable input focus
- WHEN adapter unavailable occurs
- THEN one correlated message appears with reachable detail/recovery and no focus relocation; repeated receipts do not reannounce

#### Scenario: ELM-UI-010 announce-notification arrival

- GIVEN speech and braille active with stable input focus and the frozen announcement policy permits this message
- WHEN notification arrival occurs
- THEN one correlated message appears with reachable detail/recovery and no focus relocation; repeated receipts do not reannounce

#### Scenario: ELM-UI-010 announce-notification expiration

- GIVEN speech and braille active with stable input focus and the frozen announcement policy permits this message
- WHEN notification expiration occurs
- THEN one correlated message appears with reachable detail/recovery and no focus relocation; repeated receipts do not reannounce

#### Scenario: ELM-UI-010 announce-expired action rejection

- GIVEN speech and braille active with stable input focus and the frozen announcement policy permits this message
- WHEN expired action rejection occurs
- THEN one correlated message appears with reachable detail/recovery and no focus relocation; repeated receipts do not reannounce

#### Scenario: ELM-UI-010 announcement-dnd

- GIVEN do-not-disturb active with ordinary new notification
- WHEN notification arrives
- THEN visual history updates without speech interruption or focus relocation

#### Scenario: ELM-UI-010 announcement-expiration-irrelevant

- GIVEN expired notification is neither focused nor user-invoked
- WHEN expiration is processed
- THEN expiration does not announce or move focus

#### Scenario: ELM-UI-010 announcement-urgency-opt-in

- GIVEN user explicitly opted in to this urgency class
- WHEN matching urgent notification arrives
- THEN announcement follows the opted-in interruption policy without focus theft

### Requirement: ELM-UI-011

WHEN a shell focus scope closes, the host SHALL restore its eligible identity-bound opener or the declared eligible fallback, restore surviving parent scopes for nested dismissal, reject replacement incarnations and let lock security supersede ordinary restoration.

#### Scenario: ELM-UI-011 focus-scope-nested dismissal

- GIVEN an open shell focus scope
- WHEN nested dismissal occurs
- THEN native and accessibility focus return to the eligible opener, surviving parent or MRU/desktop fallback; no dead or replacement target activates

#### Scenario: ELM-UI-011 focus-scope-opener closure

- GIVEN an open shell focus scope
- WHEN opener closure occurs
- THEN native and accessibility focus return to the eligible opener, surviving parent or MRU/desktop fallback; no dead or replacement target activates

#### Scenario: ELM-UI-011 focus-scope-workspace change

- GIVEN an open shell focus scope
- WHEN workspace change occurs
- THEN native and accessibility focus return to the eligible opener, surviving parent or MRU/desktop fallback; no dead or replacement target activates

#### Scenario: ELM-UI-011 focus-scope-opener minimize

- GIVEN an open shell focus scope
- WHEN opener minimize occurs
- THEN native and accessibility focus return to the eligible opener, surviving parent or MRU/desktop fallback; no dead or replacement target activates

#### Scenario: ELM-UI-011 focus-scope-renderer restart

- GIVEN an open shell focus scope
- WHEN renderer restart occurs
- THEN native and accessibility focus return to the eligible opener, surviving parent or MRU/desktop fallback; no dead or replacement target activates

#### Scenario: ELM-UI-011 focus-scope-address reuse

- GIVEN an open shell focus scope
- WHEN address reuse occurs
- THEN native and accessibility focus return to the eligible opener, surviving parent or MRU/desktop fallback; no dead or replacement target activates

### Requirement: ELM-UI-012

WHILE IME composition owns a field, the host SHALL respect input-method key consumption, bind callbacks to field identity and composition generation, track candidate geometry with caret/output transforms and reject late commits after focus loss, field retirement or host restart.

#### Scenario: ELM-UI-012 ime-Enter Escape arrows

- GIVEN a composing field with active candidates
- WHEN Enter Escape arrows occurs
- THEN no consumed key causes shell submit or dismissal; an explicit valid current-generation commit writes exactly once, cancellation or invalidation writes zero times, and candidate geometry matches the active caret

#### Scenario: ELM-UI-012 ime-focus transfer

- GIVEN a composing field with active candidates
- WHEN focus transfer occurs
- THEN no consumed key causes shell submit or dismissal; an explicit valid current-generation commit writes exactly once, cancellation or invalidation writes zero times, and candidate geometry matches the active caret

#### Scenario: ELM-UI-012 ime-field recreation

- GIVEN a composing field with active candidates
- WHEN field recreation occurs
- THEN no consumed key causes shell submit or dismissal; an explicit valid current-generation commit writes exactly once, cancellation or invalidation writes zero times, and candidate geometry matches the active caret

#### Scenario: ELM-UI-012 ime-output scale transfer

- GIVEN a composing field with active candidates
- WHEN output scale transfer occurs
- THEN no consumed key causes shell submit or dismissal; an explicit valid current-generation commit writes exactly once, cancellation or invalidation writes zero times, and candidate geometry matches the active caret

#### Scenario: ELM-UI-012 ime-late callback

- GIVEN a composing field with active candidates
- WHEN late callback occurs
- THEN no consumed key causes shell submit or dismissal; an explicit valid current-generation commit writes exactly once, cancellation or invalidation writes zero times, and candidate geometry matches the active caret

#### Scenario: ELM-UI-012 ime-host restart

- GIVEN a composing field with active candidates
- WHEN host restart occurs
- THEN no consumed key causes shell submit or dismissal; an explicit valid current-generation commit writes exactly once, cancellation or invalidation writes zero times, and candidate geometry matches the active caret

#### Scenario: ELM-UI-012 ime-explicit-valid-commit

- GIVEN current field identity and composition generation
- WHEN native input method explicitly commits valid composition
- THEN exactly one string commits to that field without unintended shell action

#### Scenario: ELM-UI-012 ime-invalidated-zero-commit

- GIVEN field or host generation invalidated by focus loss recreation or restart
- WHEN a late old-generation commit arrives
- THEN zero text writes and zero shell effects occur

### Requirement: ELM-UI-013

The accessibility owner SHALL freeze measurable contrast, focus visibility, effective target geometry, text enlargement and reflow thresholds before host qualification, require non-color state cues and preserve reachable controls on small outputs and long labels.

#### Scenario: ELM-UI-013 readability-high contrast

- GIVEN frozen numeric accessibility targets
- WHEN high contrast fixture executes
- THEN measured thresholds pass, state recognition has non-color cues and all focused controls remain visible and reachable

#### Scenario: ELM-UI-013 readability-largest text scale

- GIVEN frozen numeric accessibility targets
- WHEN largest text scale fixture executes
- THEN measured thresholds pass, state recognition has non-color cues and all focused controls remain visible and reachable

#### Scenario: ELM-UI-013 readability-small output

- GIVEN frozen numeric accessibility targets
- WHEN small output fixture executes
- THEN measured thresholds pass, state recognition has non-color cues and all focused controls remain visible and reachable

#### Scenario: ELM-UI-013 readability-long localized labels

- GIVEN frozen numeric accessibility targets
- WHEN long localized labels fixture executes
- THEN measured thresholds pass, state recognition has non-color cues and all focused controls remain visible and reachable

#### Scenario: ELM-UI-013 readability-color independent states

- GIVEN frozen numeric accessibility targets
- WHEN color independent states fixture executes
- THEN measured thresholds pass, state recognition has non-color cues and all focused controls remain visible and reachable

### Requirement: ELM-UX-023

The Elm desktop SHALL provide keyboard routes for launcher, taskbar groups, switcher, Task View, snap chooser, menus, settings, notifications and jump lists without requiring pointer input.

#### Scenario: ELM-UX-023 ux-023

- GIVEN pointer is unused
- WHEN keyboard-only acceptance script visits all migrated surfaces
- THEN each surface can be opened, operated and dismissed without pointer events

#### Scenario: ELM-UX-023 keyboard-launcher

- GIVEN the launcher surface and no pointer input
- WHEN the keyboard acceptance fixture opens, traverses, operates and dismisses it
- THEN each operation completes with recorded keyboard focus and no pointer events

#### Scenario: ELM-UX-023 keyboard-taskbar-groups

- GIVEN the taskbar groups surface and no pointer input
- WHEN the keyboard acceptance fixture opens, traverses, operates and dismisses it
- THEN each operation completes with recorded keyboard focus and no pointer events

#### Scenario: ELM-UX-023 keyboard-switcher

- GIVEN the switcher surface and no pointer input
- WHEN the keyboard acceptance fixture opens, traverses, operates and dismisses it
- THEN each operation completes with recorded keyboard focus and no pointer events

#### Scenario: ELM-UX-023 keyboard-task-view

- GIVEN the Task View surface and no pointer input
- WHEN the keyboard acceptance fixture opens, traverses, operates and dismisses it
- THEN each operation completes with recorded keyboard focus and no pointer events

#### Scenario: ELM-UX-023 keyboard-snap-chooser

- GIVEN the snap chooser surface and no pointer input
- WHEN the keyboard acceptance fixture opens, traverses, operates and dismisses it
- THEN each operation completes with recorded keyboard focus and no pointer events

#### Scenario: ELM-UX-023 keyboard-menus

- GIVEN the menus surface and no pointer input
- WHEN the keyboard acceptance fixture opens, traverses, operates and dismisses it
- THEN each operation completes with recorded keyboard focus and no pointer events

#### Scenario: ELM-UX-023 keyboard-settings

- GIVEN the settings surface and no pointer input
- WHEN the keyboard acceptance fixture opens, traverses, operates and dismisses it
- THEN each operation completes with recorded keyboard focus and no pointer events

#### Scenario: ELM-UX-023 keyboard-notifications

- GIVEN the notifications surface and no pointer input
- WHEN the keyboard acceptance fixture opens, traverses, operates and dismisses it
- THEN each operation completes with recorded keyboard focus and no pointer events

#### Scenario: ELM-UX-023 keyboard-jump-lists

- GIVEN the jump lists surface and no pointer input
- WHEN the keyboard acceptance fixture opens, traverses, operates and dismisses it
- THEN each operation completes with recorded keyboard focus and no pointer events

### Requirement: ELM-UX-024

WHILE a shell popup owns keyboard focus, the Elm desktop SHALL constrain traversal to its documented focus order and restore the previous eligible focus target on dismissal.

#### Scenario: ELM-UX-024 ux-024

- GIVEN taskbar menu has focus
- WHEN Tab traversal then Escape occurs
- THEN focus follows menu order and returns to original eligible target

### Requirement: ELM-UX-025

The Elm desktop SHALL expose names, roles, states and focus changes for taskbar and switcher controls through the chosen host’s native accessibility bridge.

#### Scenario: ELM-UX-025 actual-surface-at

- GIVEN the full taskbar and switcher exist on the selected host
- WHEN AT inspection and navigation run
- THEN both actual surfaces expose matching name, role, selection and focus

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

#### Scenario: ELM-UX-028 ime-spike-commit

- GIVEN a minimal shell text field on the candidate native host has IME focus
- WHEN preedit and candidate selection commit
- THEN one text string appears with correct caret and no application launch is caused

#### Scenario: ELM-UX-028 ime-spike-cancel

- GIVEN the minimal candidate-host field holds preedit
- WHEN composition is cancelled
- THEN preedit clears without committed text or unintended effect

