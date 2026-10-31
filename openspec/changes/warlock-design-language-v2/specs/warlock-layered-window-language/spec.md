## MODIFIED Requirements

### Requirement: WARLOCK-LAYER-001 — Focus and native keyboard scope

When admitted native observations identify the active application and current keyboard recipient, Warlock SHALL render a backed brand active-application contour and place sharp focus-colored chevrons or an explicit recipient label on the confirmed recipient's eligible window or owned shell chrome; an optional steady halo SHALL accompany the sharp mark only. If the recipient is unconfirmed, Warlock SHALL omit recipient marks and expose that uncertainty independently from operation outcomes.

Guardrail: Original release contracts, deadlines, evidence, authority and native qualification remain mandatory.

#### Scenario: WARLOCK-LAYER-001-01 — Chooser owns typing

- **GIVEN** application A remains the native active application while an admitted chooser owns keyboard scope
- **WHEN** the chooser selects candidate B
- **THEN** A retains its Active application contour, the chooser chrome receives the sharp recipient mark, and B receives Candidate marks without implying that A or B receives typing

#### Scenario: WARLOCK-LAYER-001-02 — Unconfirmed recipient

- **GIVEN** active application facts are available but current keyboard scope is unavailable
- **WHEN** the view renders
- **THEN** the active contour is retained where qualified, the sharp recipient mark is absent, and Input target unconfirmed does not become a Committed or Unknown operation

### Requirement: WARLOCK-LAYER-002 — Candidate distinct from active

While navigation has a prospective window candidate, Warlock SHALL show four neutral 12px corner brackets, selected wash and the visible Candidate label on its navigation tile, independently from active-application, keyboard-recipient, control-focus and outcome cues, without raising or focusing a window merely to draw decoration.

Guardrail: Original release contracts, deadlines, evidence, authority and native qualification remain mandatory.

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

While eligible layered windows are presented, Warlock SHALL use bounded neutral contact and ambient shadows selected by semantic elevation and qualified committed scene geometry, independently from focus, pin state, candidate order and effect outcome; it SHALL preserve native stack order and clipping. Focus may change floating shadow opacity but never elevation class.

Guardrail: Original release contracts, deadlines, evidence, authority and native qualification remain mandatory.

#### Scenario: WARLOCK-LAYER-003-01 — Focus does not lift

- **GIVEN** two ordinary windows have committed order and fixed geometry
- **WHEN** focus decoration changes
- **THEN** their shadow class and native order do not change solely because the focus cue changes

#### Scenario: WARLOCK-LAYER-003-02 — Occlusion and edges

- **GIVEN** an eligible decorated window is covered by an unrelated surface or touches a maximized output edge
- **WHEN** the qualified scene renders
- **THEN** its effects are occluded and clipped with its own scene surface; no glow leaks through the cover or creates an input region

### Requirement: WARLOCK-LAYER-005 — Native family relation

When admitted native observations establish a window family, Warlock SHALL represent that relation with short neutral segmented brackets and a Family or Context label; optional neutral softness SHALL stay confined to short brackets at alpha no greater than 0.06, subordinate to the confirmed recipient cue, and SHALL imply neither keyboard focus nor input eligibility.

Guardrail: Original release contracts, deadlines, evidence, authority and native qualification remain mandatory.

#### Scenario: WARLOCK-LAYER-005-01 — Same process is not family

- **GIVEN** two unrelated windows share a PID and similar titles
- **WHEN** family observations are evaluated
- **THEN** no shared family markers are inferred from PID, title, icon or proximity

#### Scenario: WARLOCK-LAYER-005-02 — Family under chooser

- **GIVEN** owner and dialog belong to one admitted family while the chooser owns keyboard scope
- **WHEN** their family is shown in navigation
- **THEN** short relation brackets remain distinct from the chooser's sharp recipient mark and neither application window is falsely identified as the typing recipient

### Requirement: WARLOCK-LAYER-006 — Modal scope and independent pin state

While native observations admit modality, blocking or pinning, Warlock SHALL show specific glyphs, labels and reasons independently from glow, depth and candidate cues; it SHALL not dim client content or surrounding windows and SHALL leave unrelated windows under their existing focus and input rules.

Guardrail: Original release contracts, deadlines, evidence, authority and native qualification remain mandatory.

#### Scenario: WARLOCK-LAYER-006-01 — Unrelated peer remains usable

- **GIVEN** a modal blocks owner O and an unrelated peer P is present
- **WHEN** layer effects are rendered
- **THEN** O shows its observed blocked glyph, label and reason without dimming and P preserves its existing click-to-focus and input eligibility

#### Scenario: WARLOCK-LAYER-006-02 — Pinned inactive window

- **GIVEN** native facts show pinned window P while window A is active
- **WHEN** the view renders
- **THEN** P shows a neutral pin marker and Pinned label without inheriting A's active contour or changing its semantic shadow class

