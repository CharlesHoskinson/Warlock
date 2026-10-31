## MODIFIED Requirements

### Requirement: WARLOCK-DL-001 — Preserve Warlock identity and philosophical priorities

The design language SHALL preserve the approved Warlock name, flow sigil, tagline and bundled typefaces, apply the Warlock philosophy when resolving conflicts, and use the Lacquer reference palette and semantic roles for Night, Dawn and High contrast; the retired schema-1 palette SHALL remain preserved in its versioned baseline and frozen evidence.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

#### Scenario: WARLOCK-DL-001-01

- **GIVEN** the identity and Lacquer token source
- **WHEN** the design is built
- **THEN** the approved mark, typefaces and theme values match their declared sources

#### Scenario: WARLOCK-DL-001-02

- **GIVEN** brand decoration is displayed
- **WHEN** a request is submitted
- **THEN** decoration does not encode confirmation or grant native authority

### Requirement: WARLOCK-DL-002 — Three token tiers and explicit role pairs

When a control renders, its styles SHALL resolve through component tokens and semantic role tokens backed by Lacquer reference primitives, with explicit measured foreground and background pairs.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

#### Scenario: WARLOCK-DL-002-01

- **GIVEN** the token source
- **WHEN** the catalog builds
- **THEN** reference, semantic and component mappings are published

#### Scenario: WARLOCK-DL-002-02

- **GIVEN** an actionable component needs a color
- **WHEN** its style resolves
- **THEN** the component uses an approved role pair rather than an unreviewed literal; artwork may use reference colors

### Requirement: WARLOCK-DL-003 — Measured contrast and non-color state cues

When tokens are built, the build SHALL verify all declared text pairs including disabled labels and placeholders at 4.5:1, and essential boundaries and focus at 3:1, against actual adjacent or composited backgrounds in Night, Dawn and High contrast; meaningful states SHALL have text or shape cues.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

#### Scenario: WARLOCK-DL-003-01

- **GIVEN** a state has an overlay or controlled backing
- **WHEN** its pair is tested
- **THEN** the actual composited adjacent colors meet the declared threshold

#### Scenario: WARLOCK-DL-003-02

- **GIVEN** a disabled control or decorative element is rendered
- **WHEN** the matrix is inspected
- **THEN** the disabled reason stays readable and decorative or inactive elements are explicitly classified

### Requirement: WARLOCK-DL-004 — Independent interaction and outcome axes

While an outcome is Pending or Unknown, the surface SHALL expose it independently from hover, focus, pressed, selection, current and unavailable states, preserve targeted intent identity, and use the typed outcome grammar without deriving a result from color or free-form text.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

#### Scenario: WARLOCK-DL-004-01

- **GIVEN** a Pending or Unknown control is focused or its surface policy moves focus
- **WHEN** the outcome renders
- **THEN** both the outcome and eligible focus or fallback remain perceivable

#### Scenario: WARLOCK-DL-004-02

- **GIVEN** an operation has an Unknown outcome
- **WHEN** activation is repeated
- **THEN** Unknown is not presented as Committed and no second intent is created for its blocked target

### Requirement: WARLOCK-DL-006 — Visible focus with theme and contrast support

When keyboard focus is visible, the surface SHALL show a focus-color outer indicator at least 2 CSS pixels wide with a 2px offset and opaque 2px gap, distinguish it from hover and selection, meet 3:1 against adjacent colors, and retain an equivalent system-color outline in forced colors.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

#### Scenario: WARLOCK-DL-006-01

- **GIVEN** a focused control appears on a selected or filled surface
- **WHEN** the focus indicator renders
- **THEN** the focus-colored outline and opaque gap remain visible without replacing selection

#### Scenario: WARLOCK-DL-006-02

- **GIVEN** Night, Dawn, High contrast or forced colors is active with enlarged text
- **WHEN** the focus matrix renders
- **THEN** the indicator remains visible and meets its declared contrast; native treatment is separately qualified

### Requirement: WARLOCK-DL-015 — Reduced motion and native presentation continuity

While reduced motion is active, Warlock SHALL set motion durations to 0ms, suppress the decorative portal and velocity-continuation motion, retain static depth and sharp state cues, and preserve native last-presented geometry and presentation continuity.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

#### Scenario: WARLOCK-DL-015-01

- **GIVEN** reduced motion is admitted during a window effect
- **WHEN** the preference is applied
- **THEN** the effect settles immediately and essential state and geometry remain available

