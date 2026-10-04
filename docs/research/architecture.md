# Omarchy parity architecture research — 2026-10-03

Research only. No running compositor, plugin, configuration, campaign evidence or historical model was changed. Read `AGENTS.md` and `docs/HANDOFF.md` first. Source pages were downloaded with Scrapling `Fetcher.get`; artifacts and URL manifest are under `/home/hoskinson/.cache/windows-parity-research/architecture/`. Search provided discovery; recommendations below use primary documentation and local source inspection.

## Findings that constrain simplification

The archived compositor tree reports **0.56.2** in `src/hyprland-motion-audit/VERSION`; archived installed configuration uses Lua. Parent inspection reports installed packages Hyprland 0.56.2-2 and Quickshell 0.3.1-1. These facts do not identify the active compositor/plugin ABI pair. Current Hyprland documentation explains Lua dispatcher APIs introduced after 0.54; copying legacy dispatch strings from old guides would introduce compatibility work. [Current dispatchers](https://wiki.hypr.land/Configuring/Basics/Dispatchers/).

The installed taskbar manifest selects `widget_v65/Windows.qml`. Its unconditional 900 ms timer launches `hypr-taskbar snapshot`; `hypr-taskbar` reparses the desktop-entry catalog in `main()` and queries monitors, workspaces and clients separately in its snapshot path. Each taskbar instance can therefore request roughly **4,000 Python snapshot launches and 12,000 compositor info calls per hour**, assuming each completes before the next timer and ignoring extra refreshes from actions. This is a calculation from the source, not an observed performance profile. Local refs: `installed/home/.config/omarchy/plugins/hoskinson.windows/widget_v65/Windows.qml:449,481`; `installed/home/.local/bin/hypr-taskbar:25,197,316`.

Hyprland warns that `hyprctl` work executes synchronously and recommends limiting information queries and batching appropriate controls. Its command socket must be opened immediately before a request and closed afterward; an unclosed connection can block the compositor until its five-second timeout. **A persistent service must persist the event connection, not leave the command socket sitting open.** [Using hyprctl](https://wiki.hypr.land/configuring/core/advanced-configuration/using-hyprctl/), [IPC](https://wiki.hypr.land/IPC/).

## Ranked proposals

| Rank | Change | Implementation effort | Benefit | Tradeoff |
| --- | --- | --- | --- | --- |
| 1 | Cache desktop-entry catalog separately from window snapshots | Low | Removes repeated recursive parsing and disk work | Must invalidate on application install/removal and user desktop-file overrides |
| 2 | Share one event-driven window view across bar, Task View and switcher | Medium | Cuts subprocess churn and duplicate compositor reads; faster visible updates | Requires reconnection reconciliation and deliberately refreshed fields |
| 3 | Route all UI actions through the existing owning-window command authority | Medium | Fewer transport paths and stale-address races | Needs a typed command facade and explicit outcome handling |
| 4 | Describe pin intent separately from sticky workspace visibility | Medium | Clearer invariants; smaller cross-workspace/modal state space | Must preserve the current user-visible policy while representation changes |
| 5 | Move fragile function interceptions toward small upstream fixes | High | Reduces update breakage and custom compositor maintenance | Needs upstream agreement or a maintained patch set; event hooks cannot replace every interception |
| 6 | Package the coherent native tuple behind a capability contract | Low–medium | Makes upgrades and failures easier to diagnose and quarantine | CI/build metadata work; native acceptance still required |

### 1. Cache application metadata

Keep the catalog generation independent of window generation. Cache parsed `.desktop` files using path/mtime or directory change notifications, with deterministic user-over-system precedence retained. Preserve existing desktop actions, Terminal handling, pins and startup WM class matching. First implementation can remain inside the current Python backend: persist a validated cache, rebuild on detected catalog changes, and leave action semantics intact. This is a narrower improvement than replacing the shell.

Verify by tracing snapshot process counts, compositor query counts, catalog rebuild counts, CPU time and first-popup latency; test a desktop entry being installed, changed and removed. Do not claim speedup until measured. This recommendation follows directly from the local source inspection, rather than a benchmark of another desktop.

### 2. Replace blanket polling with shared events and bounded reconciliation

Use Quickshell's existing Hyprland toplevel/workspace/monitor models and `rawEvent` where suitable, or a single existing backend event subscriber where custom state is required. Publish one immutable snapshot generation to all UI consumers. Coalesce bursts into one refresh, then selectively invalidate affected classes of data; keep startup, reconnect and occasional bounded full reconciliation. Read `lastIpcObject` only after its refresh completes, because undocumented fields can be stale. These APIs exist in archived `src/quickshell-accessibility/src/wayland/hyprland/ipc/{qml,connection}.hpp`. [Quickshell Hyprland 0.3.1](https://quickshell.org/docs/v0.3.1/types/Quickshell.Hyprland/Hyprland/), [HyprlandToplevel 0.3.1](https://quickshell.org/docs/v0.3.1/types/Quickshell.Hyprland/HyprlandToplevel/).

A snapshot's timestamp is not mutation authority. Preserve existing native session, identity, owner and generation guards. Measure idle refresh rate and popup response, then prove reconnect/close/monitor-removal reconciliation. This can be implemented incrementally for catalog/observational state before any critical action transport changes.

### 3. One command facade, with native identity checks

The installed Task View/taskbar source still contains direct `hyprctl` address-based close paths alongside more guarded window actions. Map each frontend command to a typed intent (focus, close, pin, maximize, minimize, restore) and let the existing native authority validate the owning target and modal family on its event loop. Return a bounded receipt containing request identity and observed result. Consolidate existing receipt protocols rather than introducing a second one. Keep titles and app IDs out of mutation authority.

Quickshell's foreign-toplevel `activate`, `close`, `minimized` and `maximized` API offers useful protocol-level requests, but requests may be ignored; it does not establish the repository's atomic family/geometry guarantees. Archived `src/quickshell-accessibility/src/wayland/toplevel/qml.hpp` confirms that limitation. The unversioned online page redirects to **v0.1.0**, so local source was checked rather than assuming that page documents installed 0.3.1. [Toplevel API](https://quickshell.org/docs/v0.1.0/types/Quickshell.Wayland/Toplevel/).

Validate same/cancelled/stale/closed/replaced-owner routes and actual Quickshell receipt delivery before retiring old paths. Standard APIs can simplify ordinary observation and requests; they cannot substitute for native acceptance of pin or restore.

### 4. Separate pin meanings in the model

Hyprland's native pin makes a floating window visible across workspaces; it is not a persistent Windows-style above-ordinary-windows layer. The installed `pin.lua` acknowledges this and raises all pinned floating windows on every active-window change, with separate address-keyed fades. Current archived headers label `m_pinned` sticky. [Versioned legacy dispatcher semantics](https://wiki.hypr.land/0.54.0/Configuring/Dispatchers/).

Represent `alwaysOnTopIntent`, `stickyVisibility`, normal geometry, and temporary fullscreen/maximize state separately in native authority, even if the current product intentionally activates both first two together. Keep modal family stacking and deepest eligible focus in that authority; leave visual feedback in the shell. Prefer an owned native animation/completion path over address-only timers when replacing fade logic. Do not silently remove cross-workspace pinning, floating conversion or restoration behavior. Model explicit unpin without geometry restoration, and retest owner/dialog ordering, maximize return, input blockers, transfer and scroll cases from the handoff.

### 5. Reduce the function-hook surface deliberately

`src/hyprbars-dragend-initfix/familyBridge.cpp` intercepts `rawWindowFocus`, `windowAt` and `raise`, including mangled-symbol matching. `dragBridge.cpp` also uses function hooks. Upstream guidance treats function hooks as a last resort and prefers events; compositor state belongs to its single event loop. [Plugin guidelines](https://wiki.hypr.land/Plugins/Development/Plugin-Guidelines/).

Inventory each hook's behavioral responsibility. Keep existing events for observation and cleanup; seek small core fixes or explicit supported callbacks for hit testing, modal focus and drag retirement. A post-focus event is too late to guarantee correct input delivery, so replacing these hooks with listeners blindly would regress the original click-to-focus requirement. Isolate unavoidable hooks into one thin adapter, retaining strict ABI validation. Benchmark and accept the improved core/plugin pair against unchanged native scenarios. This is the most expensive proposal but directly addresses update compatibility.

### 6. Ship one coherent tuple and expose capabilities

Build compositor, plugin and shell integration together with source hashes and a narrow command/schema version. Gate plugin loading using the exact compositor/header hash, as upstream's starter example requires. Maintain release-specific plugin revisions using upstream commit pins where suitable. [Plugin getting started](https://wiki.hypr.land/Plugins/Development/Getting-Started/), [Plugin guidelines](https://wiki.hypr.land/Plugins/Development/Plugin-Guidelines/).

Report capabilities such as owning-window pin transaction, family restore and thumbnail export to the frontend. For a missing capability, disable that action with explicit feedback instead of silently falling back to an unsafe address-only path. Preserve the full immutable QA inventory; a smaller runtime projection is a transport concern, not permission to drop scenarios. This aligns with the handoff's 16 MiB input issue and strict tuple requirement, but does not itself close any live acceptance gap.

## Recommended first experiment

Start with catalog caching and event-coalesced taskbar observation while leaving current native action authority intact. Compare idle subprocess/query counts and popup latency against widget_v65. Then finish the existing real Quickshell stale/cancelled action and helper-lifecycle campaign before consolidating critical command paths. Continue original 38/34 restore and 52 drag/resize acceptance; the research does not alter their deadlines or claim deployment.
