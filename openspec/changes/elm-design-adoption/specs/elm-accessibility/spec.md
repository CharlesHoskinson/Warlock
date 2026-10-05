# elm-accessibility — design adoption draft

## Purpose

Draft refinements for the existing in-flight `elm-accessibility` capability. This change contains ADDED research contracts only; it does not create or archive a main spec, replace existing pivot/right-click deltas, or establish release acceptance.

Consensus research drafts ready for internal specification integration and implementation. A reviewed baseline amendment remains a separate integration step. These artifacts do not change the canonical 242 requirements/417 scenarios, S01–S16, right-click24, original13 native preview cases, restore38/recovery34/drag-resize52 or original deadlines. Native authority and no automatic replay of Unknown remain mandatory. C00–C06 compositor replacement remains conditional.

No new native, hardware, IME, AT or full-release evidence is supplied by this packet. Frozen component/model/CPU/compiled replay evidence is not production-provider or full GUI ownership/drain/fidelity acceptance. GUI814 and toolkit391 retain separate owning ABI pairs. Implementation and qualification tasks remain unchecked.

## ADDED Requirements

### Requirement: ELM-ADOPT-012 — one announcement owner and outcome-aware deduplication

WHEN an eligible correlated outcome transition requires attention, the controller SHALL publish one accessible status through the designated announcement owner, retain focus and suppress repeats of that outcome while preserving later distinct outcome transitions.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: duplicate. Priority: 1.

Baseline mapping: ELM-UI-009, ELM-UI-010.

Existing work mapping: W08.

Source proposals: ERR-02, OPUS03-ER-02, UXA-04.

Owner: Accessibility lead. Verifier: Independent acceptance reviewer.

Guardrails: One announcement owner; deduplicate repeated outcomes, not distinct later state changes. Native speech/braille/focus transcript required; ARIA alone is insufficient. The semantic owner is the controller; delivery must reach a qualified AT-active document or declared native/fallback route, including when application focus remains outside shell.

Tradeoffs: per-view live regions are simple locally but duplicate output on multiple surfaces; one modal per failure interferes with focus and ordinary work. Cost: semantic routing, native AT integration and multi-output transcript qualification. Validation: count announcements against distinct eligible transitions, observe focus and speech/braille, include duplicate receipts and surface recreation. Preserve existing policy thresholds; freeze any missing quantitative oracle through S02/P0 rather than inventing one.

Primary sources:

- <http://www.bitsavers.org/pdf/xerox/parc/techReports/CSL-83-7_Implementing_Remote_Procedure_Calls.pdf>
- <https://arxiv.org/html/2609.17959>
- <https://developer.gnome.org/hig/guidelines/keyboard.html>
- <https://doc.qt.io/qt-6/qstyle.html>
- <https://docs.gtk.org/glib/logging.html>
- <https://docs.gtk.org/gtk4/method.Accessible.announce.html>
- <https://docs.sentry.io/platforms/python/data-management/sensitive-data/>
- <https://google.aip.dev/193>
- <https://grouplab.cpsc.ucalgary.ca/grouplab/uploads/Publications/Publications/2007-PredictiveModelMenus.CHI.pdf>
- <https://help.gnome.org/users/gnome-help/stable/keyboard-nav.html.en>
- <https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-automation-element-propids>
- <https://opentelemetry.io/docs/specs/semconv/attributes-registry/error/>
- <https://raw.githubusercontent.com/GNOME/gnome-shell/main/js/ui/ctrlAltTab.js>
- <https://raw.githubusercontent.com/GNOME/gtk/gtk-3-24/gtk/gtkmenuitem.c>
- <https://raw.githubusercontent.com/GNOME/orca/main/src/orca/live_region_presenter.py>
- <https://raw.githubusercontent.com/KDE/plasma-desktop/master/applets/taskmanager/qml/Task.qml>
- <https://raw.githubusercontent.com/grpc/grpc/master/doc/statuscodes.md>
- <https://raw.githubusercontent.com/mozilla/gecko-dev/master/toolkit/crashreporter/CrashAnnotations.yaml>
- <https://raw.githubusercontent.com/qt/qtbase/dev/src/widgets/styles/qwindowsstyle.cpp>
- <https://raw.githubusercontent.com/swaywm/wlr-protocols/master/unstable/wlr-layer-shell-unstable-v1.xml>
- <https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.journal-fields.xml>
- <https://raw.githubusercontent.com/wmww/gtk-layer-shell/master/include/gtk-layer-shell.h>
- <https://sre.google/sre-book/monitoring-distributed-systems/>
- <https://support.microsoft.com/en-us/windows/keyboard-shortcuts-in-windows-dcc61a57-8ff0-cffe-9796-cb9706c75eec>
- <https://systemd.io/CATALOG/>
- <https://wayland.app/protocols/text-input-unstable-v3>
- <https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/sosp153-glerum-web.pdf>
- <https://www.nngroup.com/articles/ten-usability-heuristics/>
- <https://www.usenix.org/events/hotos03/tech/full_papers/candea/candea.pdf>
- <https://www.w3.org/TR/uievents/>
- <https://www.w3.org/TR/wai-aria-1.2/>
- <https://www.w3.org/WAI/ARIA/apg/patterns/menubar/>
- <https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/>
- <https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html>

