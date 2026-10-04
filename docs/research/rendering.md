# Rendering and capture research — 2026-10-03

Research only: no desktop configuration, native GUI campaign, build or deployment changed. Read `AGENTS.md` and `docs/HANDOFF.md`. Sources fetched using Scrapling 0.4.15 (`Fetcher.get`); 13 successful fetches, URL/status/content SHA-256 manifest and extracted documents at `/home/hoskinson/.cache/windows-parity-research/rendering/`. Qt 6.11 documentation and Quickshell v0.3.1 are included to match installed packages; custom running binaries and archived sources require their own verified pair. Generic Qt URLs currently describe a later release. Unpinned Hyprland main is design evidence, not acceptance of an installed build.

## Local bottlenecks established by source, not timing claims

`service-hidden-capture-fusion-v29/native_desktop.py:276–370` serializes capture under `capture_lock` and `snapshot_lock`, reads cached whole-window PNG and metadata, calls `grim -T` with 650 ms timeout, checks current identity repeatedly, calls a fused `magick` with 1 s timeout, writes two thumbnail copies and metadata, then promotes a composed PNG. V29 has already removed one ImageMagick invocation per hidden member. Its tests explicitly identify grim as a file-copy fixture; the passed CPU counts are not compositor latency measurements. The archived route checks `special:win-minimized`, although the original requirement explicitly says no scratchpad minimization; this research does not endorse that route as final product semantics.

`producer-continuous-dev-v13/Renderer.cpp:212–223` PNG-decodes in memory then uploads with `glTexImage2D`. At :526–531 the existing retarget route already reuses sources and reports upload count; it must be preserved. The handoff's failed B14 had captures but no renderer seed/uploads by the original two-second deadline. Source establishes substantial serialization, conversions and copies; it does not establish which costs dominated B14.

## Ranked recommendations

### 1. Profile the unchanged V29 critical path before replacing it (immediate; small cost)

