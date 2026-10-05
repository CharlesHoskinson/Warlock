# elm-performance — design adoption draft

## Purpose

Draft refinements for the existing in-flight `elm-performance` capability. This change contains ADDED research contracts only; it does not create or archive a main spec, replace existing pivot/right-click deltas, or establish release acceptance.

Provisional research drafts awaiting ratification and a separate reviewed baseline amendment. These artifacts do not change the canonical 242 requirements/417 scenarios, S01–S16, right-click24, original13 native preview cases, restore38/recovery34/drag-resize52 or original deadlines. Native authority and no automatic replay of Unknown remain mandatory. C00–C06 compositor replacement remains conditional.

No new native, hardware, IME, AT or full-release evidence is supplied by this packet. Frozen component/model/CPU/compiled replay evidence is not production-provider or full GUI ownership/drain/fidelity acceptance. GUI814 and toolkit391 retain separate owning ABI pairs. Implementation and qualification tasks remain unchecked.

## ADDED Requirements

### Requirement: ELM-ADOPT-004 — Measured revision-bound derived caching

WHERE derived-state caching is enabled, the frontend SHALL return the same projection as uncached derivation for every accepted revision and invalidate cached results before using changed or retired dependencies.

Status: draft-refinement-awaiting-ratification. Classification: draft-refinement; original research classification: refinement. Priority: P1.

Baseline mapping: ELM-TEA-001, ELM-QA-021, ELM-QA-022, ELM-QA-023, ELM-REV-020, ELM-REV-021.

Existing work mapping: W08, W09.

Source proposals: IMM-04.

Owner: Performance qualification lead. Verifier: Independent acceptance reviewer.

Guardrails: Caching/indexing is an implementation option after profiling. Cache keys include native dependency/output/publication revisions; stale cached data grants no authority. Enable an optimization only after the frozen workload comparison shows an accepted benefit; equivalence alone does not justify adopting it.

Tradeoffs: Cache/index memory and invalidation bookkeeping may outweigh scan savings; adoption requires frozen-budget evidence, no invented thresholds.

Adoption gate: enable caching only after profiling demonstrates measured benefit within the existing frozen budgets; otherwise preserve uncached derivation. This is a conditional implementation option, not a mandatory cache feature.

Primary sources:

- <https://elm-lang.org/assets/papers/concurrent-frp.pdf>
- <https://redux.js.org/usage/deriving-data-selectors>
- <https://raw.githubusercontent.com/elm/core/1.0.5/src/Array.elm>
- <https://immutable-js.com/>

#### Scenario: Unchanged dependency

- **GIVEN** Pointer events with unchanged scene/query/policy revisions
- **WHEN** Taskbar groups are derived
- **THEN** output equals the uncached oracle under the correct dependency revision; recomputation and whole-process resource results are measured separately for the adoption decision

#### Scenario: Identity reuse race

- **GIVEN** Cached retired family incarnation
- **WHEN** Same label appears under new lifetime/incarnation during query change
- **THEN** New identities govern derivation and action eligibility; stale family/preview authority does not survive

### Requirement: ELM-ADOPT-021 — Stage-qualified feedback and physical presentation evidence

WHEN an interaction stage is observed, the native authority and read-only projection SHALL label feedback, effect commitment, renderer submission, presentation and retirement separately, accepting physical completion only from identity-matched native evidence.

Status: draft-refinement-awaiting-ratification. Classification: draft-refinement; original research classification: refinement. Priority: P0.

Baseline mapping: ELM-ARC-020, ELM-REN-005, ELM-REN-022.

Existing work mapping: W06, W08, P4-ELM-ARC-020, P4-ELM-REN-005, P6-ELM-REN-022.

Source proposals: SOL-FLUID-01, FI-01.

Owner: Performance qualification lead. Verifier: Independent acceptance reviewer.

Guardrails: Input, commit, rendering, presentation and retirement are separate stages. Record clock mappings, feedback flags and missing/discarded events. Frame callback/image-load/screenshot request is not hardware presentation.

Tradeoffs: ['Extra trace stages and correlation storage', 'Native feedback can approximate light output; independent hardware evidence is still needed']

Primary sources:

