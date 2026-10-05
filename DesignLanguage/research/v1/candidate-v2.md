# Warlock design language — candidate v2

Exact JSON SHA-256: `63f5311d840a736d109993d096ccb444adb14057acbe1e9f29ab2e3e805a8754`. Corrects four contracts after actual five-reviewer ballots. No consensus or native acceptance claimed before exact-v2 vote.

## WARLOCK-DL-001 — Preserve Warlock identity and philosophical priorities

The design language shall preserve the approved Warlock name, flow sigil, tagline, bundled typefaces and schema-1 palette values, and shall apply the existing philosophy when resolving conflicts.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Acceptance:
- A byte comparison confirms all schema-1 values are unchanged.
- Brand decoration never encodes confirmation or grants native authority.

Source proposals: WL-ID-07, OPUS05-CAT-12

## WARLOCK-DL-002 — Three token tiers and explicit role pairs

When a control renders, its styles shall resolve through component tokens and semantic role tokens backed by the preserved reference palette, with explicit foreground/background pairs.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Acceptance:
- The catalog publishes reference, semantic and component token mappings.
- Artwork may use reference colors; actionable components cannot substitute unreviewed literal colors.

Source proposals: WL-ID-01, OPUS05-CAT-05

## WARLOCK-DL-003 — Measured contrast and non-color state cues

When tokens are built, the build shall verify declared text pairs at 4.5:1 and declared large-text, boundary and focus pairs at 3:1 in dark and light themes; all meaningful states shall have text or shape cues.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Acceptance:
- Pair tests evaluate the actual composited state background, including overlays.
- Disabled items retain readable reasons; decorative or inactive elements are classified explicitly rather than claiming universal WCAG applicability.

Source proposals: WL-ID-02, WLK-WGT-03, AM-02

## WARLOCK-DL-004 — Independent interaction and outcome axes

While an outcome is Pending or Unknown, the surface shall expose that outcome independently from hover, focus, pressed, selection, current and unavailable states, and shall preserve the targeted intent identity.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Acceptance:
- Where the declared per-surface policy lets a Pending or Unknown control hold focus, focus and outcome cues are both perceivable; where policy removes it from focus, the outcome remains perceivable through status or description and focus follows the declared WARLOCK-DL-005 fallback.
- Unknown cannot be presented as Committed; repeating activation never creates a second intent for its blocked target.

Source proposals: WL-ID-03, WLK-WGT-02, WLD-DESK-07, OPUS05-CAT-04, AM-01

## WARLOCK-DL-005 — Stable focus and keyed control identity

When a publication changes control order, the renderer shall preserve identity and eligible focus for each surviving control; it shall not infer selection, current state or an effect from focus.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Acceptance:
- Reordering and inserting neighboring popup entries preserves the existing keyed control.
- Removing or disabling the focused identity invokes the declared per-surface fallback.

Source proposals: WL-ID-08, WLK-WGT-08, AM-11

## WARLOCK-DL-006 — Visible focus with theme and contrast support

When keyboard focus is visible, the surface shall display a focus treatment distinguishable from selection and hover with at least a 2 CSS pixel outer indicator and 3:1 adjacent-color contrast; forced-colors rendering shall retain it.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Acceptance:
- A two-tone 2px outer/1px inner ring is the initial catalog treatment; equivalent native treatment is separately qualified.
- Dark, light, forced colors and enlarged text are included in the rendered matrix.

Source proposals: WLK-WGT-04, AM-02, WL-ID-04

## WARLOCK-DL-007 — Accessible label, description and typed semantics

When a control is published, its accessible name shall begin with its normalized visible stable label, while transient detail and outcomes use description or state; toggle checked state shall derive from admitted observation.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Acceptance:
- A label-in-name validator reports the identity of any failing fixture.
- Menu toggles use typed checked semantics and do not infer current state from a future toggle action or display string.

Source proposals: WL-ID-09, WLK-WGT-07, AM-05, OPUS05-CAT-08

## WARLOCK-DL-008 — Explicit disabled-item policies per surface

Where a surface supports unavailable controls, the specification shall declare whether navigation focuses them, the rejection behavior, readable reason and fallback; unavailable controls shall never emit an effect intent.

Guardrail: ELM-ADOPT-030 remains authoritative. The consensus chooses focusable disabled menu items as a future guarded design target; it does not claim this behavior exists or globally change all surfaces.

