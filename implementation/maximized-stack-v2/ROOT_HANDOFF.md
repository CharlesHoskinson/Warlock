# Built native stacking fix, pending activation

The installed core's render/hit mismatch was reproduced under a private headless Weston/Hyprland session with real colored Wayland windows. A green peer remained visually above a raised red floating native MAX, while clicks went to red. The first reproduction retained a cleanup-invariant failure (all descendants were still retired); a fresh diagnostic explicitly retired private-bus auxiliaries and completed cleanly. Both reports remain in v1.

Formatted v2 corrects only the final renderer pass. Native MAX stays native; no resize workaround, alpha/input flags or saved return geometry is changed. True fullscreen and tiled MAX guards are unchanged. Pinned peers remain exempt.

The complete original-to-v1 core build passed. The formatted v2 renderer was then compiled into a fresh static archive and fresh executable without altering the v1 executable/archive. The unchanged titlebar plugin was built against exact candidate core/protocol/version headers; all 710 recorded compiler dependencies were rechecked before publishing `PAIR_READY.json`. Source/model checks cover 192 stack/pin combinations; owning clang-format validation passes.

`native-stack-smoke-1791036734961323596.json` passed seven private native checks with the paired plugin actually loaded: peer raise; MAX raise; visible MAX/click agreement; MAX lower; pinned peer above MAX; unpin followed by MAX raise; actual MAX mode preservation. Clean teardown is recorded. This is targeted stacking evidence, not completed original broad parity/native campaign or Brave-specific modal/multi-output acceptance.

A verified user-owned pair is copied to `~/.local/share/omarchy-native-pairs/floating-max-stack-v2`. The staged session drop-in retains `/usr/bin/start-hyprland`'s watchdog via `--path`, and a hash-checking launcher binds the paired plugin to the new compositor. Staged `autostart.lua` selects that plugin only when the launcher supplies its environment variable; the current desktop uses its original plugin. Python/Lua syntax and prospective systemd unit verification passed without activation.

`activation-ready.json` describes reviewable package/wiring hashes. `apply_activation.py apply` verifies them, saves the original autostart, installs only user-owned session wiring, reloads config and refuses config errors. It does not restart/log out. `rollback` restores verified original wiring. The compositor switch needs logout/login and closes current applications; no logout/restart is authorized by elapsed time or by earlier read-only testing.

Current main compositor remains original. Taskbar v3 efficiency updates are separately enabled. Once the user explicitly agrees to the disruptive session transition, apply through protected `qa_run.py`, then perform the agreed logout; after next login verify actual executable/plugin maps, native pair hashes, config errors and Brave behavior. Broader original regression gates remain open.
