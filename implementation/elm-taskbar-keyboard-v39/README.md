# Native grouped taskbar keyboard and recovery

The V38 host/V33 core-plugin pair passed all 48 checks. Actual Escape restores the
scoped opener without a native window effect; Tab/Enter selects a family and sends
keyboard input to that application. Pointer Close is visible and restores its
opener. Original grouped pointer activation, active-choice no-minimize, surviving
MRU, single-family minimize/restore and exact-journal Pending/Unknown/reconnect
checks passed. The host/backend exited normally and private cleanup passed.

V36's inactive-after-retirement assumption and V37's QA render-contract mismatch
remain preserved. No full AT/IME, production bar/popup, canonical scene, GPU,
hardware/human UX or release acceptance is claimed.
