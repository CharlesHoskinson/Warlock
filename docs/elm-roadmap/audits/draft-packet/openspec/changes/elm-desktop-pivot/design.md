# Design: Elm shell with native authority

## Context

The project is a local archival snapshot of an unfinished Windows-parity desktop. The installed taskbar has recent observation/cache improvements. Capture, switcher and native MAX corrections are partly staged; historical native campaigns remain open. [Baseline](../../../docs/elm-roadmap/BASELINE.md).

The requested GUI pivot is complete at the shell level: taskbar, launcher, switcher, Task View, snap/workspace chooser, menus and settings use Elm. The native compositor is retained initially. Elm's supported JavaScript/ports model has no direct Wayland/GPU/seat authority. An optional compositor replacement needs a native implementation regardless of the policy language.

## Goals / Non-goals

Goals are a coherent typed shell model, explicit native ownership, correct window layering and focus, hardware-accelerated rendering, reversible integration, verifiable capture/motion lifetime, accessible input and complete defined parity acceptance. GPU/WebGPU host qualification and Mutter/KWin architecture studies are first-class inputs.

The planning change does not install a new host, restart the compositor, close drafts, repair all current desktop defects or establish hardware/browser rendering acceptance. An all-Elm Wayland compositor and unqualified zero-copy imports are not assumed.

## Decisions

1. **Initial compositor: Hyprland.** Retain existing application compatibility and validated native components while proving the new shell. Correct active native layering independently. P7/P8 hold the conditional replacement scope.
2. **Host comparison before commitment.** Compare a compatible GTK/WebKitGTK/layer-shell host with a dedicated Qt WebEngine host using the same isolated workloads. Installed GTK libraries make discovery cheaper, not automatically faster or WebGPU-capable. Record versions, dependencies, layer/popup roles, focus/IME/AT and GPU evidence.
3. **Message-oriented boundary.** Elm decoders consume coherent snapshots/ordered events. Intents and outcomes carry stable native incarnation, expected revision, compositor/frontend lifetimes, generation and output. Native authority validates at the effect boundary. A request, accepted outcome and displayed frame are distinct receipts.
4. **Native scene truth.** A canonical committed scene revision supplies eligibility, layer/family constraints, stable order, native geometry and focus. Painting and input routing consume that revision with explicit input-region exceptions. Minimized/inactive windows cannot bypass eligibility via stale priority/fullscreen permission. Separate inert animation/preview actors from live application input.
5. **Hardware GPU qualification.** Require actual nonsoftware rendering in the chosen host. WebGPU is a candidate for custom effects/compute, tested at a secure local origin with sandboxing, deterministic workloads and device-loss recovery. Standard WebGPU does not establish arbitrary native DMA-BUF import. Native Vulkan/OpenGL remains an alternative.
6. **Native capture and timing.** Opaque frame leases cross ports; native components retain buffers, fences, source-stop lifetime and monotonic/presentation clocks. Per-frame pixel arrays and synchronous native hit decisions stay outside Elm ports. Sequence dependent effects through acknowledgements rather than command batching.
7. **Preserved proof obligations.** Fresh derivatives retain original case identities, deadlines, hashes and failed evidence. CPU/model/replay/native results are separate. Protected native campaigns run serially and preserve runtime/socket/process/core-limit controls.
8. **Reversible staged delivery.** Feature-selectable components, settings migration, exact compositor/plugin tuple, bundled assets, license manifests, supervised services and offline recovery precede production activation. Main-session activation is a separate authorized step following accepted evidence.

## State and lifecycle

Window identity combines stable native ID, process identity/incarnation and captured lifetime; transport addresses are not authority. A UI operation moves through requested/pending/committed/refused/cancelled/unknown states. Generation invalidation rejects stale receipts and ensures late callbacks cannot revive overlays or mutate reused identities.

Global chord ordering is captured natively before a view is ready. Observations can be coalesced only when semantics permit; Alt release, cancellation and retirement receipts retain causal order. On disconnect/restart, invalidate frontend authority, obtain a fresh coherent snapshot and reconcile uncertain outcomes rather than replay old mutating requests.

Capture leases record producer/consumer ownership, output generation, accepted frame geometry and retirement. Native actors can render an inert retained frame during animation without granting the minimized live source hit/focus eligibility. Device/output/renderer changes invalidate the relevant generation and require fresh GPU resources.

## Architecture references

[Layering design](../../../docs/elm-roadmap/LAYERING.md), [Mutter study](../../../docs/elm-roadmap/contributions/gnome-layering.md) and [KWin study](../../../docs/elm-roadmap/contributions/kde-layering.md) distinguish reference implementation behavior from Windows product choices. Their complete scoped source/documentation inventories preserve pinned revisions and source attribution. In particular, reference above/fullscreen semantics are not copied blindly into pin/MAX parity.

[GPU design](../../../docs/elm-roadmap/GPU.md) records read-only Intel/NVIDIA Vulkan availability, explicitly leaving actual host/WebGPU proof pending. Device diagnostics, visible workloads, copies/fences, failure modes and selected integrated/discrete profiles qualify the chosen path.

## Risks / Trade-offs

A webview adds processes, asynchronous transport and native surface/accessibility integration. Typed Elm models reduce ambiguity but do not make external effects atomic. Resource/latency budgets are frozen from P0 measurements before selection; failure stops the full-GUI host decision. A headless Elm policy runtime plus retained QML is a fallback, and its success cannot qualify browser GUI performance.

Native preview import may require copies or a dedicated native renderer. Qualification measures that cost and ownership rather than promising zero-copy. Source-stop/family/hardware failure stops P4 acceptance. A new compositor multiplies protocol, application, output, security and recovery scope; its optional stages do not block initial shell delivery.

## Migration Plan

Follow P0–P6 gates in [the roadmap](../../../docs/elm-roadmap/ROADMAP.md). Inventory and baselines precede isolated hosts and policy replay; taskbar/switcher establish one full-GUI native slice; capture/motion and complete shell routes precede coherent release regression. Preserve current working services until accepted replacements and rollback artifacts exist. P7/P8 require a separate go decision.

## Open Questions and decision gates

The selected host, native preview interoperability, exact cross-display model, frozen numeric performance/copy budgets and optional compositor substrate are unresolved decisions. Each has an owner, phase, experiment and stop/fallback in the roadmap. They block their corresponding implementation/selection gates; they are not placeholders for a release acceptance pass. Exact fullscreen/pin policy is frozen against the inherited case matrix before native layering qualification.

## Validation

The generated registry maps every requirement to its phase, OpenSpec scenario, task and verifier. Run the strict OpenSpec CLI and local EARS/traceability/link checks; retain four independent audit reports with a hashed reviewed packet and final dispositions. All implementation/native/GPU acceptance remains pending.
