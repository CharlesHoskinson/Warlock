# elm-capture-motion — design adoption draft

## Purpose

Draft refinements for the existing in-flight `elm-capture-motion` capability. This change contains ADDED research contracts only; it does not create or archive a main spec, replace existing pivot/right-click deltas, or establish release acceptance.

Provisional research drafts awaiting ratification and a separate reviewed baseline amendment. These artifacts do not change the canonical 242 requirements/417 scenarios, S01–S16, right-click24, original13 native preview cases, restore38/recovery34/drag-resize52 or original deadlines. Native authority and no automatic replay of Unknown remain mandatory. C00–C06 compositor replacement remains conditional.

No new native, hardware, IME, AT or full-release evidence is supplied by this packet. Frozen component/model/CPU/compiled replay evidence is not production-provider or full GUI ownership/drain/fidelity acceptance. GUI814 and toolkit391 retain separate owning ABI pairs. Implementation and qualification tasks remain unchecked.

## ADDED Requirements

### Requirement: ELM-ADOPT-023 — Reversal and live reduced motion share native semantics

WHEN motion is interrupted or the reduced-motion preference changes, the native renderer SHALL derive the successor from the last-presented geometry and preserve the same identity, cancellation, commitment and retirement rules under the approved motion profile.

Status: draft-refinement-awaiting-ratification. Classification: draft-refinement; original research classification: refinement. Priority: P1.

Baseline mapping: ELM-REN-010, ELM-REN-011, ELM-UI-014, ELM-UX-022.

Existing work mapping: W12, P4-ELM-REN-010, P4-ELM-REN-011, P4-ELM-UI-014.

Source proposals: SOL-FLUID-04, FI-06.

Owner: Graphics lead. Verifier: Independent acceptance reviewer.

Guardrails: Native last-presented geometry/velocity and approved reversal profile. Reduced motion is a live native preference, with no velocity continuation/decorative motion under the selected reduced profile. Presentation timestamps, original38/34/52 cases remain required.

Tradeoffs: ['Geometry and velocity continuity need native samples, not model time', 'The exact preference-switch policy must be frozen before qualification']

Primary sources:

- <http://direction.bordeaux.inria.fr/~roussel/publications/2015-UIST-mouse-based-lagmeter.pdf>
- <https://docs.gtk.org/gdk3/class.FrameClock.html>
- <https://docs.gtk.org/gdk4/class.FrameClock.html>
- <https://docs.gtk.org/gtk4/property.Settings.gtk-enable-animations.html>
- <https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html>
- <https://gitlab.freedesktop.org/wayland/wayland-protocols/-/blob/main/stable/presentation-time/presentation-time.xml>
- <https://idl.cs.washington.edu/files/2007-AnimatedTransitions-InfoVis.pdf>
- <https://raw.githubusercontent.com/hyprwm/hyprutils/main/include/hyprutils/animation/AnimatedVariable.hpp>
- <https://raw.githubusercontent.com/wayland-mirror/wayland-protocols/main/stable/presentation-time/presentation-time.xml>
- <https://webkitgtk.org/2026/09/16/webkitgtk-2.54-highlights.html>
- <https://www.cs.umd.edu/users/ben/papers/Shneiderman1983Direct.pdf>
- <https://www.tactuallabs.com/papers/designingLowLatencyDirectTouchInputUIST12.pdf>
- <https://www.yorku.ca/mack/p488-mackenzie.pdf>

#### Scenario: Reverse after an unpresented sample

- **GIVEN** a restore has a queued sample newer than its last native presentation
- **WHEN** a minimize intent reverses it
- **THEN** the successor starts from last-presented geometry under the native continuity rule and retires only the superseded generation

#### Scenario: Preference changes during capture

- **GIVEN** a restore is awaiting a retained frame
- **WHEN** reduced motion becomes enabled before its matching frame arrives
- **THEN** the approved reduced-motion route uses identical commit and cancellation obligations without replaying the effect or resetting its deadline

### Requirement: ELM-ADOPT-027 — Persistent demand converges to latest authorized source content

WHILE authorized preview demand persists, WHEN tracked source content advances during outstanding capture, the provider SHALL retain bounded latest-revision demand and service it under the frozen pacing policy after eligible capacity returns, admitting none after closure or revocation.

Status: draft-refinement-awaiting-ratification. Classification: draft-refinement; original research classification: refinement. Priority: P1.

Baseline mapping: ELM-ARC-015, ELM-REN-012, ELM-UI-017, ELM-TEA-004.

Existing work mapping: W03, W06.

Source proposals: FI-04.

