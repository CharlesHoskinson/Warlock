# elm-layering

## ADDED Requirements

### Requirement: ELM-GNO-001

The Elm desktop SHALL record a precedence and eligibility table covering ordinary, maximized, pinned, fullscreen, transient, popup, shell and inactive-workspace surfaces before native layering acceptance.

#### Scenario: ELM-GNO-001 gnome-layering-001

- GIVEN a pinned maximized window and fullscreen peer
- WHEN the scene-policy table is reviewed
- THEN their precedence and eligibility are explicitly recorded

### Requirement: ELM-GNO-002

WHILE an application window is minimized or absent from the current output effective workspace set including explicit sticky membership, the Elm desktop SHALL exclude its live surface from ordinary paint and hit candidates regardless of convenience visibility or fullscreen-permission flags.

#### Scenario: ELM-GNO-002 gnome-layering-002

- GIVEN Heroic on inactive win-minimized with hidden=false, visible=true, acceptsInput=true and allowedOverFullscreen=true
- WHEN paint and hit candidates are enumerated
- THEN neither list contains the source window

#### Scenario: ELM-GNO-002 sticky-workspace

- GIVEN an eligible explicitly sticky window and its originating workspace
- WHEN the originating workspace becomes inactive
- THEN the supported sticky membership keeps the live surface eligible on the current output

#### Scenario: ELM-GNO-002 pin-nonsticky

- GIVEN a pinned nonsticky window on an inactive workspace
- WHEN candidate paint and hit sets are computed
- THEN pin priority does not override inactive membership and the live surface is excluded

#### Scenario: ELM-GNO-002 minimized-sticky

- GIVEN an explicitly sticky window
- WHEN the window is minimized
- THEN the live surface is excluded on every output despite sticky membership

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

#### Scenario: ELM-GNO-006 hit-normal-top

- GIVEN overlapping opaque eligible windows with no exception declared before the test
- WHEN an overlap point is clicked
- THEN the top surface receives input at the matching committed scene revision

#### Scenario: ELM-GNO-006 hit-region-hole

- GIVEN a top surface with a native input-region hole declared before the test
- WHEN the hole is clicked
- THEN native hit testing selects the eligible lower surface and records the pre-existing region exception

#### Scenario: ELM-GNO-006 hit-modal-redirect

- GIVEN a blocked parent and modal redirection policy declared before the test
- WHEN the parent is activated
- THEN native focus redirects to the eligible modal without forwarding the parent click coordinates as a modal click

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

WHEN workspace visibility changes before native effect admission, the native authority SHALL validate current dependency revisions and eligibility at the commit point and refuse any stale or ineligible request without mutation.

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

The native authority SHALL classify layer precedence from type, pin, fullscreen, family and output context only after committed eligibility filtering, without reintroducing any excluded surface.

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

#### Scenario: ELM-KDE-004 kde-live-source-exclusion

- GIVEN Heroic live surface is minimized or on an inactive special workspace
- WHEN scene candidates and its distinct historical taskbar preview are evaluated
- THEN the live source is absent from ordinary paint, hit and direct focus; the inert preview may be painted under its own identity

### Requirement: ELM-KDE-005

The native authority SHALL derive ordinary paint, hit and focus eligibility from the same committed workspace, minimize, hidden, lock and incarnation state.

#### Scenario: ELM-KDE-005 kde-005

- GIVEN a workspace switch races a click
- WHEN eligibility is evaluated
- THEN all routes consume one native revision

### Requirement: ELM-KDE-006

WHILE a preview or animation actor represents an ineligible application, the native host SHALL exclude the actor from ordinary application hit and focus targeting; any interactive shell preview control SHALL use a separate identity and validated restore intent.

#### Scenario: ELM-KDE-006 proxy-inert

- GIVEN force-visible animation pixels cover an eligible terminal
- WHEN the animation pixels are clicked
- THEN the animation actor and minimized live source receive no application input; the underlying eligible surface or distinct shell control follows its declared region

### Requirement: ELM-KDE-007

WHEN a modal focus request is accepted, the native authority SHALL resolve the current eligible modal family before selecting the committed focus recipient.

#### Scenario: ELM-KDE-007 owner-modal-activation

- GIVEN a current eligible modal child belongs to the clicked owner
- WHEN the owner is activated
- THEN focus redirects to that child under the frozen modal rule; unrelated application activation is not redirected

#### Scenario: ELM-KDE-007 unrelated-activation

- GIVEN a blocking draft belongs to a different application family
- WHEN an eligible unrelated window is clicked
- THEN that unrelated native target activates and the draft stays open

### Requirement: ELM-KDE-008

WHEN fullscreen activation or output membership changes, the native authority SHALL recompute fullscreen and pin layering from current output and family state.

#### Scenario: ELM-KDE-008 kde-008