- <http://direction.bordeaux.inria.fr/~roussel/publications/2015-UIST-mouse-based-lagmeter.pdf>
- <https://doc.qt.io/qt-6/qquickwindow.html>
- <https://docs.gtk.org/gdk3/class.FrameClock.html>
- <https://docs.kernel.org/gpu/drm-uapi.html>
- <https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html>
- <https://gitlab.freedesktop.org/wayland/wayland-protocols/-/blob/main/stable/presentation-time/presentation-time.xml>
- <https://idl.cs.washington.edu/files/2007-AnimatedTransitions-InfoVis.pdf>
- <https://raw.githubusercontent.com/hyprwm/hyprutils/main/include/hyprutils/animation/AnimatedVariable.hpp>
- <https://raw.githubusercontent.com/wayland-mirror/wayland-protocols/main/stable/presentation-time/presentation-time.xml>
- <https://webkitgtk.org/2026/09/16/webkitgtk-2.54-highlights.html>
- <https://www.cs.umd.edu/users/ben/papers/Shneiderman1983Direct.pdf>

#### Scenario: Queued is not presented

- **GIVEN** a matching image was decoded and a renderer queued a frame
- **WHEN** only image load or frameSwapped arrives
- **THEN** presentation remains unproven and no physical-completion verdict is recorded

#### Scenario: Stale output presentation

- **GIVEN** a transaction targets one output generation
- **WHEN** a presentation receipt arrives after hotplug changed that generation
- **THEN** the receipt is retained diagnostically but cannot complete the replacement transaction

### Requirement: ELM-ADOPT-024 — Separate feedback latency and useful completion measurement

WHEN host selection or release evaluation is prepared, the performance owner SHALL freeze same-machine workload budgets that separately measure input feedback, useful native presentation, whole-process resource closure and observer overhead, declaring missing stages.

Status: draft-refinement-awaiting-ratification. Classification: draft-refinement; original research classification: refinement. Priority: P0.

Baseline mapping: ELM-QA-021, ELM-QA-023, ELM-REV-020, ELM-REV-021, ELM-REN-021, ELM-REN-022.

Existing work mapping: W08, W12, P6-ELM-QA-023, P6-ELM-REN-021, P6-ELM-REN-022.

Source proposals: SOL-FLUID-05.

Owner: Performance qualification lead. Verifier: Independent acceptance reviewer.

Guardrails: No numeric limit invented from papers. Record latency distributions, missed frames, hardware/refresh/output metadata, CPU/memory/wakeups/idle-power and resource soak; QA observers disabled for product measurements.

Tradeoffs: ['Hardware and minimally observed measurements cost time', 'Academic thresholds do not substitute for the frozen local budget contract']

Primary sources:

- <https://www.yorku.ca/mack/p488-mackenzie.pdf>
- <https://www.tactuallabs.com/papers/designingLowLatencyDirectTouchInputUIST12.pdf>
- <https://raw.githubusercontent.com/wayland-mirror/wayland-protocols/main/stable/presentation-time/presentation-time.xml>
- <https://docs.gtk.org/gdk4/class.FrameClock.html>
- <https://doc.qt.io/qt-6/qquickwindow.html>
- <https://docs.kernel.org/gpu/drm-uapi.html>

#### Scenario: Missing presentation instrument

- **GIVEN** a benchmark records CPU submission and feedback but lacks a presentation span
- **WHEN** the host comparison is evaluated
- **THEN** unsupported spans are explicit and physical latency acceptance remains blocked rather than treating submission as presentation

#### Scenario: Observer hides tail failure

- **GIVEN** a debug observer improves or perturbs scheduling
- **WHEN** the final benchmark packet is prepared
- **THEN** paired observed and minimally observed runs expose overhead and all frozen workload thresholds are evaluated without discarding misses

### Requirement: ELM-ADOPT-026 — Capture must not starve native presentation

IF a preview capture or export route exceeds its frozen presentation-impact budget on an active output, THEN the release verifier SHALL reject that route and retain a qualified alternative or explicit unavailable-preview state.

Status: draft-refinement-awaiting-ratification. Classification: draft-refinement; original research classification: refinement. Priority: P0.

Baseline mapping: ELM-REV-022, ELM-REN-012, ELM-QA-023, ELM-UI-017.

Existing work mapping: W06, W08.

Source proposals: FI-02.

Owner: Performance qualification lead. Verifier: Independent acceptance reviewer.

Guardrails: Synchronous compositor readback/encode is a concern, not a measured regression. Async readback/cropping/off-thread encoding need their own safety, fence, eligibility and ABI qualification. Unavailable fallback does not close mandatory source-stop/family gates.

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

#### Scenario: cross-output-capture-impact

- **GIVEN** restore motion on one output and capture demand on another
- **WHEN** the capture route runs on the measured hardware tuple
- **THEN** presentation gaps and latency are measured on every active output against the same workload without capture

#### Scenario: over-budget-route

- **GIVEN** measured route impact exceeds the frozen budget
- **WHEN** release admission evaluates it
- **THEN** the route is rejected and the documented unavailable fallback is truthful; no stale or unqualified route substitutes for required capture acceptance
