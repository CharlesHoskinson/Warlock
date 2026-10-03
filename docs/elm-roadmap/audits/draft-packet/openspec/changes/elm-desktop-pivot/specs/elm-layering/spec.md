# elm-layering

## ADDED Requirements

### Requirement: ELM-GNO-001

The Elm desktop SHALL record a precedence and eligibility table covering ordinary, maximized, pinned, fullscreen, transient, popup, shell and inactive-workspace surfaces before native layering acceptance.

#### Scenario: ELM-GNO-001 gnome-layering-001

- GIVEN a pinned maximized window and fullscreen peer
- WHEN the scene-policy table is reviewed
- THEN their precedence and eligibility are explicitly recorded

### Requirement: ELM-GNO-002

WHILE an application window is minimized or belongs to an inactive workspace on an output, the Elm desktop SHALL exclude that source window from ordinary paint and hit candidates on that output regardless of convenience visibility or fullscreen-permission flags.

#### Scenario: ELM-GNO-002 gnome-layering-002

- GIVEN Heroic on inactive win-minimized with hidden=false, visible=true, acceptsInput=true and allowedOverFullscreen=true
- WHEN paint and hit candidates are enumerated
- THEN neither list contains the source window

### Requirement: ELM-GNO-003

The Elm desktop SHALL determine native scene eligibility before applying layer or fullscreen precedence.

#### Scenario: ELM-GNO-003 gnome-layering-003

- GIVEN an ineligible window permitted above fullscreen
- WHEN a fullscreen scene is solved
- THEN the permission does not restore the excluded window

### Requirement: ELM-GNO-004

The Elm desktop SHALL preserve eligible child-above-owner constraints across native layer changes without promoting unrelated ordinary members of the application group.

#### Scenario: ELM-GNO-004 gnome-layering-004

- GIVEN an owner, child dialog and unrelated group peer
- WHEN the owner becomes pinned
- THEN the child remains above its owner without promoting the peer

### Requirement: ELM-GNO-005

IF native family constraints are cyclic or inconsistent, THEN the Elm desktop SHALL refuse the affected scene transaction without publishing a partially solved paint or hit order.

#### Scenario: ELM-GNO-005 gnome-layering-005

- GIVEN a cyclic transient fixture
- WHEN the solver attempts a scene commit
- THEN no partial scene is published and the refusal is recorded

### Requirement: ELM-GNO-006

The Elm desktop SHALL derive ordinary native paint order and pointer hit order from the same committed scene revision, with explicit native input-region and modal-redirection exceptions.

#### Scenario: ELM-GNO-006 gnome-layering-006

- GIVEN overlapping eligible opaque windows
- WHEN a visible overlap point is clicked
- THEN the visible top eligible surface receives input unless a recorded native exception applies

### Requirement: ELM-GNO-007

WHEN a pinned window is maximized or restored, the Elm desktop SHALL preserve its pin policy and eligible transient-family precedence until an acknowledged unpin operation changes that policy.

#### Scenario: ELM-GNO-007 gnome-layering-007

- GIVEN a pinned owner with an eligible dialog
- WHEN the owner maximizes then restores
- THEN pin state persists and its dialog remains above it

### Requirement: ELM-GNO-008

WHILE a minimized or inactive application retains an animation or preview resource, the Elm desktop SHALL expose that resource only as a noninteractive visual object and retire it through native lifetime authority.

#### Scenario: ELM-GNO-008 gnome-layering-008

- GIVEN a minimized window with a retained frame
- WHEN the frame is displayed then retired
- THEN the source receives no input and native retirement is evidenced

### Requirement: ELM-GNO-009

WHEN workspace visibility changes between intent validation and native effect commit, the Elm desktop SHALL revalidate the target scene eligibility before committing focus or pointer-target effects.

#### Scenario: ELM-GNO-009 gnome-layering-009

- GIVEN an eligible target and prepared focus intent
- WHEN its special workspace closes before commit
- THEN the stale target receives no effect and reconciliation is recorded

### Requirement: ELM-KDE-001

The native authority SHALL publish one committed constrained stack revision for ordinary scene ordering, hit testing and focus resolution.

#### Scenario: ELM-KDE-001 kde-001

- GIVEN an overlapping MAX and float
- WHEN a raise commits
- THEN ordinary paint, hit and focus use the same stack revision