- GIVEN fullscreen spans one output and pin exists
- WHEN focus moves to another output
- THEN documented per-output policy commits coherently

### Requirement: ELM-KDE-009

IF an intent references stale target, family, output or eligibility dependency revisions, THEN the native authority SHALL refuse it without mutation and reconcile observations; any later effect SHALL require a distinct newly validated request.

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

#### Scenario: ELM-LAY-001 heroic-fullscreen-peer

- GIVEN Heroic has hidden=false, visible=true, acceptsInput=true, allowedOverFullscreen=true on inactive special:win-minimized; active foot is fullscreen=1 on workspace1 and output specialWorkspace=0
- WHEN ordinary, fullscreen and effect passes solve scene and input
- THEN Heroic live pixels and input are excluded in every pass and the eligible terminal is drawn/targeted; the original screenshot/state evidence stays labeled non-atomic

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

#### Scenario: ELM-LAY-003 restore-overlay-handoff

- GIVEN minimized window has a live native incarnation, normal workspace identity and old inert overlay generation
- WHEN restore commits its accepted scene handoff
- THEN exactly one current live application input surface becomes eligible; old overlay generation is retired and late callbacks cannot revive it

### Requirement: ELM-REV-013

WHILE a window is maximized but unpinned and not true-fullscreen, the native authority SHALL retain it in the ordinary application band.

#### Scenario: ELM-REV-013 revision-013

- GIVEN ordinary peer and unpinned MAX overlap
- WHEN the peer is raised
- THEN the peer paints and hit-tests above MAX in the accepted native order

### Requirement: ELM-REV-014

The native host SHALL bound ordinary shell input regions to current interactive geometry and allow input-transparent regions to pass through to eligible underlying native surfaces.

#### Scenario: ELM-REV-014 revision-014

- GIVEN a full-output host contains a small taskbar
- WHEN the user clicks or begins a drag outside interactive shell bounds
- THEN the underlying native application receives the intended input

### Requirement: ELM-REV-015

The native input and render paths SHALL consume committed native scene state without synchronously awaiting Elm or webview replies.

#### Scenario: ELM-REV-015 revision-015

- GIVEN the Elm frontend is stalled
- WHEN native pointer input and frame composition occur
- THEN input routing and native frames continue from the committed scene without waiting for ports

### Requirement: ELM-REV-016

The native authority SHALL distinguish live-scene eligibility from shell enumeration, allowing minimized window entries in taskbar, switcher and Task View without granting their live surfaces paint or input authority.

#### Scenario: ELM-REV-016 revision-016

- GIVEN Heroic is minimized on its normal workspace
- WHEN taskbar, switcher and Task View enumerate windows
- THEN Heroic remains selectable but its live surface is absent from ordinary paint/hit until accepted restore

### Requirement: ELM-REV-017

WHILE a transient owner is minimized or excluded from the active scene, the native authority SHALL exclude its dependent transient descendants in the same revision until current native family policy accepts an independent or reparented state.

#### Scenario: ELM-REV-017 revision-017

- GIVEN a modal draft descends from an owner
- WHEN the owner is minimized
- THEN the family becomes live-scene-ineligible together without promoting unrelated same-application windows

### Requirement: ELM-REV-018

WHILE native session lock is active, the host SHALL withdraw ordinary shell keyboard and pointer eligibility and prevent shell priority or pin/fullscreen flags from bypassing native lock-surface authority.

#### Scenario: ELM-REV-018 revision-018

- GIVEN taskbar/pinned/application surfaces existed before lock
- WHEN lock input is delivered
- THEN only native-authorized lock/input-method routes receive it and ordinary shell/application surfaces cannot intercept credentials

### Requirement: ELM-REV-032

The P0 native-layering workstream SHALL qualify existing-compositor eligibility and MAX corrections against frozen native cases independently of Elm webview host selection, without restarting the main session during isolated QA.

#### Scenario: ELM-REV-032 revision-032

- GIVEN P0 layer policy and existing native sources are frozen
- WHEN WebKit/Qt comparison is delayed or fails
- THEN native diagnosis/qualification can proceed in isolation while Elm projection work remains separately gated

### Requirement: ELM-REV-033

The native authority SHALL redirect blocked-parent activation to an eligible modal without synthesizing a modal click, and SHALL retire an inert transition proxy atomically before publishing the restored live surface as interactive.

#### Scenario: ELM-REV-033 modal-no-click

- GIVEN a blocked parent with an eligible modal
- WHEN parent activation is requested
- THEN focus goes to the modal and no modal button receives a synthesized click

#### Scenario: ELM-REV-033 proxy-retirement

- GIVEN an inert restore proxy and a ready live surface
- WHEN restore handoff commits
- THEN proxy retires and the live surface becomes interactive at one publication boundary with no duplicate active surface

