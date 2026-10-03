# Private Qt WindowModal V6 diagnosis fixture

Offline only; no native launch. Preserve accepted Qt203 and failed V4/V5 packets unchanged. Host V4 and private AQ4ed46/production v18 modules are unchanged.

V6 preserves all nineteen strict routing/callback/family/lifetime feature gates. It adds a private read-only native diagnostic module with a guarded runtime/scope/core1 and actual public Hyprland API/ABI match. It observes hit/pointer/focus/modal-history and input guard state plus bounded button events; it never focuses, raises, dispatches, changes input or installs hooks. Ten host gates separately verify native maps/readiness/diagnostics/transport.

The public Qt observation fixture reports button client bounds and updated activation state. It verifies the owner button callback before opening a modal, then reuses that exact point inside the same button and outside child surface. The same positive child button is reused outside the nested child. Global input coordinates derive from actual native root surface bounds; Qt Wayland global position alone is not authoritative.

Quit success requires exact synchronous quit command/epoch event and exit0, then captures final destruction events. Private fixture env uses the official Qt6.11.2 QT_NO_XDG_DESKTOP_PORTAL opt-out. All unexpected descendants, forced shutdown and any protocol/pipe/DRM error remain failures. The old failed owner-route gate is not waived or rewritten.

Scoped offline tests and Werror native/Qt compilation are recorded. The additional probe has not been loaded, and Lua execution/modal behavior/portal suppression await an exclusive root grant.

Frozen command after review:

```bash
python3 /home/hoskinson/window-integration-qa/qa_run.py -- python3 /home/hoskinson/window-integration-qa/qt-modal-private-v6/run_native.py --attempt /home/hoskinson/window-integration-qa/qt-modal-private-v6/attempt-1
```