#### Scenario: WARLOCK-DL-015-02

- **GIVEN** native geometry changes with reduced motion active
- **WHEN** the view updates
- **THEN** the presentation uses admitted geometry without decorative travel or renewed operation deadlines

### Requirement: WARLOCK-DL-020 — Launcher search as a guarded extension

While launcher search is active, Warlock SHALL filter and rank admitted catalog entries locally using case-folded query text, handle input method composition as query state, and launch only on explicit activation of an enabled result through the typed launch and correlated native outcome path.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

#### Scenario: WARLOCK-DL-020-01

- **GIVEN** admitted catalog entries and an active launcher search
- **WHEN** the user enters or composes a query
- **THEN** the query and composition state update and matching entries are ranked without launching an application

#### Scenario: WARLOCK-DL-020-02

- **GIVEN** a matching enabled application entry
- **WHEN** the user explicitly activates that entry
- **THEN** the typed launch path submits its identity and uses the correlated native outcome; free text and process disappearance do not establish a launch outcome

### Requirement: WARLOCK-DL-024 — Read-mode website with consistent component sections

When the catalog renders navigation, it SHALL provide Home, Test drive, Foundations, Styles, Components, Architecture and Get started, with Search and the shipped subsection links; each component SHALL expose Overview, Anatomy, States, Behaviour and keyboard, Accessibility, Content and Try it sections linking to its place in the simulated desktop. Evidence SHALL remain separately identified and traceable without requiring an Evidence navigation entry.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

#### Scenario: WARLOCK-DL-024-01

- **GIVEN** a component page and primary navigation are built
- **WHEN** their sections and links are inspected
- **THEN** the required component sections, desktop context link and Home, Test drive, Foundations, Styles, Components, Architecture and Get started navigation are present

#### Scenario: WARLOCK-DL-024-02

- **GIVEN** a visitor follows Try it
- **WHEN** the desktop opens
- **THEN** the corresponding component is reachable in the simulated host and evidence remains separately identified

### Requirement: WARLOCK-DL-026 — Real Elm demonstrations with explicit fixture authority

When a demo claims Elm behavior, it SHALL run the relevant shipped Elm decoder/view/update or decision function through an isolated typed wrapper. Manually controlled outcome specimens SHALL keep Pending and Unknown unchanged until explicit reader settlement; the live simulated host SHALL process ordinary requests and return labeled simulated receipts and observations automatically. Unknown SHALL NOT be automatically retried. Simulated outcomes SHALL NOT establish native acceptance.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

#### Scenario: WARLOCK-DL-026-01

- **GIVEN** a manually controlled Pending or Unknown outcome specimen
- **WHEN** the reader has not explicitly settled it
- **THEN** the outcome remains unchanged and Unknown is not automatically retried

#### Scenario: WARLOCK-DL-026-02

- **GIVEN** a live simulated host receives an ordinary request and a static visual specimen is displayed
- **WHEN** the host processes the request and the specimen renders
- **THEN** the host automatically returns labeled simulated receipts and observations without claiming native acceptance; the static specimen is labeled as such and cannot implement a competing desktop policy in JavaScript

## ADDED Requirements

### Requirement: WARLOCK-DL-031 — Brand red and danger are distinct

When Warlock presents brand identity or consequential actions, it SHALL use brand-text for essential identity marks, including active contours, selection bars and brand glyphs, and SHALL use the theme action-fill and on-action roles for filled affirmative actions: Night and Dawn use red fill with light text, High contrast uses white fill with black text, and forced colors use appropriate system colors. Danger SHALL appear on neutral chrome with an octagonal stop glyph, reason and explicit action label; destructive confirmation SHALL use danger outline and text, retain Cancel before Confirm and follow source focus policy.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

#### Scenario: WARLOCK-DL-031-01

- **GIVEN** an enabled affirmative action and destructive confirmation share a task
- **WHEN** the controls render in Night, Dawn, High contrast or forced colors
- **THEN** the affirmative uses the applicable action-fill and on-action roles, red and light in Night and Dawn, white and black in High contrast, or system colors in forced colors; the destructive action uses neutral chrome with danger outline, text and reason

#### Scenario: WARLOCK-DL-031-02

- **GIVEN** a power or session command rests
- **WHEN** it is presented
- **THEN** it remains neutral and errors do not glow

#### Scenario: WARLOCK-DL-031-03

- **GIVEN** an active contour, selection bar and essential brand glyph
- **WHEN** the identity marks render
- **THEN** each uses the theme brand-text role

