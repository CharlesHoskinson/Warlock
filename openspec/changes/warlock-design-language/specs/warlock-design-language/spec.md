# Warlock design language

## ADDED Requirements

### Requirement: WARLOCK-DL-001 — Preserve Warlock identity and philosophical priorities

The design language SHALL preserve the approved Warlock name, flow sigil, tagline, bundled typefaces and schema-1 palette values, and SHALL apply the existing philosophy when resolving conflicts.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Source proposals: WL-ID-07, OPUS05-CAT-12

#### Scenario: WARLOCK-DL-001-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** A byte comparison confirms all schema-1 values are unchanged.

#### Scenario: WARLOCK-DL-001-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Brand decoration never encodes confirmation or grants native authority.

### Requirement: WARLOCK-DL-002 — Three token tiers and explicit role pairs

When a control renders, its styles SHALL resolve through component tokens and semantic role tokens backed by the preserved reference palette, with explicit foreground/background pairs.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Source proposals: WL-ID-01, OPUS05-CAT-05

#### Scenario: WARLOCK-DL-002-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** The catalog publishes reference, semantic and component token mappings.

#### Scenario: WARLOCK-DL-002-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Artwork may use reference colors; actionable components cannot substitute unreviewed literal colors.

### Requirement: WARLOCK-DL-003 — Measured contrast and non-color state cues

When tokens are built, the build SHALL verify declared text pairs at 4.5:1 and declared large-text, boundary and focus pairs at 3:1 in dark and light themes; all meaningful states SHALL have text or shape cues.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Source proposals: WL-ID-02, WLK-WGT-03, AM-02

#### Scenario: WARLOCK-DL-003-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Pair tests evaluate the actual composited state background, including overlays.

#### Scenario: WARLOCK-DL-003-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Disabled items retain readable reasons; decorative or inactive elements are classified explicitly rather than claiming universal WCAG applicability.

### Requirement: WARLOCK-DL-004 — Independent interaction and outcome axes

While an outcome is Pending or Unknown, the surface SHALL expose that outcome independently from hover, focus, pressed, selection, current and unavailable states, and SHALL preserve the targeted intent identity.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Source proposals: WL-ID-03, WLK-WGT-02, WLD-DESK-07, OPUS05-CAT-04, AM-01

#### Scenario: WARLOCK-DL-004-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Where the declared per-surface policy lets a Pending or Unknown control hold focus, focus and outcome cues are both perceivable; where policy removes it from focus, the outcome remains perceivable through status or description and focus follows the declared WARLOCK-DL-005 fallback.

#### Scenario: WARLOCK-DL-004-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Unknown cannot be presented as Committed; repeating activation never creates a second intent for its blocked target.

### Requirement: WARLOCK-DL-005 — Stable focus and keyed control identity

When a publication changes control order, the renderer SHALL preserve identity and eligible focus for each surviving control; it SHALL not infer selection, current state or an effect from focus.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Source proposals: WL-ID-08, WLK-WGT-08, AM-11

#### Scenario: WARLOCK-DL-005-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Reordering and inserting neighboring popup entries preserves the existing keyed control.

#### Scenario: WARLOCK-DL-005-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Removing or disabling the focused identity invokes the declared per-surface fallback.

### Requirement: WARLOCK-DL-006 — Visible focus with theme and contrast support

When keyboard focus is visible, the surface SHALL display a focus treatment distinguishable from selection and hover with at least a 2 CSS pixel outer indicator and 3:1 adjacent-color contrast; forced-colors rendering SHALL retain it.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Source proposals: WLK-WGT-04, AM-02, WL-ID-04

#### Scenario: WARLOCK-DL-006-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** A two-tone 2px outer/1px inner ring is the initial catalog treatment; equivalent native treatment is separately qualified.

#### Scenario: WARLOCK-DL-006-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Dark, light, forced colors and enlarged text are included in the rendered matrix.

### Requirement: WARLOCK-DL-007 — Accessible label, description and typed semantics

