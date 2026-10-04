# Preserved external unfocused native-state failure

The authenticated supervisor minimized an unfocused root with Committed outcome,
kept the peer focused, and confirmed native minimized state. The V38/V33 frontend
picker did not retire automatically within the original six-second deadline.
Existing pointer/keyboard/modal checks reached their original assertions; no
manual refresh substituted for invalidation. Host/backend normal exit and complete
private cleanup passed. V43/V44 address this defect through native invalidation.
