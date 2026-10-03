# Cross-output decorated minimize/restore route

Status: offline design and geometry/model prototype only. No installed code, accepted reversal stage, native plugin, shell or user window was changed. This remains an unmet visual requirement until actual decorated pixels are observed across outputs.

## Confirmed gaps

| Layer | Current behavior | Required extension |
| --- | --- | --- |
| Native export | v14 `snapshotBridge.cpp` rejects non-normal transform and clients spanning the owning monitor. Its `makeSnapshotFB(window)` framebuffer is exactly that monitor's pixel size. | Capture a complete canonical decorated window image, independently of occlusion, including client portions outside a single output. |
| Service | `prepare` rejects taskbar screen differing from source/destination, and rejects either client or decorated rect outside that output. | Plan a global source→actual visible taskbar icon route and capture/present all participating outputs before native hide. |
| QML | `motionReceive` accepts only `request.target.screenName`; each frame has a local independent NumberAnimation and subtracts one monitor origin. | Share one token/clock/global rectangle; project that same image/rectangle into every intersecting output. |
| Geometry | Service bounds use width/scale and height/scale without transform swaps. | Use monitor logical bounds from transformed physical extent divided by scale (90/270 and their flipped forms swap axes). |
| Fullscreen | Native renderWindow deliberately disables borders and caption for actual fullscreen. Taskbar may be hidden, so no actual icon endpoint exists. | Preserve native fullscreen state and exact displayed client image; reveal the owning taskbar endpoint through its existing transient reveal policy, or explicitly classify unavailable endpoint. Never invent a caption that was not present. |

Removing current checks is insufficient: it would produce an incomplete client/caption image or a route clipped at the output seam.

## Source-supported capture path

Primary source inspected locally: `~/src/hyprland-motion-audit/src/render/Renderer.cpp` and `.hpp`, `GLRenderer.cpp`, `render/gl/GLFramebuffer.cpp`, `OpenGL.cpp`; accepted `whole-window/native/{snapshotBridge.cpp,barDeco.cpp,BarPassElement.cpp}`. Installed ABI guard remains mandatory.

`IHyprRenderer::makeSnapshotFB(PHLWINDOW)` (Renderer.cpp:3087) selects `window->m_monitor`, allocates owning-monitor pixel dimensions, begins a full fake render, clears transparent, and draws that window with native decorations. Thus it cannot export the complete spanning rectangle simply by widening the readback crop.

`IHyprRenderer::renderWindow(window, monitor, time, decorate, RENDER_PASS_ALL)` is public in the installed header. The nearby “old private” text is a comment; the actual private section starts later. `createFB`, `beginFullFakeRender`, `startRenderPass`, `draw`, `endRender`, projection and monitor-transform stack methods are also public. This permits a dedicated, ABI-guarded native export without modifying window at/size/monitor/workspace/alpha.

Two paths:

1. **Per-output own-window fake-render tiles:** explicitly render the same window and decorations into each touched output's transparent framebuffer using that output's scale/color description. Normalize each rotated/reflected readback into global logical orientation, and assemble tiles at a declared canonical scale. This can deliver the common case where the entire decorated/client rectangle is covered by connected outputs. Each tile must come from the own-window render; desktop screenshots cannot be used because occluders contaminate pixels.
2. **Canonical window atlas:** required for window pixels in display gaps or beyond all output bounds. A complete window image includes these currently invisible pixels, since shrinking can bring them into visible outputs. Stitching visible-output crops cannot supply them. Render the full decorated bounding box into an offscreen canonical atlas with a scoped projection/translation and matching viewport, damage, scissor, stencil and render-pass bounding-box coordinates. Public render state can be scoped; no native window geometry or monitor configuration may be rewritten. This is the complete required solution.

The exact atlas implementation is unproven. `CGLFramebuffer::bind` uses monitor pixel size for viewport when a monitor is active; projection-only changes are insufficient. Surface/border/bar scissor and pass bounding boxes also need the same atlas translation. Retain and restore compositor render-data, current pass, transform stack, snapshot flag, GL framebuffer/pack/viewport/scissor/stencil/blend state and EGL context on every success/failure. The existing v14 normal-output crop is top-left fake-framebuffer coordinates with no Y inversion; rotated/reflected normalization must be proved with asymmetric actual native pixels rather than assumed from desktop screenshot conventions.

