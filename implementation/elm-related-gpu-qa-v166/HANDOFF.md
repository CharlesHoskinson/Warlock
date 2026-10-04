# Related-view shared-renderer graphics qualification

V165 combines the reviewed V162 related-view construction with V156 QA-only
WebGL canvas/readback and the restricted native WebKit GPU diagnostics view.
V166 passes142 native checks, including original91/shared-output behavior. Shader
readback17,193,71,255 agrees with the native displayed screenshot pixel17,193,71.
Native diagnostics identify Mesa Intel Graphics(ARL), EGL/renderD129 and accelerated
canvas. WebGL's Apple GPU debug identity is ignored for hardware identification.
Secure local origin still exposes no navigator.gpu: WebGPU remains unavailable.

The unprivileged diagnostics view has no bridge, admits only webkit://gpu, is0x0
and retires on exit. It is a separate QA-only view/renderer; the nine-process
production-like result belongs to V162/V163/V164, not this instrumented GPU run.
Actual displayed pixels come from the bar screenshot, not the hidden diagnostics.

The host/backend exit normally and protected ordered cleanup passes. Source/ABI
closure retains original check/wait/click/choose/key ASTs/deadlines. Exact Elm
37+58+12 and Quint10 named/1000 sampled traces are inherited, not newly rerun.
No zero-copy, fence/import, actual device/context loss, cadence/power/budget,
hybrid/physical-display, AT/IME or release acceptance is claimed. Native recovery
work follows the separately retained V167/V168 failure packets. Installed GUI unchanged.
