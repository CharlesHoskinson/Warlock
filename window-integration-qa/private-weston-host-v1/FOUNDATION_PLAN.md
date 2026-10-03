# Native foundation pending root review/grant

No compositor/probe execution is included in stage preparation. Signed package,
source provenance, actual ldd and offline launcher guards only are accepted here.
Root owns the first composite execution and read-only main snapshots enclosing
the complete context. Old standalone-headless attempt1 stays immutable.

Complete runner command: `python3 ~/window-integration-qa/qa_run.py -- python3
<root frozen foundation runner> <reviewed arguments>`. The wrapper creates a
dedicated qa-harness.slice scope and applies `prlimit --core=1:1` before any
private bus/client. This systemd261 rejects LimitCORE scope properties; root's
actual scope smoke verified the corrected prlimit route and inherited child
(1,1). Explicit `--backtrace` selects unlimited:unlimited for reviewed diagnosis.
The context requires the scope/limits before any output/runtime creation.

```python
from weston_host import PrivateHyprSession
main = dict(os.environ)  # root's main observer uses this exact original copy
with PrivateHyprSession(output=fresh_session_dir, main_env=main,
        width=1600, height=1000, nested_lua=reviewed_lua_bytes,
        dri_prime='pci-0000_00_02_0', mesa_vendor=True) as session:
    private = dict(session.env)
    monitors = session.data('monitors')
    # Enforce root's frozen exact dimensions, renderer/hardware predicates.
    # Root's native producer/GL observation uses private only.
    # Close all fixture input normally and terminate its scoped AX/apps first.
```

`dri_prime`/`mesa_vendor` are explicit device selection, not evidence. Require:

1. Weston logs real GL vendor and renderer, real rendering device, no software
   renderer or pixman fallback. Its live maps record actual Mesa/libgallium paths
   and hashes. The selected real Intel PCI 0000:00:02.0 exposes renderD129.
2. Probe's real wl_linux_dmabuf v4 default feedback completes, main_device maps
   through libdrm to a real render node, its O_RDWR succeeds and DRM driver/PRIME
   capability are reported. No hardcoded feedback, fake main_device or rendering.
3. Private Hyprland starts with AQ_BACKENDS=wayland, against Weston host socket
   only; its own socket/signature/PID-start/config identity and actual monitor
   geometry are recorded. Host surfaceless EGL override is absent in its env.
4. Root's producer hardware predicates remain unchanged. Actual GL context,
   DMA-BUF/buffer/capture/mapped-driver evidence must come from that producer;
   a selected DRI_PRIME or successful compositor startup cannot replace it.
5. Original main identities, public/UI state, focus/cursor, catalog/clipboard,
   reader false and a11y socket are compared read-only. No main surface, input,
   focus/cursor restoration, plugin load, config or reader changes.
6. Normal fixture EOF/quiescent private plugin unload/application/AX shutdown,
   then context terminates private Hyprland, Weston and bus by UID/PID-start.
   All live mapped process data, both persistent renderer logs and inner runtime
   logs/configs are retained before runtime removal. Unexpected private survivor
   is failure even when scoped fallback termination succeeds. Record all tracked
   process identities gone and runtime absent. Failed setup archives logs too.

Qt requests physical host1600x1000 and reviewed Lua scale1. Pointer requests
physical1280x800 and reviewed scale1.25 yielding logical1024x640. Do not infer
visible/full capture of areas without validating actual private monitor/surface.

Runtime isolation addresses the host-window disturbance of earlier native tests;
it does not change their conclusions or upgrade failed hardware/popup/reader
gates. Product v8 and all pointer V8c311 inputs remain immutable.
