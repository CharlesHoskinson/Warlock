# Warlock design-language EARS

Exact consensus candidate v2; implementation and native qualification open. Requirement text and guardrails are preserved from the voted JSON.

## WARLOCK-DL-001 — Preserve Warlock identity and philosophical priorities

The design language shall preserve the approved Warlock name, flow sigil, tagline, bundled typefaces and schema-1 palette values, and shall apply the existing philosophy when resolving conflicts.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

## WARLOCK-DL-002 — Three token tiers and explicit role pairs

When a control renders, its styles shall resolve through component tokens and semantic role tokens backed by the preserved reference palette, with explicit foreground/background pairs.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

## WARLOCK-DL-003 — Measured contrast and non-color state cues

When tokens are built, the build shall verify declared text pairs at 4.5:1 and declared large-text, boundary and focus pairs at 3:1 in dark and light themes; all meaningful states shall have text or shape cues.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

## WARLOCK-DL-004 — Independent interaction and outcome axes

While an outcome is Pending or Unknown, the surface shall expose that outcome independently from hover, focus, pressed, selection, current and unavailable states, and shall preserve the targeted intent identity.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

## WARLOCK-DL-005 — Stable focus and keyed control identity

When a publication changes control order, the renderer shall preserve identity and eligible focus for each surviving control; it shall not infer selection, current state or an effect from focus.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

## WARLOCK-DL-006 — Visible focus with theme and contrast support

When keyboard focus is visible, the surface shall display a focus treatment distinguishable from selection and hover with at least a 2 CSS pixel outer indicator and 3:1 adjacent-color contrast; forced-colors rendering shall retain it.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

## WARLOCK-DL-007 — Accessible label, description and typed semantics

When a control is published, its accessible name shall begin with its normalized visible stable label, while transient detail and outcomes use description or state; toggle checked state shall derive from admitted observation.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

## WARLOCK-DL-008 — Explicit disabled-item policies per surface

Where a surface supports unavailable controls, the specification shall declare whether navigation focuses them, the rejection behavior, readable reason and fallback; unavailable controls shall never emit an effect intent.

Guardrail: ELM-ADOPT-030 remains authoritative. The consensus chooses focusable disabled menu items as a future guarded design target; it does not claim this behavior exists or globally change all surfaces.

## WARLOCK-DL-009 — Complete popup keyboard and dismissal contract

While a qualified popup holds keyboard scope, Up/Down and Home/End shall follow its declared navigation policy; Escape shall dismiss by exact identity and restore eligible invoker focus or declared fallback without settling or replaying Pending or Unknown operations.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

## WARLOCK-DL-010 — Taskbar entry, navigation and exit through existing contracts

When taskbar keyboard interaction is qualified, its entry, arrow movement, popup invocation and exit shall follow the existing ELM-ADOPT-029 contract without introducing an unreviewed default global shortcut or altering activation history.

Guardrail: Existing native keyboard ownership and input identity gates are prerequisites. No automatic F6/global shortcut adoption.

## WARLOCK-DL-011 — One announcement owner with honest feedback channels

When an allowlisted outcome needs an announcement, the designated route shall announce it once under the existing attention policy without moving focus; persistent blocking or unconfirmed conditions shall remain readable.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

## WARLOCK-DL-012 — Plain status copy and safe reconciliation

When a status is presented, its catalog entry shall distinguish the condition and any safe next action without exposing unnecessary protocol jargon or fabricating a refusal reason; Unknown shall never offer automatic replay.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

## WARLOCK-DL-013 — Responsive type, density and target geometry

When density or text scale changes, surfaces shall preserve labels, accessible names, outcomes and focus indicators; catalog compact actionable targets shall be at least 24x24 CSS pixels, and a comfortable profile shall be available.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

## WARLOCK-DL-014 — Live appearance with action-target continuity

When appearance or contrast preference changes, the controller shall publish applicable presentation preferences while preserving pending target and control identity and respecting actual native dependency-generation changes.

Guardrail: Do not forbid legitimate publication/lease or native rendering-generation changes; continuity preserves identity and authority rather than freezing revision numbers.

## WARLOCK-DL-015 — Reduced motion and native presentation continuity

While reduced motion is active, the catalog shall run no decorative or velocity-continuation motion, and product motion shall convey equivalent state with instant or permitted opacity changes driven by native last-presented geometry.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

