# Architecture contribution: a complete Elm shell with native authority

Planning contribution, 2026-10-03. This document proposes future work; it establishes no implementation or native acceptance. Companion `architecture.json` contains 29 atomic EARS requirements, ELM-ARC-001 through ELM-ARC-029. Existing accepted, failed and staged evidence remains distinct.

## Target and boundary

Replace the entire shell GUI with Elm model/update/HTML presentation: taskbar, switcher, launcher, Task View, snap chooser, menus, notifications and settings. Retain Hyprland initially. A controller-only worker is a useful reducer experiment, but cannot satisfy the full GUI target. Files application migration is separate; existing file-operation semantics and drafts remain outside shell ownership.

| Component | Authority | Explicit boundary |
|---|---|---|
| Elm policy owner | Selection, desired layout, popup states, transactions, display projections | Pure update proposes effects; it never declares native acceptance |
| JavaScript adapter | Port transport and supported Elm initialization | Small schema adapter; no parallel desktop policy or generated Elm internals |
| GTK or Qt host | Layer surfaces, popup roles, input regions, webview and renderer supervision | Native Wayland surfaces contain DOM views; DOM nodes are not application windows |
| Native broker | Identity, deadlines, admission, cancellation, receipts, snapshot publication | Checks current authority immediately before mutation |
| Compositor/native helpers | Focus, stacking, hit testing, modal families, captures, motion and buffers | No input/composition hot path waits for Elm or webview scheduling |

Use one canonical Elm policy owner and read-only per-output projections. Start with one host process managing output surfaces; renderer processes may be separate. If isolation requires multiple Elm view instances, they receive projections and emit intents to the canonical owner. They cannot independently commit cross-output policy. Evaluate a headless policy worker only if measured scheduling and serialization costs justify the extra process boundary.

## Protocol design

Publish a versioned envelope union for snapshot, observation, chord input, receipt, presentation and host-lifecycle events; expose one incoming port and one outgoing intent port. Carry compositor lifetime, frontend epoch, request ID, operation generation, window incarnation, output generation and expected native revision. Native identity is an opaque broker-issued incarnation associated with native object lifetime; reusable addresses and PID alone are insufficient. Surface native family and input-policy observations explicitly.

Snapshot publication has a sequence watermark. The authority orders events after that watermark; observations may be coalesced only when the stream retains enough sequence information to distinguish declared replacement from unexplained loss. Gaps stop effect admission until resynchronization. Record why dropped old observations are harmless. Chord edge events and terminal outcomes are never silently coalesced. Capture press/repeat/release/Escape natively even while the frontend is not ready.

Represent Pending, Committed, Refused, Cancelled and Unknown independently. Acknowledged dependencies replace assumptions about `Cmd.batch` completion order. A bounded epoch-scoped ledger deduplicates requests; when an ID falls outside the retained deduplication window, reject reuse rather than guessing that it is new. An Unknown outcome requires native reconciliation before retry. Neither command acceptance nor a browser animation callback proves native presentation.

Deadlines are immutable absolute native monotonic timestamps. Queueing, retry, capture fusion, restart and reconciliation consume the existing budget. A deadline from another process clock must be normalized by the native authority rather than trusting wall-clock timestamps. Preserve original acceptance deadlines and scenario identity; report timings separately instead of raising limits to obtain passes.

Queues have explicit byte and item caps recorded in the prototype configuration and measurement report. Select caps from observed payload distributions and the archived 16 MiB input failure; that historical bound is evidence, not a universal new queue budget. Reserve bounded control capacity for receipts, cancellation and retirement. Preview saturation discards replaceable preview observations or refuses new preview jobs. Effect admission failure returns an explicit refusal. If control capacity itself becomes unavailable, stop new effect admission and force supervised reconciliation; do not continue with silent outcome loss.

Opaque preview keys include owner lifetime and revision. Native components retain buffers, perform composition, sample motion clocks and retire callbacks, textures and helpers. The host mediates image access without arbitrary filesystem paths. Elm does not carry pixel arrays, PNG data or per-frame motion JSON. Source-stop lifetime and accepted minimized previews remain native gates.