### Requirement: WARLOCK-DL-032 — Secondary colors convey typed information

When Warlock presents a typed state, it SHALL use focus blue for control focus and confirmed recipient, info for information, positive for confirmed success, warning for attention or Unknown and danger for refusal or error, each with its specified shape and words; Pending, Submitted, Cancelled and untyped text SHALL remain neutral.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

#### Scenario: WARLOCK-DL-032-01

- **GIVEN** a typed Unknown outcome is published
- **WHEN** the outcome renders
- **THEN** a question diamond and unconfirmed words accompany warning color without a success mark

#### Scenario: WARLOCK-DL-032-02

- **GIVEN** untyped status text is supplied
- **WHEN** it is displayed
- **THEN** neutral text is used without classifying the string as an outcome

### Requirement: WARLOCK-DL-033 — Measured theme roles and color-vision checks

When semantic colors are compiled, Warlock SHALL publish opaque sRGB Night, Dawn and High contrast roles and a manifest of actual unrounded pair ratios, verify text at 4.5:1 and essential marks at 3:1, and measure severity-1.0 protanopia and deuteranopia simulations with redundant non-color meaning.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

#### Scenario: WARLOCK-DL-033-01

- **GIVEN** Night and Dawn action states and neutral backgrounds are compiled
- **WHEN** contrast is measured
- **THEN** the declared text and boundary pairs and both simulated color-vision checks are recorded and meet their thresholds

#### Scenario: WARLOCK-DL-033-02

- **GIVEN** High contrast or forced colors is requested
- **WHEN** the view renders
- **THEN** black and white high contrast roles or system colors preserve boundaries and state meaning without relying on color alone

### Requirement: WARLOCK-DL-034 — Observed window focus and Hyprland mapping

When admitted observation changes window focus, Warlock SHALL immediately render a neutral 2px focused or unfocused edge with opaque 1px inner and outer guards, a focused title beacon and matching taskbar marker; at least the focused versus unfocused edge SHALL differ by 3:1. Hyprland active/inactive borders SHALL respectively be f6efe8ff/707078ff in Night, 181314ff/706562ff in Dawn and ffffffff/767676ff in High contrast, at border size 2.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

#### Scenario: WARLOCK-DL-034-01

- **GIVEN** a window gains admitted focus in Night
- **WHEN** the frame and taskbar render
- **THEN** the neutral focused edge, title beacon and taskbar marker appear independently of the red application contour

#### Scenario: WARLOCK-DL-034-02

- **GIVEN** the theme changes to Dawn or High contrast
- **WHEN** the compositor values resolve
- **THEN** active and inactive borders match the theme values, opacity stays 1 and inactive dimming stays disabled

### Requirement: WARLOCK-DL-035 — Independent attention vocabulary

While attention facts coexist, Warlock SHALL render active application as a backed brand contour and diamond or wording, focused window as a neutral edge and beacon, candidate as four neutral corner brackets and wording, control focus as a blue outline and opaque gap, confirmed recipient as blue chevrons or a label, selection as a brand bar and check or wording, and observed family as short neutral brackets.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

#### Scenario: WARLOCK-DL-035-01

- **GIVEN** a chooser receives input while A is active and B is candidate
- **WHEN** the scene renders
- **THEN** the chooser recipient, A activity and B candidate remain separately identifiable

#### Scenario: WARLOCK-DL-035-02

- **GIVEN** recipient facts are unavailable
- **WHEN** the scene renders
- **THEN** no recipient cue is inferred from hover, labels or a command receipt

### Requirement: WARLOCK-DL-036 — Elevation shadows and limited glow

While surfaces render, Warlock SHALL use flush level 0 for rows and tiled, snapped or maximized clients, rest level 1 for taskbar and floating clients, raised level 2 for detached popups, and dialog level 3 for separate blocking surfaces, with explicit boundaries and at most two black, zero-spread contact and ambient shadows: levels 1, 2 and 3 use 0 2px 4px plus 0 6px 16px, 0 3px 6px plus 0 8px 24px, and 0 4px 8px plus 0 12px 32px respectively, at Night alphas .28/.20 and Dawn alphas .16/.12. Glow SHALL be restricted to a confirmed recipient halo, short family softness or the temporary portal bloom.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

#### Scenario: WARLOCK-DL-036-01

- **GIVEN** focus moves between floating windows
- **WHEN** the view renders
- **THEN** elevation class and stack order do not change merely because focus changes

