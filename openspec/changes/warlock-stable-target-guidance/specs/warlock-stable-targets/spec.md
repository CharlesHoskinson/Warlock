# Warlock stable targets

## ADDED Requirements

### Requirement: Stable picker target geometry

The picker SHALL reserve the same thumbnail slot and bounded status/detail geometry across Loading, Live, Historical and Unavailable. Asynchronous content SHALL NOT move a pressed target before release. Admission SHALL retain the press-time identity/publication/lease guard.

#### Scenario: Preview arrives during context press

- **GIVEN** a Loading picker row under an admitted right-button press
- **WHEN** that row receives an authorized Live frame before release
- **THEN** its target bounds remain stable and release is evaluated against the original target and current admission guards
- **AND** no neighboring family becomes the action target

#### Scenario: Target retires before release

- **GIVEN** a picker row under an admitted press
- **WHEN** its identity retires or its publication/lease no longer admits the gesture
- **THEN** release is refused without a window mutation or replacement-target activation

#### Scenario: Preview freshness changes

- **GIVEN** a visible picker with an authorized preview state
- **WHEN** the source becomes Historical, Unavailable or Loading
- **THEN** reserved layout geometry remains unchanged and the source state is labeled accurately
- **AND** another incarnation's pixels are never substituted

### Requirement: Observed Always on top toggle

The window menu SHALL use the stable label Always on top and expose checked state only from the current correlated native observation. Taskbar Pin/Unpin vocabulary SHALL remain specific to application persistence. Interaction outcome SHALL remain separate from confirmed pin state.

#### Scenario: Native pin observation confirms

- **GIVEN** an eligible maximized family with an admitted Always on top request
- **WHEN** the matching current native observation confirms pin state
- **THEN** the control's checked state and displayed pin/MAX status reflect that observation
- **AND** native geometry and visible input targets retain their original UX-016 obligations

#### Scenario: Pending or Unknown outcome

- **GIVEN** an unresolved Always on top request
- **WHEN** its outcome remains Pending or becomes Unknown
- **THEN** the shell keeps the last confirmed checked state and displays the unresolved outcome separately
- **AND** it does not replay the mutation automatically or infer success from menu dismissal

#### Scenario: Stale observation or refusal

- **GIVEN** a menu bound to a current window incarnation
- **WHEN** a stale pin observation arrives or native authority refuses the request
- **THEN** stale state cannot change the toggle and the refusal is reported without mutation or optimistic confirmation
