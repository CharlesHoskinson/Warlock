# Focused Quick shutdown candidate

This folder is offline staging. No installed binary or loaded V3 library was overwritten.

Build the fresh bridge with:

```sh
cmake -S source -B build
cmake --build build -j2
c++ -fPIC -std=c++20 -Wall -Wextra focus-cleanup-probe.cpp -o focus-cleanup-probe $(pkg-config --cflags --libs Qt6Quick Qt6Gui Qt6Qml)
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software QT_ACCESSIBILITY=0 NO_AT_BRIDGE=1 ./focus-cleanup-probe "$PWD/WindowAccessibilityV4/libwindowaccessibility.so"
```

The probe loads the actual plugin, verifies a Quick leaf has active focus, quits through the event loop, verifies leaf/scope/content focus cleared, then deletes the GUI app before the Quick window to match the observed Quickshell ownership order. `offscreen-probe.log` records exit zero. It does not connect to the physical Wayland session or enable the session AX flags. Its helper covers inactive focus scopes as well as the active leaf.

The fresh copied `disposable-controls/shell.qml` imports V4 and adds observer IPC `focusDiagnostic` plus QA-only `forceQtFocus`. It has a dedicated layer namespace and ignores any inherited menu payload. This configuration must only be launched with the root agent's GUI slot grant. Use normal `qs kill -p <disposable-controls-path>` after confirming actual internal active focus; do not hide the controls first and do not substitute SIGKILL.

The stronger Quickshell ownership correction is `quickshell-root-before-app.patch`. It ensures RootWrapper/QML engine/window destruction precedes GUI app destruction. It is reviewable source only; no global quickshell build or package replacement was performed.

## Native result and deployment

The exact copied-controls normal shutdown passed. `disposable-controls-report.json` records the actual Qt leafFocus=true and leafActiveFocus=true immediately before normal `qs kill`; the menu stayed opened until shutdown, kill returned zero, and the process exited zero. `disposable-controls.log` has no teardown crash. The fresh library was then copied to `~/.local/share/hypr-window-controls/qml/WindowAccessibilityV4`, original V3 controls hidden and stopped normally, and controls relaunched with V4. Taskbar widget_reader_v3 and TaskView overlay_v13 use the fresh V4 import. `deployment.json` records the paths and original control PID.