## GTK/WebKit versus Qt/WebEngine experiment

Build custom dedicated hosts rather than adding an unreviewed late WebEngine import to Quickshell. The research records installed GTK-related dependencies and absent Qt WebEngine/WebChannel packages at acquisition time; P0 rechecks these facts. GTK major version and layer-shell integration must match before realizing surfaces. Qt initialization must occur at the documented application startup boundary. Tauri/WRY may supply plumbing, but an ordinary application webview does not demonstrate shell roles.

Both candidates render the same optimized Elm asset bundle and exercise the same recorded/native workload against the same frozen compositor/plugin pair. Test native layer exclusivity, keyboard interactivity, popup dismissal, input transparency, output removal, fractional scale, negative coordinates, IME/preedit, clipboard/DND, accessibility and renderer failure. Include release-before-ready, stale receipts, cancellation and source-stop preview survival. Report input-to-effect and input-to-visible-frame separately; collect latency distributions, frame gaps, CPU/wakeups, PSS/RSS, renderer count, startup and long-running growth. Baseline budgets are selected and frozen during P0 before candidate results are examined. No host has a presumption of better efficiency.

Host selection deliverable is a decision record: passed/failed native capabilities, baseline comparison, dependency/packaging burden, accessibility limitations, remaining adaptation work and rollback evidence. A host that cannot satisfy required shell roles or native input/accessibility gates is rejected even if its synthetic DOM benchmark is faster. If neither candidate passes, retain the accepted shell and revise the host design; do not redefine the target as a headless worker.

## Host security and recovery

Only packaged local shell assets can access the bridge. Allowlist asset origin/resource schemes, deny external navigation and remote bridge access, and constrain the exposed native operation union. Do not disable webview sandboxing to simplify embedding. Evaluate renderer isolation, CSP and host-specific navigation/resource interception with hostile document and image URL probes. No arbitrary JS-to-native method registry, shell execution or unconstrained filesystem path is exposed. Authenticate local broker peers using UID-bound runtime endpoints and frontend session identity; derive capabilities from the broker session, not message claims. Runtime directories follow the archived private UID-owned nonsymlink 0700 rule.

Keep the broker separate from renderer lifetime. Renderer death invalidates its epoch, revokes owned surfaces/preview references, prevents obsolete intents and triggers snapshot reconciliation. Native helpers have explicit ownership and termination evidence. Reconciliation does not recall already committed effects; such effects retain their receipts or Unknown state. Recovery restarts only the shell frontend, preserving application connections and drafts. Repeated host failure restores the recorded accepted shell configuration under a supervisor with a documented bounded restart policy chosen during P1. Fallback leaves diagnostic evidence and does not hide failed acceptance.

Hyprland plugins remain exact ABI pairs. Record compositor executable, plugin build, owning headers and source hashes; refuse loading mismatches. Elm's bridge stability cannot make a native plugin ABI stable. Isolated QA precedes activation; installed source roots and original frozen artifacts are not rewritten for convenience.

## Stages, dependencies and deliverables

| Phase | Architecture deliverable and exit dependency | Estimate |
|---|---|---|
| P0 | Source/ABI inventory, ownership map, taskbar-v3 baseline, frozen workload and performance/resource budgets | 1–2 engineer-weeks |
| P1 | Two native host spikes, bridge schema/decoders, sandbox/resource policy, role/input probes, selection decision | 4–8 engineer-weeks |
| P2 | Pure Elm reducer plus native identity ledger, snapshot/replay, queue admission, cancellation, restart reconciliation and deadline proof | 3–6 engineer-weeks |
| P3 | Canonical taskbar/switcher vertical slice; native family/stacking actions; multi-output projections | 3–6 engineer-weeks |
| P4 | Opaque preview/motion integration with accepted source-stop and retirement evidence | 4–8 engineer-weeks |
| P5 | Entire shell surface migration, native IME/accessibility/DND/output compatibility matrix; retire duplicate QML policy only after parity | 6–12 engineer-weeks |
| P6 | Reproducible packaging, serial coherent-tuple native regression, supervised restart and exercised shell rollback | 3–6 engineer-weeks |
| P7 conditional | Separate native compositor feasibility and compatibility scope; explicit go/no-go | 4–8 engineer-weeks |
| P8 conditional | Native compositor implementation, protocol compatibility and nested/hardware validation | 26–78+ engineer-weeks |

