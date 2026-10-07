# elm-shell-experience — design adoption draft

## Purpose

Draft refinements for the existing in-flight `elm-shell-experience` capability. This change contains ADDED research contracts only; it does not create or archive a main spec, replace existing pivot/right-click deltas, or establish release acceptance.

Consensus research drafts ready for internal specification integration and implementation. A reviewed baseline amendment remains a separate integration step. These artifacts do not change the canonical 242 requirements/417 scenarios, S01–S16, right-click24, original13 native preview cases, restore38/recovery34/drag-resize52 or original deadlines. Native authority and no automatic replay of Unknown remain mandatory. C00–C06 compositor replacement remains conditional.

No new native, hardware, IME, AT or full-release evidence is supplied by this packet. Frozen component/model/CPU/compiled replay evidence is not production-provider or full GUI ownership/drain/fidelity acceptance. GUI814 and toolkit391 retain separate owning ABI pairs. Implementation and qualification tasks remain unchecked.

## ADDED Requirements

### Requirement: ELM-ADOPT-011 — preserve uncertainty in a structured reporting contract

WHEN an operation report is presented, the shell SHALL derive its message and available recovery actions from a validated correlated outcome and SHALL distinguish definitive refusal from Unknown without implying completion or authorizing replay.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: 1.

Baseline mapping: ELM-ARC-007, ELM-ARC-008, ELM-ARC-014.

Existing work mapping: W04, W11.

Source proposals: ERR-01, OPUS03-ER-01.

Owner: Desktop experience lead. Verifier: Independent acceptance reviewer.

Guardrails: Stable bounded outcome/reason catalog and actionable, reviewed text from a catalog that supports localization. Unknown remains perceivable. Unknown reason within a validated Refused class may use generic refusal text; unknown schema/outcome cannot fabricate Refused. Supporting localization does not add a translation release gate.

Tradeoffs: status-only messages are cheaper but obscure safe recovery; raw native messages reduce mapping work but leak details and blur semantics. Cost: category registry, compatibility review and differential fixtures. Validation: enumerate every existing outcome/recovery reason; every class has reviewed text and enabled-action oracle; corrupt or future reasons fail closed without fabricating a terminal outcome.

Primary sources:

- <http://www.bitsavers.org/pdf/xerox/parc/techReports/CSL-83-7_Implementing_Remote_Procedure_Calls.pdf>
- <https://docs.gtk.org/glib/logging.html>
- <https://docs.rs/thiserror/latest/thiserror/>
- <https://docs.sentry.io/platforms/python/data-management/sensitive-data/>
- <https://google.aip.dev/193>
- <https://opentelemetry.io/docs/specs/semconv/attributes-registry/error/>
- <https://raw.githubusercontent.com/grpc/grpc/master/doc/statuscodes.md>
- <https://raw.githubusercontent.com/mozilla/gecko-dev/master/toolkit/crashreporter/CrashAnnotations.yaml>
- <https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.journal-fields.xml>
- <https://systemd.io/CATALOG/>
- <https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/sosp153-glerum-web.pdf>
- <https://www.microsoft.com/en-us/research/wp-content/uploads/2019/01/Guidelines-for-Human-AI-Interaction-camera-ready.pdf>
- <https://www.nngroup.com/articles/ten-usability-heuristics/>
- <https://www.usenix.org/events/hotos03/tech/full_papers/candea/candea.pdf>
- <https://www.w3.org/TR/wai-aria-1.2/>
- <https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html>

#### Scenario: ELM-ADOPT-011 ERR-01-01

- **GIVEN** an admitted restore with lost receipt
- **WHEN** transport disconnects
- **THEN** the report states that completion is unconfirmed, preserves Unknown and offers no automatic repeat.

#### Scenario: ELM-ADOPT-011 ERR-01-02

- **GIVEN** an exact unsent certificate and a simultaneous late receipt for a different request
- **WHEN** reports are reduced
- **THEN** refusal is attached only to the certified request and the foreign receipt cannot alter its message or actions.

### Requirement: ELM-ADOPT-016 — Preserve control identity across publication and focus changes

WHILE a shell focus scope is open, the host SHALL preserve an eligible focused control through unrelated publications and dispatch admitted keyboard or assistive activation only to that native AT-exposed identity, rejecting retired or changed-scope targets and applying the frozen fallback when focus becomes ineligible.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P0.

Baseline mapping: ELM-UI-011, ELM-UX-023, ELM-UX-024.

Existing work mapping: W07.

