# Native minimized/modal family picker

All 61 native checks passed on the frozen V38 host/V33 pair. A separate supervisor
PID/session supplies an explicit focused-peer minimize setup; the actual Elm picker
retains its labeled minimized choice and emits Restore, with real keyboard delivery
to the restored peer. A modal child does not duplicate a picker entry; root selection
activates the unique modal and real keyboard input reaches it. All V39 keyboard,
pointer, MRU, single-family minimize/restore and exact-journal reconnect scenarios
remain. Host/backend normal exit and complete private cleanup passed.

A real picker capture is preserved in the native evidence. Labels and state text
currently adjoin without spacing; this is a bounded UX finding for the next view
refinement. The test host's 420px surface is not production taskbar/popup geometry.
Full human UX/AT/IME, native popup/input and scene, catalog/icons/pins, GPU/WebGPU,
hardware/performance and release gates remain open. No live desktop changes.