#### Scenario: WARLOCK-DL-036-02

- **GIVEN** effects are reduced or off
- **WHEN** depth is rendered
- **THEN** reduced removes glow; off and High contrast remove soft shadows and highlights while retaining sharp boundaries

### Requirement: WARLOCK-DL-037 — Observed application-window portal

When an admitted observation establishes an eligible individual newly mapped application window or removal of the same window incarnation, Warlock SHALL admit at most one decorative portal. Initial snapshots, session restoration, bulk mapping, workspace redisplay, minimize or restore, ordinary focus changes, shell popups, notifications, preview frames, search results and snapping SHALL settle without a portal. Intent or receipt alone SHALL NOT trigger a portal.

Full opening SHALL last 520ms: ignite 0–120ms grows extent .04 to .16 and opacity 0 to .65 with cubic-bezier(.16,0,.3,1); expand 120–380ms grows extent .16 to 1 with rotation at most 12 degrees and cubic-bezier(.2,.72,.2,1); resolve 380–460ms reaches final frame radius and fades .65 to .20 with cubic-bezier(.2,0,0,1); settle 460–520ms fades .20 to 0 with cubic-bezier(0,0,.2,1). Full closing SHALL last 360ms: release 0–90ms acquires a .65-opacity ring with cubic-bezier(.4,0,1,1); contract 90–270ms reduces extent 1 to .06 with reverse rotation at most 8 degrees and cubic-bezier(.4,0,.8,.3); extinguish 270–360ms reduces extent .06 to .02 and opacity to 0 with cubic-bezier(0,0,.2,1).

The portal SHALL use a separate decorative plane with transparent ring center, at most 8% dimensional overscan clipped to output and no paint over live text, controls or focus indicators. Its decorative aperture SHALL interpolate inset(48% 48% round 480px), inset(40% 42% round 420px), inset(3.5% 3.5% round 220px), and inset(0 round 8px) for floating or inset(0 round 0) for snapped or tiled frames. Native clients SHALL use a guarded frame effect. The live input plane SHALL remain at final geometry without scaling, translation, fading or clipping; observed removal SHALL retire input immediately.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

#### Scenario: WARLOCK-DL-037-01

- **GIVEN** a launch is Pending or Submitted without a mapped observation
- **WHEN** the host reports a receipt
- **THEN** no portal starts and no completion is inferred

#### Scenario: WARLOCK-DL-037-02

- **GIVEN** the full effects tier is active and the same observed window incarnation is removed
- **WHEN** the close effect starts
- **THEN** only a non-interactive aria-hidden remnant remains and the 360ms full effect retires after completion

#### Scenario: WARLOCK-DL-037-03

- **GIVEN** an eligible individual application window maps with full effects
- **WHEN** opening is sampled at 0, 120, 380, 460 and 520ms
- **THEN** the phase boundaries, extent, opacity, easing and maximum rotation match the opening contract; the transparent decorative plane stays within 8% overscan and does not paint over live content or focus cues

#### Scenario: WARLOCK-DL-037-04

- **GIVEN** an eligible observed application incarnation is removed with full effects
- **WHEN** closing is sampled at 0, 90, 270 and 360ms
- **THEN** the remnant follows the release, contract and extinguish limits, input is retired immediately and no effect paint covers live content

#### Scenario: WARLOCK-DL-037-05

- **GIVEN** an initial snapshot, session restoration or bulk mapping is observed
- **WHEN** windows become visible
- **THEN** all settle without portal playback

#### Scenario: WARLOCK-DL-037-06

- **GIVEN** a window is redisplayed on a workspace, minimized or restored, focused or snapped
- **WHEN** the corresponding observation arrives
- **THEN** no portal starts or replays

### Requirement: WARLOCK-DL-038 — Portal effects tiers and photosensitivity

While a portal is eligible, Warlock SHALL resolve full, reduced or off from user preference and host capability; high contrast and forced colors select effects off, and an unknown motion preference suppresses motion. Reduced uses decorative opacity only for 120ms opening and 90ms closing, and off or reduced motion settles immediately. It SHALL admit at most one full start per rolling 1000ms, keep luminous coverage below 5% of viewport, cap bloom opacity at 0.16 Night or 0.10 Dawn, and use a single rise and fall without repeated flashing. It SHALL perform flash-threshold testing on rapid open and close sequences and immediately settle interrupted, hidden, stale or retired effects without replay.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