Shell architecture estimate: 24–48 engineer-weeks across P0–P6, not elapsed schedule or a commitment. Assumes experienced Elm and native Wayland/GTK/Qt engineers, available isolated QA hardware, reuse of reviewed native helpers, and no new GPU driver defect. Surface teams can overlap after P2, but GUI campaigns are serial. Full native compositor work is excluded from shell estimates and can exceed the range if protocol/application compatibility expands. The ranges include integration and architecture validation; they do not imply all existing parity blockers are already solved.

P1 depends on P0 budgets. P2 can develop replay against fixtures while host probes proceed, but live P3 requires both accepted host capability and protocol guards. P4 depends on P2 lifetime/queue/deadline handling. P5 depends on the taskbar/switcher slice and preview architecture. P6 requires all required native shell routes and a coherent source tuple. Existing stacking fixes, original restore baseline38/recovery34, 52 drag/resize cases and real popup/lifetime campaigns remain independent prerequisites, not tests automatically superseded by rewriting presentation. Root serial QA retains the protected launcher and crash-preservation rules in `docs/HANDOFF.md`.

## Decisions and risks

The first decision is host viability, not language popularity. Highest risk is losing native causality or authority across renderer IPC: mitigate with incarnations, epochs, snapshot watermarks, receipts, replay and boundary refusal. Second is preview lifetime and upload cost: retain native ownership and require source-stop evidence. Third is host accessibility/input behavior: run real IME/Orca/braille and focus tests before broad surface migration. Fourth is duplicated policy during transition: route each migrated operation to one owner and leave the accepted path available for rollback. Fifth is comparison contamination from staged native corrections: freeze and report the exact tuple rather than mixing desktop activation with host evaluation.

Open implementation decisions have explicit closure deliverables rather than placeholder requirements: P0 sets baseline budgets and queue-workload evidence; P1 fixes host, runtime transport, restart bounds and resource scheme; P2 fixes ledger retention and canonical owner topology; P4 selects the native texture/image delivery mechanism from measured lifetime and scale results. A failed mandatory gate blocks expansion and remains preserved as failed evidence.

## Optional compositor replacement

A complete Elm shell is the recommended target and retains Hyprland. Replacing Hyprland means building a separate native compositor with Wayland server protocols, Xwayland, DRM/KMS, seats, output lifecycle, rendering, capture/security and application compatibility. Elm may own high-level policy and shell presentation; native execution still owns these mechanisms. Standard Elm does not supply an all-Elm window-system backend.

P7 produces a protocol inventory, native backend choice, security model, migration/session-loss plan and compatibility acceptance matrix. Smithay or other libraries are candidates, not proof of Windows parity. P8 is conditional on that separate admission decision and proceeds from nested sessions to hardware sessions using sacrificial apps. Main compositor replacement can disconnect application surfaces, so draft preservation requires an explicit user session transition plan. Shell restart recovery must never be presented as evidence that full compositor replacement preserves existing application connections.

## Evidence basis

Read `docs/HANDOFF.md`, `implementation/STATUS.md`, and `docs/research/elm-pivot/{README,ARCHITECTURE,IMPLEMENTATION}.md` together. Existing native stack evidence is in `implementation/maximized-stack-v2/`; accepted taskbar observation and rollback evidence is in `implementation/taskbar-v3/`. The research reports retain versioned upstream sources and explain their acquisition limitations. This contribution adds architecture requirements and planned verification, not new upstream factual claims or newly executed native coverage.