When a control is published, its accessible name SHALL begin with its normalized visible stable label, while transient detail and outcomes use description or state; toggle checked state SHALL derive from admitted observation.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Source proposals: WL-ID-09, WLK-WGT-07, AM-05, OPUS05-CAT-08

#### Scenario: WARLOCK-DL-007-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** A label-in-name validator reports the identity of any failing fixture.

#### Scenario: WARLOCK-DL-007-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Menu toggles use typed checked semantics and do not infer current state from a future toggle action or display string.

### Requirement: WARLOCK-DL-008 — Explicit disabled-item policies per surface

Where a surface supports unavailable controls, the specification SHALL declare whether navigation focuses them, the rejection behavior, readable reason and fallback; unavailable controls SHALL never emit an effect intent.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: ELM-ADOPT-030 remains authoritative. The consensus chooses focusable disabled menu items as a future guarded design target; it does not claim this behavior exists or globally change all surfaces.

Source proposals: AM-07, WLK-WGT-07

#### Scenario: WARLOCK-DL-008-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** The current source skip-disabled policy is labeled Source, not silently rewritten.

#### Scenario: WARLOCK-DL-008-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** The proposed menu focus-disabled policy is separately documented and gated on model, browser and native AT/keyboard qualification; other surfaces keep their declared policy.

### Requirement: WARLOCK-DL-009 — Complete popup keyboard and dismissal contract

While a qualified popup holds keyboard scope, Up/Down and Home/End SHALL follow its declared navigation policy; Escape SHALL dismiss by exact identity and restore eligible invoker focus or declared fallback without settling or replaying Pending or Unknown operations.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Source proposals: WLK-WGT-06, WLD-DESK-04, AM-06

#### Scenario: WARLOCK-DL-009-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Menu wrap, Enter/Space and typeahead are documented with exact Msg mapping and source status.

#### Scenario: WARLOCK-DL-009-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Dismissal retains outstanding intent and cleanup obligations; no keyboard event gains authority merely from a browser demo.

### Requirement: WARLOCK-DL-010 — Taskbar entry, navigation and exit through existing contracts

When taskbar keyboard interaction is qualified, its entry, arrow movement, popup invocation and exit SHALL follow the existing ELM-ADOPT-029 contract without introducing an unreviewed default global shortcut or altering activation history.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing native keyboard ownership and input identity gates are prerequisites. No automatic F6/global shortcut adoption.

Source proposals: WLK-WGT-09, WLD-DESK-05, OPUS05-CAT-07

#### Scenario: WARLOCK-DL-010-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Source, proposed and binding-unverified key rows are distinct.

#### Scenario: WARLOCK-DL-010-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Toolbar role, roving focus and Down-to-picker are design targets until coherent native scope and recipient tests pass.

### Requirement: WARLOCK-DL-011 — One announcement owner with honest feedback channels

When an allowlisted outcome needs an announcement, the designated route SHALL announce it once under the existing attention policy without moving focus; persistent blocking or unconfirmed conditions SHALL remain readable.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Source proposals: WLK-WGT-10, WLD-DESK-06, AM-09, AM-01

#### Scenario: WARLOCK-DL-011-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Repeated same-outcome publications do not re-announce; unrelated controls remain usable.

#### Scenario: WARLOCK-DL-011-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Routine Committed window changes use the resulting visible state rather than unsolicited success toasts.

### Requirement: WARLOCK-DL-012 — Plain status copy and safe reconciliation

When a status is presented, its catalog entry SHALL distinguish the condition and any safe next action without exposing unnecessary protocol jargon or fabricating a refusal reason; Unknown SHALL never offer automatic replay.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Source proposals: WLK-WGT-11, OPUS05-CAT-09, AM-01

#### Scenario: WARLOCK-DL-012-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Existing strings are inventoried with source locations; proposed replacements remain reviewable entries.

#### Scenario: WARLOCK-DL-012-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Reconcile refreshes native truth and does not resend the original Unknown action.

### Requirement: WARLOCK-DL-013 — Responsive type, density and target geometry

