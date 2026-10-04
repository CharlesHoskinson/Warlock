# GPU acceleration and WebGPU qualification

**Hardware GPU acceleration is a mandatory host/release gate. WebGPU is a candidate API whose availability must be proven in the actual pinned shell host.** Its absence does not require CPU rendering: native Vulkan/OpenGL and hardware-accelerated webview composition remain alternatives. Neither an Elm reducer nor finding `navigator.gpu` proves hardware-rendered shell output.

## What is available on this machine

The protected read-only [inventory](gpu-inventory.json) completed on 2026-10-03. Vulkan enumerates Intel Graphics ARL (integrated, Mesa 26.2.2) and NVIDIA GeForce RTX 5090 Laptop GPU (discrete, driver 615.71.09), each reporting Vulkan 1.4 capability. The Vulkan loader reports 1.4.357. Driver enumeration and `nvidia-smi` succeeded.

This establishes hardware and Vulkan API availability, not an executed shell render workload, GPU buffer import, webview acceleration or WebGPU adapter/device acceptance. Those are P1/P4 native proof obligations. The installed WebKitGTK package is 2.52.6; Qt WebEngine is a candidate dependency, not an installed qualified host. Hardware findings do not justify changing Brave flags or compositor settings.

## Three different acceleration layers

| Layer | Owner | Candidate | Qualification |
| --- | --- | --- | --- |
| Elm HTML/CSS shell rendering | Native webview and engine compositor | WebKitGTK or Qt WebEngine hardware path | Actual renderer/backend diagnostics, nonsoftware device, workload trace and displayed frame |
| Optional custom GPU effects/compute | Narrow JavaScript/custom-element renderer inside the host | WebGPU and WGSL | Secure local origin, adapter/device capabilities, known render/compute result, bounded resources, device-loss handling |
| Native application previews and window composition | Native capture/renderer/compositor | Existing native Vulkan/OpenGL, or separately evaluated native wgpu/Dawn backend | Buffer ownership/import/fences, last-presented timing, source-stop survival, output transforms and GPU retirement |

Elm sends declarative effect parameters and opaque identities. The JS adapter/native renderer owns GPU objects and execution; no unsupported Elm kernel extension or raw GPU pointer crosses ports. Elm's standard APIs do not directly bind WebGPU. A native wgpu/Dawn renderer is a separate native integration, even though it follows WebGPU concepts.

Qt's documented path uses Chromium GPU rendering imported into Qt's scene graph; the pinned Qt version and device/driver interoperability need testing, particularly with NVIDIA. Installed GTK components likewise do not prove the required runtime path. [Qt hardware acceleration](https://doc.qt.io/qt-6.11/qtwebengine-features.html).

## P1 WebGPU experiment

1. Create an isolated host with bundled local assets and a secure-origin scheme appropriate to that host. Preserve renderer sandboxing and keep privileged native commands behind authenticated host IPC. Remote debugging and remote navigation remain disabled for release.
2. Record engine/runtime versions and whether `navigator.gpu` is exposed. Request an adapter; record feature/limit availability and independently classify hardware versus software using pinned API/engine diagnostics. A null adapter, rejected device request or software-only adapter fails WebGPU qualification.
3. Request only required features/limits. Run deterministic WGSL render and compute probes; verify output/readback and validation errors, then independently observe a displayed native frame. Readback is test instrumentation, not the production rendering path.
4. Keep GPU objects and frame scheduling local to the renderer. Bound textures, buffers and outstanding frames. Dispose owned resources and test device loss, adapter failure, renderer restart, output changes and resynchronization.
5. Compare end-to-end input/presentation latency, memory, power/wakeups, upload/copy volume and frame deadlines with native GPU and normal accelerated DOM paths. Try integrated and discrete selection where the host supports it; compare battery and performance profiles without assuming that high-performance hints choose a specific device.

WebGPU is a secure-context API and adapters can be unavailable; device loss invalidates dependent GPU resources. Pin behavior against the actual runtime specification/API rather than assume every browser has identical flags or fallback-detection properties. [WebGPU specification](https://gpuweb.github.io/gpuweb/), [device/error handling design](https://github.com/gpuweb/gpuweb/blob/main/design/ErrorHandling.md).

## Preview import and copy budget

Standard browser WebGPU does not establish arbitrary native DMA-BUF import merely because a native frame lease exists. Prove the selected host's actual interoperability path. A VideoFrame/video-based import, native overlay, engine extension or native renderer has different ownership, copy, synchronization and security properties. Keep a native GPU preview path available while evaluating them.

Record external-memory/fence support on each native adapter, copy count/bytes and cross-GPU transfer. Define the acceptable copy budget from measurements in P0; do not promise zero-copy before proof. Source-stop survival, decorated/modal-family capture and producer/consumer retirement remain mandatory. WebGPU device loss must not replay a stale window focus/minimize intent.

## Release and failure policy

Select a host only after actual hardware-accelerated rendering passes the frozen P0 budgets and protected native acceptance. Publish the selected GPU/backend and qualification verdict in the release evidence. A software renderer can preserve essential controls during failure, but is explicitly degraded and cannot satisfy the GPU acceleration gate.

If WebGPU is unsupported or fails, disable its optional effects and retain an accepted native/engine GPU path. If every GPU path fails, preserve essential controls in a disclosed recovery mode and block promotion of that configuration as an accelerated release. Recovery must remain usable without a GPU-accelerated Elm view.

## Shared-host native result — 2026-10-04 UTC

The [V157 source/evidence packet](../../implementation/elm-shared-gpu-qa-v157/HANDOFF.md) passes142 native checks with the actual shared output host. A compiled WebGL shader reads backRGBA(17,193,71,255), and an independent native screenshot showsRGB(17,193,71). WebKit native diagnostics identify Mesa Intel Graphics(ARL), EGL/OpenGL and renderD129. Web-exposed debug strings instead say Apple GPU; those strings are not hardware identification evidence.

The local origin is secure, but this pinned WebKitGTK2.52.6 host exposes no navigator.gpu. No WebGPU device/WGSL execution is accepted. This bounded graphics result does not close measured workload/presentation/resource budgets, context loss, hybrid devices, preview imports/fences, actual AT/IME or release gates. Native diagnostics support DMABuf, which alone is not zero-copy or import-safety proof.