#### Scenario: ELM-ADOPT-012 ERR-02-01

- **GIVEN** bar and popup projections on two outputs with stable focus
- **WHEN** the same refusal receipt is delivered repeatedly and a popup recreates
- **THEN** one eligible announcement occurs and recovery detail remains reachable.

#### Scenario: ELM-ADOPT-012 ERR-02-02

- **GIVEN** Unknown was announced and the original deadline has elapsed
- **WHEN** a valid late correlated receipt settles knowledge
- **THEN** a distinct policy-eligible update is exposed without restarting the effect or changing its deadline; unauthenticated, unrelated or unauthorized receipts cause no update, while exact authenticated historical evidence may reconcile retained Unknown through the declared recovery route

### Requirement: ELM-ADOPT-017 — Treat native semantics and announcements as a coherent projection

WHEN a shell projection changes, the shell SHALL expose coherent native names, roles, states, relationships and actions for the current control identities, keeping preview imagery inert and keyboard focus distinct from selection.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P0.

Baseline mapping: ELM-UI-009, ELM-UI-010, ELM-UX-025, ELM-UX-026.

Existing work mapping: W08, W07, W06.

Source proposals: SOL04-02, UXA-03.

Owner: Accessibility lead. Verifier: Independent acceptance reviewer.

Guardrails: Control semantics plus actual native bridge required. Announcement ownership is separately ELM-ADOPT-012; multiple read-only status regions do not establish a single AT announcement. Keep the visible stable control label as the accessible name; expose transient state and action descriptions separately, within the frozen per-control naming policy. Verify cross-surface relationships in the native AT tree; DOM-local relationships do not automatically cross WebView documents.

Tradeoffs: One outcome owner requires lifecycle correlation and native speech/braille inspection; API availability differs by ABI.

Primary sources:

- <https://arxiv.org/html/2609.17959>
- <https://developer.gnome.org/hig/guidelines/keyboard.html>
- <https://doc.qt.io/qt-6/qstyle.html>
- <https://docs.gtk.org/gtk4/method.Accessible.announce.html>
- <https://gnome.pages.gitlab.gnome.org/orca/help/howto_forms.html>
- <https://grouplab.cpsc.ucalgary.ca/grouplab/uploads/Publications/Publications/2007-PredictiveModelMenus.CHI.pdf>
- <https://help.gnome.org/users/gnome-help/stable/keyboard-nav.html.en>
- <https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-automation-element-propids>
- <https://raw.githubusercontent.com/GNOME/gnome-shell/main/js/ui/ctrlAltTab.js>
- <https://raw.githubusercontent.com/GNOME/gtk/gtk-3-24/gtk/gtkmenuitem.c>
- <https://raw.githubusercontent.com/GNOME/orca/main/src/orca/live_region_presenter.py>
- <https://raw.githubusercontent.com/KDE/plasma-desktop/master/applets/taskmanager/qml/Task.qml>
- <https://raw.githubusercontent.com/qt/qtbase/dev/src/widgets/styles/qwindowsstyle.cpp>
- <https://raw.githubusercontent.com/swaywm/wlr-protocols/master/unstable/wlr-layer-shell-unstable-v1.xml>
- <https://raw.githubusercontent.com/wmww/gtk-layer-shell/master/include/gtk-layer-shell.h>
- <https://support.microsoft.com/en-us/windows/keyboard-shortcuts-in-windows-dcc61a57-8ff0-cffe-9796-cb9706c75eec>
- <https://wayland.app/protocols/text-input-unstable-v3>
- <https://www.w3.org/TR/uievents/>
- <https://www.w3.org/WAI/ARIA/apg/patterns/menubar/>
- <https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/>

#### Scenario: ELM-ADOPT-017 SOL04-02-scenario-1

- **GIVEN** bar and popup show the same pending operation
- **WHEN** the matching refusal arrives twice
- **THEN** both projections expose the same refusal state for the same control identity and focus remains on the user's control; announcement count follows ELM-ADOPT-012

#### Scenario: ELM-ADOPT-017 SOL04-02-scenario-2

- **GIVEN** a preview image has retired while its restore control survives
- **WHEN** AT explores the control
- **THEN** source state and supported action are available without an actionable image object or stale-incarnation activation

#### Scenario: ELM-ADOPT-017 stable-name-state-change

- **GIVEN** a single-window group whose visible identity label is unchanged becomes active or pending
- **WHEN** native AT re-reads the control
- **THEN** the accessible name remains aligned with the same visible label while state/description changes under the frozen naming policy

### Requirement: ELM-ADOPT-018 — Qualify composition as native field ownership