Acceptance:
- The current source skip-disabled policy is labeled Source, not silently rewritten.
- The proposed menu focus-disabled policy is separately documented and gated on model, browser and native AT/keyboard qualification; other surfaces keep their declared policy.

Source proposals: AM-07, WLK-WGT-07

## WARLOCK-DL-009 — Complete popup keyboard and dismissal contract

While a qualified popup holds keyboard scope, Up/Down and Home/End shall follow its declared navigation policy; Escape shall dismiss by exact identity and restore eligible invoker focus or declared fallback without settling or replaying Pending or Unknown operations.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Acceptance:
- Menu wrap, Enter/Space and typeahead are documented with exact Msg mapping and source status.
- Dismissal retains outstanding intent and cleanup obligations; no keyboard event gains authority merely from a browser demo.

Source proposals: WLK-WGT-06, WLD-DESK-04, AM-06

## WARLOCK-DL-010 — Taskbar entry, navigation and exit through existing contracts

When taskbar keyboard interaction is qualified, its entry, arrow movement, popup invocation and exit shall follow the existing ELM-ADOPT-029 contract without introducing an unreviewed default global shortcut or altering activation history.

Guardrail: Existing native keyboard ownership and input identity gates are prerequisites. No automatic F6/global shortcut adoption.

Acceptance:
- Source, proposed and binding-unverified key rows are distinct.
- Toolbar role, roving focus and Down-to-picker are design targets until coherent native scope and recipient tests pass.

Source proposals: WLK-WGT-09, WLD-DESK-05, OPUS05-CAT-07

## WARLOCK-DL-011 — One announcement owner with honest feedback channels

When an allowlisted outcome needs an announcement, the designated route shall announce it once under the existing attention policy without moving focus; persistent blocking or unconfirmed conditions shall remain readable.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Acceptance:
- Repeated same-outcome publications do not re-announce; unrelated controls remain usable.
- Routine Committed window changes use the resulting visible state rather than unsolicited success toasts.

Source proposals: WLK-WGT-10, WLD-DESK-06, AM-09, AM-01

## WARLOCK-DL-012 — Plain status copy and safe reconciliation

When a status is presented, its catalog entry shall distinguish the condition and any safe next action without exposing unnecessary protocol jargon or fabricating a refusal reason; Unknown shall never offer automatic replay.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Acceptance:
- Existing strings are inventoried with source locations; proposed replacements remain reviewable entries.
- Reconcile refreshes native truth and does not resend the original Unknown action.

Source proposals: WLK-WGT-11, OPUS05-CAT-09, AM-01

## WARLOCK-DL-013 — Responsive type, density and target geometry

When density or text scale changes, surfaces shall preserve labels, accessible names, outcomes and focus indicators; catalog compact actionable targets shall be at least 24x24 CSS pixels, and a comfortable profile shall be available.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Acceptance:
- The catalog checks constrained width, text enlargement, long names and RTL.
- 24px is a catalog design choice, not a claim that every native handle or input device meets a new blanket threshold; native targets retain their frozen device/geometry contracts.

Source proposals: WL-ID-06, WLK-WGT-05

## WARLOCK-DL-014 — Live appearance with action-target continuity

When appearance or contrast preference changes, the controller shall publish applicable presentation preferences while preserving pending target and control identity and respecting actual native dependency-generation changes.

Guardrail: Do not forbid legitimate publication/lease or native rendering-generation changes; continuity preserves identity and authority rather than freezing revision numbers.

Acceptance:
- Changing theme cannot rebind a Pending intent or activate a control.
- Forced-colors uses system roles; native preference observation and in-flight adoption require real qualification.

Source proposals: WL-ID-04, WL-ID-05

## WARLOCK-DL-015 — Reduced motion and native presentation continuity

While reduced motion is active, the catalog shall run no decorative or velocity-continuation motion, and product motion shall convey equivalent state with instant or permitted opacity changes driven by native last-presented geometry.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Acceptance:
- The website starts still, pauses hidden decorative work and responds live to preference changes.
- Motion never delays input, extends a native deadline or settles an outcome; native timing stays under frozen S02/ELM-ADOPT-023/024.

Source proposals: WL-ID-10, AM-03, AM-04

## WARLOCK-DL-016 — Timers and composition never fabricate authority

