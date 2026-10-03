# Crash-notification noise: final solution

Sources: A-watcher.md (the crash watcher), B-source.md (the QA harness under the sandbox), C-system.md (kernel and coredump mechanisms, upstream bugs).

## What is happening
- 22 of the 26 crashes since 2026-09-30 came from one terminal running another Claude session's window-integration QA: nested Hyprland, its Xwayland on :1, a test quickshell, Orca probes, and a portal on a private bus.
- They run inside Claude Code's sandbox, which blocks /run/user/1000, /tmp/.X11-unix and /dev/dri.
  - Xwayland and Hyprland abort at startup.
  - The test shell and the Orca probe then crash on the dead display connection.
- The real desktop's Xwayland (:0), bar and portal never crashed. Its real crashes were grim (fixed by the local grim 1.5.0-2.1) and gnome-keyring (fixed by the local 1:50.0-1.1).
- `OMARCHY_CRASH_IGNORE` matches only the program's basename. The current value, `^(node|npm|vitest|Hyprland)$`, caught 5 of the 26 crashes and is too broad: it would also hide any Node or Electron app.

## The solution, in three layers

### 1. This machine: a provenance-aware crash watcher
A user override replaces only what the unit runs. Nothing in /usr is edited.
- `~/.local/bin/omarchy-crash-watch-filtered` is a copy of the 4.0.4 loop (stamped with the source version) with two extra rules:
  - Ignore `Hyprland | Xwayland | qs | quickshell | xdg-desktop-portal*` when `COREDUMP_USER_UNIT` is a terminal scope (`app-*-xdg\x2dterminal\x2dexec-*.scope`). The desktop's own copies run under `wayland-wm@hyprland.desktop.service` or their own services, so they still notify.
  - Ignore any crash whose `COREDUMP_CMDLINE` or `COREDUMP_CWD` lies under `~/window-integration-qa` or `~/window-behavior-spec`, and node or vitest under `~/src/*/web` dev lanes. Hermes (python) crashes elsewhere still notify.
- `~/.config/systemd/user/omarchy-crash-watch.service.d/override.conf` points `ExecStart=` at that script. `ignore-dev.conf` is removed, because its name-only rule is replaced by the provenance rules.
- **Verify:** replay the 26 recorded journal entries through the filter. Expected: 22 QA crashes and 2 vitest crashes ignored; grim and gnome-keyring notified.
- **Undo:** delete the override file, then `systemctl --user daemon-reload && systemctl --user restart omarchy-crash-watch`.
- **After `omarchy update`:** diff /usr/bin/omarchy-crash-watch against the stamped copy.

### 2. At the source: the QA harness (the other session's code)
- Launch the harness tree as `systemd-run --user --scope --slice=qa-harness.slice -p LimitCORE=1 -- <launcher>`.
  - With a pipe core_pattern, a limit of exactly 1 makes the kernel skip systemd-coredump (`fs/coredump.c`), so there is no journal entry and no toast.
  - Use `-p LimitCORE=infinity` for a run where a backtrace is wanted.
- In nested_*.lua that need no X11, disable Xwayland: `hl.config({ xwayland = { enabled = false } })`.
- Pass a verified-live parent `WAYLAND_DISPLAY` explicitly. Use one `XDG_RUNTIME_DIR` scheme (three are in use today).
- Run compositor launchers outside the sandbox (`sandbox.excludedCommands`), or allow their sockets explicitly.
- Shut down clients first and the nested compositor last. Have abi_client.py check its AT-SPI/X connection before using it.

### 3. Upstream (optional)
- omacom/omarchy: a feature request for cgroup, unit or cwd filtering in crash-watch, citing #10662, #11992 and #11569. Then layer 1 can be retired.
- at-spi2-core: libatspi calls `XKeysymToKeycode` with no live X display (an unguarded client path).
- quickshell: a SIGSEGV in `QInputMethod::commit` during `~QQuickItem` (the same class as #1228, #1165 and #1169). This one needs a repro outside the harness first.
- Xwayland's InitOutput FatalError is already known upstream (#1239, #884, #1574), so there is nothing to file.
