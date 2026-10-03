# Rendering, capture, motion and native window authority contribution

This roadmap replaces shell presentation and ordinary policy with Elm while retaining native GPU, surface, input and window authority. Optional replacement of Hyprland is a separate Rust/C++ compositor program with Elm policy. It is not a promise that standard Elm can implement DRM, Wayland server protocols or native buffer ownership.

## Evidence and boundaries

Read [handoff](../../HANDOFF.md), [pivot](../../research/elm-pivot/README.md), [FRP](../../research/elm-pivot/FRP.md), [architecture](../../research/elm-pivot/ARCHITECTURE.md) and [status](../../../implementation/STATUS.md) together. Modern Elm uses Model/update/view, commands and subscriptions; historical Signals examples are not the implementation API. Elm purity does not confer atomic native effects or make Cmd.batch ordered.

The V29 capture derivative has 462 CPU tests and retained model evidence; native acceptance remains open. The failed B14 restore reached 19 checks with 17 passing and obtained captures without renderer seeding/uploads before its original two-second deadline. Preservation success does not establish restore success. [Capture profiling](../../../implementation/capture-profile-v30/README.md) distinguishes queue/seed/renderer receipts from physical presentation and cannot currently measure exact GPU upload or physical presentation. Preserve these limitations when extending instrumentation.

The [retained-frame prototype](../../../implementation/retained-frame-v1/README.md) is staged QML, not an accepted Elm-host renderer. Source-stop survival remains unverified. Its thumbnail excludes server decorations and out-of-base popup extents; full-resolution capture allocation precedes its admission check. The [MAX correction](../../../implementation/maximized-stack-v2/README.md) has bounded private rendered/click evidence for an exact pair, but activation and broad regression remain pending. Seven isolated checks do not establish complete stacking parity.

## Ownership design

Elm owns desired minimized/restored state, policy preferences, request generations, selection, cancellation intent and projections of native outcomes. The authority owns eligibility, modal-family redirects, native focus, stack/hit order, committed geometry, fullscreen and pin predicates. Keep one cross-output policy owner. A per-output view cannot independently commit a transfer or snap group.

A native frame broker owns captured SHM/DMA-BUF resources, fences and renderer leases. Elm receives opaque frame keys and bounded metadata, never serialized pixel arrays. A frame key includes compositor lifetime, window incarnation, capture revision, output generation and lease generation. The renderer retains independently owned pixels after source stop and reports retirement only after callbacks, buffers, surfaces and supervised helpers close. Separate logical window retirement from source-context shutdown: retaining pixels after a temporary stop is permitted, presenting old pixels for a reused identity is forbidden.

Track capture requested, source acquired, composed-family ready, seed queued, renderer seed accepted, first independently verified presentation, live handoff and retired as distinct states. A seed receipt is not presentation. Use a documented native monotonic clock and explicit clock mapping for observers. Browser requestAnimationFrame is a UI scheduling observation, not the clock for native minimize or restore trajectories.

Keep the original restore deadline origin and absolute two-second deadline through retries and renderer handoff. Prioritize cancellation and retirement traffic over preview work. Bound outstanding capture count, pixel footprint, helpers and queue size, with refusal receipts and pressure telemetry. Record observer overhead and incomplete trace stages. Fallback to a labelled last valid preview or explicit unavailable state; do not silently substitute another incarnation's frame.

Minimize preserves workspace membership and saved restore geometry; it never moves a window into a scratchpad. The last accepted frame bridges hidden-to-live restore. Reverse motion from the last presented geometry; reconcile uncertain effects before retrying. Cancellation is checked at the native mutation and submission boundary, with owned-generation cleanup. Reduced motion shares the same state machine and final native receipts while omitting decorative motion.

Decorations, shadows, rounding and modal/popup extents need explicit composed-family acquisition and clipping contracts. Stock thumbnail fidelity is insufficient evidence for motion replacement. A stale or vanished family member cannot authorize focus. Preserve draft windows and current GTK/Qt/Xwayland modality; an input blocker is established from native eligibility rather than assuming allows_input=false blocks focus.

MAX is not true fullscreen. Painted order, native hit test and committed focus must agree for overlapping floating MAX windows. Pin/unpin and MAX return geometry need complete predicates for masks, ignore, scroll, output transfer, menus and exclusive/render paths. Renderer-only stacking fixes remain necessary even with a correct Elm reducer. Each capture and input observation names the coherent native core/plugin pair.

## Phases and estimates

Estimates are planning ranges in engineer-weeks for experienced Elm and native graphics engineers, not measured throughput or commitments. They include local implementation and review, exclude procurement and upstream delays, and require revision after P1. Some work overlaps other roadmap authors; do not sum overlapping bridge/policy estimates blindly.

