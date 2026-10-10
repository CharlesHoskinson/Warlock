# Task View AT crash diagnosis and current native restoration

The selected-filter revision `4c3e31ddc8ac46756ed8a53ebfd0f8179f834bbb` passes [the original native cross-workspace restore journey](current-native-navigation.report.json): Task View and taskbar selection produce exact native receipts, workspace-2 pixels, physical keyboard delivery to the peer, unchanged membership and stale-context refusal. Owned clients and protected session cleanup pass. This covers the native journey; the AT obligation remains open.

[The ancestor debugger](diagnostic-runner.py) captures SIGABRT in the WebKit main-thread GIO callback. Library resolution identifies libc, WebKit and GIO frames; graphics workers wait. The exact WebKit function symbols remain unavailable. The stack shape resembles [upstream text-offset bug 278980](https://bugs.webkit.org/show_bug.cgi?id=278980), which is a hypothesis rather than an established identity. No core limit, ptrace setting, system package or main desktop configuration was changed.

A presentation-only experiment hid redundant visible label children from the accessible subtree while retaining canonical names and state. It still crashed before original AT filter activation; source and compiled assets were reverted. Both its build and failed native report remain retained. No original AT scenario or release is accepted. Exact original artifacts, source and library identities are in [manifest.json](manifest.json).

Stop expanding this investigation; continue mandatory original overview-retire behavior. The selected transfer member can disappear while the destination chooser remains open with no destinations. That concrete product gap needs coherent exact-incarnation retirement and a safe browse-focus fallback without any native mutation.
