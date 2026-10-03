# Canonical decorated atlas candidate v15

Compiled offline; never loaded. Built against current installed Hyprland headers, retaining existing PLUGIN_INIT ABI hash comparison. `build-report.json` records exact native binary/source hashes and running ABI.

## API and scope

`hl.plugin.hyprbars.window_atlas(address, stableId, pid, pngPath, captureEpoch)` returns the complete canonical decorated rectangle at owning output scale, including pixels in output gaps/off-output extents. Capture epoch must match `[a-f0-9]{12}-[0-9]+` and the private PNG filename. Identity, native geometry and capture restrictions are checked; epoch is echoed for the later route coordinator to validate against its latest accepted request. The native API has no independent authority over service request epochs.

Existing `window_snapshot` API is preserved (metadata has additional canonical=false/captureEpoch empty fields). No production helper calls the new API yet.

Renderer uses an atlas-sized framebuffer with RPT_EXPORT, transformDamage=false, noSimplify=true and translation through renderModif. The real monitor/window at/size/scale/transform/workspace/pin are unchanged. Legal protected member access uses a derived pointer-to-member adapter called on the actual base renderer; no reinterpret cast or private layout access. Native caption scissor is translated and unrotated only for snapshot+export rendering.

Shader restore uses public useShader and currently rejects an unknown prior GL shader (including program0). This is an explicit safe unsupported path until validated; it must not be removed solely to make a native trial pass. Render pass/data/mode/snapshot flag, viewport/scissor backend caches, blend/capabilities, stencil/color state, audited texture units0/1/2/8 and active texture/VAO/buffer bindings are restored. Framebuffer/readback/EGL restoration remains in the outer snapshot bridge. Monitor blur scheduling flag is retained.

## Outstanding proof and integration

No visual/native acceptance yet. Requires bounded nested smoke: gold caption/red client exact placement and full spanning/gap pixels, byte-equal capture under blue occluder, all8 output transforms and mixed scale, fullscreen respecting native decoration absence, stale ID/PID/epoch reply rejected, at/size/pin identity preserved, GL/backend cache equivalence and subsequent normal rendering, unload cleanup. Border code has monitor-based geometry calculations that require actual transformed-output proof. Shader rejection frequency and conversion behavior must be measured. Any incomplete capture must fail explicitly.

Service/QML global route coordinator, per-output handshake and shared frame clock are not implemented in this candidate. A compiled atlas alone does not resolve the cross-output motion gap.

## Shader/cache boundary

Uniform values and private CShader.uniformStatus are not restored to their earlier contents. Atlas uses public setUniform* methods, keeping each touched program's cache coherent with its GL uniforms. Normal drawing must set its required projection/color/geometry/sampling values again. Source texture rendering also updates shader VBO UV data and usesCustomUV together; the next non-custom draw reloads defaults if needed. Attribute layouts are initialized only for new shader VAOs in Shader.cpp232–246; existing per-draw rendering changes VBO data rather than attribute pointers/EBOs. These are material cache changes, not full shader-state equivalence. The nested matrix checks subsequent normal frame pixels. No raw GL uniform restoration is used.

Hash-pinned native runner is ../nested_atlas_smoke.py. It has not been executed and is only for the coordinated isolated GUI slot. Default16 transform/scale cases plus off-output and mixed-scale gap coverage. Unknown prior shader rejection remains an explicit failure report.