### Requirement: ELM-KDE-002

The native authority SHALL derive layer eligibility from window type, pin state, fullscreen state, family constraints and current output context.

#### Scenario: ELM-KDE-002 kde-002

- GIVEN MAX, fullscreen and pin combinations
- WHEN layer policy is computed
- THEN explicit policy rather than a blanket allowed-over flag selects order

### Requirement: ELM-KDE-003

WHEN a transient family changes, the native authority SHALL recompute parent-child constraints and preserve documented sibling order before committing the stack.

#### Scenario: ELM-KDE-003 kde-003

- GIVEN a parent with two transients
- WHEN one family relation changes
- THEN constraints update without stale parent or arbitrary sibling inversion

### Requirement: ELM-KDE-004

IF a window belongs to an inactive special workspace, THEN the native eligibility SHALL exclude its ordinary live painting, pointer targeting and direct focus despite permissive cached visibility or input flags.

#### Scenario: ELM-KDE-004 kde-004

- GIVEN Heroic resides on inactive special:win-minimized with permissive flags
- WHEN ordinary painting, clicking or direct focus is evaluated
- THEN the hidden window cannot appear or receive focus

### Requirement: ELM-KDE-005

The native authority SHALL derive ordinary paint, hit and focus eligibility from the same committed workspace, minimize, hidden, lock and incarnation state.

#### Scenario: ELM-KDE-005 kde-005

- GIVEN a workspace switch races a click
- WHEN eligibility is evaluated
- THEN all routes consume one native revision

### Requirement: ELM-KDE-006

WHILE an effect paints a hidden or minimized window representation, IF that representation lacks explicit input authority, THEN the native host SHALL keep it outside ordinary hit and focus eligibility.

#### Scenario: ELM-KDE-006 kde-006

- GIVEN a minimized window is painted for motion
- WHEN the user clicks its animation pixels
- THEN input follows explicit proxy policy rather than live-window visibility

### Requirement: ELM-KDE-007

WHEN a modal focus request is accepted, the native authority SHALL resolve the current eligible modal family before selecting the committed focus recipient.

#### Scenario: ELM-KDE-007 kde-007

- GIVEN a modal family and unrelated eligible window overlap
- WHEN a click or focus request arrives
- THEN the current native family policy selects the eligible recipient

### Requirement: ELM-KDE-008

WHEN fullscreen activation or output membership changes, the native authority SHALL recompute fullscreen and pin layering from current output and family state.

#### Scenario: ELM-KDE-008 kde-008

- GIVEN fullscreen spans one output and pin exists
- WHEN focus moves to another output
- THEN documented per-output policy commits coherently

### Requirement: ELM-KDE-009

IF an Elm intent references a stale stack or eligibility revision, THEN the native authority SHALL refuse or reconcile it before committing focus or layering effects.

#### Scenario: ELM-KDE-009 kde-009

- GIVEN an intent captured old workspace truth
- WHEN a newer workspace revision commits
- THEN the stale intent cannot override current eligibility

### Requirement: ELM-LAY-001

IF a window is minimized or belongs to an inactive nonsticky workspace, THEN the native authority SHALL exclude its live surface from display and application input regardless of prior raise or fullscreen permissions.

#### Scenario: ELM-LAY-001 layer-001

- GIVEN Heroic is minimized while a terminal is active
- WHEN an old raised/maximized surface is considered for scene publication
- THEN Heroic receives neither live drawing nor application input; an independently owned inert preview may remain

### Requirement: ELM-LAY-002

WHEN a scene revision is committed, the native authority SHALL derive painting, hit testing and focus eligibility from the same accepted surface identities and ordered scene revision.

#### Scenario: ELM-LAY-002 layer-002

- GIVEN overlapping application windows with an accepted stack revision
- WHEN painting and pointer routing execute
- THEN the top eligible painted application receives the corresponding hit and focus, subject to explicit input regions and modal constraints

### Requirement: ELM-LAY-003

WHEN a minimized window is restored, the native authority SHALL make it eligible in one accepted scene transition while preserving its normal workspace identity and rejecting old transition generations.

#### Scenario: ELM-LAY-003 layer-003

- GIVEN a minimized window with retained preview and original workspace identity
- WHEN restore completes through a current generation
- THEN one current live surface becomes eligible and no stale overlay remains

