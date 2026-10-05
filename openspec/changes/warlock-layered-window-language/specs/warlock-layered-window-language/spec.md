# Warlock layered-window language

## ADDED Requirements

### Requirement: WARLOCK-LAYER-001 — Focus and native keyboard scope

WHEN admitted native observations identify the active application and current keyboard recipient, Warlock SHALL render an opaque solid active-application contour and SHALL place its steady primary violet halo only on the confirmed keyboard recipient's eligible window or Warlock-owned shell chrome; IF that recipient is unconfirmed, it SHALL omit the primary halo and expose that uncertainty independently from operation outcomes.

Status: design-target; implementation-and-native-qualification-open.

#### Scenario: WARLOCK-LAYER-001-01 — Chooser owns typing

- **GIVEN** application A remains the native active application while an admitted chooser owns keyboard scope
- **WHEN** the chooser selects candidate B
- **THEN** A retains its Active application contour, the chooser chrome receives the primary halo, and B receives Candidate marks without implying that A or B receives typing

#### Scenario: WARLOCK-LAYER-001-02 — Unconfirmed recipient

- **GIVEN** active application facts are available but current keyboard scope is unavailable
- **WHEN** the view renders
- **THEN** the active contour is retained where qualified, the primary halo is absent, and Input target unconfirmed does not become a Committed or Unknown operation

### Requirement: WARLOCK-LAYER-002 — Candidate distinct from active

WHILE navigation has a prospective window candidate, Warlock SHALL show violet corner marks or a dashed boundary and the visible Candidate label on its navigation tile, independently from active-application, keyboard-recipient, control-focus and outcome cues, without raising or focusing a window merely to draw that decoration.

Status: design-target; implementation-and-native-qualification-open.

#### Scenario: WARLOCK-LAYER-002-01 — Cancel navigation

- **GIVEN** A is active and B is a candidate in the existing chooser
- **WHEN** navigation is cancelled through its effective binding
- **THEN** B's Candidate cue is removed and no decorative action focuses or raises B

#### Scenario: WARLOCK-LAYER-002-02 — Valid focus after candidate advances

- **GIVEN** candidate C follows B and a newer valid native observation confirms focus on B
- **WHEN** the observation is admitted against native revision and incarnation
- **THEN** B becomes observed active while C remains Candidate; validity is not inferred from whether B equals the current candidate

#### Scenario: WARLOCK-LAYER-002-03 — Retired candidate

- **GIVEN** candidate B has a fixed native incarnation
- **WHEN** B retires during navigation
- **THEN** existing eligibility rules choose or clear the candidate, stale target decorations retire, and no replacement with a reused title or address inherits B's identity

### Requirement: WARLOCK-LAYER-003 — Neutral shadow depth

WHILE eligible layered windows are presented, Warlock SHALL use bounded neutral contact and ambient shadows selected by semantic surface role and qualified committed scene geometry, independently from focus, pin state, candidate order and effect outcome; it SHALL preserve native stack order and clipping.

Status: design-target; implementation-and-native-qualification-open.

#### Scenario: WARLOCK-LAYER-003-01 — Focus does not lift

- **GIVEN** two ordinary windows have committed order and fixed geometry
- **WHEN** focus decoration changes
- **THEN** their shadow class and native order do not change solely because the halo changes

#### Scenario: WARLOCK-LAYER-003-02 — Occlusion and edges

- **GIVEN** an eligible decorated window is covered by an unrelated surface or touches a maximized output edge
- **WHEN** the qualified scene renders
- **THEN** its effects are occluded and clipped with its own scene surface; no glow leaks through the cover or creates an input region

### Requirement: WARLOCK-LAYER-004 — Owned chrome shading

WHILE layer grouping is displayed, Warlock SHALL shade opaque Warlock-owned chrome and shell backplates through the additive token tiers, and SHALL preserve client-owned pixels, readable chrome text, actual source geometry and input eligibility.

Status: design-target; implementation-and-native-qualification-open.

#### Scenario: WARLOCK-LAYER-004-01 — Editor content preserved

- **GIVEN** an inactive editor sits behind a focused dialog
- **WHEN** depth treatment is drawn
- **THEN** the editor's client pixels retain their original color and opacity except actual native occlusion; only qualified owned chrome receives shading

#### Scenario: WARLOCK-LAYER-004-02 — No owned titlebar

- **GIVEN** a client supplies all of its own chrome
- **WHEN** Warlock presents its layer relationship
- **THEN** relationship marks and labels appear on qualified shell framing or navigation tiles without recoloring the client titlebar

### Requirement: WARLOCK-LAYER-005 — Native family relation

WHEN admitted native observations establish a window family, Warlock SHALL represent that relation with segmented brackets and a Family or Context label; any optional relationship glow SHALL stay confined to short brackets at alpha no greater than 0.06, subordinate to the primary halo, and SHALL imply neither keyboard focus nor input eligibility.

Status: design-target; implementation-and-native-qualification-open.

#### Scenario: WARLOCK-LAYER-005-01 — Same process is not family