#### Scenario: WARLOCK-DL-038-01

- **GIVEN** several windows map within one second
- **WHEN** the portal admission limit is reached
- **THEN** additional windows settle immediately without a queued effect

#### Scenario: WARLOCK-DL-038-02

- **GIVEN** the document becomes hidden or motion preference changes during an effect
- **WHEN** the new condition is observed
- **THEN** the effect settles immediately and does not replay on return

#### Scenario: WARLOCK-DL-038-03

- **GIVEN** high contrast or forced colors is active
- **WHEN** an eligible window opens or closes
- **THEN** effects resolve to off and the window settles without a portal

#### Scenario: WARLOCK-DL-038-04

- **GIVEN** a portal is in progress
- **WHEN** high contrast or forced colors is enabled, or motion preference becomes unknown
- **THEN** the effect settles immediately without replay and motion remains suppressed while the preference is unknown

### Requirement: WARLOCK-DL-039 — CSS and Elm presentation contract

When a surface renders, Elm SHALL own interaction state and emit semantic elements, classes, ARIA and typed data attributes; CSS SHALL own visual presentation under the ordered legacy, reset, tokens, base, layouts, components, states, effects and accessibility layers. Runtime rules SHALL scope to html[data-warlock-design="v1"], documentation to .wl-doc-*, specimens to .wl-specimen-*, and area rules to the actual .surface-popup[data-mode] or .surface-bar; only shared foundations SHALL define document-level rules. The shipped legacy stylesheet SHALL be imported or wrapped in the legacy layer without a duplicate unlayered copy; where an unlayered legacy link is required, a scoped unlayered compatibility build SHALL be generated from the same token and component sources.

The effective effects tier SHALL use data-effects="on" as full unless host capability selects reduced or high contrast or forced colors selects off, data-effects="off" as off, and data-effects-tier="full|reduced|off" as the resolved tier without a new preference owner. When motion preference is unknown, the surface SHALL suppress motion until the preference is known. Token compilation SHALL resolve typed reference, semantic and component aliases deterministically, reject cycles, and produce CSS, contrast and Hyprland values. Globally registered properties SHALL have inherits: false and literal initial values: --wl-portal-progress syntax '<number>' initial 0; --wl-portal-turn syntax '<angle>' initial 0deg; --wl-effect-alpha syntax '<number>' initial 0; --wl-capture-delay syntax '<time>' initial 0ms. Ordinary transform and opacity keyframes SHALL work without registration, and runtime capture SHALL supply validated negative animation-delay directly to effect nodes.

Elm SHALL retain only a presentation record keyed by incarnation, output epoch and effect cycle; observed removal SHALL retire input immediately. If no completion event arrives, a watchdog SHALL retire the decoration at the animation duration plus 100ms without changing input authority or operation outcomes.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

#### Scenario: WARLOCK-DL-039-01

- **GIVEN** registered portal properties or CSS masks are unsupported
- **WHEN** the effect renders
- **THEN** ordinary transform and opacity keyframes or the reduced tier retain usable interaction

#### Scenario: WARLOCK-DL-039-02

- **GIVEN** an application close animation ends or is cancelled
- **WHEN** the bridge validates sentinel target, animation and cycle
- **THEN** Elm receives a completion Msg, ignores stale or duplicate events, and a valid completion or cancellation settles only decoration

#### Scenario: WARLOCK-DL-039-03

- **GIVEN** a legacy stylesheet is loaded alongside layered component rules
- **WHEN** the cascade is audited for an unlayered override
- **THEN** a duplicate unlayered legacy stylesheet is rejected, or the required unlayered link uses the scoped compatibility build generated from the same sources

#### Scenario: WARLOCK-DL-039-04

- **GIVEN** effects are on and host capability permits only reduced effects
- **WHEN** the rendering attributes resolve
- **THEN** data-effects-tier is reduced without changing the preference; effects off always resolves to off

#### Scenario: WARLOCK-DL-039-05

- **GIVEN** effects are on while high contrast or forced colors is active, or motion preference is unknown
- **WHEN** the presentation attributes and motion policy resolve
- **THEN** high contrast and forced colors resolve data-effects-tier to off, and an unknown motion preference suppresses motion without changing the stored effects preference

#### Scenario: WARLOCK-DL-039-06

- **GIVEN** a close decoration remains active and no completion event arrives
- **WHEN** the animation duration plus 100ms elapses
- **THEN** the watchdog retires the decoration without changing input authority or operation outcomes