### Requirement: WARLOCK-LAYER-007 — Outcomes remain independent

While an operation is Pending, Refused, Cancelled or Unknown, Warlock SHALL preserve its correlated target and readable typed outcome cue independently from focus, hover, candidate, family and depth effects; decoration SHALL neither confirm an effect nor replay an Unknown operation.

Guardrail: Original release contracts, deadlines, evidence, authority and native qualification remain mandatory.

#### Scenario: WARLOCK-LAYER-007-01 — Pending focus request

- **GIVEN** candidate B has a Pending activation while A remains admitted active
- **WHEN** B's tile is drawn
- **THEN** B remains Candidate with Pending text and does not receive a native-confirmed sharp recipient mark

#### Scenario: WARLOCK-LAYER-007-02 — Unknown with observed focus

- **GIVEN** an operation is Unknown and a separate valid observation changes focus
- **WHEN** the observation is admitted
- **THEN** focus decorations update from the observation while the correlated Unknown outcome remains unresolved and is not automatically replayed

### Requirement: WARLOCK-LAYER-009 — Contrast and non-color cues

When layered-window tokens are built or rendered, Warlock SHALL verify all text including disabled text at 4.5:1 and required non-text boundary and focus pairs at 3:1 against their actual adjacent or composited backgrounds in Night, Dawn and High contrast, measure protanopia and deuteranopia, supply visible shape or text for meaningful states, and provide opaque controlled backing for essential contours over arbitrary content.

Guardrail: Original release contracts, deadlines, evidence, authority and native qualification remain mandatory.

#### Scenario: WARLOCK-LAYER-009-01 — Contrast extremes

- **GIVEN** black, white and patterned adjacent pixels occur in all three appearances
- **WHEN** focus and candidate contours are rendered
- **THEN** essential contours meet their declared threshold against their controlled adjacent backing; decorative halo is not counted as the sole state indicator

#### Scenario: WARLOCK-LAYER-009-02 — Grayscale navigation

- **GIVEN** color distinctions are unavailable
- **WHEN** active, candidate, family, pin, minimized, blocked and outcome states coexist
- **THEN** their different contours, glyphs and visible labels remain distinguishable; accessible names alone do not substitute for visible non-color cues

### Requirement: WARLOCK-LAYER-010 — Equivalent preference modes

Where high contrast, forced colors, reduced transparency, reduced motion or effects-off is requested through the qualified preference route, Warlock SHALL retain equivalent focus, candidate, family, depth and outcome information using opaque boundaries, shapes and labels while preserving native observations, target identity, outstanding obligations and original deadlines; reduced motion SHALL suppress portal motion and effects-off SHALL remove soft effects.

Guardrail: Original release contracts, deadlines, evidence, authority and native qualification remain mandatory.

#### Scenario: WARLOCK-LAYER-010-01 — High contrast

- **GIVEN** native preferences request high contrast
- **WHEN** the view projects layered windows
- **THEN** soft halos and shadows are disabled, opaque system-role boundaries and state distinctions remain, and effects-off does not change desktop policy

#### Scenario: WARLOCK-LAYER-010-02 — Preference during Unknown

- **GIVEN** an operation is Unknown and a theme or motion preference changes
- **WHEN** the new view is presented
- **THEN** the same target and outcome remain, no intent is replayed or confirmed, and the original operation deadline is not renewed

### Requirement: WARLOCK-LAYER-011 — Palette and brand scope

When the layered-window language is applied, Warlock SHALL use the Lacquer Night, Dawn and High contrast palette, preserve typefaces and applicable design contracts, resolve reference-to-semantic-to-component tokens, and restrict glow to the confirmed recipient, short neutral family brackets and the temporary portal; ordinary controls and small logos SHALL remain crisp.

Guardrail: Original release contracts, deadlines, evidence, authority and native qualification remain mandatory.

#### Scenario: WARLOCK-LAYER-011-01 — Dark and light accents

- **GIVEN** the user switches between approved dark and light themes
- **WHEN** the layer tokens resolve
- **THEN** the approved Lacquer theme roles and distinct neutral focus and brand activity cues are used

#### Scenario: WARLOCK-LAYER-011-02 — User accent fails contrast

- **GIVEN** a user-supplied accent fails a declared role pair
- **WHEN** essential cues render
- **THEN** a contrast-qualified derived role or preserved default is used without silently changing the stored personal preference or losing non-color meaning

### Requirement: WARLOCK-LAYER-012 — Bounded motion and resource work

While layered-window effects are displayed, Warlock SHALL keep idle chrome static, schedule no recurring decorative frame work, limit elevation to two neutral shadows and recipient halo blur to 12 logical units, bound portal effects and qualify actual lifetime and costs against the original S02 and presentation gates before release.

Guardrail: Original release contracts, deadlines, evidence, authority and native qualification remain mandatory.

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