Owner: Graphics lead. Verifier: Independent acceptance reviewer.

Guardrails: No forced allocation while backpressured/exhausted. Follow-up is a genuine new native-scoped request with its own original issued clock, not renewal of expired work. Control/retirement events are lossless. Pacing/refresh is frozen in the existing budget matrix before qualification; continuous change cannot create unbounded back-to-back capture. Latest revision is limited to native-tracked coverage, currently root-surface commits only; no subsurface/family fidelity expansion.

Tradeoffs: Additional protocol/evidence complexity must meet the frozen workload/resource budget. Reuse current modules and incrementally qualify changed paths.

Primary sources:

- <http://direction.bordeaux.inria.fr/~roussel/publications/2015-UIST-mouse-based-lagmeter.pdf>
- <https://docs.gtk.org/gdk3/class.FrameClock.html>
- <https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html>
- <https://gitlab.freedesktop.org/wayland/wayland-protocols/-/blob/main/stable/presentation-time/presentation-time.xml>
- <https://idl.cs.washington.edu/files/2007-AnimatedTransitions-InfoVis.pdf>
- <https://raw.githubusercontent.com/hyprwm/hyprutils/main/include/hyprutils/animation/AnimatedVariable.hpp>
- <https://webkitgtk.org/2026/09/16/webkitgtk-2.54-highlights.html>
- <https://www.cs.umd.edu/users/ben/papers/Shneiderman1983Direct.pdf>

#### Scenario: final-content-while-busy

- **GIVEN** one admitted capture and multiple newer same-source revisions while visible demand persists
- **WHEN** the first job terminates and capacity returns
- **THEN** bounded demand selects the latest valid revision without losing the final update or extending the first job deadline

#### Scenario: close-or-lock-before-followup

- **GIVEN** a pending latest-content update
- **WHEN** demand closes, lock/revocation occurs or source identity changes before admission
- **THEN** no unauthorized follow-up capture is admitted; existing jobs and cleanup obligations remain accounted

#### Scenario: continuous-change-and-final-revision

- **GIVEN** authorized visible demand, continuously changing tracked content and eventually available eligible capacity
- **WHEN** the provider runs and then content change stops
- **THEN** capture follows the frozen pacing policy, the final tracked revision is serviced when eligible, and presentation impact is measured under026 with no original deadline renewal

### Requirement: ELM-ADOPT-028 — Source liveness and frame freshness are separate facts

WHEN an authorized preview is displayed, the shell SHALL distinguish source liveness, captured content revision and frame age, and SHALL NOT describe historical or stale pixels as current content.

Status: draft-refinement-awaiting-ratification. Classification: draft-refinement; original research classification: refinement. Priority: P1.

Baseline mapping: ELM-REN-004, ELM-REN-014, ELM-UI-016, ELM-UX-006, ELM-UX-007.

Existing work mapping: W03, W06.

Source proposals: FI-05.

Owner: Graphics lead. Verifier: Independent acceptance reviewer.

Guardrails: Refine labels only after reviewing the frozen historical/live/unavailable policy; do not relabel stale pixels as current-live or alter original13 S09 assertions.

Tradeoffs: Additional protocol/evidence complexity must meet the frozen workload/resource budget. Reuse current modules and incrementally qualify changed paths.

Primary sources:

- <http://direction.bordeaux.inria.fr/~roussel/publications/2015-UIST-mouse-based-lagmeter.pdf>
- <https://docs.gtk.org/gdk3/class.FrameClock.html>
- <https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html>
- <https://gitlab.freedesktop.org/wayland/wayland-protocols/-/blob/main/stable/presentation-time/presentation-time.xml>
- <https://idl.cs.washington.edu/files/2007-AnimatedTransitions-InfoVis.pdf>
- <https://raw.githubusercontent.com/hyprwm/hyprutils/main/include/hyprutils/animation/AnimatedVariable.hpp>
- <https://webkitgtk.org/2026/09/16/webkitgtk-2.54-highlights.html>
- <https://www.cs.umd.edu/users/ben/papers/Shneiderman1983Direct.pdf>

#### Scenario: live-source-with-old-frame

- **GIVEN** a live source advances after its authorized frame was captured
- **WHEN** the old frame remains valid while a replacement is pending
- **THEN** source liveness and frame age/freshness are distinguished; no false current-content claim or target substitution is made

#### Scenario: revocation-or-minimize

- **GIVEN** a displayed frame and native source-state/lease update
- **WHEN** the source minimizes or lease revokes
- **THEN** the existing historical/unavailable policy and native revocation govern display before replacement; no revoked pixels remain eligible