- **GIVEN** two unrelated windows share a PID and similar titles
- **WHEN** family observations are evaluated
- **THEN** no shared family markers are inferred from PID, title, icon or proximity

#### Scenario: WARLOCK-LAYER-005-02 — Family under chooser

- **GIVEN** owner and dialog belong to one admitted family while the chooser owns keyboard scope
- **WHEN** their family is shown in navigation
- **THEN** short relation brackets remain distinct from the chooser's primary halo and neither application window is falsely identified as the typing recipient

### Requirement: WARLOCK-LAYER-006 — Modal scope and independent pin state

WHILE native observations admit modality, blocking or pinning, Warlock SHALL show their specific glyphs, labels and reasons independently from glow, depth and candidate cues; modal shading SHALL affect only admitted blocked owned chrome and SHALL leave unrelated windows under their existing focus and input rules.

Status: design-target; implementation-and-native-qualification-open.

#### Scenario: WARLOCK-LAYER-006-01 — Unrelated peer remains usable

- **GIVEN** a modal blocks owner O and an unrelated peer P is present
- **WHEN** layer effects are rendered
- **THEN** O alone receives its observed blocked chrome treatment and P preserves its existing click-to-focus and input eligibility

#### Scenario: WARLOCK-LAYER-006-02 — Pinned inactive window

- **GIVEN** native facts show pinned window P while window A is active
- **WHEN** the view renders
- **THEN** P shows a neutral pin marker and Pinned label without inheriting A's active contour or changing its semantic shadow class

### Requirement: WARLOCK-LAYER-007 — Outcomes remain independent

WHILE an operation is Pending, Refused, Cancelled or Unknown, Warlock SHALL preserve its correlated target and readable outcome cue independently from focus, hover, candidate, family and depth effects; decoration SHALL neither confirm an effect nor replay an Unknown operation.

Status: design-target; implementation-and-native-qualification-open.

#### Scenario: WARLOCK-LAYER-007-01 — Pending focus request

- **GIVEN** candidate B has a Pending activation while A remains admitted active
- **WHEN** B's tile is drawn
- **THEN** B remains Candidate with Pending text and does not receive a native-confirmed primary halo

#### Scenario: WARLOCK-LAYER-007-02 — Unknown with observed focus

- **GIVEN** an operation is Unknown and a separate valid observation changes focus
- **WHEN** the observation is admitted
- **THEN** focus decorations update from the observation while the correlated Unknown outcome remains unresolved and is not automatically replayed

### Requirement: WARLOCK-LAYER-008 — Minimized and ineligible surfaces

WHEN a surface is minimized, retired, fully occluded or ineligible in the admitted scene, Warlock SHALL suppress its desktop decoration according to that native eligibility and SHALL keep its permitted taskbar or navigation representation distinct, preserving Source Live, Historical, Loading and Unavailable preview meanings.

Status: design-target; implementation-and-native-qualification-open.

#### Scenario: WARLOCK-LAYER-008-01 — Minimized Historical card

- **GIVEN** a minimized window has an authorized Historical preview
- **WHEN** the taskbar shows its card
- **THEN** the card retains Historical and Minimized cues without a phantom desktop halo or relabeling the pixels as Live

#### Scenario: WARLOCK-LAYER-008-02 — Workspace retirement

- **GIVEN** a decorated surface becomes ineligible through workspace or output change
- **WHEN** the scene generation advances
- **THEN** its desktop effects retire under the qualified scene and output generation, with no ghost glow or surviving hit region

### Requirement: WARLOCK-LAYER-009 — Contrast and non-color cues

WHEN layered-window tokens are built or rendered, Warlock SHALL verify declared small-text pairs at 4.5:1 and required non-text boundary and focus pairs at 3:1 against their actual adjacent or composited backgrounds, SHALL supply visible shape or text for each meaningful state, and SHALL provide opaque controlled backing for essential contours over arbitrary content.

Status: design-target; implementation-and-native-qualification-open.

#### Scenario: WARLOCK-LAYER-009-01 — Contrast extremes

- **GIVEN** black, white and patterned adjacent pixels occur in both themes
- **WHEN** focus and candidate contours are rendered
- **THEN** essential contours meet their declared threshold against their controlled adjacent backing; decorative halo is not counted as the sole state indicator

#### Scenario: WARLOCK-LAYER-009-02 — Grayscale navigation

- **GIVEN** color distinctions are unavailable
- **WHEN** active, candidate, family, pin, minimized, blocked and outcome states coexist
- **THEN** their different contours, glyphs and visible labels remain distinguishable; accessible names alone do not substitute for visible non-color cues

### Requirement: WARLOCK-LAYER-010 — Equivalent preference modes

WHERE high contrast, reduced transparency, reduced motion or effects-off is requested through the qualified preference route, Warlock SHALL retain equivalent focus, candidate, family, depth and outcome information using opaque boundaries, shapes, labels and permitted shading while preserving native observations, target identity, outstanding obligations and original deadlines.

Status: design-target; implementation-and-native-qualification-open.

#### Scenario: WARLOCK-LAYER-010-01 — High contrast

