# Shared-host graphics qualification

V156 preserves the actual one-controller/one-backend output host and adds
QA-only graphics instrumentation. Each bar draws one32x32 WebGL triangle in a
known color, reads one pixel, retires its shader/program/buffer objects, and keeps
the small canvas alive for independent native screenshot comparison. The probe
creates no animation loop or privileged effect interface. An unprivileged hidden
WebKit diagnostics view uses the same native context/settings, admits only
webkit://gpu, has no registered native message bridge, and retires on host exit.

V157 passes142 native checks, including all original91 assertions/helpers and
the shared-host output, resize/scale/rotation, removal/replug and broker recovery
campaign. WebGL readback is[17,193,71,255], error0. The independently captured
native screenshot pixel at(780,24) is[17,193,71]. Both bars execute the shader.
Native WebKit diagnostics report GL_RENDERER Mesa Intel(R) Graphics(ARL), vendor
Intel, OpenGL4.6 Mesa26.2.2, EGL, render node /dev/dri/renderD129, accelerated2D
canvas, policy always and DMABuf support for hardware/shared-memory buffers.
This combines actual shader execution/display with engine/device diagnostics;
settings or renderer-string presence alone are not the proof.

WebGL's debug extension instead reports Apple GPU/Apple Inc. on this Linux
machine. Treat those web-exposed strings as unreliable hardware identification.
V155's named nonsoftware-string check was insufficient and is superseded by
V157's separately captured native diagnostics. Preserve both packets. V153
stopped when Pillow was unavailable; V155 samples the same native PNG using the
already installed ImageMagick executable, whose hash is recorded.

The pinned runtime is WebKitGTK2.52.6, GTK3.24.52 and gtk-layer-shell0.10.1.
The local origin is secure, but navigator.gpu is absent on both tested views.
Therefore browser WebGPU is unavailable for this host; no WGSL/device/compute
execution is accepted. The optional branch is build-only code until an engine
actually exposes the API. Its deadline marks cancellation and destroys late
returned devices/owned buffers. Native GPU or another qualified engine remains
an alternative; do not disable sandboxing or change the live desktop to obtain it.

Every Elm module still matches frozen V145 (37 shared-controller,58 controller,
12 presenter checks; abstract Quint10 named/1000 traces). Actual optimized
Main/Bar/Popup and C host compile; native11 host groups and4 surface groups pass.
The host/backend exit normally and protected ordered cleanup passes. Failed and
superseded source/evidence are included in qa/slice-manifest.json.

This is a bounded shared-host graphics component, not host-selection/release
acceptance. The diagnostics view has size0x0 and cannot independently establish
a displayed frame; the separate actual bar screenshot supplies that observation.
Support for DMABuf does not establish zero-copy, fence/import safety or selected
buffer format. Dense workloads, p95/p99 latency/cadence, resource/power/soak
budgets, context/device loss, hybrid GPU selection, physical displays, native
preview imports, actual AT/IME, menu integration, full scene and release remain
open. No requirement or complete sprint is closed. The installed session is
unchanged.