Source proposals: SOL04-01, UXA-01.

Owner: Desktop experience lead. Verifier: Independent acceptance reviewer.

Guardrails: Publication, lease and incarnation captured at press remain authoritative at release. Preserve the surviving focused identity while eligible under the frozen per-surface policy; disabled-but-focusable controls remain focused when030 allows it, otherwise apply the declared fallback. Selection is distinct from focus. Keyed DOM is an implementation choice.

Tradeoffs: Identity propagation and native focus evidence; preserve identity rather than index or automatic selected-row refocus.

Primary sources:

- <https://arxiv.org/html/2609.17959>
- <https://developer.gnome.org/hig/guidelines/keyboard.html>
- <https://doc.qt.io/qt-6/qstyle.html>
- <https://docs.gtk.org/gtk4/method.Accessible.announce.html>
- <https://grouplab.cpsc.ucalgary.ca/grouplab/uploads/Publications/Publications/2007-PredictiveModelMenus.CHI.pdf>
- <https://help.gnome.org/users/gnome-help/stable/keyboard-nav.html.en>
- <https://learn.microsoft.com/en-us/windows/apps/develop/input/keyboard-interactions>
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

#### Scenario: ELM-ADOPT-016 SOL04-01-scenario-1

- **GIVEN** Close is focused while another row is selected
- **WHEN** an unrelated catalog publication arrives
- **THEN** Close keeps focus and the next activation invokes only Close

#### Scenario: ELM-ADOPT-016 SOL04-01-scenario-2

- **GIVEN** an activation press belongs to a window incarnation and lease
- **WHEN** that incarnation retires and the row position is reused before release
- **THEN** release dispatches no replacement action and eligible fallback remains reachable

#### Scenario: ELM-ADOPT-016 focus-without-publication

- **GIVEN** Close has keyboard/native AT focus while another row is selected
- **WHEN** Enter or Space is admitted without an intervening publication
- **THEN** only Close is invoked, no window intent is dispatched and selection cannot override focused identity

### Requirement: ELM-ADOPT-020 — Make action discovery agree with acknowledged outcomes

WHEN a shell action is unavailable or unresolved, the shell SHALL expose the correlated reason and safe next step, retain eligible focus and controls outside its dependency domain, and never queue, defer or automatically replay input not accepted in that state or a rejected or Unknown action.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P1.

Baseline mapping: ELM-UI-005, ELM-UI-007, ELM-UI-015, ELM-UI-020.

Existing work mapping: W07, W08, W01, W02.

Source proposals: SOL04-05, FI-03.

Owner: Desktop experience lead. Verifier: Independent acceptance reviewer.

Guardrails: Unrelated refresh means an unchanged declared family/target dependency domain and must preserve a valid picker/focus. Do not require concurrent native transactions. Repeated input during Pending follows INTERACTION.md feedback policy and ELM-UI-015; no second intent or announcement storm.

Tradeoffs: Shared vocabulary must follow native outcomes; no optimistic success or Unknown replay.

Primary sources:

- <http://direction.bordeaux.inria.fr/~roussel/publications/2015-UIST-mouse-based-lagmeter.pdf>
- <https://docs.gtk.org/gdk3/class.FrameClock.html>
- <https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html>
- <https://gitlab.freedesktop.org/wayland/wayland-protocols/-/blob/main/stable/presentation-time/presentation-time.xml>
- <https://idl.cs.washington.edu/files/2007-AnimatedTransitions-InfoVis.pdf>
- <https://raw.githubusercontent.com/KDE/kirigami/master/src/controls/Action.qml>
- <https://raw.githubusercontent.com/hyprwm/hyprutils/main/include/hyprutils/animation/AnimatedVariable.hpp>
- <https://webkitgtk.org/2026/09/16/webkitgtk-2.54-highlights.html>
- <https://www.cs.umd.edu/users/ben/papers/Shneiderman1983Direct.pdf>
- <https://www.cs.umd.edu/~ben/papers/Shneiderman1983Direct.pdf>

#### Scenario: ELM-ADOPT-020 SOL04-05-scenario-1

- **GIVEN** a minimized generic application family is selected
- **WHEN** activation is refused natively
- **THEN** it is not shown as restored, the reason and next action are reachable, and its preserved identity remains selected

#### Scenario: ELM-ADOPT-020 SOL04-05-scenario-2

- **GIVEN** an operation has Unknown disposition and guidance was dismissed
- **WHEN** the user opens help or recovery with the keyboard
- **THEN** guidance is available without resetting the desktop and reconciliation creates no automatic repeated mutation