- **GIVEN** native preferences request high contrast
- **WHEN** the view projects layered windows
- **THEN** soft halos and shadows are disabled, opaque system-role boundaries and state distinctions remain, and effects-off does not change desktop policy

#### Scenario: WARLOCK-LAYER-010-02 — Preference during Unknown

- **GIVEN** an operation is Unknown and a theme or motion preference changes
- **WHEN** the new view is presented
- **THEN** the same target and outcome remain, no intent is replayed or confirmed, and the original operation deadline is not renewed

### Requirement: WARLOCK-LAYER-011 — Palette and brand scope

WHEN the layered-window language is applied, Warlock SHALL preserve the frozen schema-1 palette, typefaces and existing thirty design contracts, SHALL resolve additive reference-to-semantic-to-component tokens, and SHALL restrict major glow to eligible window or shell chrome and short relationship brackets; ordinary controls and small logos SHALL retain their existing crisp treatment.

Status: design-target; implementation-and-native-qualification-open.

#### Scenario: WARLOCK-LAYER-011-01 — Dark and light accents

- **GIVEN** the user switches between approved dark and light themes
- **WHEN** the layer tokens resolve
- **THEN** the approved lilac and darker light-theme violet roles are used without changing frozen reference values

#### Scenario: WARLOCK-LAYER-011-02 — User accent fails contrast

- **GIVEN** a user-supplied accent fails a declared role pair
- **WHEN** essential cues render
- **THEN** a contrast-qualified derived role or preserved default is used without silently changing the stored personal preference or losing non-color meaning

### Requirement: WARLOCK-LAYER-012 — Bounded motion and resource work

WHILE layered-window effects are displayed, Warlock SHALL keep them static at rest, SHALL schedule no recurring frame work solely for decorative glow, SHALL limit the initial recipe to two neutral shadow components and one primary halo per eligible surface with blur caps of 32 and 12 logical units respectively, and SHALL qualify their actual lifetime and costs against the original measured S02 and presentation gates before release.

Status: design-target; implementation-and-native-qualification-open.

#### Scenario: WARLOCK-LAYER-012-01 — Idle effects

- **GIVEN** window geometry and admitted layer states are stable
- **WHEN** the desktop remains idle
- **THEN** decorations create no periodic animation timers or independent clocks; ordinary client damage remains governed by the existing renderer

#### Scenario: WARLOCK-LAYER-012-02 — Rapid transitions

- **GIVEN** native focus changes again during an optional at-most-120ms decorative opacity transition
- **WHEN** the latest valid observation is admitted
- **THEN** the essential boundary updates immediately, reduced motion removes the decorative transition, and no transition extends an operation deadline

#### Scenario: WARLOCK-LAYER-012-03 — Outputs and physical retirement

- **GIVEN** decorated windows cross scales or rendering generations then retire
- **WHEN** native output and lifecycle events are exercised
- **THEN** owning renderer resources are generation-qualified and physically retired, with actual S02 and hardware evidence required rather than browser timing claims

### Requirement: WARLOCK-LAYER-013 — Omarchy interaction compatibility

WHEN layered-window navigation is exercised, Warlock SHALL preserve the effective Omarchy command vocabulary, arguments, keybindings and user override precedence, including chooser or immediate-cycle behavior as actually configured, release/repeat/submap/mouse/lock/consumption semantics, popup and IME ownership; visual cues SHALL add no speculative native effects or new shortcut meaning.

Status: design-target; implementation-and-native-qualification-open.

#### Scenario: WARLOCK-LAYER-013-01 — User AltTab chooser

- **GIVEN** the frozen user override maps Alt+Tab to the chooser
- **WHEN** navigation and Alt release are exercised
- **THEN** the effective chooser and non-consuming release behavior are retained, with no replacement by a packaged immediate-cycle assumption

#### Scenario: WARLOCK-LAYER-013-02 — Different effective map

- **GIVEN** the admitted effective configuration uses immediate cycle behavior
- **WHEN** its native binding executes
- **THEN** the actual behavior and observation-driven cues are preserved without fabricating a chooser commit or importing runtime Lua callback numbers as portable action names

### Requirement: WARLOCK-LAYER-014 — Qualification and one authority

WHEN layered-window work is integrated or reported, Warlock SHALL derive policy and view state from the one immutable Elm owner and admitted native facts, SHALL distinguish token/model/browser evidence from native focus, presented pixels, accessibility and physical retirement evidence, and SHALL preserve every original release gate and scenario identity.

Status: design-target; implementation-and-native-qualification-open.

#### Scenario: WARLOCK-LAYER-014-01 — Browser specimen

- **GIVEN** the catalog renders illustrative layer states with explicit supplied fixtures
- **WHEN** it is inspected
- **THEN** it demonstrates design only and cannot establish native focus, stack order, eligibility, rendered desktop pixels or full release acceptance

#### Scenario: WARLOCK-LAYER-014-02 — Native adoption

- **GIVEN** the new effects are integrated into a fresh owning GUI derivative
- **WHEN** release qualification runs
- **THEN** the exact core/plugin/host tuple and original preview13, restore38/recovery34, drag52, input, hardware/output, AT/IME, resource, journeys and rollback gates remain applicable

