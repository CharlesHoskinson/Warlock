# Fluid interaction review — sol-05-fluid-interaction

Draft research, retrieved 2026-10-05. This report proposes refinements and qualification work, not accepted native behavior. It preserves all 242 requirements, 417 scenarios, S01–S16, the 13 native preview scenarios, restore38/recovery34, drag/resize52 and their original deadlines. Nothing below authorizes deployment, a compositor replacement, source eligibility expansion or automatic replay of Unknown. The two host ABI lanes must remain separate.

## Findings from the frozen design

The central design is already stronger than an animation-centric definition of fluidity. Native authority owns pixels, input, clocks and physical retirement; Elm owns immutable interaction state and read-only projections around one controller. The useful research question is how to expose progress promptly without letting a pleasant response become false evidence that an effect completed. A spinner, selected-row highlight or decoded preview can acknowledge intent. None supplies proof that the corresponding native window or pixels became visible.

Frozen path anchors below are relative to `inputs/`. `docs/elm-roadmap/REQUIREMENTS.md:165` defines ELM-REN-005 clock correlation, `:195` retains the original restore deadline, `:225` requires shared reduced-motion semantics, `:1265` bounds bridge demand, `:1315` separates commit and presentation, and `:1519` freezes measured budgets. `:1579` and `:1589` specify the workload and metric matrix. These are proposed obligations, not evidence of already qualified production behavior. Their detailed mapping makes most recommendations below refinements rather than new requirements.

`docs/elm-roadmap/delivery/FRP-ELM-WORKPLAN.md:63–69` identifies W05 deadline enforcement, W06 opaque native ownership, W08 measured performance and W12 native motion. Its earlier W01 discussion explicitly warns that splitting byte budgets must preserve atomic projection/effect dependencies. Its later evidence notes distinguish bounded prototypes from release resource budgets. The existing previous-review workplan is therefore a dependency, not a competing plan to replace.

Actual frozen code offers a useful small example. `implementation/elm-preview-shared-bridge-v509/src/PreviewPresenter.elm:62` documents retaining lifecycle owners after UI closure so late cleanup still arrives. `present` cancels stale demand; `receive` guards a fixed picker incarnation and limits admitted entries. The entry-count constant is a component policy, not a complete byte/GPU/helper budget. `src/PreviewLifecycle.elm:15` and `:16` carry native-origin clock/deadline fields into triggers and jobs; `:135` guards authorization; `:204` checks adoption against demand and deadline; `:258` admits capture only against current native context. These are real implemented transition checks. They do not prove provider integration, source-family fidelity, compositor presentation or whole-tree closure.

The inventory limits are decisive. GUI509 and native513 qualify a shared dispatcher, fallback presentation and ordinary cleanup, not a production provider. Source492 observes scoped root commits but marks its root monitor-plane route previewEligible:false. Private rendering cannot promote it into an authorized production family preview. Broker517/qualification520 cover unadopted reservations and cancellation races; provider519 remains unfinished. No recommendation presumes otherwise. GUI814 and toolkit391 supply separate source/ABI evidence, and no cross-loading follows from their presence.

## Verified primary sources

All links were opened directly on 2026-10-05. Publication years describe papers; rolling documentation does not establish the deployed software version. The official GitLab presentation XML URL returned an anti-bot page, so the project mirror XML was read instead. The generated Wayland Explorer text was useful for navigation but is not counted as an official primary source.

