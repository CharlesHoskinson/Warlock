# Recommended simplification plan — 2026-10-03

Three research agents reviewed the architecture, rendering and implementation using online primary sources retrieved with Scrapling. These are proposals, not accepted native behavior. Only research documentation was added; no desktop configuration, runtime, historical proof packet or deployment changed.

Subsequent implementation and activation status: [implementation/STATUS.md](../../implementation/STATUS.md).

Detailed reports: [architecture](architecture.md), [rendering](rendering.md), [implementation](implementation.md). Downloaded pages and source manifests are in `/home/hoskinson/.cache/windows-parity-research/`. Installed package versions observed: Omarchy 4.0.4.legion-2, Hyprland 0.56.2-2, Aquamarine 0.15.0-2, Quickshell 0.3.1-1, Qt 6.11.2. Packages do not establish the active custom compositor/plugin ABI pair.

## Recommended architecture

Keep the existing Omarchy shell and built-in bar. Make the parity UI a user-owned service-backed plugin: one shared presentation model for taskbar, previews, Task View and switcher; one acknowledged command interface to the existing native authority; one bounded capture resource owner. Native authority continues to own lifetime validation, modal-family transactions and compositor effects. Presentation caches never authorize an effect.

Use a persistent event subscription with fresh, short-lived command requests. Hyprland documents synchronous command-socket handling and a five-second stall from unclosed connections: a persistent backend is not permission to leave the command socket idle. Quickshell's models also document gaps in event coverage, so retain startup/reconnect reconciliation and fresh observations at mutation boundaries. [Hyprland IPC](https://wiki.hypr.land/IPC/), [Quickshell 0.3.1 Hyprland](https://quickshell.org/docs/v0.3.1/types/Quickshell.Hyprland/Hyprland/).

## Priorities

| Order | Work | Relative effort | Reviewable outcome |
| --- | --- | --- | --- |
| 1 | Cache application metadata and share event-coalesced observational state | Small to medium | Reduced idle process/query counts; correct catalog updates and reconnect behavior |
| 2 | Finish the existing bounded runtime-source projection and real popup routes | Small | Fresh matching source/CPU report; unchanged changed/same/cancelled/stale and reliability acceptance |
| 3 | Measure unchanged V29 preparation and presentation | Small | Phase timings for query, lock wait, journal, capture, conversion, upload and actual presentation at the original deadline |
| 4 | Consolidate acknowledged UI commands and reload ownership | Medium | No detached per-signal helper requirement; same lifetime, cancellation and closure guarantees |
| 5 | Prototype independently retained native frames | Medium to large | One visible-window capture survives hide/source stop; bounded memory; no duplicate upload on reversal |
| 6 | Stabilize native hook/ABI boundary; replace journal only if measurements justify it | Large | Smaller maintained native adapter, coherent release tuple; equivalent recovery durability |

The archived selected widget_v65 launches a snapshot every 900 ms. Its helper rebuilds the desktop-entry catalog and separately queries monitors, workspaces and clients. The source-derived upper activity is about 4,000 Python launches and 12,000 queries hourly per taskbar instance when requests finish before the next tick; this is not a measured production profile. Catalog caching can be introduced inside the existing Python helper first. Event-driven UI state follows without changing native action authority. Preserve actions, pins, user desktop-file precedence and install/remove invalidation.

Keep the taskbar as a service-backed widget under the built-in bar. Current Omarchy documents service-less facades for widgets hosted by third-party replacement bars, making a full bar replacement unnecessary integration work. KeepLoaded services survive reload but their code changes require a shell restart; maintain the local versioned QML URL procedure. [Omarchy shell contract](https://github.com/omacom/omarchy/blob/quattro/docs/omarchy-shell.md).

For commands, reuse existing typed receipts and add a backend epoch to bind responses to the current lifetime. A socket transport can remove repeated control helper launches, but writing bytes is not acknowledgement and SIGTERM is not process-tree retirement. Preserve the existing Keeper and native completion checks. [Quickshell Process](https://quickshell.org/docs/v0.3.1/types/Quickshell.Io/Process/), [Socket](https://quickshell.org/docs/v0.3.1/types/Quickshell.Io/Socket/).

## Capture and correctness constraints

Quickshell already supports native still/live toplevel capture. A retained frame could replace repeated grim, ImageMagick, PNG encoding/decoding and texture upload in the critical path. This is a prototype, not a stock drop-in replacement: capture context shutdown clears stock content; server decorations/rounding are excluded and popup extent is clipped by the export protocol. Display constraintSize does not reduce compositor capture allocation. Retain the existing decorated-frame path until an alternative meets exact pixel and family requirements. [ScreencopyView 0.3.1](https://quickshell.org/docs/v0.3.1/types/Quickshell.Wayland/ScreencopyView/), [export protocol](https://github.com/hyprwm/hyprland-protocols/blob/main/protocols/hyprland-toplevel-export-v1.xml).

Capture before hiding where feasible; independently retain the last verified frame with window generation, output/scale and source ownership. Subscribe visible previews on demand. Preserve the already implemented continuous reversal model rather than replace it with independent per-property animations. Memory budgets matter: an uncompressed 4K RGBA frame is about 31.6 MiB. No latency or resource savings are claimed without measurement.

Resolve two semantic boundaries explicitly. Hyprland pin is sticky workspace visibility, not Windows-style always-on-top; model those intents separately without silently changing current behavior. The archived capture route refers to `special:win-minimized`, while the original outcome prohibits scratchpad minimization. Audit that route against the requirement before declaring parity, and provide proper native hidden/minimized state if required. This is a source observation, not a new test of the live desktop.

The current journal persists complete nested state under the manager lock. Earlier CPU evidence recorded 24 trivial queries plus 98 fsynced snapshots taking 1,777.233 ms; it does not prove V29's native bottleneck. Measure serialization, lock wait and synchronization first. An append-only journal or SQLite WAL may reduce rewriting, but must preserve durable registration/completion, complete history, quarantine and restart semantics. Reducing durability or changing deadlines is not an efficiency improvement. [Qt profiling guidance](https://doc.qt.io/qt-6.11/qtquick-performance.html), [SQLite WAL](https://www.sqlite.org/wal.html).

Every implementation should use a fresh derivative, preserve prior evidence and run the original native acceptance. Start with catalog/presentation changes and finish already prepared components; a full rewrite would discard useful proven behavior and increase validation work.