WHILE an input method owns a shell field composition, the host SHALL preserve native preedit and candidate interaction, suppress shell handling of consumed keys, and accept commits only for the current field identity and composition generation.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: duplicate. Priority: P0.

Baseline mapping: ELM-UI-012, ELM-UX-028.

Existing work mapping: W07.

Source proposals: SOL04-03, UXA-06.

Owner: Accessibility lead. Verifier: Independent acceptance reviewer.

Guardrails: Native field/composition epoch binds commits; consumed keys cannot trigger shell shortcuts. Native candidate/preedit and actual input target evidence required.

Tradeoffs: Native IME campaigns are costly; toolkit API examples cannot be transplanted across host lanes.

Primary sources:

- <https://arxiv.org/html/2609.17959>
- <https://developer.gnome.org/hig/guidelines/keyboard.html>
- <https://doc.qt.io/qt-6/qstyle.html>
- <https://docs.gtk.org/gtk4/method.Accessible.announce.html>
- <https://docs.gtk.org/gtk4/method.IMContext.filter_keypress.html>
- <https://gnome.pages.gitlab.gnome.org/orca/help/howto_forms.html>
- <https://grouplab.cpsc.ucalgary.ca/grouplab/uploads/Publications/Publications/2007-PredictiveModelMenus.CHI.pdf>
- <https://help.gnome.org/users/gnome-help/stable/keyboard-nav.html.en>
- <https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-automation-element-propids>
- <https://raw.githubusercontent.com/GNOME/gnome-shell/main/js/ui/ctrlAltTab.js>
- <https://raw.githubusercontent.com/GNOME/gtk/gtk-3-24/gtk/gtkmenuitem.c>
- <https://raw.githubusercontent.com/GNOME/gtk/main/gtk/gtkimcontext.h>
- <https://raw.githubusercontent.com/GNOME/orca/main/src/orca/live_region_presenter.py>
- <https://raw.githubusercontent.com/KDE/plasma-desktop/master/applets/taskmanager/qml/Task.qml>
- <https://raw.githubusercontent.com/qt/qtbase/dev/src/widgets/styles/qwindowsstyle.cpp>
- <https://raw.githubusercontent.com/swaywm/wlr-protocols/master/unstable/wlr-layer-shell-unstable-v1.xml>
- <https://raw.githubusercontent.com/wmww/gtk-layer-shell/master/include/gtk-layer-shell.h>
- <https://support.microsoft.com/en-us/windows/keyboard-shortcuts-in-windows-dcc61a57-8ff0-cffe-9796-cb9706c75eec>
- <https://wayland.app/protocols/text-input-unstable-v3>
- <https://www.w3.org/TR/uievents/>
- <https://www.w3.org/WAI/ARIA/apg/patterns/menubar/>
- <https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/>

#### Scenario: ELM-ADOPT-018 SOL04-03-scenario-1

- **GIVEN** a launcher field has active preedit
- **WHEN** the input method consumes Enter to commit text
- **THEN** the query receives the commit once and no launch occurs from that consumed key

#### Scenario: ELM-ADOPT-018 SOL04-03-scenario-2

- **GIVEN** composition belongs to a retired field generation
- **WHEN** its delayed commit arrives after a new field takes focus
- **THEN** neither field nor shell action receives the stale commit

### Requirement: ELM-ADOPT-019 — Preserve hierarchy and reachability under constrained geometry

WHEN output geometry, text scale or label length changes, the shell SHALL preserve readable control names, visible focus, non-color state cues and keyboard-reachable actions using the frozen contrast, geometry and reflow policy.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P1.

Baseline mapping: ELM-UI-013, ELM-UX-027, ELM-UI-019.

Existing work mapping: W08.

Source proposals: SOL04-04.

Owner: Accessibility lead. Verifier: Independent acceptance reviewer.

Guardrails: Freeze measurable contrast/target/text/reflow budgets and test constrained outputs, long labels, scaling and non-color cues. Do not assume CSS tokens or screenshots establish native reachability.

Tradeoffs: Layout choices need measured geometry and AT bounds; freeze thresholds before qualification.

Primary sources:

- <https://faculty.washington.edu/wobbrock/pubs/taccess-11.pdf>
- <https://raw.githubusercontent.com/KDE/kirigami/master/src/controls/Action.qml>
- <https://learn.microsoft.com/en-us/windows/apps/develop/input/keyboard-interactions>

#### Scenario: ELM-ADOPT-019 SOL04-04-scenario-1

- **GIVEN** enlarged text and long localized labels on a small output
- **WHEN** the picker opens
- **THEN** every action remains reachable and focused labels are legible according to the frozen oracle

#### Scenario: ELM-ADOPT-019 SOL04-04-scenario-2

- **GIVEN** a popup owns focus on a removed output
- **WHEN** surviving-output recovery runs
- **THEN** its declared fallback or rehosted scope is reachable and removed-generation input cannot activate controls