When a prepared-choice deadline expires or composition is active, the interface shall preserve user context while invalidating expired authority and suppressing shortcut/typeahead interpretation during owned composition.

Guardrail: Original choice, transport and operation deadlines are unchanged. No expired choice stays actionable; original AT/IME qualification remains open.

Acceptance:
- Expired choices may remain visibly unavailable with a safe refresh path but cannot activate under the old grant or deadline.
- IME commits bind to native composition identity; browser IME behavior is not native qualification.

Source proposals: AM-08, AM-10

## WARLOCK-DL-017 — Publish exact taskbar activation decisions

When a taskbar group is activated, the controller shall derive its decision from the shipped Taskbar.primary call and present pending feedback for Apply decisions until correlated settlement.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Acceptance:
- The truth table records the shipped call Taskbar.primary False (TaskbarShell.elm and Surface.elm); zero-family and pinned-to-Launch rows are function-level Source and unreachable from shipped groups, while pinned launch remains a separate native contract.
- A decision or sent request is never labeled a confirmed native result.

Source proposals: WLD-DESK-01

## WARLOCK-DL-018 — Preview identity, eligibility and honest freshness

While a preview is displayed, its title/application and state shall remain understandable; Live shall retain its frozen PreviewLifecycle definition, and any stronger native-presented claim shall require the applicable native presentation evidence.

Guardrail: Preserve the frozen S09/ELM-ADOPT-028 Historical/Live/Unavailable meanings, authorized historical pixels and original preview13 oracles. A timestamp, browser canvas or unqualified root-plane capture does not prove native presentation.

Acceptance:
- Source Live preview, Historical preview, Preview loading and Preview unavailable and their fidelity text are documented under the frozen historical/live/unavailable policy and original S09 preview13. Existing authorized Historical display is neither removed nor relabeled.
- Current, Placeholder and Earlier frame are proposed catalog terms only. Any label rename or added Live evidence condition is gated on ELM-ADOPT-028 review; only new retention beyond the existing authorized, unexpired, privacy-matched lease is deferred. Existing expiry/lock revocation and native492 root-plane previewEligible:false remain unchanged.

Source proposals: WLK-WGT-12, WLD-DESK-02

## WARLOCK-DL-019 — Capability-driven window-actions content

When window actions are shown, unsupported actions shall be omitted and supported but currently unavailable actions shall have a reason, with checkable states derived from native observation.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Acceptance:
- The catalog documents all existing Menu.Action constructors, targets and outcome states.
- At most three groups is a content preference for the initial design, not permission to omit required actions or alter provider semantics.

Source proposals: WLD-DESK-03, WLK-WGT-07

## WARLOCK-DL-020 — Launcher search as a guarded extension

While a proposed launcher search is active, filtering shall remain local to admitted catalog entries and composition-safe; activation shall use the existing typed launch and correlated native outcome path.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Acceptance:
- Current source without search is documented accurately.
- Search never executes a command from free text or infers a launch outcome from process disappearance.

Source proposals: WLD-DESK-08

## WARLOCK-DL-021 — Host-owned workspaces and gated placement patterns

Where the catalog explains workspaces, snapping or tiling, it shall identify current host ownership and existing roadmap gates and shall not present an unsupported browser arrangement as implemented native placement.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Acceptance:
- Existing mandatory release requirements remain in scope; no design deferral removes them.
- Snap geometry is a native proposal and an applied layout requires correlated authority; no default maximize-hover flyout is added by this catalog.

Source proposals: WLD-DESK-09, WLD-DESK-10

## WARLOCK-DL-022 — Settings declare behavioral guarantees

When a setting is designed, its documentation shall state the behavior changed, defaults, keyboard/accessibility behavior, privacy/ownership implications and guarantees preserved.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Acceptance:
- Settings illustrations are Proposed until integrated.
- A setting cannot silently retarget a pending action or bypass bounded admission/recovery.

Source proposals: WLD-DESK-11

## WARLOCK-DL-023 — Source-derived complete widget registry

When the catalog builds, it shall compare a versioned source inventory for the selected coherent GUI closure against the widget registry and fail on an uncovered rendered surface, role, mode, action or outcome constructor.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Acceptance:
- The full Elm source, stylesheet and bridge closure supplement replaces inference from the initial ten-module subset.
- Removing a current menu action or preview state from coverage fails with its source identity; other integration lanes are explicitly tracked rather than asserted integrated.