#### Scenario: ELM-ADOPT-020 unrelated-observation-refresh

- **GIVEN** a picker is open for a family
- **WHEN** an unrelated observation refresh completes with that family's dependency revision unchanged
- **THEN** picker identity and focus persist and no new intent is emitted

#### Scenario: ELM-ADOPT-020 same-control-during-pending

- **GIVEN** a native operation is Pending for a control
- **WHEN** the same control is activated again
- **THEN** no second intent is emitted; one truthful not-accepted result is exposed under the frozen feedback policy without repeated announcement or later replay

### Requirement: ELM-ADOPT-029 — Native keyboard entry and exit for the taskbar

WHEN the declared taskbar-focus binding is admitted, the native host SHALL enter a bounded keyboard scope on the current output and retain the prior eligible application identity for the frozen exit/fallback policy, keeping the binding inert while locked.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: existing-phase-P5; early-feasibility-only.

Baseline mapping: ELM-UX-023, ELM-UX-024, ELM-UI-011, ELM-UI-019.

Existing work mapping: W07.

Source proposals: UXA-02.

Owner: Desktop experience lead. Verifier: Independent acceptance reviewer.

Guardrails: This is native keyboard scope qualification, not a mandated permanent EXCLUSIVE mode or a new default shortcut. Declare which history changes are focus-only versus real accepted activation; do not override existing MRU policy.

Tradeoffs: Additional protocol/evidence complexity must meet the frozen workload/resource budget. Reuse current modules and incrementally qualify changed paths.

Ordering gate: preserve existing P5 keyboard qualification. Earlier feasibility investigation does not promote implementation into the immediate W07/P0 lane.

Primary sources:

- <https://arxiv.org/html/2609.17959>
- <https://developer.gnome.org/hig/guidelines/keyboard.html>
- <https://doc.qt.io/qt-6/qstyle.html>
- <https://docs.gtk.org/gtk4/method.Accessible.announce.html>
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

#### Scenario: ELM-ADOPT-029 enter-and-escape

- **GIVEN** an eligible application has focus and the taskbar is idle
- **WHEN** the declared conflict-resolved taskbar focus binding is invoked and then Escape ends the scope
- **THEN** native keyboard and AT focus enter the bar and return under the frozen policy, with no unintended activation-history change

#### Scenario: ELM-ADOPT-029 retired-source-output-or-lock

- **GIVEN** a bar keyboard scope whose prior application or output retires
- **WHEN** the scope exits or the session locks
- **THEN** no replacement incarnation or removed output receives stale focus; the frozen eligible fallback/lock policy applies and idle bar does not intercept application input

### Requirement: ELM-ADOPT-030 — Versioned disabled-action navigation policy

WHEN a supported shell action becomes disabled, the shell SHALL retain its declared position, expose disabled state and any reason required by the frozen per-surface policy, and follow that navigation policy without dispatching it through pointer, keyboard or accessibility activation.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P1.

Baseline mapping: ELM-UI-011, ELM-UX-024, ELM-UX-025.

Existing work mapping: W07, W08.

Source proposals: UXA-05.

Owner: Desktop experience lead. Verifier: Independent acceptance reviewer.

Guardrails: GTK and Windows/APG differ. Freeze the chosen per-surface policy; no universal requirement to focus every disabled control. Preserve existing right-click24 amendment and unsupported-action semantics.

Tradeoffs: Additional protocol/evidence complexity must meet the frozen workload/resource budget. Reuse current modules and incrementally qualify changed paths.

Primary sources:

- <https://arxiv.org/html/2609.17959>
- <https://developer.gnome.org/hig/guidelines/keyboard.html>
- <https://doc.qt.io/qt-6/qstyle.html>
- <https://docs.gtk.org/gtk4/method.Accessible.announce.html>
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

#### Scenario: ELM-ADOPT-030 supported-disabled-action

- **GIVEN** a state change disables a supported menu action
- **WHEN** the user navigates with the declared per-surface policy
- **THEN** the action position remains stable, native AT exposes unavailable state and any reason required by the frozen per-surface policy, and attempted activation dispatches no effect

#### Scenario: ELM-ADOPT-030 all-disabled-and-focus-retirement

- **GIVEN** all menu actions are disabled or the focused action becomes disabled
- **WHEN** navigation, Enter/Space or Escape occurs
- **THEN** the frozen policy keeps focus and dismissal reachable without invoking a disabled action or trapping focus