When density or text scale changes, surfaces SHALL preserve labels, accessible names, outcomes and focus indicators; catalog compact actionable targets SHALL be at least 24x24 CSS pixels, and a comfortable profile SHALL be available.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Source proposals: WL-ID-06, WLK-WGT-05

#### Scenario: WARLOCK-DL-013-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** The catalog checks constrained width, text enlargement, long names and RTL.

#### Scenario: WARLOCK-DL-013-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** 24px is a catalog design choice, not a claim that every native handle or input device meets a new blanket threshold; native targets retain their frozen device/geometry contracts.

### Requirement: WARLOCK-DL-014 — Live appearance with action-target continuity

When appearance or contrast preference changes, the controller SHALL publish applicable presentation preferences while preserving pending target and control identity and respecting actual native dependency-generation changes.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Do not forbid legitimate publication/lease or native rendering-generation changes; continuity preserves identity and authority rather than freezing revision numbers.

Source proposals: WL-ID-04, WL-ID-05

#### Scenario: WARLOCK-DL-014-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Changing theme cannot rebind a Pending intent or activate a control.

#### Scenario: WARLOCK-DL-014-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Forced-colors uses system roles; native preference observation and in-flight adoption require real qualification.

### Requirement: WARLOCK-DL-015 — Reduced motion and native presentation continuity

While reduced motion is active, the catalog SHALL run no decorative or velocity-continuation motion, and product motion SHALL convey equivalent state with instant or permitted opacity changes driven by native last-presented geometry.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Source proposals: WL-ID-10, AM-03, AM-04

#### Scenario: WARLOCK-DL-015-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** The website starts still, pauses hidden decorative work and responds live to preference changes.

#### Scenario: WARLOCK-DL-015-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Motion never delays input, extends a native deadline or settles an outcome; native timing stays under frozen S02/ELM-ADOPT-023/024.

### Requirement: WARLOCK-DL-016 — Timers and composition never fabricate authority

When a prepared-choice deadline expires or composition is active, the interface SHALL preserve user context while invalidating expired authority and suppressing shortcut/typeahead interpretation during owned composition.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Original choice, transport and operation deadlines are unchanged. No expired choice stays actionable; original AT/IME qualification remains open.

Source proposals: AM-08, AM-10

#### Scenario: WARLOCK-DL-016-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Expired choices may remain visibly unavailable with a safe refresh path but cannot activate under the old grant or deadline.

#### Scenario: WARLOCK-DL-016-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** IME commits bind to native composition identity; browser IME behavior is not native qualification.

### Requirement: WARLOCK-DL-017 — Publish exact taskbar activation decisions

When a taskbar group is activated, the controller SHALL derive its decision from the shipped Taskbar.primary call and present pending feedback for Apply decisions until correlated settlement.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Source proposals: WLD-DESK-01

#### Scenario: WARLOCK-DL-017-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** The truth table records the shipped call Taskbar.primary False (TaskbarShell.elm and Surface.elm); zero-family and pinned-to-Launch rows are function-level Source and unreachable from shipped groups, while pinned launch remains a separate native contract.

#### Scenario: WARLOCK-DL-017-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** A decision or sent request is never labeled a confirmed native result.

### Requirement: WARLOCK-DL-018 — Preview identity, eligibility and honest freshness

While a preview is displayed, its title/application and state SHALL remain understandable; Live SHALL retain its frozen PreviewLifecycle definition, and any stronger native-presented claim SHALL require the applicable native presentation evidence.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Preserve the frozen S09/ELM-ADOPT-028 Historical/Live/Unavailable meanings, authorized historical pixels and original preview13 oracles. A timestamp, browser canvas or unqualified root-plane capture does not prove native presentation.

Source proposals: WLK-WGT-12, WLD-DESK-02

#### Scenario: WARLOCK-DL-018-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Source Live preview, Historical preview, Preview loading and Preview unavailable and their fidelity text are documented under the frozen historical/live/unavailable policy and original S09 preview13. Existing authorized Historical display is neither removed nor relabeled.