Instrument a fresh derivative, recording monotonic request, identity/query completion, frame-ready, PNG encode/decode, ImageMagick, renderer upload, seed and first *presented* frame timestamps. Count helpers, file bytes and uploads; include cold/warm cache and 1/3-member families. Compare at the original two-second deadline and preserve baseline38/recovery34 case identities. Qt recommends using the profiler to identify actual bottlenecks rather than assuming them: [Qt 6.11 performance guidance](https://doc.qt.io/qt-6.11/qtquick-performance.html).

**Inference:** This is the lowest-risk way to decide whether V29 is sufficient or a structural capture change is justified. No speedup estimate can be supported without these measurements. Keep durable ownership/closure evidence; collapsing work must not replace genuine completion with process disappearance.

### 2. Prototype one retained native frame instead of subprocess PNG capture (architectural investment; medium/high cost)

Use existing Quickshell `ScreencopyView` for a bounded visible-window proof: `captureSource: toplevel`, `live: false`, `paintCursor: false`; wait for `hasContent`, then animate/display the native frame. [Quickshell v0.3.1 docs](https://quickshell.org/docs/v0.3.1/types/Quickshell.Wayland/ScreencopyView/) document single-frame capture; [v0.3.1 implementation](https://raw.githubusercontent.com/quickshell-mirror/quickshell/v0.3.1/src/wayland/screencopy/view.cpp) feeds its Wayland swapchain into `WlBufferQSGDisplayNode` rather than PNG files. Archived Quickshell buffer code supports DMA-BUF textures and SHM fallbacks.

**Inference:** A persistent capture owner plus an independently retained texture could serve taskbar, Alt+Tab and motion, removing grim/ImageMagick launch and repeated PNG conversions from the hot path. This is not an immediate V29 patch or proven latency improvement. Stock `ScreencopyView` is not a durable cache: `destroyContext` clears `hasContent`; source destruction and `stopped` trigger destruction. Prove a single retained frame survives source stop/window hide before adopting it. Keep PNG golden evidence and fault fixtures offline.

**Limits/cost:** Implement retention in a supported QQuickItem/texture owner or a small version-pinned Quickshell extension, with render-thread release, buffer lifetime and bounded memory. DMA-BUF import is conditional on backend/device/format support; SHM must work. `constraintSize` constrains implicit display size, not compositor allocation or bandwidth. Texture reuse across separate windows or graphics contexts is not automatically safe. Prototype client-only previews first; full decorated minimize motion is harder.

### 3. Capture before hide; keep a bounded fallback and separate decoration metadata (medium cost)

The [Hyprland protocol](https://raw.githubusercontent.com/hyprwm/hyprland-protocols/main/protocols/hyprland-toplevel-export-v1.xml) exports client surfaces, excludes server-side decoration and compositor rounding, and clips popups to the base surface. Its existence does not guarantee fresh frames from a minimized application. [Upstream screenshare session](https://raw.githubusercontent.com/hyprwm/Hyprland/main/src/managers/screenshare/ScreenshareSession.cpp) stops on unmap/monitor disconnect; the [frame renderer](https://raw.githubusercontent.com/hyprwm/Hyprland/main/src/managers/screenshare/ScreenshareFrame.cpp) remains tied to a monitor and rendering of the source window. These restrictions also occur in the local snapshot.

**Inference:** Acquire a valid frame before the minimizing state transition, retain it with identity `{stableId,pid,generation}`, output/scale and decoration version; restore should immediately use that verified frame, then optionally refresh after presentation. Cache client pixels independently from titlebar/border/rounding metadata, and compose geometry on GPU if exact appearance is validated. Add memory budget/LRU and terminal leases so close, identity reuse, reload and output changes cannot expose the wrong pixels. Treat a retained stale preview as explicit fallback; do not call it a fresh hidden capture. Disabling background frame capture avoids waking minimized apps continuously.

**Limits:** Current cache has exact whole-window pixel requirements and outside-base modal/popup support; synthetic QML decorations are not automatically equivalent. A compositor export extension for a whole window family may be needed for exact fidelity and carries Hyprland ABI/upstream maintenance cost. Preserve current full-frame fallback until a replacement passes the original native cases.

### 4. Share one captured resource, request only visible live previews (medium cost)

Use one bounded source owner per stable window generation; subscribe taskbar/Alt+Tab/Task View to that resource instead of allocating one capture stream per card. Default to stills; enable live only for an actually visible hovered card and stop when it disappears. `ScreencopyView.live` requests subsequent frames while painting: [implementation](https://raw.githubusercontent.com/quickshell-mirror/quickshell/v0.3.1/src/wayland/screencopy/view.cpp). Keep one low-resolution retained preview per minimized window and a full-resolution frame only while its motion/family lease needs it.

**Inference:** Coalescing duplicate work reduces capture count and ownership paths. Do not promise source-resolution reduction via `constraintSize`; downsampling once into an owned texture is separate work. Raw RGBA at 3840×2160 costs about 31.6 MiB per frame before double buffering or other overhead, versus about 0.206 MiB at 300×180; set explicit budgets rather than keeping every full-size frame forever.

### 5. Animate retained transforms and reuse the current interruption model (small/medium cost)

The [Qt retained scene graph](https://doc.qt.io/qt-6/qtquick-visualcanvas-scenegraph.html) preserves rendering primitives and permits geometry transforms without recreating their content. Animate position/scale/opacity of a retained source, keeping an authoritative state machine for destination, generation, cancellation and reduced motion. The repository already has continuous trajectories, presentation receipts and source reuse for retargeting; avoid replacing those proven semantics with four independent ad hoc QML animations.

[Qt 6.11 SmoothedAnimation](https://doc.qt.io/qt-6.11/qml-qtquick-smoothedanimation.html) supports retargeting and direction reversal and is suitable for decorative hover/snap affordances. **Inference:** It can simplify non-authoritative UI motion, but does not establish native family handover, velocity coordination or cross-display presentation. Test fast minimize/restore reversal with retained frames and assert no extra uploads. Use geometry/opacity directly; [ShaderEffectSource documentation](https://doc.qt.io/qt-6/qml-qtquick-shadereffectsource.html) warns that offscreen layers add video memory and usually hurt performance, so adding `layer.enabled` to every preview is not a default optimization.

## Suggested proof boundary

Start with measurements on V29, then one private visible toplevel and one retained-frame owner: acquire → preview → hide without scratchpad → reverse → source stop → output/scale change → destroy. Establish no wrong-window frame, no unbounded allocations, no new texture upload on reversal and real presentation before advancing to decorated family capture. Read-only source research and Scrapling fetches prove API availability and limits; they do not satisfy the open native restore baseline, recovery, hardware or accessibility campaigns.
