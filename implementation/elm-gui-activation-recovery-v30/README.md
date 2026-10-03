# Actual activation and recovery with stable window order

Verification pending. Fresh V29 derivative fixes the QA reconnect reporter scope
error and keeps Elm window controls sorted by opaque incarnation within the current
binding, so native raise/activation does not reorder displayed controls. Reruns real
pointer/Elm/native focus and keyboard delivery, original minimize/restore and actual
broker interruption/fresh-binding reconnect. Preserves original deadlines and
failures. This remains a control integration harness, not completed taskbar, scene,
accessibility/IME/GPU, full UX or release acceptance.