#### Scenario: WARLOCK-DL-018-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Current, Placeholder and Earlier frame are proposed catalog terms only. Any label rename or added Live evidence condition is gated on ELM-ADOPT-028 review; only new retention beyond the existing authorized, unexpired, privacy-matched lease is deferred. Existing expiry/lock revocation and native492 root-plane previewEligible:false remain unchanged.

### Requirement: WARLOCK-DL-019 — Capability-driven window-actions content

When window actions are shown, unsupported actions SHALL be omitted and supported but currently unavailable actions SHALL have a reason, with checkable states derived from native observation.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Source proposals: WLD-DESK-03, WLK-WGT-07

#### Scenario: WARLOCK-DL-019-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** The catalog documents all existing Menu.Action constructors, targets and outcome states.

#### Scenario: WARLOCK-DL-019-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** At most three groups is a content preference for the initial design, not permission to omit required actions or alter provider semantics.

### Requirement: WARLOCK-DL-020 — Launcher search as a guarded extension

While a proposed launcher search is active, filtering SHALL remain local to admitted catalog entries and composition-safe; activation SHALL use the existing typed launch and correlated native outcome path.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Source proposals: WLD-DESK-08

#### Scenario: WARLOCK-DL-020-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Current source without search is documented accurately.

#### Scenario: WARLOCK-DL-020-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Search never executes a command from free text or infers a launch outcome from process disappearance.

### Requirement: WARLOCK-DL-021 — Host-owned workspaces and gated placement patterns

Where the catalog explains workspaces, snapping or tiling, it SHALL identify current host ownership and existing roadmap gates and SHALL not present an unsupported browser arrangement as implemented native placement.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Source proposals: WLD-DESK-09, WLD-DESK-10

#### Scenario: WARLOCK-DL-021-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Existing mandatory release requirements remain in scope; no design deferral removes them.

#### Scenario: WARLOCK-DL-021-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Snap geometry is a native proposal and an applied layout requires correlated authority; no default maximize-hover flyout is added by this catalog.

### Requirement: WARLOCK-DL-022 — Settings declare behavioral guarantees

When a setting is designed, its documentation SHALL state the behavior changed, defaults, keyboard/accessibility behavior, privacy/ownership implications and guarantees preserved.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Source proposals: WLD-DESK-11

#### Scenario: WARLOCK-DL-022-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Settings illustrations are Proposed until integrated.

#### Scenario: WARLOCK-DL-022-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** A setting cannot silently retarget a pending action or bypass bounded admission/recovery.

### Requirement: WARLOCK-DL-023 — Source-derived complete widget registry

When the catalog builds, it SHALL compare a versioned source inventory for the selected coherent GUI closure against the widget registry and fail on an uncovered rendered surface, role, mode, action or outcome constructor.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Source proposals: WLK-WGT-01, OPUS05-CAT-01, WL-ID-11

#### Scenario: WARLOCK-DL-023-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** The full Elm source, stylesheet and bridge closure supplement replaces inference from the initial ten-module subset.

#### Scenario: WARLOCK-DL-023-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Removing a current menu action or preview state from coverage fails with its source identity; other integration lanes are explicitly tracked rather than asserted integrated.

### Requirement: WARLOCK-DL-024 — Read-mode website with consistent component sections

The catalog SHALL provide Overview, Foundations, Components, Patterns, Accessibility, Tokens, Evidence and Changelog navigation, and every component SHALL expose Overview, Anatomy & states, Behavior & keyboard, Accessibility, Content and Evidence sections.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Source proposals: OPUS05-CAT-02, WL-ID-11

#### Scenario: WARLOCK-DL-024-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Search, deep links, theme choice and responsive navigation work with keyboard.

#### Scenario: WARLOCK-DL-024-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Unknown or absent information is marked Not yet specified rather than implied to exist; long pages may use linked headings instead of mandatory tab widgets.

### Requirement: WARLOCK-DL-025 — Claim-specific status and evidence records

