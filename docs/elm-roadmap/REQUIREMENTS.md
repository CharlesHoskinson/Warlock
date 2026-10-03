# EARS requirement inventory

All statements below are proposed requirements for the Elm desktop and optional native compositor track. This file and the OpenSpec capability deltas are generated from [the canonical registry](requirements.json); identical normative text and stable IDs are retained. A requirement being listed does not mean it is implemented or accepted.

Patterns use EARS: The/system/SHALL for ubiquitous behavior; WHEN for events; WHILE for states; IF/THEN for unwanted behavior; WHERE for selected features; combinations retain their clause order. [Originator guidance](https://alistairmavin.com/ears/).

`must` requirements apply to the mandatory shell scope unless explicitly state-conditioned; `conditional` requirements apply only when the specified optional feature is selected. P7/P8 belong to the optional native compositor track. Every acceptance must execute its verification and retain evidence; existing CPU/native/model results are not interchangeable.

[Traceability](TRACEABILITY.md) connects requirements, scenarios, tasks, phases and legacy/new proof obligations. [Author input normalizations](normalizations.json) record EARS keyword and pattern normalization; original inputs remain unchanged.

## elm-accessibility

### ELM-UI-009

The Elm desktop SHALL expose names, roles, states, values, relationships and supported actions for every interactive control on every migrated surface through the native accessibility bridge, with decorative pixels inert and restore controls separately identified.

Pattern: ubiquitous. Phase: P5. Priority: must. Status: proposed. Owner: Accessibility lead; verifier: Independent acceptance reviewer.

Verification: Named native, keyboard and assistive-technology fixtures where applicable; independent observed results, exact identities, source hashes and frozen product-policy oracle.

Evidence obligation: docs/elm-roadmap/INTERACTION.md; new coverage: final UI/UX review

### ELM-UI-010

WHEN an action needs user attention or a notification changes, the shell SHALL publish concise identity-correlated accessible status without moving focus, deduplicate repeated receipts and apply the frozen notification announcement/interruption policy.

Pattern: event-driven. Phase: P3. Priority: must. Status: proposed. Owner: Accessibility lead; verifier: Independent acceptance reviewer.

Verification: Named native, keyboard and assistive-technology fixtures where applicable; independent observed results, exact identities, source hashes and frozen product-policy oracle.

Evidence obligation: docs/elm-roadmap/INTERACTION.md; new coverage: final UI/UX review

### ELM-UI-011

WHEN a shell focus scope closes, the host SHALL restore its eligible identity-bound opener or the declared eligible fallback, restore surviving parent scopes for nested dismissal, reject replacement incarnations and let lock security supersede ordinary restoration.

Pattern: event-driven. Phase: P3. Priority: must. Status: proposed. Owner: Accessibility lead; verifier: Independent acceptance reviewer.

Verification: Named native, keyboard and assistive-technology fixtures where applicable; independent observed results, exact identities, source hashes and frozen product-policy oracle.

Evidence obligation: docs/elm-roadmap/INTERACTION.md; new coverage: final UI/UX review

### ELM-UI-012

WHILE IME composition owns a field, the host SHALL respect input-method key consumption, bind callbacks to field identity and composition generation, track candidate geometry with caret/output transforms and reject late commits after focus loss, field retirement or host restart.

Pattern: state-driven. Phase: P1. Priority: must. Status: proposed. Owner: Accessibility lead; verifier: Independent acceptance reviewer.

Verification: Named native, keyboard and assistive-technology fixtures where applicable; independent observed results, exact identities, source hashes and frozen product-policy oracle.

Evidence obligation: docs/elm-roadmap/INTERACTION.md; new coverage: final UI/UX review

### ELM-UI-013

The accessibility owner SHALL freeze measurable contrast, focus visibility, effective target geometry, text enlargement and reflow thresholds before host qualification, require non-color state cues and preserve reachable controls on small outputs and long labels.

Pattern: ubiquitous. Phase: P0. Priority: must. Status: proposed. Owner: Accessibility lead; verifier: Independent acceptance reviewer.

Verification: Named native, keyboard and assistive-technology fixtures where applicable; independent observed results, exact identities, source hashes and frozen product-policy oracle.

Evidence obligation: docs/elm-roadmap/INTERACTION.md; new coverage: final UI/UX review

### ELM-UX-023

The Elm desktop SHALL provide keyboard routes for launcher, taskbar groups, switcher, Task View, snap chooser, menus, settings, notifications and jump lists without requiring pointer input.

Pattern: ubiquitous. Phase: P5. Priority: must. Status: proposed. Owner: Accessibility lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: each surface can be opened, operated and dismissed without pointer events.

Evidence obligation: window-behavior-spec/accessibility.qnt

### ELM-UX-024

WHILE a shell popup owns keyboard focus, the Elm desktop SHALL constrain traversal to its documented focus order and restore the previous eligible focus target on dismissal.

Pattern: state-driven. Phase: P5. Priority: must. Status: proposed. Owner: Accessibility lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: focus follows menu order and returns to original eligible target.

Evidence obligation: window-behavior-spec/accessibility.qnt

### ELM-UX-025

The Elm desktop SHALL expose names, roles, states and focus changes for taskbar and switcher controls through the chosen host’s native accessibility bridge.

Pattern: ubiquitous. Phase: P3. Priority: must. Status: proposed. Owner: Accessibility lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: inspector and Orca observe matching name, role, selection and focus.

Evidence obligation: window-behavior-spec/accessibility.qnt

### ELM-UX-026

WHEN a shell control gains focus or changes selection, the Elm desktop SHALL expose that state to configured speech and braille consumers without duplicate announcements from parallel shell hosts.

Pattern: event-driven. Phase: P5. Priority: must. Status: proposed. Owner: Accessibility lead; verifier: Independent acceptance reviewer.

Verification: Preserve native accessibility trace, speech transcript and braille device or approved emulator output.

Evidence obligation: docs/HANDOFF.md

### ELM-UX-027

The Elm desktop SHALL preserve readable labels and visible focus indicators in normal, high-contrast and enlarged-text theme fixtures without clipping actionable controls.

Pattern: ubiquitous. Phase: P5. Priority: must. Status: proposed. Owner: Accessibility lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: labels and focus remain visible and every action retains a hit target.

Evidence obligation: window-behavior-spec/accessibility.qnt

### ELM-UX-028

WHEN an input method composes text in a shell field, the Elm desktop SHALL retain preedit and candidate interaction until explicit commit or cancellation.

Pattern: event-driven. Phase: P1. Priority: must. Status: proposed. Owner: Accessibility lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: one committed query appears and preedit is not dispatched as a launch.

Evidence obligation: docs/research/elm-pivot/ARCHITECTURE.md; new IME native coverage

## elm-capture-motion

### ELM-REN-001

The project SHALL preserve the original 38 restore-baseline, 34 fault/recovery and 52 drag/resize scenario identities and deadlines in a fresh acceptance ledger.

Pattern: ubiquitous. Phase: P0. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Ledger diff retains all IDs and original time origins.

Evidence obligation: docs/HANDOFF.md

### ELM-REN-002

The native host SHALL own GPU buffers and expose opaque identity-bound frame leases to Elm without sending pixels in port JSON.

Pattern: ubiquitous. Phase: P1. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: IPC schema audit and native allocation trace show no pixel payload.

Evidence obligation: docs/research/elm-pivot/ARCHITECTURE.md

### ELM-REN-003

WHEN a capture source stops, the native renderer SHALL retain the last independently owned accepted frame until its lease is retired.

Pattern: event-driven. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Source-stop trace plus independently sampled output pixels and release log.

Evidence obligation: implementation/retained-frame-v1/README.md

### ELM-REN-004

WHEN a window incarnation is replaced, the native host SHALL revoke its frame leases before accepting previews for the replacement.

Pattern: event-driven. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Address-reuse fault test rejects old lease and releases its resources.

Evidence obligation: implementation/retained-frame-v1/README.md

### ELM-REN-005

The native renderer SHALL associate motion samples and presentation receipts with one documented monotonic clock domain or an explicitly measured clock mapping.

Pattern: ubiquitous. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Trace schema and clock-correlation test identify each timestamp origin.

Evidence obligation: implementation/capture-profile-v30/README.md

### ELM-REN-006

WHEN minimizing a window, the native authority SHALL preserve its normal workspace identity and restore geometry without moving it to a scratchpad.

Pattern: event-driven. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Native minimize/restore observation records workspace, family and geometry.

Evidence obligation: docs/HANDOFF.md

### ELM-REN-007

WHEN restore motion begins, the native renderer SHALL use the accepted retained frame until an identity-matched live frame is ready for a continuous handoff.

Pattern: event-driven. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Frame-by-frame native capture identifies retained/live handoff without blank frames.

Evidence obligation: docs/HANDOFF.md; implementation/retained-frame-v1/README.md

### ELM-REN-008

The restore pipeline SHALL retain the original two-second deadline and its original start event across capture, retries, uploads and presentation checks.

Pattern: ubiquitous. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Delayed capture and retry injections fail at the original deadline.

Evidence obligation: docs/HANDOFF.md

### ELM-REN-009

IF cancellation invalidates a motion generation, THEN the native authority SHALL reject further effects and retire only resources owned by that generation.

Pattern: unwanted. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Late helper/frame receipt fault proves no focus or restore after cancellation.

Evidence obligation: docs/HANDOFF.md

### ELM-REN-010

WHEN motion reverses between minimize and restore, the renderer SHALL start the new trajectory from the last presented geometry of the current transaction.

Pattern: event-driven. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Native presentation sequence and geometry replay demonstrate continuity.

Evidence obligation: docs/HANDOFF.md; new reversal coverage

### ELM-REN-011

WHILE reduced motion is enabled, the native host SHALL complete the same minimize and restore state transitions without decorative motion.

Pattern: state-driven. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Native reduced-motion campaign compares final state and resources.

Evidence obligation: docs/HANDOFF.md

### ELM-REN-012

The capture service SHALL enforce declared limits on outstanding frames, native pixels and helper processes and publish refusals rather than silently reuse stale pixels.

Pattern: ubiquitous. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Pressure test records bounded ownership counts and explicit refusal receipts.

Evidence obligation: implementation/retained-frame-v1/README.md

### ELM-REN-013

WHEN a capture transaction ends, the native supervisor SHALL verify closure of owned helpers, callbacks, buffers and surfaces before reporting retirement complete.

Pattern: event-driven. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Fault/recovery packet records child exit status and zero owned resources.

Evidence obligation: docs/HANDOFF.md

### ELM-REN-014

The capture service SHALL label preview fidelity for client content, decorations and modal or popup extents according to independently verified native coverage.

Pattern: ubiquitous. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Decorated and out-of-base-popup pixel fixtures expose supported bounds.

Evidence obligation: implementation/retained-frame-v1/README.md

### ELM-REN-019

WHEN an output scale, transform or generation changes, the native renderer SHALL invalidate incompatible frame geometry and rebuild presentation against current output truth.

Pattern: event-driven. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Mixed-scale native screenshots and receipts confirm geometry revision changes.

Evidence obligation: docs/research/elm-pivot/ARCHITECTURE.md; new output coverage

### ELM-REN-021

WHERE 240 Hz hardware is available, WHILE motion is active, the native renderer SHALL sample motion in its native presentation loop and record cadence against a same-machine baseline.

Pattern: complex. Phase: P6. Priority: conditional. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: 240 Hz hardware packet records frame gaps, latency quantiles and hardware configuration.

Evidence obligation: docs/research/elm-pivot/ARCHITECTURE.md; new hardware coverage

### ELM-REN-022

The release gate SHALL distinguish renderer receipts from independent presentation evidence and report latency, memory, wakeups and resource growth against the chosen host baseline.

Pattern: ubiquitous. Phase: P6. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Comparison packet separates unsupported GPU/presentation spans and measured metrics.

Evidence obligation: implementation/capture-profile-v30/README.md

### ELM-REV-003

WHEN native lock, capture permission revocation or session replacement invalidates a capture generation, the authority SHALL cancel pending captures and revoke retained-lease publication access before subsequent scene publication.

Pattern: event-driven. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Queued-completion/lock, permission-revocation and session-replacement races with publication/generation/pixel receipts.

Evidence obligation: docs/elm-roadmap/audits/sol-architecture.json; docs/elm-roadmap/audits/sol-delivery.json

### ELM-REV-004

WHEN a locked session unlocks, the capture authority SHALL reconcile current authorization and source identity into a fresh publication generation before exposing previews, and SHALL retire revoked or prior-session leases.

Pattern: event-driven. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Unlock-before-late-callback, destroyed-source and revoked-lease fixtures; ownership ledger distinguishes private retention from presentation rights.

Evidence obligation: docs/elm-roadmap/audits/sol-architecture.json; docs/elm-roadmap/audits/sol-delivery.json

### ELM-REV-023

WHEN a native buffer is imported, the renderer SHALL wait for accepted acquire synchronization before sampling it and prohibit sampling after lease revocation or rendering-generation invalidation.

Pattern: event-driven. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

### ELM-REV-024

The broker SHALL issue opaque preview capabilities bound to authenticated frontend epoch, source incarnation and output generation, refusing unissued, wrong-session or revoked capabilities before foreign buffer access.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

### ELM-UI-014

WHEN the effective reduced-motion preference changes, the renderer SHALL apply the declared source/override policy without restart and settle decorative transitions without changing acknowledged targets, focus, original deadlines or resource ownership.

Pattern: event-driven. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Named native, keyboard and assistive-technology fixtures where applicable; independent observed results, exact identities, source hashes and frozen product-policy oracle.

Evidence obligation: docs/elm-roadmap/INTERACTION.md; new coverage: final UI/UX review

### ELM-UI-016

The preview view SHALL distinguish loading, authorized historical, current-live and unavailable source states visually and accessibly without borrowing pixels from another incarnation.

Pattern: ubiquitous. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Frozen threshold/policy plus independently observed named fixtures, native counters or user/AT records as applicable; hashes and failure outcomes retained.

Evidence obligation: docs/elm-roadmap/INTERACTION.md; new coverage: final UI/UX review

### ELM-UI-017

WHILE no visible consumer or required transition needs new content, the capture and rendering services SHALL suspend recurring preview acquisition, uploads and decorative work within the frozen quiescence interval while preserving authorized retained frames, control events and bounded cleanup.

Pattern: state-driven. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Frozen threshold/policy plus independently observed named fixtures, native counters or user/AT records as applicable; hashes and failure outcomes retained.

Evidence obligation: docs/elm-roadmap/INTERACTION.md; new coverage: final UI/UX review

### ELM-UI-018

WHEN reduced motion becomes enabled during window or overlay motion, the renderer SHALL settle at the next valid presentation opportunity without restarting deadlines or duplicating effects, and SHALL avoid replaying completed motion when the preference is disabled.

Pattern: event-driven. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Frozen threshold/policy plus independently observed named fixtures, native counters or user/AT records as applicable; hashes and failure outcomes retained.

Evidence obligation: docs/elm-roadmap/INTERACTION.md; new coverage: final UI/UX review

## elm-delivery

### ELM-DEL-001

The release plan SHALL preserve baseline source hashes, scenario identities, failures and original deadlines in an immutable migration ledger.

Pattern: ubiquitous. Phase: P0. Priority: must. Status: proposed. Owner: Release integration lead; verifier: Independent acceptance reviewer.

Verification: Diff archived hashes and inspect all inherited case mappings.

Evidence obligation: docs/HANDOFF.md

### ELM-DEL-002

The release plan SHALL assign an owner, engineer-week range, dependencies and acceptance evidence to each mandatory phase and separately estimate optional compositor work.

Pattern: ubiquitous. Phase: P0. Priority: must. Status: proposed. Owner: Release integration lead; verifier: Independent acceptance reviewer.

Verification: Review phase ledger against staffed capacity and dependency graph.

Evidence obligation: docs/elm-roadmap/ROADMAP.md

### ELM-DEL-003

The release builder SHALL pin compiler, Elm packages, test runner, JavaScript adapter, native dependencies and build-tool versions with source and artifact hashes.

Pattern: ubiquitous. Phase: P6. Priority: must. Status: proposed. Owner: Release integration lead; verifier: Independent acceptance reviewer.

Verification: Rebuild with the manifest and reject one altered dependency hash.

Evidence obligation: docs/research/elm-pivot/IMPLEMENTATION.md

### ELM-DEL-004

WHEN a release is rebuilt in two clean isolated environments, the builder SHALL produce identical distributable hashes or block release with the differing inputs recorded.

Pattern: event-driven. Phase: P6. Priority: must. Status: proposed. Owner: Release integration lead; verifier: Independent acceptance reviewer.

Verification: Compare SHA-256 manifests and retain differing build logs.

Evidence obligation: new coverage: reproducible build campaign

### ELM-DEL-005

The release package SHALL include an SBOM, upstream notices and a reviewed redistribution disposition for compiler, packages, host, native libraries and bundled assets.

Pattern: ubiquitous. Phase: P6. Priority: must. Status: proposed. Owner: Release integration lead; verifier: Independent acceptance reviewer.

Verification: Cross-check package files, SBOM components and license dispositions.

Evidence obligation: docs/research/elm-pivot/IMPLEMENTATION.md

### ELM-DEL-006

WHEN a host candidate is qualified, the host decision SHALL record compatible GTK and layer-shell major versions or Qt WebEngine initialization and transitive runtime dependencies.

Pattern: event-driven. Phase: P1. Priority: must. Status: proposed. Owner: Release integration lead; verifier: Independent acceptance reviewer.

Verification: Capture runtime loaded-library versions and native surface/IME/AT probes.

Evidence obligation: docs/research/elm-pivot/README.md

### ELM-DEL-007

The release package SHALL identify Arch Linux with Omarchy as the supported initial target and label other distributions unsupported until their dependency and native acceptance matrices pass.

Pattern: ubiquitous. Phase: P6. Priority: must. Status: proposed. Owner: Release integration lead; verifier: Independent acceptance reviewer.

Verification: Inspect support matrix; retain separate distro build and native verdicts.

Evidence obligation: docs/elm-roadmap/ROADMAP.md

### ELM-DEL-009

WHEN a component migration is selected, the launcher SHALL activate only that qualified component and retain a selectable working predecessor for rollback.

Pattern: event-driven. Phase: P3. Priority: must. Status: proposed. Owner: Release integration lead; verifier: Independent acceptance reviewer.

Verification: Exercise taskbar-only selection, conflicting owners and restoration.

Evidence obligation: docs/elm-roadmap/BASELINE.md

### ELM-DEL-016

WHEN a release is rolled back, the recovery tooling SHALL restore the preceding compatible settings copy without silently interpreting a newer schema.

Pattern: event-driven. Phase: P6. Priority: must. Status: proposed. Owner: Release integration lead; verifier: Independent acceptance reviewer.

Verification: Compare pre-upgrade and restored settings hashes in rollback drill.

Evidence obligation: new coverage: settings downgrade campaign

### ELM-DEL-018

WHEN a host or authority restarts, the supervisor SHALL invalidate old epochs and reconcile a fresh native snapshot before enabling new mutating requests.

Pattern: event-driven. Phase: P6. Priority: must. Status: proposed. Owner: Release integration lead; verifier: Independent acceptance reviewer.

Verification: Kill renderer and authority separately; inspect epochs and effect receipts.

Evidence obligation: docs/elm-roadmap/ROADMAP.md

### ELM-DEL-019

WHEN an upgrade is interrupted, the activation tooling SHALL recover to one complete validated release tuple and preserve user settings and application drafts.

Pattern: event-driven. Phase: P6. Priority: must. Status: proposed. Owner: Release integration lead; verifier: Independent acceptance reviewer.

Verification: Inject interruptions and compare tuple/settings/application inventories.

Evidence obligation: new coverage: interrupted upgrade drill

### ELM-DEL-020

The release SHALL provide an offline command-line recovery path that restores the preceding shell without a working Elm host or a main-compositor restart.

Pattern: ubiquitous. Phase: P6. Priority: must. Status: proposed. Owner: Release integration lead; verifier: Independent acceptance reviewer.

Verification: Disable Elm startup and network, execute recovery and record session identity.

Evidence obligation: docs/elm-roadmap/ROADMAP.md

### ELM-DEL-021

WHEN an owned session stops, the supervision SHALL stop clients and helpers, verify normal exits and retired resources, unload owned modules, and then stop its private compositor and bus.

Pattern: event-driven. Phase: P6. Priority: must. Status: proposed. Owner: Release integration lead; verifier: Independent acceptance reviewer.

Verification: Use protected qa_run.py; inspect exit status, empty clients and lease counts.

Evidence obligation: docs/HANDOFF.md

### ELM-DEL-022

IF a compositor and plugin ABI pair differs from the frozen accepted tuple, THEN the launcher SHALL refuse plugin loading and retain the working shell.

Pattern: unwanted. Phase: P6. Priority: must. Status: proposed. Owner: Release integration lead; verifier: Independent acceptance reviewer.

Verification: Supply a deliberately mismatched pair and retain refusal receipt.

Evidence obligation: AGENTS.md

### ELM-DEL-023

WHEN production activation is prepared, the release owner SHALL require one coherent source/runtime/ABI tuple with all mandatory native, model, CPU and user acceptance gates satisfied.

Pattern: event-driven. Phase: P6. Priority: must. Status: proposed. Owner: Release integration lead; verifier: Independent acceptance reviewer.

Verification: Audit case identities, original deadlines and separate verdict columns.

Evidence obligation: docs/HANDOFF.md

### ELM-DEL-024

The maintenance plan SHALL assign dependency-security triage, host-engine update cadence, regression owners and rollback responsibility for every supported release.

Pattern: ubiquitous. Phase: P6. Priority: must. Status: proposed. Owner: Release integration lead; verifier: Independent acceptance reviewer.

Verification: Runbook field/cadence validation and urgent/overdue-update tabletop; support admission fails if any required owner or numeric interval is missing.

Evidence obligation: new coverage: operational maintenance runbook

### ELM-DEL-025

WHEN the user acceptance session runs, the candidate SHALL preserve existing windows and drafts while demonstrating the named taskbar, focus, minimize, restore, pin, snap and keyboard flows.

Pattern: event-driven. Phase: P6. Priority: must. Status: proposed. Owner: Release integration lead; verifier: Independent acceptance reviewer.

Verification: Retain flow observations and before/after application inventory.

Evidence obligation: docs/HANDOFF.md

### ELM-DEL-026

The host qualification SHALL identify the actual GPU adapter, driver, backend and hardware-acceleration status on each pinned host/driver tuple before claiming accelerated rendering.

Pattern: ubiquitous. Phase: P1. Priority: must. Status: proposed. Owner: Release integration lead; verifier: Independent acceptance reviewer.

Verification: Capture engine diagnostics plus GPU submission/presentation evidence.

Evidence obligation: new coverage: GPU host qualification matrix

### ELM-DEL-027

IF hardware acceleration is unavailable or disabled, THEN the host SHALL report the active software fallback and qualify its performance independently without claiming GPU acceleration.

Pattern: unwanted. Phase: P1. Priority: must. Status: proposed. Owner: Release integration lead; verifier: Independent acceptance reviewer.

Verification: Compare enabled/disabled adapter reports and whole-process latency budgets.

Evidence obligation: new coverage: disabled acceleration campaign

### ELM-DEL-028

WHERE WebGPU is enabled, the host SHALL require a qualified adapter and device, retain an accepted non-WebGPU rendering route, and invalidate GPU resources on device loss before recovery.

Pattern: optional. Phase: P4. Priority: conditional. Status: proposed. Owner: Release integration lead; verifier: Independent acceptance reviewer.

Verification: Record adapter/device limits, loss injection, lease retirement and recovered frames.

Evidence obligation: new coverage: WebGPU adapter and device-loss campaign

### ELM-REV-028

WHEN the machine resumes from suspend, the native host SHALL invalidate changed output and rendering generations, reconcile a fresh snapshot and refuse replay of pre-suspend mutating intents.

Pattern: event-driven. Phase: P6. Priority: must. Status: proposed. Owner: Release integration lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

## elm-gpu

### ELM-GPU-001

The host selector SHALL require hardware-accelerated rendering by the shell webview’s own nonsoftware backend before host selection and accelerated release admission, separately from native preview or WebGPU execution.

Pattern: ubiquitous. Phase: P1. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Pinned engine/driver diagnostics plus a deterministic displayed workload on a nonsoftware device.

Evidence obligation: docs/elm-roadmap/GPU.md; docs/elm-roadmap/gpu-inventory.json

### ELM-GPU-002

The graphics qualification SHALL distinguish hardware discovery, native GPU rendering, accelerated webview composition and WebGPU adapter/device execution as separate evidence claims.

Pattern: ubiquitous. Phase: P0. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Evidence ledger with four separate verdicts linked to executed probes.

Evidence obligation: docs/elm-roadmap/GPU.md; docs/elm-roadmap/gpu-inventory.json

### ELM-GPU-003

WHEN WebGPU is evaluated, the native host SHALL expose bundled assets through a qualified secure local origin without disabling renderer sandboxing.

Pattern: event-driven. Phase: P1. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Origin/security-state probe, effective sandbox flags and denied remote navigation.

Evidence obligation: docs/elm-roadmap/GPU.md; docs/elm-roadmap/gpu-inventory.json

### ELM-GPU-004

WHEN a WebGPU adapter or device is unavailable, the host SHALL record WebGPU as unqualified and continue evaluation of alternative hardware paths; host selection SHALL remain blocked until at least one complete webview hardware path qualifies.

Pattern: event-driven. Phase: P1. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Null-adapter, rejected-device and unsupported-feature fault reports.

Evidence obligation: docs/elm-roadmap/GPU.md; docs/elm-roadmap/gpu-inventory.json

### ELM-GPU-005

WHEN WebGPU evaluation obtains a nonsoftware adapter and device, the host SHALL verify deterministic render and compute results against supported limits and features and independently observe the native displayed frame.

Pattern: event-driven. Phase: P1. Priority: conditional. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: WGSL validation/readback results plus output capture and backend classification.

Evidence obligation: docs/elm-roadmap/GPU.md; docs/elm-roadmap/gpu-inventory.json

### ELM-GPU-006

WHILE GPU effects are active, the renderer SHALL own GPU objects locally and keep per-frame pixel buffers outside Elm port messages.

Pattern: state-driven. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: IPC payload and resource-allocation traces over motion/reversal workload.

Evidence obligation: docs/elm-roadmap/GPU.md; docs/elm-roadmap/gpu-inventory.json

### ELM-GPU-007

WHEN any GPU device used by shell composition or preview import is lost, the host SHALL invalidate its dependent objects and rendering generation and revalidate current lease identity, output and scene state before new presentation, without replaying stale window effects.

Pattern: event-driven. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Device-loss injection and generation/effect logs with no stale native mutation.

Evidence obligation: docs/elm-roadmap/GPU.md; docs/elm-roadmap/gpu-inventory.json

### ELM-GPU-008

The preview qualification SHALL measure actual native-buffer import, synchronization and copy volume instead of inferring zero-copy support from WebGPU availability.

Pattern: ubiquitous. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Native fence/import trace and copy bytes/counts on both GPU configurations.

Evidence obligation: docs/elm-roadmap/GPU.md; docs/elm-roadmap/gpu-inventory.json

### ELM-GPU-009

IF every qualified GPU path becomes unavailable, THEN the host SHALL expose essential recovery controls in a disclosed degraded mode and block accelerated release admission.

Pattern: unwanted. Phase: P6. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: All-backend-failure fault plus offline recovery/qualification report.

Evidence obligation: docs/elm-roadmap/GPU.md; docs/elm-roadmap/gpu-inventory.json

### ELM-GPU-010

The GPU qualification SHALL compare integrated and discrete execution, where selectable, against frozen latency, memory, power and transfer budgets on the actual output configuration.

Pattern: ubiquitous. Phase: P1. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Hardware profile manifest and controlled sample distributions including cross-GPU transfers.

Evidence obligation: docs/elm-roadmap/GPU.md; docs/elm-roadmap/gpu-inventory.json

### ELM-REV-019

IF device loss invalidates the only accepted storage for a retained frame, THEN the broker SHALL atomically revoke and retire that lease and publish an explicit unavailable-preview state rather than reuse invalid objects or label historical pixels as current.

Pattern: unwanted. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

### ELM-REV-022

IF preview copy volume, acquire-fence wait or cross-GPU transfer exceeds its frozen budget, THEN the preview qualification SHALL reject that import route and preserve a qualified native route or an explicit unavailable state.

Pattern: unwanted. Phase: P4. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

### ELM-REV-025

WHEN the active adapter, driver or engine differs from its qualified tuple, the host SHALL invalidate that acceleration verdict and require matching qualification before presenting the configuration as an accelerated release.

Pattern: event-driven. Phase: P1. Priority: must. Status: proposed. Owner: Graphics lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

## elm-host

### ELM-ARC-001

The Elm desktop SHALL record the deployed compositor, plugin, shell, compiler and host versions and source hashes before a comparative native run.

Pattern: ubiquitous. Phase: P0. Priority: must. Status: proposed. Owner: Native host lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: the report identifies every participating artifact; artifact hashes and matching scenario receipts included.

Evidence obligation: implementation/STATUS.md

### ELM-ARC-002

The Elm desktop SHALL assign DOM presentation to Elm, Wayland surface lifetime to the native host, and application-window effects to native authority.

Pattern: ubiquitous. Phase: P1. Priority: must. Status: proposed. Owner: Native host lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: only native authority mutates the application window; artifact hashes and matching scenario receipts included.

Evidence obligation: docs/research/elm-pivot/ARCHITECTURE.md

### ELM-ARC-021

The Elm desktop SHALL compare GTK/WebKitGTK and a dedicated Qt/WebEngine host using the same Elm assets, compositor tuple, workload and measurement definitions.

Pattern: ubiquitous. Phase: P1. Priority: must. Status: proposed. Owner: Native host lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: separate native results and resource measurements are retained; artifact hashes and matching scenario receipts included.

Evidence obligation: docs/research/elm-pivot/ARCHITECTURE.md

### ELM-ARC-022

The Elm desktop SHALL create native layer and popup roles, input regions and keyboard-interactivity settings before exposing their Elm views.

Pattern: ubiquitous. Phase: P1. Priority: must. Status: proposed. Owner: Native host lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: roles and input masks precede frontend readiness; artifact hashes and matching scenario receipts included.

Evidence obligation: docs/research/elm-pivot/ARCHITECTURE.md

### ELM-ARC-023

The Elm desktop SHALL pass native host tests for IME preedit, keyboard navigation, Orca and braille, clipboard, file drag-and-drop, fractional scale and negative output coordinates.

Pattern: ubiquitous. Phase: P5. Priority: must. Status: proposed. Owner: Native host lead; verifier: Independent acceptance reviewer.

Verification: All eight named host compatibility routes pass with native/AT evidence; a separate gate fixture verifies a missing/failed route blocks qualification.

Evidence obligation: docs/research/elm-pivot/ARCHITECTURE.md

### ELM-ARC-024

The Elm desktop SHALL load packaged shell assets from an allowlisted local origin and deny remote navigation, arbitrary native method invocation and unapproved resource URLs.

Pattern: ubiquitous. Phase: P1. Priority: must. Status: proposed. Owner: Native host lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: navigation or capability access is denied; artifact hashes and matching scenario receipts included.

Evidence obligation: new coverage: hostile document and resource-origin probes

### ELM-ARC-026

WHEN the frontend, renderer or native authority restarts, the native authority SHALL invalidate old epochs and resources and install a fresh coherent snapshot before admitting effects.

Pattern: event-driven. Phase: P2. Priority: must. Status: proposed. Owner: Native host lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: old work is refused and effects await snapshot reconciliation; failure injection and artifact hashes included.

Evidence obligation: docs/research/elm-pivot/README.md

### ELM-ARC-027

WHEN Elm shell activation fails its release checks, the Elm desktop SHALL restore the recorded accepted shell configuration without restarting the compositor or closing application windows.

Pattern: event-driven. Phase: P6. Priority: must. Status: proposed. Owner: Native host lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: the accepted shell returns and drafts remain connected; artifact hashes and matching scenario receipts included.

Evidence obligation: implementation/taskbar-v3/deployment.json

### ELM-TEA-001

The Elm frontend SHALL represent lifecycle, receipt and operation state with custom types, keep native observations separate from desired UI state and derive projections from one authoritative snapshot without duplicated native authority.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Native host lead; verifier: Independent acceptance reviewer.

Verification: Typed compiler checks, deterministic replay and independent boundary fixtures with source hashes; native behavior qualified separately.

Evidence obligation: docs/elm-roadmap/ELM-PRACTICES.md; official Elm corpus

### ELM-TEA-002

The Elm frontend SHALL implement state transitions as pure Model and Msg reducers with typed effect descriptions, and SHALL reproduce identical models and effects for identical sanitized message histories.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Native host lead; verifier: Independent acceptance reviewer.

Verification: Typed compiler checks, deterministic replay and independent boundary fixtures with source hashes; native behavior qualified separately.

Evidence obligation: docs/elm-roadmap/ELM-PRACTICES.md; official Elm corpus

### ELM-TEA-003

The Elm frontend SHALL sequence dependent native effects through matching committed receipts, reserve Cmd.batch for independent effects and validate observations at typed decoders before model mutation.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Native host lead; verifier: Independent acceptance reviewer.

Verification: Typed compiler checks, deterministic replay and independent boundary fixtures with source hashes; native behavior qualified separately.

Evidence obligation: docs/elm-roadmap/ELM-PRACTICES.md; official Elm corpus

### ELM-TEA-004

The Elm frontend SHALL derive recurring subscriptions from visible consumers and active transactions while preserving ordered native control and revocation delivery independently of overlay visibility.

Pattern: ubiquitous. Phase: P3. Priority: must. Status: proposed. Owner: Native host lead; verifier: Independent acceptance reviewer.

Verification: Typed compiler checks, deterministic replay and independent boundary fixtures with source hashes; native behavior qualified separately.

Evidence obligation: docs/elm-roadmap/ELM-PRACTICES.md; official Elm corpus

### ELM-TEA-005

The Elm host adapter SHALL keep JavaScript limited to validated transport and approved host integrations, keep GPU resources and per-frame work outside Elm messages and use current commands and subscriptions rather than historical Signal APIs.

Pattern: ubiquitous. Phase: P1. Priority: must. Status: proposed. Owner: Native host lead; verifier: Independent acceptance reviewer.

Verification: Typed compiler checks, deterministic replay and independent boundary fixtures with source hashes; native behavior qualified separately.

Evidence obligation: docs/elm-roadmap/ELM-PRACTICES.md; official Elm corpus

## elm-layering

### ELM-GNO-001

The Elm desktop SHALL record a precedence and eligibility table covering ordinary, maximized, pinned, fullscreen, transient, popup, shell and inactive-workspace surfaces before native layering acceptance.

Pattern: ubiquitous. Phase: P0. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Frozen scene/model trace plus native paint and input receipts proving: their precedence and eligibility are explicitly recorded. Retain scenario identity and source/ABI hashes.

Evidence obligation: docs/elm-roadmap/contributions/gnome-layering.md

### ELM-GNO-002

WHILE an application window is minimized or absent from the current output effective workspace set including explicit sticky membership, the Elm desktop SHALL exclude its live surface from ordinary paint and hit candidates regardless of convenience visibility or fullscreen-permission flags.

Pattern: state-driven. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Frozen scene/model trace plus native paint and input receipts proving: neither list contains the source window. Retain scenario identity and source/ABI hashes.

Evidence obligation: docs/elm-roadmap/contributions/gnome-layering.md: user-supplied Heroic counterexample

### ELM-GNO-003

The Elm desktop SHALL determine native scene eligibility before applying layer or fullscreen precedence.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Frozen scene/model trace plus native paint and input receipts proving: the permission does not restore the excluded window. Retain scenario identity and source/ABI hashes.

Evidence obligation: docs/elm-roadmap/reference/mutter/src__core__window.c

### ELM-GNO-004

The Elm desktop SHALL preserve eligible child-above-owner constraints across native layer changes without promoting unrelated ordinary members of the application group.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Frozen scene/model trace plus native paint and input receipts proving: the child remains above its owner without promoting the peer. Retain scenario identity and source/ABI hashes.

Evidence obligation: docs/elm-roadmap/reference/mutter/src__core__stack.c

### ELM-GNO-005

IF native family constraints are cyclic or inconsistent, THEN the Elm desktop SHALL refuse the affected scene transaction without publishing a partially solved paint or hit order.

Pattern: unwanted. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Frozen scene/model trace plus native paint and input receipts proving: no partial scene is published and the refusal is recorded. Retain scenario identity and source/ABI hashes.

Evidence obligation: new coverage: cyclic family scene transaction fixtures

### ELM-GNO-006

The Elm desktop SHALL derive ordinary native paint order and pointer hit order from the same committed scene revision, with explicit native input-region and modal-redirection exceptions.

Pattern: ubiquitous. Phase: P3. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Frozen scene/model trace plus native paint and input receipts proving: the visible top eligible surface receives input unless a recorded native exception applies. Retain scenario identity and source/ABI hashes.

Evidence obligation: implementation/maximized-stack-v2/native-stack-smoke-1791036734961323596.json

### ELM-GNO-007

WHEN a pinned window is maximized or restored, the Elm desktop SHALL preserve its pin policy and eligible transient-family precedence until an acknowledged unpin operation changes that policy.

Pattern: event-driven. Phase: P3. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Frozen scene/model trace plus native paint and input receipts proving: pin state persists and its dialog remains above it. Retain scenario identity and source/ABI hashes.

Evidence obligation: docs/HANDOFF.md; docs/elm-roadmap/reference/mutter/src__core__window.c

### ELM-GNO-008

WHILE a minimized or inactive application retains an animation or preview resource, the Elm desktop SHALL expose that resource only as a noninteractive visual object and retire it through native lifetime authority.

Pattern: state-driven. Phase: P4. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Frozen scene/model trace plus native paint and input receipts proving: the source receives no input and native retirement is evidenced. Retain scenario identity and source/ABI hashes.

Evidence obligation: docs/elm-roadmap/reference/mutter/src__compositor__meta-window-actor.c

### ELM-GNO-009

WHEN workspace visibility changes before native effect admission, the native authority SHALL validate current dependency revisions and eligibility at the commit point and refuse any stale or ineligible request without mutation.

Pattern: event-driven. Phase: P3. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Frozen scene/model trace plus native paint and input receipts proving: the stale target receives no effect and reconciliation is recorded. Retain scenario identity and source/ABI hashes.

Evidence obligation: new coverage: workspace generation race native fixtures

### ELM-KDE-001

The native authority SHALL publish one committed constrained stack revision for ordinary scene ordering, hit testing and focus resolution.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Revision-correlated native pixel/hit/focus trace shows one canonical commit.

Evidence obligation: docs/elm-roadmap/reference/kwin/src__layers.cpp: Workspace::updateStackingOrder; input.cpp: findToplevel; windowitem.cpp: updateStackingOrder

### ELM-KDE-002

The native authority SHALL classify layer precedence from type, pin, fullscreen, family and output context only after committed eligibility filtering, without reintroducing any excluded surface.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Policy matrix replay plus native overlap/fullscreen tests.

Evidence obligation: docs/elm-roadmap/reference/kwin/src__window.cpp: belongsToLayer and isActiveFullScreen

### ELM-KDE-003

WHEN a transient family changes, the native authority SHALL recompute parent-child constraints and preserve documented sibling order before committing the stack.

Pattern: event-driven. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Constraint replay and native modal pixel/hit observations.

Evidence obligation: docs/elm-roadmap/reference/kwin/src__layers.cpp: constrainedStackingOrder; workspace.cpp: constrain/unconstrain

### ELM-KDE-004

IF a window belongs to an inactive special workspace, THEN the native eligibility SHALL exclude its ordinary live painting, pointer targeting and direct focus despite permissive cached visibility or input flags.

Pattern: unwanted. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Native inactive-special pixel, click and explicit-focus probes reject the hidden window.

Evidence obligation: docs/elm-roadmap/reference/kwin/New Heroic fixture: visible=true, acceptsInput=true, allowedOverFullscreen=true, specialWorkspace.id=0

### ELM-KDE-005

The native authority SHALL derive ordinary paint, hit and focus eligibility from the same committed workspace, minimize, hidden, lock and incarnation state.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: State-race fault tests record matching revision and exclusion rationale.

Evidence obligation: docs/elm-roadmap/reference/kwin/src__input.cpp: findToplevel; windowitem.cpp: computeVisibility

### ELM-KDE-006

WHILE a preview or animation actor represents an ineligible application, the native host SHALL exclude the actor from ordinary application hit and focus targeting; any interactive shell preview control SHALL use a separate identity and validated restore intent.

Pattern: state-driven. Phase: P4. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Native minimize/overview tests show visible animation proxies do not steal input.

Evidence obligation: docs/elm-roadmap/reference/kwin/src__scene__windowitem.cpp: force-visible counters and elevation; input.cpp: hidden/minimized exclusion

### ELM-KDE-007

WHEN a modal focus request is accepted, the native authority SHALL resolve the current eligible modal family before selecting the committed focus recipient.

Pattern: event-driven. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Native draft/modal tests record focus target and preserve unrelated drafts.

Evidence obligation: docs/elm-roadmap/reference/kwin/src__window.cpp: modality helpers; new GTK/Qt/Xwayland acceptance

### ELM-KDE-008

WHEN fullscreen activation or output membership changes, the native authority SHALL recompute fullscreen and pin layering from current output and family state.

Pattern: event-driven. Phase: P5. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Multi-output native pixel/hit matrix records explicit Windows-policy differences.

Evidence obligation: docs/elm-roadmap/reference/kwin/src__window.cpp: isActiveFullScreen; belongsToLayer

### ELM-KDE-009

IF an intent references stale target, family, output or eligibility dependency revisions, THEN the native authority SHALL refuse it without mutation and reconcile observations; any later effect SHALL require a distinct newly validated request.

Pattern: unwanted. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Delayed-intent faults produce refusal/reconciliation without hidden-window focus.

Evidence obligation: docs/elm-roadmap/reference/kwin/Engineering inference from pinned KWin canonical order; bridge architecture

### ELM-LAY-001

IF a window is minimized or belongs to an inactive nonsticky workspace, THEN the native authority SHALL exclude its live surface from display and application input regardless of prior raise or fullscreen permissions.

Pattern: unwanted. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Protected native pixel/hit/focus fixture reproducing the recorded Heroic-versus-terminal symptom with visibility, stack and generation receipts.

Evidence obligation: docs/elm-roadmap/heroic-layering-observation.json

### ELM-LAY-002

WHEN a scene revision is committed, the native authority SHALL derive painting, hit testing and focus eligibility from the same accepted surface identities and ordered scene revision.

Pattern: event-driven. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Native opaque overlap, input-transparent-region and modal-owner fixtures record one constrained scene revision, independent overlap pixels, input region/hit recipient and documented focus outcome; a Heroic-only run cannot qualify this requirement.

Evidence obligation: docs/elm-roadmap/heroic-layering-observation.json

### ELM-LAY-003

WHEN a minimized window is restored, the native authority SHALL make it eligible in one accepted scene transition while preserving its normal workspace identity and rejecting old transition generations.

Pattern: event-driven. Phase: P3. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Record original workspace identity, old/new scene and operation generations, live input candidate count, overlay retirement and stale-callback rejection through actual restore handoff.

Evidence obligation: docs/elm-roadmap/heroic-layering-observation.json

### ELM-REV-013

WHILE a window is maximized but unpinned and not true-fullscreen, the native authority SHALL retain it in the ordinary application band.

Pattern: state-driven. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

### ELM-REV-014

The native host SHALL bound ordinary shell input regions to current interactive geometry and allow input-transparent regions to pass through to eligible underlying native surfaces.

Pattern: ubiquitous. Phase: P1. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

### ELM-REV-015

The native input and render paths SHALL consume committed native scene state without synchronously awaiting Elm or webview replies.

Pattern: ubiquitous. Phase: P1. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

### ELM-REV-016

The native authority SHALL distinguish live-scene eligibility from shell enumeration, allowing minimized window entries in taskbar, switcher and Task View without granting their live surfaces paint or input authority.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

### ELM-REV-017

WHILE a transient owner is minimized or excluded from the active scene, the native authority SHALL exclude its dependent transient descendants in the same revision until current native family policy accepts an independent or reparented state.

Pattern: state-driven. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

### ELM-REV-018

WHILE native session lock is active, the host SHALL withdraw ordinary shell keyboard and pointer eligibility and prevent shell priority or pin/fullscreen flags from bypassing native lock-surface authority.

Pattern: state-driven. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

### ELM-REV-032

The P0 native-layering workstream SHALL qualify existing-compositor eligibility and MAX corrections against frozen native cases independently of Elm webview host selection, without restarting the main session during isolated QA.

Pattern: ubiquitous. Phase: P0. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

### ELM-REV-033

The native authority SHALL redirect blocked-parent activation to an eligible modal without synthesizing a modal click, and SHALL retire an inert transition proxy atomically before publishing the restored live surface as interactive.

Pattern: ubiquitous. Phase: P3. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Independent named fixture receipts with native scene/protocol traces, artifact hashes and explicit pass/fail verdicts.

Evidence obligation: new coverage: independent audit correction

## elm-native-bridge

### ELM-ARC-003

The Elm desktop SHALL expose one incoming event stream and one outgoing intent stream with versioned, discriminated envelopes.

Pattern: ubiquitous. Phase: P1. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: both conform to the recorded schema; artifact hashes and matching scenario receipts included.

Evidence obligation: docs/research/elm-pivot/IMPLEMENTATION.md

### ELM-ARC-004

IF an envelope is malformed or has an unsupported protocol version, THEN the Elm desktop SHALL reject it without a native effect and record the rejection reason.

Pattern: unwanted. Phase: P1. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: no compositor action occurs and a reason is recorded; failure injection and artifact hashes included.

Evidence obligation: new coverage: bridge decoder and authority negative fixtures

### ELM-ARC-005

The Elm desktop SHALL attach request identity, compositor lifetime, frontend epoch, operation generation, window incarnation, output generation and expected native revision to window-effect intents.

Pattern: ubiquitous. Phase: P1. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: the serialized request contains the full authority tuple; artifact hashes and matching scenario receipts included.

Evidence obligation: docs/research/elm-pivot/ARCHITECTURE.md

### ELM-ARC-006

IF an intent incarnation, authority epoch or expected dependency revision differs from current native authority, THEN the native authority SHALL refuse that request without mutation; reconciliation SHALL produce a new snapshot and never silently convert it into a commit.

Pattern: unwanted. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: the new window remains unchanged; failure injection and artifact hashes included.

Evidence obligation: docs/HANDOFF.md

### ELM-ARC-007

The Elm desktop SHALL correlate each outcome with its request and represent Pending, Committed, Refused, Cancelled and Unknown as distinct states.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: its state is Unknown rather than Committed; artifact hashes and matching scenario receipts included.

Evidence obligation: docs/research/elm-pivot/ARCHITECTURE.md

### ELM-ARC-008

WHEN a dependent mutation is requested, the authority SHALL release it only after a correlated Committed prerequisite satisfies the same incarnation and generation; Pending, Refused, Cancelled and Unknown SHALL leave it withheld.

Pattern: event-driven. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Dependency fixtures cover Pending, Refused, Cancelled, Unknown, wrong incarnation/generation and a matching Committed prerequisite.

Evidence obligation: docs/research/elm-pivot/README.md

### ELM-ARC-009

WHEN a duplicate request is received within a frontend epoch, the Elm desktop SHALL return the existing request disposition without executing the effect again.

Pattern: event-driven. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: only one mutation is recorded; failure injection and artifact hashes included.

Evidence obligation: new coverage: authority idempotency ledger

### ELM-ARC-010

WHEN a snapshot is installed, the Elm desktop SHALL apply only ordered events after its native sequence watermark and request reconciliation on a sequence gap.

Pattern: event-driven. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: 9 is discarded and the gap before 12 triggers reconciliation; artifact hashes and matching scenario receipts included.

Evidence obligation: implementation/taskbar-v3/widget_v68/SnapshotStream.js

### ELM-ARC-011

The Elm desktop SHALL capture modifier press, repeat, release and Escape in native order with chord generation and ordinal before frontend readiness.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: the ready view receives the release in its original chord order; artifact hashes and matching scenario receipts included.

Evidence obligation: implementation/STATUS.md

### ELM-ARC-012

WHEN native effect admission executes, the authority SHALL validate cancellation, incarnation and dependency revisions in the same serialized critical section as its commit point; cancellation ordered before commit SHALL prevent mutation and retire that generation’s resources.

Pattern: event-driven. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Controlled native interleavings at one defined linearization point; cancellation-before versus commit-before outcomes are distinct, acknowledged and resource-bounded.

Evidence obligation: docs/HANDOFF.md

### ELM-ARC-013

The Elm desktop SHALL retain each original acceptance deadline through retries, queueing, reconciliation and frontend restart.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: the deadline remains unchanged; artifact hashes and matching scenario receipts included.

Evidence obligation: docs/HANDOFF.md

### ELM-ARC-014

IF an effect outcome is Unknown, THEN the Elm desktop SHALL reconcile native state before permitting a retry of that effect.

Pattern: unwanted. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: native truth is read before another mutation; failure injection and artifact hashes included.

Evidence obligation: docs/research/elm-pivot/IMPLEMENTATION.md

### ELM-ARC-015

The Elm desktop SHALL enforce configured byte and item bounds on bridge queues, coalesce replaceable observations, and reject new effect work explicitly when admission fails.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: memory remains bounded and effect refusal is explicit; artifact hashes and matching scenario receipts included.

Evidence obligation: docs/HANDOFF.md

### ELM-ARC-016

The Elm desktop SHALL reserve bounded control capacity for cancellation, receipts and retirement independently of preview work.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: it uses reserved control capacity and is processed; artifact hashes and matching scenario receipts included.

Evidence obligation: docs/research/elm-pivot/ARCHITECTURE.md

### ELM-ARC-017

The Elm desktop SHALL use one canonical owner for cross-output snap, pin and switcher transactions and send read-only projections to display views.

Pattern: ubiquitous. Phase: P3. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: one authority serializes the transaction; artifact hashes and matching scenario receipts included.

Evidence obligation: docs/research/elm-pivot/README.md

### ELM-ARC-018

The Elm desktop SHALL resolve modal-family focus, input blockers, stacking and hit testing from native authority rather than DOM state.

Pattern: ubiquitous. Phase: P3. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: the native family policy determines focus and hit order; artifact hashes and matching scenario receipts included.

Evidence obligation: implementation/maximized-stack-v2/native-stack-smoke-1791036734961323596.json

### ELM-ARC-019

The Elm desktop SHALL transport preview identifiers and revisions through ports while native components retain pixel buffers and verify source-stop lifetime.

Pattern: ubiquitous. Phase: P4. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: the valid retained frame remains available without JSON pixels; artifact hashes and matching scenario receipts included.

Evidence obligation: implementation/STATUS.md

### ELM-ARC-020

The Elm desktop SHALL distinguish native effect receipts from native frame-presentation receipts and keep motion sampling and buffer retirement under native ownership.

Pattern: ubiquitous. Phase: P4. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: presentation is unproven until the native receipt; artifact hashes and matching scenario receipts included.

Evidence obligation: docs/research/elm-pivot/ARCHITECTURE.md

### ELM-ARC-025

IF a compositor plugin does not match its recorded owning compositor ABI tuple, THEN the Elm desktop SHALL refuse plugin loading.

Pattern: unwanted. Phase: P1. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: the plugin is not loaded and the mismatch is reported; failure injection and artifact hashes included.

Evidence obligation: implementation/maximized-stack-v2/PAIR_READY.json

### ELM-ARC-028

WHERE native compositor replacement is selected, the Elm desktop SHALL require a separate feasibility record covering Wayland protocols, Xwayland, seats, outputs, rendering, IME, capture security and application compatibility before implementation admission.

Pattern: optional. Phase: P7. Priority: conditional. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: a separate scope and feasibility gate controls admission; artifact hashes and matching scenario receipts included.

Evidence obligation: docs/research/elm-pivot/ARCHITECTURE.md

### ELM-ARC-029

WHERE native compositor replacement is implemented, the Elm desktop SHALL pass its declared compatibility matrix in nested and hardware sessions with sacrificial applications before any main-session activation.

Pattern: optional. Phase: P8. Priority: conditional. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Preserved scenario report with native or bridge trace showing: nested and hardware evidence precedes main-session use; artifact hashes and matching scenario receipts included.

Evidence obligation: new coverage: optional compositor native acceptance matrix

### ELM-REV-001

WHEN stale global scene state delays a valid activation, the authority SHALL reconcile current dependencies and use a distinct freshly validated request to reach a terminal result by the original deadline without waiting for unrelated scene activity to stop.

Pattern: event-driven. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Continuous unrelated-window-motion fixture plus target-invalidated control; valid activation commits after safe dependency revalidation and invalid target is refused.

Evidence obligation: docs/elm-roadmap/audits/sol-architecture.json; docs/elm-roadmap/audits/sol-delivery.json

### ELM-REV-007

The bridge SHALL encode authority identities, generations, revisions and absolute native deadlines as lossless schema-defined canonical strings and reject numeric JSON values for those fields.

Pattern: ubiquitous. Phase: P1. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

### ELM-REV-008

WHEN an event sequence gap occurs, the frontend SHALL withhold later deltas and new effect admission until a coherent reconciliation snapshot establishes a fresh contiguous watermark.

Pattern: event-driven. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

### ELM-REV-009

The bridge SHALL preserve native order for chord press, repeat, release, Escape, cancellation, effect receipts and retirement receipts; observation coalescing SHALL exclude those control events.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

### ELM-REV-010

IF reserved control capacity cannot admit a cancellation or receipt, THEN the authority SHALL stop new effect admission, invalidate uncertain pending generations and supervise reconciliation without silently losing cancellation.

Pattern: unwanted. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

### ELM-REV-011

IF a request identity is expired, retired or outside its bounded deduplication window, THEN the authority SHALL refuse it without mutation and record an expired-identity outcome.

Pattern: unwanted. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

### ELM-REV-012

The authority SHALL measure effect and restore deadlines in one documented native monotonic clock domain, preserving their time origin through queueing and restart without wall-clock reinterpretation.

Pattern: ubiquitous. Phase: P1. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

### ELM-REV-034

The protocol schema SHALL version capability negotiation, lossless identities, queue classes, byte and item bounds, admission refusals and control-event failure outcomes before bridge implementation admission.

Pattern: ubiquitous. Phase: P1. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Independent named fixture receipts with native scene/protocol traces, artifact hashes and explicit pass/fail verdicts.

Evidence obligation: new coverage: independent audit correction

## elm-native-compositor

### ELM-REN-023

WHERE a compositor replacement is selected, the project SHALL document a native Rust or C++ execution boundary and an Elm policy interface before implementation.

Pattern: optional. Phase: P7. Priority: conditional. Status: proposed. Owner: Native compositor lead; verifier: Independent acceptance reviewer.

Verification: Reviewed feasibility decision records staffing, excluded scope and native authority.

Evidence obligation: docs/research/elm-pivot/ARCHITECTURE.md

### ELM-REN-024

WHERE compositor replacement is selected, the native compositor SHALL implement a versioned Wayland and Xwayland compatibility matrix with explicit unsupported cases.

Pattern: optional. Phase: P8. Priority: conditional. Status: proposed. Owner: Native compositor lead; verifier: Independent acceptance reviewer.

Verification: Nested client matrix covers Brave, GTK, Qt and X11 lifecycle and modality.

Evidence obligation: docs/research/elm-pivot/ARCHITECTURE.md; new compatibility coverage

### ELM-REN-025

WHERE compositor replacement is selected, the native compositor SHALL own DRM/KMS outputs, seat input and session transitions independently of Elm responsiveness.

Pattern: optional. Phase: P8. Priority: conditional. Status: proposed. Owner: Native compositor lead; verifier: Independent acceptance reviewer.

Verification: Hardware campaign logs modes, input, suspend/resume and hotplug recovery.

Evidence obligation: new native backend coverage

### ELM-REN-026

WHERE compositor replacement is selected, the native compositor SHALL provide tested IME, preedit and text-input integration for its supported application matrix.

Pattern: optional. Phase: P8. Priority: conditional. Status: proposed. Owner: Native compositor lead; verifier: Independent acceptance reviewer.

Verification: Native multilingual preedit/commit tests cover GTK, Qt, browser and Xwayland support.

Evidence obligation: docs/research/elm-pivot/ARCHITECTURE.md; new IME coverage

### ELM-REN-027

WHERE compositor replacement is selected, the native compositor SHALL gate capture and remote-control access through documented portal and permission boundaries.

Pattern: optional. Phase: P8. Priority: conditional. Status: proposed. Owner: Native compositor lead; verifier: Independent acceptance reviewer.

Verification: Consent, denial, revocation and cross-session capture tests record no unauthorized frames.

Evidence obligation: docs/research/elm-pivot/ARCHITECTURE.md; new portal coverage

### ELM-REN-028

WHERE compositor replacement is selected, the native compositor SHALL validate client requests and isolate privileged protocols from untrusted shell content.

Pattern: optional. Phase: P8. Priority: conditional. Status: proposed. Owner: Native compositor lead; verifier: Independent acceptance reviewer.

Verification: Malformed-client fuzzing and lock/input/capture isolation results identify residual risks.

Evidence obligation: new compositor security coverage

### ELM-REN-029

WHERE compositor replacement is selected, the native compositor SHALL retain frame scheduling, fences, hit testing and buffer retirement in native loops without awaiting Elm port replies.

Pattern: optional. Phase: P8. Priority: conditional. Status: proposed. Owner: Native compositor lead; verifier: Independent acceptance reviewer.

Verification: Injected frontend stalls preserve native frame/input progress and bounded ownership.

Evidence obligation: docs/research/elm-pivot/ARCHITECTURE.md

### ELM-REN-030

WHERE compositor replacement is selected, the deployment plan SHALL provide tested session fallback and recovery instructions that disclose loss of application connections on compositor failure.

Pattern: optional. Phase: P8. Priority: conditional. Status: proposed. Owner: Native compositor lead; verifier: Independent acceptance reviewer.

Verification: Recovery drill logs shell-only restart separately from compositor crash and fallback login.

Evidence obligation: docs/HANDOFF.md; docs/research/elm-pivot/ARCHITECTURE.md

## elm-performance

### ELM-QA-021

The performance owner SHALL freeze measured current-shell workload baselines and numeric absolute and regression budgets before host selection or release evaluation.

Pattern: ubiquitous. Phase: P0. Priority: must. Status: proposed. Owner: Performance qualification lead; verifier: Independent acceptance reviewer.

Verification: Versioned budgets.json contains measured baseline, units, workload, hardware and approved thresholds; missing values block evaluation.

Evidence obligation: docs/elm-roadmap/ROADMAP.md: Performance qualification

### ELM-QA-022

The performance verifier SHALL compare host candidates and the current shell using identical workloads and report p50, p95, p99, sample counts, cold/warm state and instrumentation overhead.

Pattern: ubiquitous. Phase: P1. Priority: must. Status: proposed. Owner: Performance qualification lead; verifier: Independent acceptance reviewer.

Verification: Raw samples and reproducible aggregation for startup, input-to-present, switcher, previews and capture-to-first-frame.

Evidence obligation: docs/research/elm-pivot/README.md; new host benchmark packet

### ELM-QA-023

The performance verifier SHALL measure CPU, wakeups, resident/private memory, resource growth, uploads and missed frames across the complete host process group including renderer children and helpers.

Pattern: ubiquitous. Phase: P6. Priority: must. Status: proposed. Owner: Performance qualification lead; verifier: Independent acceptance reviewer.

Verification: Whole-tree samples and long-running soak receipts compare all metrics with frozen budgets and expose resource bounds.

Evidence obligation: docs/elm-roadmap/ROADMAP.md; new whole-tree performance coverage

### ELM-QA-024

The graphics verifier SHALL record actual hardware adapter, driver, backend, capabilities and displayed acceleration for the selected shell webview; WebGPU availability and execution SHALL be reported separately.

Pattern: ubiquitous. Phase: P1. Priority: must. Status: proposed. Owner: Performance qualification lead; verifier: Independent acceptance reviewer.

Verification: Pinned-host runtime adapter/backend reports, real GPU render and readback plus native presentation on the actual display; API availability or hardware inventory alone cannot qualify.

Evidence obligation: new selected-host GPU/WebGPU qualification

### ELM-QA-025

WHEN a selected host GPU path suffers device loss or allocation failure, the native host SHALL invalidate rendering generations, retire invalid owned resources and reconcile current leases without presenting stale frames.

Pattern: event-driven. Phase: P4. Priority: must. Status: proposed. Owner: Performance qualification lead; verifier: Independent acceptance reviewer.

Verification: Injected device-loss/allocation faults record lease cancellation, retirement, recovery, readback correctness and visible-frame identity on the actual display.

Evidence obligation: new GPU device-loss fault corpus

### ELM-QA-026

IF a proposed GPU path uses a software adapter or CPU fallback, THEN the qualification report SHALL label that execution as software and exclude it from GPU acceptance.

Pattern: unwanted. Phase: P1. Priority: must. Status: proposed. Owner: Performance qualification lead; verifier: Independent acceptance reviewer.

Verification: Forced software backend fixture records backend change and rejects accelerated verdict despite API success.

Evidence obligation: new GPU/software backend classification

### ELM-REV-020

The performance owner SHALL freeze a workload budget matrix covering cold startup, idle, catalog refresh, switcher open/navigation, minimized preview, first capture frame, reversible motion, output transfer and whole-process-tree soak.

Pattern: ubiquitous. Phase: P0. Priority: must. Status: proposed. Owner: Performance qualification lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

### ELM-REV-021

The budget matrix SHALL record units, sample counts, device/output metadata, latency distributions, CPU, wakeups, memory, frame misses, power and copy/transfer costs, with numeric absolute and regression thresholds for applicable metrics and explicit justified exclusions.

Pattern: ubiquitous. Phase: P0. Priority: must. Status: proposed. Owner: Performance qualification lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

## elm-security

### ELM-DEL-008

The installer SHALL place shell assets and configuration in reviewed user-owned versioned paths without modifying /usr/share/omarchy.

Pattern: ubiquitous. Phase: P6. Priority: must. Status: proposed. Owner: Native security lead; verifier: Independent acceptance reviewer.

Verification: Compare filesystem manifests, owners and modes before and after rehearsal.

Evidence obligation: AGENTS.md

### ELM-DEL-010

The native service SHALL authenticate bridge peers by local user identity and approved session lifetime before accepting effect requests.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Native security lead; verifier: Independent acceptance reviewer.

Verification: Retain peer-credential traces for allowed and cross-user/replayed sessions.

Evidence obligation: new coverage: bridge peer authentication

### ELM-DEL-011

The native service SHALL expose an allowlisted versioned operation schema and reject arbitrary command execution, filesystem paths and unrecognized methods from web content.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Native security lead; verifier: Independent acceptance reviewer.

Verification: Fuzz bridge operations and confirm no spawned command or arbitrary file read.

Evidence obligation: docs/research/elm-pivot/IMPLEMENTATION.md

### ELM-DEL-012

WHEN a privileged operation requires authorization, the shell SHALL delegate to the established native authorization flow and keep credentials outside Elm and JavaScript.

Pattern: event-driven. Phase: P2. Priority: must. Status: proposed. Owner: Native security lead; verifier: Independent acceptance reviewer.

Verification: Inspect IPC and renderer memory/log fixtures for password absence.

Evidence obligation: AGENTS.md

### ELM-DEL-013

The host SHALL load executable assets only from the hash-verified local release and deny remote scripts, remote navigation and runtime network fetches from shell content.

Pattern: ubiquitous. Phase: P1. Priority: must. Status: proposed. Owner: Native security lead; verifier: Independent acceptance reviewer.

Verification: Run with network disabled plus attempted fetch/navigation probes.

Evidence obligation: new coverage: offline host asset policy

### ELM-DEL-014

The host SHALL enforce a restrictive Content Security Policy that allows only required local assets and denies remote origins, eval and unapproved inline scripts.

Pattern: ubiquitous. Phase: P1. Priority: must. Status: proposed. Owner: Native security lead; verifier: Independent acceptance reviewer.

Verification: Retain CSP headers/policy and execution-negative probe reports.

Evidence obligation: new coverage: CSP negative probes

### ELM-DEL-015

The settings store SHALL use a versioned validated schema with atomic writes and a preserved pre-migration copy before any schema upgrade.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Native security lead; verifier: Independent acceptance reviewer.

Verification: Inject invalid fields, interrupted writes and migration failure.

Evidence obligation: new coverage: settings migration matrix

### ELM-DEL-017

The shell SHALL keep credentials in the existing system credential service and exclude secrets, draft contents and captured pixels from ordinary diagnostic logs.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Native security lead; verifier: Independent acceptance reviewer.

Verification: Inject identifiable synthetic secrets and scan collected logs.

Evidence obligation: docs/HANDOFF.md

### ELM-REV-002

WHILE native session lock is active, the host SHALL suppress application previews and reject new application capture admission.

Pattern: state-driven. Phase: P2. Priority: must. Status: proposed. Owner: Native security lead; verifier: Independent acceptance reviewer.

Verification: Protected lock fixture with independent output observation and rejected capture receipts.

Evidence obligation: docs/elm-roadmap/audits/sol-architecture.json; docs/elm-roadmap/audits/sol-delivery.json

### ELM-REV-026

The native capture broker SHALL admit preview capture only for current authenticated-session surfaces allowed by preview policy and refuse lock-screen, policy-classified credential-entry and cross-session sources.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Native security lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

### ELM-REV-027

WHILE the frontend is unready, the native chord journal SHALL retain only declared chord control events and omit unrelated text and credential keystrokes.

Pattern: state-driven. Phase: P1. Priority: must. Status: proposed. Owner: Native security lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

## elm-shell-experience

### ELM-UI-002

WHEN a listed target outside the effective workspace set is activated, the native authority SHALL navigate to its preserved workspace on its owning output before visible activation without implicit transfer, and SHALL maintain an eligible visible fallback or separately validated compensation if a later restore is refused.

Pattern: event-driven. Phase: P2. Priority: must. Status: proposed. Owner: Desktop experience lead; verifier: Independent acceptance reviewer.

Verification: Named native, keyboard and assistive-technology fixtures where applicable; independent observed results, exact identities, source hashes and frozen product-policy oracle.

Evidence obligation: docs/elm-roadmap/INTERACTION.md; new coverage: final UI/UX review

### ELM-UI-005

The launcher SHALL bind results and selection to the current query and catalog generation, apply the frozen matching/ranking policy, expose initial, loading, no-match and unavailable states, and preserve the query with reachable recovery on refusal.

Pattern: ubiquitous. Phase: P5. Priority: must. Status: proposed. Owner: Desktop experience lead; verifier: Independent acceptance reviewer.

Verification: Named native, keyboard and assistive-technology fixtures where applicable; independent observed results, exact identities, source hashes and frozen product-policy oracle.

Evidence obligation: docs/elm-roadmap/INTERACTION.md; new coverage: final UI/UX review

### ELM-UI-006

The Task View SHALL provide keyboard and pointer selection of windows and workspaces, identity-correlated visible activation and transfer outcomes, usable empty states and dismissal with focus return, according to the frozen workspace-management scope.

Pattern: ubiquitous. Phase: P5. Priority: must. Status: proposed. Owner: Desktop experience lead; verifier: Independent acceptance reviewer.

Verification: Named native, keyboard and assistive-technology fixtures where applicable; independent observed results, exact identities, source hashes and frozen product-policy oracle.

Evidence obligation: docs/elm-roadmap/INTERACTION.md; new coverage: final UI/UX review

### ELM-UI-007

The shell SHALL expose correlated pending, committed, refused, cancelled and unknown/reconciling action states, suppress duplicate dispatch during pending work, and provide reachable recovery after native reconciliation without replaying uncertain mutations or discarding user context.

Pattern: ubiquitous. Phase: P3. Priority: must. Status: proposed. Owner: Desktop experience lead; verifier: Independent acceptance reviewer.

Verification: Named native, keyboard and assistive-technology fixtures where applicable; independent observed results, exact identities, source hashes and frozen product-policy oracle.

Evidence obligation: docs/elm-roadmap/INTERACTION.md; new coverage: final UI/UX review

### ELM-UI-015

WHEN an operation exceeds its frozen feedback threshold, the shell SHALL expose accessible pending or reconciling feedback, keep cancellation and independent controls usable and show success only after matching native confirmation.

Pattern: event-driven. Phase: P3. Priority: must. Status: proposed. Owner: Desktop experience lead; verifier: Independent acceptance reviewer.

Verification: Frozen threshold/policy plus independently observed named fixtures, native counters or user/AT records as applicable; hashes and failure outcomes retained.

Evidence obligation: docs/elm-roadmap/INTERACTION.md; new coverage: final UI/UX review

### ELM-UI-019

WHEN an output disappears, the host SHALL recover shell controls and displaced popup focus on a declared surviving output, preserve workspace identity and reachable application recovery, and reject removed-generation effects until available outputs reconcile.

Pattern: event-driven. Phase: P5. Priority: must. Status: proposed. Owner: Desktop experience lead; verifier: Independent acceptance reviewer.

Verification: Frozen threshold/policy plus independently observed named fixtures, native counters or user/AT records as applicable; hashes and failure outcomes retained.

Evidence obligation: docs/elm-roadmap/INTERACTION.md; new coverage: final UI/UX review

### ELM-UI-020

WHEN a migrated component is first enabled, the shell SHALL offer dismissible keyboard-accessible guidance, preserve approved preference mappings, require explicit shortcut-conflict decisions and expose offline recovery without mandatory onboarding.

Pattern: event-driven. Phase: P5. Priority: must. Status: proposed. Owner: Desktop experience lead; verifier: Independent acceptance reviewer.

Verification: Frozen threshold/policy plus independently observed named fixtures, native counters or user/AT records as applicable; hashes and failure outcomes retained.

Evidence obligation: docs/elm-roadmap/INTERACTION.md; new coverage: final UI/UX review

### ELM-UX-001

The Elm desktop SHALL maintain a scope inventory that assigns each shell surface a migration owner, acceptance scenario and rollback destination.

Pattern: ubiquitous. Phase: P0. Priority: must. Status: proposed. Owner: Desktop experience lead; verifier: Independent acceptance reviewer.

Verification: Review signed inventory against source paths; no unassigned surface.

Evidence obligation: docs/HANDOFF.md

### ELM-UX-015

WHEN a user activates a modal family, the Elm desktop SHALL request the native eligible modal target while preserving the application’s draft content.

Pattern: event-driven. Phase: P2. Priority: must. Status: proposed. Owner: Desktop experience lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: native modal target or terminal activates and draft content remains intact.

Evidence obligation: docs/research/elm-pivot/ARCHITECTURE.md

### ELM-UX-016

WHEN a user toggles always-on-top on a maximized family, the Elm desktop SHALL display pin and maximize state only after correlated native observations.

Pattern: event-driven. Phase: P2. Priority: must. Status: proposed. Owner: Desktop experience lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: displayed pin/MAX state agrees with native state and visible hit target.

Evidence obligation: implementation/maximized-stack-v2/native_stack_smoke.py

### ELM-UX-017

WHEN Task View opens, the Elm desktop SHALL show eligible windows grouped by workspace with a keyboard-selectable active-workspace marker.

Pattern: event-driven. Phase: P5. Priority: must. Status: proposed. Owner: Desktop experience lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: groups match native membership and active workspace is named.

Evidence obligation: docs/research/elm-pivot/ARCHITECTURE.md; new Task View coverage

### ELM-UX-018

WHEN a user transfers a window through Task View, the Elm desktop SHALL update workspace membership only after native transfer acceptance.

Pattern: event-driven. Phase: P5. Priority: must. Status: proposed. Owner: Desktop experience lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: accepted transfer updates membership; refusal retains workspace 1.

Evidence obligation: docs/HANDOFF.md

### ELM-UX-019

WHEN a user chooses a snap region, the Elm desktop SHALL submit geometry keyed to the selected output generation and show the accepted native placement.

Pattern: event-driven. Phase: P5. Priority: must. Status: proposed. Owner: Desktop experience lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: accepted placement matches half work area within native rounding tolerance.

Evidence obligation: window-behavior-spec/snap.lua

### ELM-UX-020

IF an output changes during snap selection, THEN the Elm desktop SHALL invalidate the old preview and require geometry derived from the new output generation before commit.

Pattern: unwanted. Phase: P5. Priority: must. Status: proposed. Owner: Desktop experience lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: old generation geometry is never committed.

Evidence obligation: docs/HANDOFF.md

### ELM-UX-021

WHEN a user drags or resizes an application window, the Elm desktop SHALL preserve native pointer ownership until release or explicit cancellation.

Pattern: event-driven. Phase: P4. Priority: must. Status: proposed. Owner: Desktop experience lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: exactly one gesture ends and no shell surface steals the drag.

Evidence obligation: window-behavior-spec/native_drag.qnt; window-behavior-spec/caption_drag.qnt

### ELM-UX-022

WHILE reduced motion is enabled, the Elm desktop SHALL use the documented reduced-motion transition profile for minimize, restore and shell overlays.

Pattern: state-driven. Phase: P4. Priority: must. Status: proposed. Owner: Desktop experience lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: recorded transitions match approved reduced-motion profile.

Evidence obligation: window-behavior-spec/accessibility.qnt

### ELM-UX-029

WHEN a user searches and launches a catalog entry, the Elm desktop SHALL issue one identity-bound launch request and show failure feedback when native launch is refused.

Pattern: event-driven. Phase: P5. Priority: must. Status: proposed. Owner: Desktop experience lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: one request occurs and refused launch displays an error.

Evidence obligation: implementation/taskbar-v3/taskbar_catalog.py; new launcher coverage

### ELM-UX-030

WHEN a user changes shell settings, the Elm desktop SHALL persist validated preferences and restore them after host restart without applying invalid values.

Pattern: event-driven. Phase: P5. Priority: must. Status: proposed. Owner: Desktop experience lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: valid preference survives and invalid scale is rejected.

Evidence obligation: new settings-schema and restart coverage

### ELM-UX-031

WHEN a notification action is invoked, the Elm desktop SHALL dispatch the action to its current notification identity and remove expired action targets.

Pattern: event-driven. Phase: P5. Priority: must. Status: proposed. Owner: Desktop experience lead; verifier: Independent acceptance reviewer.

Verification: Valid/expired/reused notification identity fixtures with exactly-once current dispatch and no stale producer action.

Evidence obligation: new notification lifecycle coverage

### ELM-UX-032

WHEN a user opens a system menu, the Elm desktop SHALL present capability-supported controls and display native outcomes for requested system changes.

Pattern: event-driven. Phase: P5. Priority: must. Status: proposed. Owner: Desktop experience lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: network control indicates unavailable and remaining controls show observed state.

Evidence obligation: new system-menu adapter coverage

### ELM-UX-033

WHEN a user opens Files from the Elm shell, the Elm desktop SHALL invoke the installed explorer with the requested path or collection and preserve its existing operation semantics.

Pattern: event-driven. Phase: P5. Priority: must. Status: proposed. Owner: Desktop experience lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: existing explorer is reused at requested collection; no ops.sh semantics change.

Evidence obligation: AGENTS.md; new Files integration coverage

### ELM-UX-034

WHERE a later Elm Files replacement is approved, the Elm desktop SHALL preserve Quint-specified copy, move, collision, trash and authorization semantics before replacing the installed operation adapter.

Pattern: optional. Phase: P5. Priority: conditional. Status: proposed. Owner: Desktop experience lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: collision suffix and authorization behavior match spec with no destructive deletion.

Evidence obligation: AGENTS.md; new archived Files spec/adaptor mapping

### ELM-UX-035

The Elm desktop SHALL release the defined shell scope only after original native campaigns and each migrated surface’s acceptance scenarios pass against one frozen source and ABI tuple.

Pattern: ubiquitous. Phase: P6. Priority: must. Status: proposed. Owner: Desktop experience lead; verifier: Independent acceptance reviewer.

Verification: Review hash-bound native evidence and preserve failures; CPU/model success alone cannot satisfy this gate.

Evidence obligation: docs/HANDOFF.md

## elm-switcher

### ELM-UI-003

The product owner SHALL freeze the INTERACTION.md switcher scope, committed-MRU order, modal-family representation, initial forward/reverse selection, wraparound, zero/one-entry behavior and candidate-retirement fallback before P3 qualification.

Pattern: ubiquitous. Phase: P0. Priority: must. Status: proposed. Owner: Elm policy lead; verifier: Independent acceptance reviewer.

Verification: Named native, keyboard and assistive-technology fixtures where applicable; independent observed results, exact identities, source hashes and frozen product-policy oracle.

Evidence obligation: docs/elm-roadmap/INTERACTION.md; new coverage: final UI/UX review

### ELM-UX-011

WHEN native Alt-Tab chord events arrive, the Elm desktop SHALL advance selection in the frozen eligible-window order for that chord generation.

Pattern: event-driven. Phase: P3. Priority: must. Status: proposed. Owner: Elm policy lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: selection advances then returns within the same frozen order.

Evidence obligation: implementation/switcher-v1/SwitcherState.js

### ELM-UX-012

WHEN Alt release precedes switcher readiness, the Elm desktop SHALL resolve the native chord once without leaving an open switcher or issuing a second activation.

Pattern: event-driven. Phase: P1. Priority: must. Status: proposed. Owner: Elm policy lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: one resolution occurs and no switcher remains open.

Evidence obligation: implementation/switcher-v1/README.md

### ELM-UX-013

WHEN Escape cancels a switcher chord before native commit, the Elm desktop SHALL close the switcher and preserve the previously focused window.

Pattern: event-driven. Phase: P3. Priority: must. Status: proposed. Owner: Elm policy lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: switcher closes and focus is unchanged.

Evidence obligation: implementation/switcher-v1/SwitcherState.js

### ELM-UX-014

IF the selected switcher window closes or its identity becomes stale, THEN the Elm desktop SHALL reselect a surviving eligible member or dismiss an empty chord without activating a replacement incarnation.

Pattern: unwanted. Phase: P3. Priority: must. Status: proposed. Owner: Elm policy lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: reused address is never activated as the closed window.

Evidence obligation: implementation/switcher-v1/SwitcherState.js

## elm-taskbar

### ELM-UI-004

The taskbar SHALL follow the INTERACTION.md primary-action table for zero, single and multiple family entries, distinguish application pin from always-on-top, and expose explicit new-instance actions without launching duplicates on ordinary activation.

Pattern: ubiquitous. Phase: P3. Priority: must. Status: proposed. Owner: Elm presentation lead; verifier: Independent acceptance reviewer.

Verification: Named native, keyboard and assistive-technology fixtures where applicable; independent observed results, exact identities, source hashes and frozen product-policy oracle.

Evidence obligation: docs/elm-roadmap/INTERACTION.md; new coverage: final UI/UX review

### ELM-UI-008

The shell SHALL keep every configured icon, group member and action reachable through bounded scrolling or overflow, reveal keyboard selection, preserve identity/order across resizing, and expose labeled menu and window-operation affordances through pointer and keyboard.

Pattern: ubiquitous. Phase: P3. Priority: must. Status: proposed. Owner: Elm presentation lead; verifier: Independent acceptance reviewer.

Verification: Named native, keyboard and assistive-technology fixtures where applicable; independent observed results, exact identities, source hashes and frozen product-policy oracle.

Evidence obligation: docs/elm-roadmap/INTERACTION.md; new coverage: final UI/UX review

### ELM-UX-002

The Elm desktop SHALL place taskbar application icons at the left edge of each configured taskbar output.

Pattern: ubiquitous. Phase: P3. Priority: must. Status: proposed. Owner: Elm presentation lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: first icon begins at the configured left inset on each output.

Evidence obligation: implementation/taskbar-v3/widget_v68/Windows.qml

### ELM-UX-003

WHEN the desktop catalog changes, the Elm desktop SHALL refresh application entries using desktop-file visibility and launch semantics.

Pattern: event-driven. Phase: P3. Priority: must. Status: proposed. Owner: Elm presentation lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: only eligible entries appear and launches preserve recorded arguments.

Evidence obligation: implementation/taskbar-v3/taskbar_catalog.py

### ELM-UX-004

WHEN a user reorders or pins an application icon, the Elm desktop SHALL persist its desktop identity and relative order across shell restart.

Pattern: event-driven. Phase: P3. Priority: must. Status: proposed. Owner: Elm presentation lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: both identities retain the chosen relative order.

Evidence obligation: implementation/taskbar-v3/widget_v68/Windows.qml

### ELM-UX-005

WHEN a taskbar group is opened, the Elm desktop SHALL list each eligible window incarnation once and route selection to that incarnation.

Pattern: event-driven. Phase: P3. Priority: must. Status: proposed. Owner: Elm presentation lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: three entries appear and only selected incarnation receives activation.

Evidence obligation: implementation/taskbar-v3/widget_v68/Windows.qml

### ELM-UX-006

WHILE a window is minimized, the Elm desktop SHALL retain its taskbar identity and label its retained preview as historical.

Pattern: state-driven. Phase: P4. Priority: must. Status: proposed. Owner: Elm presentation lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: entry remains present with historical preview label.

Evidence obligation: docs/HANDOFF.md

### ELM-UX-007

WHEN a retained preview is unavailable, the Elm desktop SHALL display the application icon and window title without substituting another incarnation’s pixels.

Pattern: event-driven. Phase: P4. Priority: must. Status: proposed. Owner: Elm presentation lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: fallback shows correct title and icon with no unrelated pixels.

Evidence obligation: window-behavior-spec/whole_snapshot.qnt

### ELM-UX-008

WHEN an eligible taskbar window is selected, the Elm desktop SHALL request activation or restore through native authority without moving it to a scratchpad.

Pattern: event-driven. Phase: P3. Priority: must. Status: proposed. Owner: Elm presentation lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: native receipt confirms restore and workspace membership has not become scratchpad.

Evidence obligation: docs/HANDOFF.md

### ELM-UX-009

WHILE native observations mark a window active or attention-requesting, the Elm desktop SHALL expose distinct active and attention indicators.

Pattern: state-driven. Phase: P3. Priority: must. Status: proposed. Owner: Elm presentation lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: attention indicator differs from active indicator in pixels and accessible state.

Evidence obligation: implementation/taskbar-v3/widget_v68/Windows.qml

### ELM-UX-010

WHEN a user invokes an application jump list, the Elm desktop SHALL show only catalog-declared actions and supported recent-item actions for that application identity.

Pattern: event-driven. Phase: P5. Priority: must. Status: proposed. Owner: Elm presentation lead; verifier: Independent acceptance reviewer.

Verification: Elm replay assertion and isolated native recording: two declared actions appear and unsupported actions are absent.

Evidence obligation: window-behavior-spec/taskbar_menu.qnt; new recent-item provider coverage

## elm-verification

### ELM-QA-001

The verification owner SHALL retain hash-bound original source inventories, proof packets, failures, scenario identities and deadlines unchanged and create reviewed derivatives for new evidence.

Pattern: ubiquitous. Phase: P0. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Compare archived SHA-256 manifests before and after; derivative manifest links every ancestor.

Evidence obligation: provenance/snapshot.jsonl; docs/HANDOFF.md

### ELM-QA-002

The verification owner SHALL map all original 38 restore-baseline, 34 fault/recovery and 52 drag/resize/reload cases to fresh Elm acceptance scenarios without removing cases or extending deadlines.

Pattern: ubiquitous. Phase: P0. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Identity-set comparison is exactly 38/34/52; each original time origin and assertion remains linked.

Evidence obligation: docs/HANDOFF.md; docs/elm-roadmap/BASELINE.md

### ELM-QA-003

WHEN fault/recovery case 34 is executed, the protected runner SHALL enforce its original frozen deadline and time origin independently of campaign completion.

Pattern: event-driven. Phase: P4. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Timestamped case-34 observations and runner timeout show the original bound; a deliberately late completion fails.

Evidence obligation: docs/HANDOFF.md; new case-34 deadline derivative

### ELM-QA-004

WHEN a Quint campaign is reported, the formal verifier SHALL explicitly select every claimed scenario by exact name and retain selected names, execution results, seed and tool/model hashes.

Pattern: event-driven. Phase: P2. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Requested and executed name sets match; non-Test names are executed; invariant traces are reported separately.

Evidence obligation: docs/HANDOFF.md: restore45/producer14 selector correction

### ELM-QA-005

The verification ledger SHALL distinguish formal, CPU, replay, fuzz, native, hardware and accessibility evidence and block substitution between these acceptance levels.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Ledger validation rejects a native gate backed only by CPU or model results.

Evidence obligation: docs/HANDOFF.md; new evidence-level schema

### ELM-QA-006

WHEN an Elm reducer changes, the policy verifier SHALL compare deterministic replay against frozen ordered native observations including identities, receipts and expected effects.

Pattern: event-driven. Phase: P2. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Replay diff includes desired/pending/acknowledged state and emitted intent sequence with minimized counterexamples.

Evidence obligation: docs/research/elm-pivot/README.md; new replay corpus

### ELM-QA-007

WHEN foreign protocol input is malformed, stale, duplicated or out of order, the native authority SHALL reject unsafe effects and the verifier SHALL retain a reproducible fault trace.

Pattern: event-driven. Phase: P2. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Seeded property/fuzz runs exercise schema bounds, generations, revisions and epochs; native commit logs show rejection.

Evidence obligation: docs/HANDOFF.md; new protocol fuzz corpus

### ELM-QA-008

The formal verifier SHALL cover focus, modal families, pin/maximize, capture leases, cancellation, retirement and output generations with invariants and named transition scenarios.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Model-to-requirement coverage report plus exact named results and independent invariant traces.

Evidence obligation: docs/HANDOFF.md: 503 named scenarios across 39 models

### ELM-QA-009

WHEN a native QA campaign starts, the protected launcher SHALL verify a live parent Wayland socket, a private UID-owned nonsymlink 0700 runtime directory and a dedicated QA scope with inherited core limit 1.

Pattern: event-driven. Phase: P1. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Preflight receipts include socket connection, lstat/UID/mode and scope/core-limit checks; bad fixtures fail before launch.

Evidence obligation: docs/crash-noise/HANDOFF-codex-window-qa.md; docs/HANDOFF.md

### ELM-QA-010

The QA owner SHALL serialize native GUI campaigns, disable Xwayland unless X11 is under test, prohibit DRM fallback and preserve all five crash-handoff protections.

Pattern: ubiquitous. Phase: P1. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Serialized launch ledger and environment/config receipts prove nesting, X11 scope and protected settings.

Evidence obligation: docs/crash-noise/HANDOFF-codex-window-qa.md

### ELM-QA-011

WHEN QA teardown begins, the runner SHALL stop owned clients and helpers, verify empty clients and unload modules before stopping nested compositor and private bus.

Pattern: event-driven. Phase: P1. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Ordered teardown receipts include normal exit status, helper ownership and module/client inventories.

Evidence obligation: docs/HANDOFF.md; docs/crash-noise/HANDOFF-codex-window-qa.md

### ELM-QA-012

IF a process disappears without a recorded exit status, THEN the verifier SHALL mark process closure unproven rather than infer normal exit.

Pattern: unwanted. Phase: P1. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Killed helper fixture records abnormal status or unknown closure and fails the normal-exit gate.

Evidence obligation: docs/HANDOFF.md

### ELM-QA-013

The QA runner SHALL preserve user drafts and the main compositor session during research and acceptance campaigns.

Pattern: ubiquitous. Phase: P1. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Before/after main-session identity and user-window inventory; no close/restart command targets user processes.

Evidence obligation: docs/HANDOFF.md

### ELM-QA-014

WHEN a gate verdict is recorded, the verifier SHALL bind it to source/tool hashes, command, environment, ABI pair, deadlines, observations, closure receipts and reviewer disposition.

Pattern: event-driven. Phase: P6. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Receipt-schema validator rejects missing tuple, time origin, exit evidence or verdict provenance.

Evidence obligation: docs/elm-roadmap/ROADMAP.md; new gate receipt schema

### ELM-QA-015

The release verifier SHALL qualify all mandatory gates against one coherent frozen source/runtime/ABI tuple and retain every failed attempt and rerun.

Pattern: ubiquitous. Phase: P6. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Combined regression manifest references matching tuple hashes for all native gates and immutable rerun ancestry.

Evidence obligation: docs/HANDOFF.md; new combined regression ledger

### ELM-QA-016

The planning verifier SHALL map every requirement to an OpenSpec scenario, phase, actionable task, owner and concrete verifier and retain audit findings with final dispositions.

Pattern: ubiquitous. Phase: P0. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Registry/traceability/task scenario cross-check plus audit records including severity, correction and disposition.

Evidence obligation: docs/elm-roadmap/ROADMAP.md; new audit ledger

### ELM-QA-017

The application verifier SHALL exercise representative native applications including maximized Brave, modal drafts and Files against visible order, hit order, focus, pin, minimize and restore assertions.

Pattern: ubiquitous. Phase: P5. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Application fixture matrix records versions, actions, native observations and failures; bounded stack proof remains separately scoped.

Evidence obligation: docs/HANDOFF.md; new Elm application fixture matrix

### ELM-QA-018

The native verifier SHALL qualify actual changed, unchanged, cancelled and stale popup/input routes before the fixed two-process, three-slot, twelve-helper reliability campaign.

Pattern: ubiquitous. Phase: P3. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Route receipts precede unchanged fixed-campaign inventory; original helper/worker/receipt/cursor bounds remain enforced.

Evidence obligation: window-integration-qa/pin-private-qs-native-v1/; docs/HANDOFF.md

### ELM-QA-019

The accessibility verifier SHALL qualify keyboard-only operation, focus announcements, audible and braille output, IME composition and reduced motion on the selected native host.

Pattern: ubiquitous. Phase: P5. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: AT/IME device and version matrix with observed announcements, braille output, composition/cancellation and motion traces.

Evidence obligation: docs/HANDOFF.md; new selected-host accessibility coverage

### ELM-QA-020

The hardware verifier SHALL qualify scale, rotation, hotplug, output transfer and high-refresh motion on actual supported displays using native presentation feedback.

Pattern: ubiquitous. Phase: P5. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Hardware/display metadata, presentation timestamps and output-generation fault receipts; simulated outputs are separately labeled.

Evidence obligation: docs/HANDOFF.md; new physical-display coverage

### ELM-QA-027

WHERE compositor replacement is proposed, the feasibility verifier SHALL require isolated native Wayland/Xwayland application, input, output, capture, IME and accessibility evidence before a recorded go decision.

Pattern: optional. Phase: P7. Priority: conditional. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Go/no-go packet maps representative compatibility fixtures, failures, costs and scope owner approval.

Evidence obligation: docs/elm-roadmap/ROADMAP.md: P7; new compositor feasibility coverage

### ELM-QA-028

WHERE compositor implementation is authorized, the release verifier SHALL require equivalent mandatory shell parity and complete new native compatibility gates before that compositor replaces Hyprland.

Pattern: optional. Phase: P8. Priority: conditional. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: New tuple has full protocol/application/seat/output/security/recovery ledger and original parity mappings.

Evidence obligation: docs/elm-roadmap/ROADMAP.md: P8; new replacement release coverage

### ELM-REV-005

The requirement registry SHALL assign each requirement an accountable owner role, independent verifier role, phase, task and named acceptance scenario before implementation admission.

Pattern: ubiquitous. Phase: P0. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Registry/task/traceability bijection and explicit nonempty role mapping with separate acceptance reviewer.

Evidence obligation: docs/elm-roadmap/audits/sol-architecture.json; docs/elm-roadmap/audits/sol-delivery.json

### ELM-REV-006

The final audit record SHALL bind reviewed documents, author-input JSON, primary corpus inventories and retained source/body hash roots to a mechanically verified supporting-evidence manifest.

Pattern: ubiquitous. Phase: P0. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Document and supporting-evidence manifests with exact source hashes, crawl closure/failure counts and body/archive integrity verification.

Evidence obligation: docs/elm-roadmap/audits/sol-architecture.json; docs/elm-roadmap/audits/sol-delivery.json

### ELM-REV-029

The QA runner SHALL preserve the protected scope/core limit, verified nested parent socket, explicit X11 selection, authorized runtime/device access and client-before-compositor teardown controls from the frozen crash handoff.

Pattern: ubiquitous. Phase: P1. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

### ELM-REV-030

The QA runner SHALL preserve the installed crash-watch override and the system grim and gnome-keyring builds during all planning, proof and acceptance work.

Pattern: ubiquitous. Phase: P1. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

### ELM-REV-035

The QA baseline SHALL freeze original restore baseline38, recovery34, drag/resize/reload52 and B12 through B24 scenario identities, oracles and original deadlines before claiming inherited native coverage.

Pattern: ubiquitous. Phase: P0. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Independent named fixture receipts with native scene/protocol traces, artifact hashes and explicit pass/fail verdicts.

Evidence obligation: new coverage: independent audit correction

### ELM-UI-021

The product verifier SHALL freeze representative usability tasks, participant profiles, assistance rules and measurable success thresholds before candidate evaluation, and SHALL block acceptance for failed or unobserved required outcomes.

Pattern: ubiquitous. Phase: P0. Priority: must. Status: proposed. Owner: Verification lead; verifier: Independent acceptance reviewer.

Verification: Frozen threshold/policy plus independently observed named fixtures, native counters or user/AT records as applicable; hashes and failure outcomes retained.

Evidence obligation: docs/elm-roadmap/INTERACTION.md; new coverage: final UI/UX review

## elm-window-policy

### ELM-REN-015

The native window authority SHALL derive MAX overlap painting and hit traversal from one committed constrained scene, applying explicit input-region and transform rules and committing the documented modal recipient after a qualifying activation.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Native committed-scene, overlap pixels, input region/transform and activation/modal receipts; explicit passthrough and no-activation exceptions are independently checked.

Evidence obligation: implementation/maximized-stack-v2/README.md

### ELM-REN-016

WHEN pin state changes, the native authority SHALL preserve documented MAX return geometry and evaluate painted and input order under the new pin state.

Pattern: event-driven. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Full pin campaign reports individual outcomes including genuine blocker cases.

Evidence obligation: docs/HANDOFF.md; implementation/maximized-stack-v2/README.md

### ELM-REN-017

WHILE true fullscreen is active, the native authority SHALL apply an explicit fullscreen and pinned-surface policy without treating fullscreen as floating MAX.

Pattern: state-driven. Phase: P5. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Fullscreen/pin/menu matrix independently records pixels, hit and focus.

Evidence obligation: implementation/maximized-stack-v2/README.md

### ELM-REN-018

WHEN focusing a modal family, the native authority SHALL resolve eligible recipients from current native family and input state before committing focus.

Pattern: event-driven. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Native family tests preserve drafts and distinguish input blockers from allows_input.

Evidence obligation: docs/HANDOFF.md; docs/research/elm-pivot/ARCHITECTURE.md

### ELM-REN-020

WHEN a window transfers between outputs, the canonical authority SHALL commit placement, snap membership and frame ownership using current output generations.

Pattern: event-driven. Phase: P5. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Transfer/hotplug race packet records one committed owner and correct geometry.

Evidence obligation: docs/HANDOFF.md; new transfer coverage

### ELM-REV-031

The native focus policy SHALL distinguish genuine input blockers from allows_input=false and SHALL refuse no-focus only when an independently verified native blocking predicate applies.

Pattern: ubiquitous. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Protected native or protocol fixture with explicit positive/negative receipts, source tuple and frozen deadline.

Evidence obligation: docs/elm-roadmap/audits/grok-layering.md; docs/elm-roadmap/audits/grok-delivery.md

### ELM-UI-001

WHEN the focused family minimizes, the native authority SHALL focus the most recently committed eligible successor or the desktop no-application-focus state in the same scene revision, and SHALL preserve current focus when an unfocused family minimizes.

Pattern: event-driven. Phase: P2. Priority: must. Status: proposed. Owner: Native authority lead; verifier: Independent acceptance reviewer.

Verification: Named native, keyboard and assistive-technology fixtures where applicable; independent observed results, exact identities, source hashes and frozen product-policy oracle.

Evidence obligation: docs/elm-roadmap/INTERACTION.md; new coverage: final UI/UX review

