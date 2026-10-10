# Minimized output-area recovery

A real taskbar Minimize committed before the returned output changed to 400x200 at (-400,-200). The application remained minimized across reconciliation, then a real taskbar Restore committed exactly once at reachable position (-360,-32), preserving size108x440/workspace2 and its unsaved draft. Actual client pointer press/release, physical keyboard editing and painted pixels pass normal cleanup. Existing production placement already covers this ordinary minimized case; no new production behavior is claimed.

[Manifest](manifest.json) records the original EARS/oracle, exact unchanged native tuple and native report/image hashes. Original deadlines and normal helper cleanup are retained. The preceding zero-output/drag/draft journey runs unchanged before this added minimize-before-reconfigure fixture. UI-019 and full-release acceptance remain open.
