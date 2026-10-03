# Actual output movement, scale and 180-degree transform

The private native campaign passed 111 checks with cleanup. It reuses the frozen
V23 core/plugin, preserves the original regressions and adds real output movement,
125% scale and a 180-degree transform. Fresh frames receive higher configuration
generations; retained frames preserve their original configuration. Actual pixels,
pointer presses/releases and keyboard receipts agree inside and outside the peer
input hole at fractional scale and after the transform. The source and full native
packet are preserved in `qa/native-1791067430470077279/report.json`.

The V24 failure remains unchanged. grim normalizes output transforms, while the
virtual-pointer protocol maps normalized absolute coordinates to logical output
space. The fresh runner uses integer helper coordinates consistent with those
interfaces. This proves neither physical-device calibration nor raw scanout
orientation. Buffer/viewport/clip mapping, multi-output hardware, complete roles,
presentation, performance, human UX, accessibility/IME and release remain open.
V26 extends this fixture to all eight transform values. No live desktop changes.