Source proposals: WLK-WGT-01, OPUS05-CAT-01, WL-ID-11

## WARLOCK-DL-024 — Read-mode website with consistent component sections

The catalog shall provide Overview, Foundations, Components, Patterns, Accessibility, Tokens, Evidence and Changelog navigation, and every component shall expose Overview, Anatomy & states, Behavior & keyboard, Accessibility, Content and Evidence sections.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Acceptance:
- Search, deep links, theme choice and responsive navigation work with keyboard.
- Unknown or absent information is marked Not yet specified rather than implied to exist; long pages may use linked headings instead of mandatory tab widgets.

Source proposals: OPUS05-CAT-02, WL-ID-11

## WARLOCK-DL-025 — Claim-specific status and evidence records

When a behavioral claim is displayed, the catalog shall separate Proposed/Implemented status from scoped evidence records and shall require a frozen receipt, scenario identity and owning ABI tuple for any Native-qualified label.

Guardrail: Evidence levels are distinct scopes, not a universal confidence ladder. Multiple records are allowed; the prominent badge names the scope of the exact claim.

Acceptance:
- A claim may link Source and Browser-demo records with distinct scopes; neither implies CPU or native acceptance.
- Demo interaction cannot change recorded evidence or acceptance badges.

Source proposals: OPUS05-CAT-03, WLD-DESK-12, AM-12

## WARLOCK-DL-026 — Real Elm demonstrations with explicit fixture authority

When a demo claims Elm behavior, it shall run the relevant shipped Elm decoder/view/update or decision function through an isolated typed wrapper; any native outcome shall be supplied only through a clearly labeled simulated-authority panel.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Acceptance:
- Pending and Unknown examples remain unchanged until explicit reader settlement; Unknown cannot be automatically retried.
- Static visual specimens may use semantic CSS but are labeled style specimens and cannot implement a competing desktop policy in JavaScript.

Source proposals: WL-ID-12, OPUS05-CAT-06

## WARLOCK-DL-027 — Content and accessible semantics inventory

When the catalog builds, it shall inventory source labels/status text, show wording and semantic findings with source locations, and keep proposed fixes separate from the original source.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Acceptance:
- Sentence case, stable labels, toggle roles and announcement duplication have reviewable findings.
- Source strings are never silently rewritten inside the frozen input packet.

Source proposals: OPUS05-CAT-08, OPUS05-CAT-09

## WARLOCK-DL-028 — Responsive, accessible and offline-capable catalog

When the catalog is viewed at constrained width or enlarged zoom, content shall reflow without two-dimensional scrolling except explicitly labeled fixed-size specimen canvases or data tables; core content, fonts and demos shall work from bundled local assets.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Acceptance:
- 320 CSS pixel viewport, desktop, text enlargement, focus, reduced motion and forced colors are exercised.
- No external CDN or native control socket is necessary to read or exercise the catalog; network references are links.

Source proposals: OPUS05-CAT-10, AM-02

## WARLOCK-DL-029 — Versioned assets, coverage and bounded finish review

When a covered source or token changes, its manifest hash and changelog shall be reconciled before publication; the catalog shall retain asset/source licenses and actual generated-art provenance and receive bounded independent finish review.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Acceptance:
- Failing source hash/coverage tests name the drift.
- One batched desktop/mobile inspection and at most one correction inspection are planned; unavailable visual evidence stays explicitly unverified.

Source proposals: OPUS05-CAT-11, OPUS05-CAT-01

## WARLOCK-DL-030 — Reference adoption matrix with original visual identity

The design language shall publish borrow/adapt/reject/defer decisions for Material Design, Impeccable, Apple Human Interface Guidelines (iOS design language, with supplemental macOS desktop guidance), Plasma/KDE, Windows/Fluent and GNOME, with primary-source links and explicit Warlock rationale.

Guardrail: Existing release contracts, deadlines, authority, ownership and native qualification remain mandatory.

Acceptance:
- Borrow token/component documentation, readable craft, continuity, desktop conventions and approachable defaults where compatible.
- Reject platform logos/themes and unmeasured glass, blur, ripples or animation costs; inaccessible or snippet-only sources do not establish binding numeric values.

Source proposals: OPUS05-CAT-12, WL-ID-01