Capture must validate exact mapped address/stable ID/PID, noScreenShare, geometry/fullscreen/decorative bounds, output topology/scale/transform and framebuffer sizes before and after rendering. Output image staging remains per token in the private runtime, with atomic metadata publication and accepted bounded janitor behavior. A topology change discards the candidate atlas, leaving native geometry untouched. Canonical alpha is premultiplied; color space conversion between differently configured outputs requires a declared common atlas image description and native proof.

## Route coordinator

1. Capture exact identity, native geometry and home desktop/display as today. Switch a restore destination while native remains minimized. Resolve the **actual visible icon rectangle**, including a remote output if policy puts its icon there.
2. Snapshot one immutable complete decorated atlas at a declared scale. `rect` is global logical whole-frame bounds; `nativeRect` is the exact client rectangle. Atlas metadata preserves insets, source pixels, transform/color description and fullscreen/decorative mode.
3. Compute output participants from the enclosing bound of source and icon rectangles. New `routePlan` carries topology generation, token/identity, both global rectangles, image, and all required screen names/logical extents. Static over-inclusion is safe; discovering new outputs during a running route is unnecessary.
4. A single QML route coordinator owns progress and current global rectangle for the token. Every passive output panel binds to that same rectangle/image, subtracts only its logical origin, and clips at its screen. Panels retain transparent surroundings, an empty input region and keyboardFocus=None. Screen rotation is handled by Quickshell/compositor presentation of the normalized image; do not rotate that image a second time.
5. Every required output must acknowledge the decoded image and a presentation opportunity before native minimize. One output's Image.Ready cannot authorize hiding the whole spanning native window. Restore reveals native only once, after the shared endpoint. Per-output done callbacks have no native authority.
6. Latest captured reversal freezes the **shared** rectangle/image before slow metadata queries, preserving the deployed freeze contract. All panels retain the same epoch and source lineage. A shell/output loss, reduced motion, capture/readiness failure or deadline cancels every fragment and freshly validates the identity before settling latest native intent.
7. Presentation rate differences require measured seam skew. A shared JS property prevents independent easing phases but does not by itself prove atomic presentation across 60/144/240Hz outputs. Native evidence must measure actual per-output rectangles against the same monotonic route sample, recording refresh misses.

A later native compositor render-pass coordinator could draw the same atlas directly into all outputs, avoiding Quickshell decode/panel cadence. This should be a separate implementation decision after profiling; it is not necessary to weaken the required global rectangle or introduce native geometry tweens.

## Model and planner evidence

`cross_output_motion.qnt` represents complete-atlas proof, both output readiness acknowledgements, one progress value, global fragment coverage, native geometry/pixel preservation, latest reversal, output removal, reduced motion and identity reuse. `cross_output_motion_test.qnt`: **6 named scenarios** pass; **2000 samples ×100 steps** pass. This is a design contract, not installed implementation verification.

`route_planner.py` is an offline mathematical prototype. **10 tests** pass, including all eight Wayland transform extents, mixed scale, negative coordinates, spanning seam UV coverage, fullscreen bounds, exact reversal source, and 2000 seeded sampled routes. A gap example proves monitor crops cover only 40/90 of the source width, rejecting the assumption that visible tiles form a full image.

```bash
cd ~/window-behavior-spec/minimize-motion-stage/cross-output-design
python3 test_route_planner.py
quint test cross_output_motion_test.qnt --verbosity 1
quint run cross_output_motion.qnt --invariant allProps --max-samples 2000 --max-steps 100 --verbosity 1
```

## Required isolated native proof before main deployment

- Two output nested compositor: centered and seam-spanning client, full native gold caption and asymmetric client quadrants, independently occluded on both outputs. Capture must include both sides and no occluder bytes; hidden gap/off-output bytes must remain present in the full atlas.
- All eight transforms plus scales 1/1.25/1.5/2: corner colors, exact client inset/rectangle recovery, full caption baseline, rounded alpha and full-buffer dimensions. Include mixed scale and negative output origins.
- Fullscreen/maximized mode parity: expected caption visibility, exact saved at/size/fullscreen/pin and endpoint state, taskbar transient visibility with a real icon endpoint.
- Global route source→remote icon→source, including seam/gap and reduction/reversal after observed active presentation; same image lineage/epoch and bounded cross-output phase skew.
- Missing output, topology change, unknown icon, output removal during capture/readiness/tween, shell reload, close/reuse, stale output-ready/done, native failures, and all modal family pin bits.
- Plugin unload, GL/EGL/render-state restoration, and original main desktop identity/focus/cursor/AX preservation.

No production readiness claim is made from the offline prototype. Root coordinates every GUI run and native installation.