## WARLOCK-DL-016 — Timers and composition never fabricate authority

When a prepared-choice deadline expires or composition is active, the interface shall preserve user context while invalidating expired authority and suppressing shortcut/typeahead interpretation during owned composition.

Guardrail: Original choice, transport and operation deadlines are unchanged. No expired choice stays actionable; original AT/IME qualification remains open.

## WARLOCK-DL-017 — Publish exact taskbar activation decisions

When a taskbar group is activated, the controller shall derive its decision from the shipped Taskbar.primary call and present pending feedback for Apply decisions until correlated settlement.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

## WARLOCK-DL-018 — Preview identity, eligibility and honest freshness

While a preview is displayed, its title/application and state shall remain understandable; Live shall retain its frozen PreviewLifecycle definition, and any stronger native-presented claim shall require the applicable native presentation evidence.

Guardrail: Preserve the frozen S09/ELM-ADOPT-028 Historical/Live/Unavailable meanings, authorized historical pixels and original preview13 oracles. A timestamp, browser canvas or unqualified root-plane capture does not prove native presentation.

## WARLOCK-DL-019 — Capability-driven window-actions content

When window actions are shown, unsupported actions shall be omitted and supported but currently unavailable actions shall have a reason, with checkable states derived from native observation.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

## WARLOCK-DL-020 — Launcher search as a guarded extension

While a proposed launcher search is active, filtering shall remain local to admitted catalog entries and composition-safe; activation shall use the existing typed launch and correlated native outcome path.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

## WARLOCK-DL-021 — Host-owned workspaces and gated placement patterns

Where the catalog explains workspaces, snapping or tiling, it shall identify current host ownership and existing roadmap gates and shall not present an unsupported browser arrangement as implemented native placement.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

## WARLOCK-DL-022 — Settings declare behavioral guarantees

When a setting is designed, its documentation shall state the behavior changed, defaults, keyboard/accessibility behavior, privacy/ownership implications and guarantees preserved.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

## WARLOCK-DL-023 — Source-derived complete widget registry

When the catalog builds, it shall compare a versioned source inventory for the selected coherent GUI closure against the widget registry and fail on an uncovered rendered surface, role, mode, action or outcome constructor.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

## WARLOCK-DL-024 — Read-mode website with consistent component sections

The catalog shall provide Overview, Foundations, Components, Patterns, Accessibility, Tokens, Evidence and Changelog navigation, and every component shall expose Overview, Anatomy & states, Behavior & keyboard, Accessibility, Content and Evidence sections.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

## WARLOCK-DL-025 — Claim-specific status and evidence records

When a behavioral claim is displayed, the catalog shall separate Proposed/Implemented status from scoped evidence records and shall require a frozen receipt, scenario identity and owning ABI tuple for any Native-qualified label.

Guardrail: Evidence levels are distinct scopes, not a universal confidence ladder. Multiple records are allowed; the prominent badge names the scope of the exact claim.

## WARLOCK-DL-026 — Real Elm demonstrations with explicit fixture authority

When a demo claims Elm behavior, it shall run the relevant shipped Elm decoder/view/update or decision function through an isolated typed wrapper; any native outcome shall be supplied only through a clearly labeled simulated-authority panel.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

## WARLOCK-DL-027 — Content and accessible semantics inventory

When the catalog builds, it shall inventory source labels/status text, show wording and semantic findings with source locations, and keep proposed fixes separate from the original source.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

## WARLOCK-DL-028 — Responsive, accessible and offline-capable catalog

When the catalog is viewed at constrained width or enlarged zoom, content shall reflow without two-dimensional scrolling except explicitly labeled fixed-size specimen canvases or data tables; core content, fonts and demos shall work from bundled local assets.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

## WARLOCK-DL-029 — Versioned assets, coverage and bounded finish review

When a covered source or token changes, its manifest hash and changelog shall be reconciled before publication; the catalog shall retain asset/source licenses and actual generated-art provenance and receive bounded independent finish review.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

## WARLOCK-DL-030 — Reference adoption matrix with original visual identity

The design language shall publish borrow/adapt/reject/defer decisions for Material Design, Impeccable, Apple Human Interface Guidelines (iOS design language, with supplemental macOS desktop guidance), Plasma/KDE, Windows/Fluent and GNOME, with primary-source links and explicit Warlock rationale.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

