# Private Qt WindowModal orchestration review

Prepared offline only. No Qt/private compositor was launched by this packet. Accepted main Qt203 manifest stays unchanged. The public QtWidgets6.11.2 fixture/source/binary remain byte-identical.

The runner uses the signed user-local host through private-weston-aq-host-v2 adapter, explicit1600×1000 headless Weston GL→private Hyprland Wayland scale1, and explicit Intel pci-0000_00_02_0/Mesa vendor selection matching root's graphics foundation. Scope/core/runtime guards are the unchanged shared qa_run.py/qa_launch.py. Both source and effective Lua explicitly disable Xwayland. No main top-level or input is requested.

Exactly19 Qt feature gates retain the accepted plan: same QApplication peer action under genuine QDialog.open WindowModal, blocked parent/deepest routing, real button callbacks, native/public parent metadata, one production-helper family minimize/restore pair, close/destroy lifetimes and independent peer survival. Host gates and fixture command acknowledgments are counted separately. The real pointer motion is observed through private IPC before buttons; no physical hardware, reader, or taskbar-rendered motion claim is made.

The main observer runs before host startup and after complete host cleanup, using the original explicit environment in separate workers. It captures whichever zero/one original Files process is currently running, its actual PID/start/instance/full/public state and actual visibility. Strict focus/cursor/client/catalog/clipboard/a11y preservation may fail if the user changes them during the run; no main restoration or overrides are performed. The accepted observations helper remains unchanged; this fresh stage owns its dynamic version.

All owned Qt/pointer/motion clients exit normally before native plugin unload, child compositor, private bus and Weston teardown. Any forced cleanup or retained survivor is a failure with evidence. Private socket basename may equal main's basename when absolute paths/runtime/inodes differ; raw basename equality is not a target identity.

Fresh exclusive0700 attempt command, pending root review/grant:

```bash
python3 /home/hoskinson/window-integration-qa/qa_run.py -- python3 /home/hoskinson/window-integration-qa/qt-modal-private-v2/run_native.py --attempt /home/hoskinson/window-integration-qa/qt-modal-private-v2/attempt-1
```

`python3 run_native.py --preflight` reads/verifies hashes only and launches no native process. Source freeze includes actual host package/module/probe/dependencies/link targets, production native/helper/pointer inputs, main observer and fixtures. Freeze and native execution are held: the first accepted graphics-bootstrap proof did not establish healthy configure/ACK ordering. Root is preparing a fresh private AQ selection/configure repair; the final packet must reference that reviewed adapter and actual healthy foundation result before any execution.