| ID | Source, year/version | Supporting observation | Limitation |
|---|---|---|---|
| A1 | [MacKenzie and Ware, Lag as a Determinant of Human Performance in Interactive Systems, CHI 1993](https://www.yorku.ca/mack/p488-mackenzie.pdf) | Controlled target-acquisition work links feedback lag with movement performance and errors. | Older apparatus and task; cannot provide this shell's numeric acceptance threshold. |
| A2 | [Ng et al., Designing for Low-Latency Direct-Touch Input, UIST 2012](https://www.tactuallabs.com/papers/designingLowLatencyDirectTouchInputUIST12.pdf) | A low-latency demonstrator and direct-touch comparisons motivate studying input-to-display delay, including a fast feedback layer. | Direct touch differs from mouse/window effects; feedback must not claim authoritative completion. |
| O1 | [Wayland presentation-time protocol XML, maintained main](https://raw.githubusercontent.com/wayland-mirror/wayland-protocols/main/stable/presentation-time/presentation-time.xml) | Per-commit presented/discarded outcomes, clock identity, output association and hardware-quality flags distinguish display evidence. | A compositor may approximate presentation; deployed capability and flags require qualification. |
| O2 | [Wayland core protocol specification, rolling](https://wayland.freedesktop.org/docs/html/apa.html#protocol-spec-wl_surface) | Surface frame callbacks pace rendering and can be withheld for invisible content. Buffer reuse follows release, not rendering intent. | A scheduling hint cannot serve as operation expiry or physical proof. |
| O3 | [GTK4 Gdk.FrameClock, rolling](https://docs.gtk.org/gdk4/class.FrameClock.html) | Phased, demand-driven rendering coordinates animation; frame time differs from a fresh monotonic clock read. | Toolkit timing is neither a native transaction deadline nor independent scanout proof. |
| O4 | [GTK4 gtk-enable-animations setting, rolling](https://docs.gtk.org/gtk4/property.Settings.gtk-enable-animations.html) | Maintained native toolkit exposes an animation preference. | A setting does not define application-specific interruption or ownership semantics. |
| O5 | [Qt6 QQuickWindow, retrieved documentation identifying 6.12.0](https://doc.qt.io/qt-6/qquickwindow.html) | afterFrameEnd reports submission; frameSwapped reports queuing for presentation; rendering has distinct thread stages. | These callbacks must not be promoted to physical display completion. |
| O6 | [Linux DRM userland interfaces, rolling](https://docs.kernel.org/gpu/drm-uapi.html) | DRM exposes graphics/display interfaces and explicit synchronization concepts for native evidence and ownership integration. | Generic kernel capabilities do not prove this host's GPU path, fences or output timing. |

Academic results justify measuring the closed feedback loop and treating tail delays seriously. They do not justify copying a preferred threshold, predicting a shell user's tolerance or changing original semantic deadlines. The maintained systems demonstrate practical separation of scheduling, submission and presentation. They do not establish that this project's bridge currently implements those APIs correctly.

## Prioritized draft adoption proposals

### SOL-FLUID-01 — Stage-qualified feedback and physical presentation evidence

Priority P0; refinement. Baseline: ELM-ARC-020, ELM-REN-005, ELM-REN-022. Work: W06, W08, P4-ELM-ARC-020, P4-ELM-REN-005, P6-ELM-REN-022. Primary sources: [O1](https://raw.githubusercontent.com/wayland-mirror/wayland-protocols/main/stable/presentation-time/presentation-time.xml), [O5](https://doc.qt.io/qt-6/qquickwindow.html), [O6](https://docs.kernel.org/gpu/drm-uapi.html).

This refines the existing distinction into an auditable stage vocabulary. A read-only UI can promptly show Pending while pin/MAX indicators continue to represent committed native state. Record stage identity, native clock domain, operation generation, output generation and evidence quality. Presentation denial/discard is not permission to retire someone else's buffers; release remains a separate ownership event. The alternative of one “done” timestamp is cheap but conceals queue delay and unsupported GPU spans. Incrementally extend W06/W08 trace reporting before changing visible feedback. Validation must deliberately supply queued-only, discarded and stale-output receipts and independently sample output in the appropriate protected hardware campaign.

**EARS draft:** WHEN an interaction stage is observed, the native authority and read-only projection SHALL label feedback, effect commitment, renderer submission, presentation and retirement separately, accepting physical completion only from identity-matched native evidence.

- **Queued is not presented**: GIVEN a matching image was decoded and a renderer queued a frame; WHEN only image load or frameSwapped arrives; THEN presentation remains unproven and no physical-completion verdict is recorded.

- **Stale output presentation**: GIVEN a transaction targets one output generation; WHEN a presentation receipt arrives after hotplug changed that generation; THEN the receipt is retained diagnostically but cannot complete the replacement transaction.

### SOL-FLUID-02 — Demand scheduling with bounded control liveness

Priority P0; refinement. Baseline: ELM-ARC-015, ELM-ARC-016, ELM-REN-012. Work: W01, W03, W06, W10. Primary sources: [O2](https://wayland.freedesktop.org/docs/html/apa.html#protocol-spec-wl_surface), [O3](https://docs.gtk.org/gdk4/class.FrameClock.html), [O5](https://doc.qt.io/qt-6/qquickwindow.html).

The requirement is existing bounded demand, not a novel event-stream architecture. Rendering pacing can guide acquisition demand only within authorized source and ownership rules. Keep close/cancel/receipts/retirement on the reserved control route while latest-value observations coalesce only inside their documented domain. A newest observation cannot erase an effect receipt, press/release pair or dependency needed for an atomic projection. Do not infer invisibility merely from output enter/leave. Compare explicit refusal with backpressure; refusal is simpler to audit, while blocking needs a liveness argument. Validate measured bytes, items, native pixels and helpers under saturation plus cancellation. Include reopen before old cleanup: retained owners must not be replaced by a superficially fresh model.

**EARS draft:** WHILE preview or observation demand exceeds admitted capacity, the bridge SHALL coalesce only replaceable observations within their identity domain, refuse unadmitted effects explicitly and preserve ordered cancellation, receipts and retirement capacity.

- **Observation storm with cancellation**: GIVEN preview queues are saturated within frozen byte and item bounds; WHEN new observations and a cancellation arrive; THEN only semantically replaceable observations coalesce; cancellation and all retirement receipts remain deliverable in order.

- **Close during producer reservation**: GIVEN a producer owns a reservation and the picker closes; WHEN a late producer result arrives; THEN demand remains cancelled and the existing owner receives cleanup; no new capture is admitted until capacity is legitimately released.

### SOL-FLUID-03 — Absolute semantic deadline independent of paint scheduling

Priority P0; duplicate. Baseline: ELM-ARC-013, ELM-ARC-014, ELM-REN-008. Work: W05, P4-ELM-REN-008. Primary sources: [O1](https://raw.githubusercontent.com/wayland-mirror/wayland-protocols/main/stable/presentation-time/presentation-time.xml), [O2](https://wayland.freedesktop.org/docs/html/apa.html#protocol-spec-wl_surface), [O3](https://docs.gtk.org/gdk4/class.FrameClock.html).

This is explicitly duplicate advice, consolidated under W05 rather than another deadline task. Paint suspension, reduced refresh cadence or frontend restart must not stop native expiry. Separate the original product deadline from when feedback happens to repaint. Recovery case34 remains a negative gate at its original time origin; eventual reconciliation cannot rewrite its result. The alternative browser timer is easy to prototype but neither survives frontend failure nor establishes native authority. Validate queue delay, capture retry and late exact receipts with the protected native clock. No new numerical timeout, grace period or renewed two-second interval is proposed.

**EARS draft:** WHEN work crosses a queue, retry, frontend restart or paint suspension, the native authority SHALL preserve its original absolute deadline and start event; late exact outcomes SHALL reconcile uncertainty without extending acceptance or automatically replaying Unknown.

- **Obscured frontend deadline**: GIVEN the transaction has its original native deadline; WHEN paint callbacks stop while capture is queued; THEN native expiry still occurs at that deadline and UI silence cannot extend the operation.

- **Late exact commit**: GIVEN an operation became Unknown at its original deadline; WHEN an authenticated exact commit receipt arrives later; THEN native truth is reconciled while the original deadline verdict remains a failure and no automatic replay occurs.

### SOL-FLUID-04 — Reversal and live reduced motion share native semantics

Priority P1; refinement. Baseline: ELM-REN-010, ELM-REN-011, ELM-UI-014, ELM-UX-022. Work: W12, P4-ELM-REN-010, P4-ELM-REN-011, P4-ELM-UI-014. Primary sources: [A1](https://www.yorku.ca/mack/p488-mackenzie.pdf), [A2](https://www.tactuallabs.com/papers/designingLowLatencyDirectTouchInputUIST12.pdf), [O1](https://raw.githubusercontent.com/wayland-mirror/wayland-protocols/main/stable/presentation-time/presentation-time.xml), [O3](https://docs.gtk.org/gdk4/class.FrameClock.html), [O4](https://docs.gtk.org/gtk4/property.Settings.gtk-enable-animations.html).

Preserve W12's native motion owner and last-presented geometry/velocity. A queued but unseen interpolation sample is the wrong starting point for a reversal. Freeze the exact interruption policy and approved reduced-motion profile before testing; a preference change must not replay an operation, discard a cleanup obligation or extend a deadline. Native preferences are evidence for offering such a mode, not an imported GTK implementation mandate. Incremental work begins with deterministic intent/reversal traces, followed by native recordings and the original restore/fault campaigns. Decorative interpolation and state commitment remain separate decisions. An instantaneous route is a possible approved profile, not permission to skip ownership or frame authorization.

**EARS draft:** WHEN motion is interrupted or the reduced-motion preference changes, the native renderer SHALL derive the successor from the last-presented geometry and preserve the same identity, cancellation, commitment and retirement rules under the approved motion profile.

- **Reverse after an unpresented sample**: GIVEN a restore has a queued sample newer than its last native presentation; WHEN a minimize intent reverses it; THEN the successor starts from last-presented geometry under the native continuity rule and retires only the superseded generation.

- **Preference changes during capture**: GIVEN a restore is awaiting a retained frame; WHEN reduced motion becomes enabled before its matching frame arrives; THEN the approved reduced-motion route uses identical commit and cancellation obligations without replaying the effect or resetting its deadline.

### SOL-FLUID-05 — Separate feedback latency and useful completion measurement

Priority P0; refinement. Baseline: ELM-QA-021, ELM-QA-023, ELM-REV-020, ELM-REV-021, ELM-REN-021, ELM-REN-022. Work: W08, W12, P6-ELM-QA-023, P6-ELM-REN-021, P6-ELM-REN-022. Primary sources: [A1](https://www.yorku.ca/mack/p488-mackenzie.pdf), [A2](https://www.tactuallabs.com/papers/designingLowLatencyDirectTouchInputUIST12.pdf), [O1](https://raw.githubusercontent.com/wayland-mirror/wayland-protocols/main/stable/presentation-time/presentation-time.xml), [O3](https://docs.gtk.org/gdk4/class.FrameClock.html), [O5](https://doc.qt.io/qt-6/qquickwindow.html), [O6](https://docs.kernel.org/gpu/drm-uapi.html).

Refine existing budget qualification rather than propose a magic “responsive” number. Pair early feedback with useful completion, including failure/refusal paths, and report distributions, frame misses, resource growth and whole-tree costs. Freeze workload, units, sample counts, hardware, output metadata, cold/warm state, baseline and approved absolute/regression thresholds before evaluation. Separate missing measurements from measured zero and quantify instrumentation overhead. First-frame success can coexist with later queue accumulation, so include sustained navigation, preview churn, reversals, output transfer and soak. Native presentation observations and independent physical samples answer different questions. Instrument both candidate hosts serially with their owning ABI, then compare equivalent workloads without claiming CPU replay qualifies physical motion.

**EARS draft:** BEFORE host selection or release evaluation, the performance owner SHALL freeze measured same-machine workload budgets with separate input-to-feedback, input-to-native-presentation and resource-closure measures, stage coverage, observer overhead and missing-stage declarations.

- **Missing presentation instrument**: GIVEN a benchmark records CPU submission and feedback but lacks a presentation span; WHEN the host comparison is evaluated; THEN unsupported spans are explicit and physical latency acceptance remains blocked rather than treating submission as presentation.

- **Observer hides tail failure**: GIVEN a debug observer improves or perturbs scheduling; WHEN the final benchmark packet is prepared; THEN paired observed and minimally observed runs expose overhead and all frozen workload thresholds are evaluated without discarding misses.

## Rejected alternatives and remaining unknowns

Reject per-frame Elm JSON or historical Elm Signals as the motion mechanism: both conflict with the frozen modern architecture and native presentation owner. Reject speculative native-state success justified by quick feedback. Reject reducing deadlines to benchmark targets or extending them to absorb backpressure. Reject cancelling by dropping the owning lifecycle, automatically replaying Unknown, and releasing imported buffers because image load finished. Reject promoting root-plane captures or private pixels into eligible family previews. Defer compositor C00–C06 replacement pending its existing evidence-driven gate; academic latency work does not supply that go/no-go decision.

There is no verified production provider budget, no complete physical latency packet and no proof here of client/decor/modal/subsurface/color fidelity. The actual presentation protocol version, hardware flags, multi-output timestamp behavior, clock mapping and native reduced-motion preference bridge need local qualification. Missing data should be written as missing, not inferred from successful compilation or model replay. Determine which feedback controls can safely update immediately without representing commit; verify their keyboard and AT interpretation through W08. Keep resource-retirement measurements distinct from helpful visual feedback so a fast UI cannot hide leaking producers.

Every implementation item remains unchecked. Each proposal supplies two falsifiable scenarios, but these are draft additions or refinements, not replacements for any original scenario. This is one independent review. Agreement with a parallel review would be initial corroboration; consensus requires the promised shared matrix, explicit votes and recorded dissent.