When a behavioral claim is displayed, the catalog SHALL separate Proposed/Implemented status from scoped evidence records and SHALL require a frozen receipt, scenario identity and owning ABI tuple for any Native-qualified label.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Evidence levels are distinct scopes, not a universal confidence ladder. Multiple records are allowed; the prominent badge names the scope of the exact claim.

Source proposals: OPUS05-CAT-03, WLD-DESK-12, AM-12

#### Scenario: WARLOCK-DL-025-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** A claim may link Source and Browser-demo records with distinct scopes; neither implies CPU or native acceptance.

#### Scenario: WARLOCK-DL-025-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Demo interaction cannot change recorded evidence or acceptance badges.

### Requirement: WARLOCK-DL-026 — Real Elm demonstrations with explicit fixture authority

When a demo claims Elm behavior, it SHALL run the relevant shipped Elm decoder/view/update or decision function through an isolated typed wrapper; any native outcome SHALL be supplied only through a clearly labeled simulated-authority panel.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Source proposals: WL-ID-12, OPUS05-CAT-06

#### Scenario: WARLOCK-DL-026-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Pending and Unknown examples remain unchanged until explicit reader settlement; Unknown cannot be automatically retried.

#### Scenario: WARLOCK-DL-026-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Static visual specimens may use semantic CSS but are labeled style specimens and cannot implement a competing desktop policy in JavaScript.

### Requirement: WARLOCK-DL-027 — Content and accessible semantics inventory

When the catalog builds, it SHALL inventory source labels/status text, show wording and semantic findings with source locations, and keep proposed fixes separate from the original source.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Source proposals: OPUS05-CAT-08, OPUS05-CAT-09

#### Scenario: WARLOCK-DL-027-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Sentence case, stable labels, toggle roles and announcement duplication have reviewable findings.

#### Scenario: WARLOCK-DL-027-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Source strings are never silently rewritten inside the frozen input packet.

### Requirement: WARLOCK-DL-028 — Responsive, accessible and offline-capable catalog

When the catalog is viewed at constrained width or enlarged zoom, content SHALL reflow without two-dimensional scrolling except explicitly labeled fixed-size specimen canvases or data tables; core content, fonts and demos SHALL work from bundled local assets.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Source proposals: OPUS05-CAT-10, AM-02

#### Scenario: WARLOCK-DL-028-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** 320 CSS pixel viewport, desktop, text enlargement, focus, reduced motion and forced colors are exercised.

#### Scenario: WARLOCK-DL-028-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** No external CDN or native control socket is necessary to read or exercise the catalog; network references are links.

### Requirement: WARLOCK-DL-029 — Versioned assets, coverage and bounded finish review

When a covered source or token changes, its manifest hash and changelog SHALL be reconciled before publication; the catalog SHALL retain asset/source licenses and actual generated-art provenance and receive bounded independent finish review.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Source proposals: OPUS05-CAT-11, OPUS05-CAT-01

#### Scenario: WARLOCK-DL-029-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Failing source hash/coverage tests name the drift.

#### Scenario: WARLOCK-DL-029-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** One batched desktop/mobile inspection and at most one correction inspection are planned; unavailable visual evidence stays explicitly unverified.

### Requirement: WARLOCK-DL-030 — Reference adoption matrix with original visual identity

The design language SHALL publish borrow/adapt/reject/defer decisions for Material Design, Impeccable, Apple Human Interface Guidelines (iOS design language, with supplemental macOS desktop guidance), Plasma/KDE, Windows/Fluent and GNOME, with primary-source links and explicit Warlock rationale.

Status: accepted-design-target; implementation-and-qualification-open.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Source proposals: OPUS05-CAT-12, WL-ID-01

#### Scenario: WARLOCK-DL-030-01

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Borrow token/component documentation, readable craft, continuity, desktop conventions and approachable defaults where compatible.

#### Scenario: WARLOCK-DL-030-02

- **GIVEN** the declared component, foundation or catalog claim within the requirement scope
- **WHEN** its specified stimulus and acceptance fixture are exercised
- **THEN** Reject platform logos/themes and unmeasured glass, blur, ripples or animation costs; inaccessible or snippet-only sources do not establish binding numeric values.