| Phase | Deliverable and exit evidence | Estimate / dependency |
| --- | --- | --- |
| P0 inventory/baseline | Freeze original identities, hash lineage, deadline origins, failed packets and same-machine metrics; identify GPU/presentation observer gaps | 1–2; access to archived scenarios and controlled baseline |
| P1 host bridge | Select GTK/WebKit or Qt/WebEngine only after native surface/input proof; frame broker lease schema, clock contract and native ownership ledger | 3–6; host work owned jointly with bridge authors |
| P2 policy | Elm intents with native effects; MAX/hit truth, modal/input eligibility, pin and generation-safe geometry | 3–6; native stacking correction and receipt bridge |
| P3 taskbar/switcher | Preview lease consumer, minimized visibility, release-before-ready and cancellation integration; UI does not own texture retirement | 2–4; other shell author owns full UI scope |
| P4 capturemotion | Independent retained frames, composed family, continuous minimize/restore, reversal, deadlines, reduced motion, limits and fault closure | 6–12; validated host and actual native capture APIs |
| P5 fullshell | Fullscreen/pin/menu interactions; mixed-scale transfers, snap-group/output ownership, resize/drag and display removal | 4–8; full shell and input routes |
| P6 release | Original campaigns plus new gaps; hardware cadence, long-running resource checks, accessibility integration and reversible rollout | 4–8; coherent frozen tuple and serial QA access |
| P7 optional feasibility | Native framework/protocol matrix, security/backend architecture, maintenance staffing, costs and go/no-go | 4–8; explicit optional scope decision |
| P8 optional implementation | Native compositor MVP followed by compatibility, hardware, security, recovery and production hardening | 40–100+; multi-specialist project, estimated duration highly uncertain |

## Acceptance and performance

The companion JSON supplies 30 atomic requirements with verification and scenario seeds. Replay and Quint complement native proof; explicitly select named scenarios rather than trusting default selectors. Preserve historical counts and corrected reports without relabelling retained proof as a new run.

Required gates remain the original 38 restore baseline and 34 fault/recovery checks at unchanged deadlines, the original 52 drag/resize/reload cases, genuine input-block/no-focus proof and the remaining B11–B24 pin predicates, actual changed/same/cancelled/stale popup routes and the fixed process reliability campaign. Earlier drag/resize testing reached three passes before failing minimized-preview movement; the full matrix remains open. Cancellation, reduced motion, multi-output, hardware cadence and audible/braille accessibility remain open. Source review/freezing, exact ABI pairing and combined regression are release dependencies; documentation does not authorize running them.

New source-stop proof observes visible accepted pixels, stops the source, independently samples the retained output, destroys/replaces identity and verifies final releases. Native acceptance must cover compositor/host restart, late receipts, helper failure, scale/rotation changes, allocation pressure and decorated modal families. Neither a QML snapshotReady signal nor an Elm view update is displayed-frame evidence.

Use same machine, compositor, workload, host versions and observer configuration for latency and cost comparisons. Record input-to-native-effect separately from input-to-visible-frame, p50/p95/p99, frame gaps, CPU/wakeups, RSS/PSS, GPU allocations, startup and long-run growth. Set acceptance budgets from measured baseline before migration. No available result proves Elm/WebKit is faster or cheaper than QML. On available 240 Hz hardware, keep sampling and fences native and measure real presentation cadence; do not promise every frame meets a numeric budget without measurements. Hardware not present is an explicit unverified gate, not a pass.

## Optional compositor program

P7 chooses Rust building blocks or a C++ stack based on supported protocols, renderer/backend integration, licensing, maintenance and team expertise. Framework demos establish feasibility, not Windows parity. Elm proposes high-level placements, workspace/snap/pin state and shell views. Native loops own frame scheduling, damage, buffer/fence release, hit testing, seats and privileged operations without synchronous Elm replies. A stalled frontend uses bounded native fallback policy.

P8 implements Wayland surface roles, configure/ack and buffer lifecycle, layer/popups, activation, idle/lock, clipboard/DND, fractional scale and protocol version negotiation; independently validate supported client matrices. Xwayland requires native legacy focus, transient families, grabs and WM interoperability. Unsupported protocols must be disclosed. DRM/KMS outputs, modes, hotplug, rotation, multi-GPU paths, seat/session access, suspend/resume and input-device removal need hardware coverage, not just nested tests. Color management and variable refresh require explicit scope and compatibility decisions.

IME/preedit/text-input, keyboard layouts, shortcut inhibition, accessibility integration, capture and PipeWire/desktop portals are native interoperability work. Portal consent, revocation and remote input boundaries need explicit security tests. Threat-model untrusted clients, privileged shell IPC, malformed buffers/protocols, screen-lock isolation and cross-session capture; isolate authority from web content. Fuzzing supplements native compatibility and failure tests.

First run nested isolated sessions, then sacrificial hardware sessions. Shell/webview restart can reconcile with existing applications; compositor failure generally disconnects their Wayland connections. Do not claim transparent application recovery or close drafts for cutover. Document fallback login/session and recovery drills, keep the known working Hyprland path and require a separate deliberate production migration.

## Risks and open decisions

The largest unresolved risks are source-stop ownership in the selected webview host, full composed-family fidelity, queue pressure under heavy captures, input-to-present latency across multiple processes, output transfer during hotplug, and divergent native modal semantics. Investigate whether native texture embedding can meet host lifecycle constraints before investing in full-motion views. PNG encode/decode stages and GPU uploads are currently observer gaps; instrumentation must not alter deadline semantics or leak titles/pixels.

Choose the capture transport, decoration source, independent presentation observer, admission budgets, cross-clock mapping and supported GPU/output matrix in P1/P4. Choose native compositor protocol breadth, X11 support level, backend/framework and minimum maintenance staffing in P7. Keep unresolved work explicit rather than inferring acceptance from staged candidates. Release requires both the intended user's draft/modal flow and combined frozen native regression, followed by verified deployment with rollback.

## Integrated estimate authority

The contribution ranges above are preserved first-draft inputs. The reconciled [roadmap phase ledger](../ROADMAP.md) supersedes them for scheduling, after independent audit and scope updates. Do not use a contribution table as an alternative delivery estimate.
