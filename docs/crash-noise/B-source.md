# Why the overnight window-integration-qa crashes happened, and how to fix the harness

Read-only research, 2026-10-01. Source material: `~/window-integration-qa/*.lua`,
`~/window-integration-qa/*.py` (esp. `recovery-audit/keyboard-monitor/abi_client.py`,
`live_drag_bridge_nested.py`, `run_pinned_modal_nested.py`), `~/.local/share/hypr-window-controls/`,
plus Claude Code's own sandboxing docs (code.claude.com/docs/en/sandboxing) and public
Hyprland/aquamarine/Xwayland issue trackers.

## tl;dr

All four crash signatures are one root cause wearing different faces: **the compositor
process tree is launched as a child of a sandboxed Bash command, so bubblewrap's mount
namespace and (if installed) its seccomp filter apply to Hyprland, Xwayland, quickshell
and the AT-SPI probes too** — and none of those binaries' actual runtime homes
(`$XDG_RUNTIME_DIR` under `/run/user/1000`, `/tmp/.X11-unix`, GPU/seat devices) are in
the sandbox's default allow-list. Two of the four crashes are the sandbox blocking a
resource outright; the other two are *downstream* collateral damage from the session
dying mid-flight.

## What Claude Code's Linux sandbox actually restricts

From `/docs/en/sandboxing` (fetched 2026-10-01):

- Linux/WSL2 isolation = **bubblewrap** (mount/pid/user namespace) for filesystem, plus
  an **optional** seccomp filter (`npm install -g @anthropic-ai/sandbox-runtime`) that
  additionally blocks arbitrary Unix-domain-socket `connect()`/`bind()`.
- **Default write access**: current working directory + the per-user `$TMPDIR` + any
  `--add-dir` paths. Nothing else.
- **Default read access**: broad (whole machine, minus denied paths).
- **Restrictions apply to the Bash/PowerShell/Monitor command *and all its child
  processes*.** A compositor spawned from a sandboxed Bash call stays inside the jail
  for its entire process tree, including Xwayland and any clients it `exec`s.
- Unix sockets: "the `allowUnixSockets` configuration can inadvertently grant access to
  system services... consider carefully any Unix sockets you allow." Config keys are
  `sandbox.network.allowUnixSockets` (array of socket paths) and
  `sandbox.network.allowAllUnixSockets` (boolean escape hatch), and
  `sandbox.filesystem.allowWrite` for the mount-namespace side.
- Troubleshooting section explicitly tells you to **exclude** tools that are
  architecturally incompatible with the sandbox rather than fight it: *"`docker` is
  incompatible with the sandbox. Add `docker *` to `excludedCommands`."* A nested
  compositor belongs in that same bucket (see recommendation below).
- Bubblewrap's own default device/namespace policy (independent of Claude Code's
  settings) does not forward GPU render nodes like `/dev/dri/*` — that's normal
  bubblewrap behavior, not something `sandbox.filesystem.allowWrite` can fix, since it's
  a device node, not a regular path grant.

Critically, `$XDG_RUNTIME_DIR` (`/run/user/1000` and the `/run/user/1000/wqa` subdir the
QA scripts use) and `/tmp/.X11-unix` are **not** in the default write allow-list. Every
Wayland/X11 surface in this stack lives under one of those two paths.

## Mapping each crash to the mechanism

### 1. Nested Hyprland: `CBackend::create() failed` (libseat no seat, DRM failed, no Wayland parent)
Aquamarine tries backends in order: DRM (needs `/dev/dri/*` + a seat via
logind D-Bus or seatd's socket) → Wayland (needs a *connectable* `WAYLAND_DISPLAY`
pointing at a real parent compositor socket) → headless (fallback, but per
hyprwm/Hyprland#7917 headless-mode has had regressions and isn't guaranteed). If the
process was started inside the sandbox:
- DRM fails because bubblewrap doesn't forward `/dev/dri` by default, and/or the seat
  socket (`/run/seatd.sock` or the logind D-Bus system socket) isn't in
  `allowUnixSockets`.
- The Wayland fallback fails if `WAYLAND_DISPLAY` wasn't actually propagated to a live
  parent socket when the nested Hyprland process was `Popen`'d, or if the socket's
  directory (`/run/user/1000`) isn't writable inside the jail so the client-side
  connection setup fails.
- All backends exhausted → fatal `CBackend::create() failed`, matching "no Wayland
  parent" in the report.

This is consistent with what's in the repo: `nested_pinned.lua` declares both a
`HEADLESS-1` and a `WAYLAND-1` monitor —
```
hl.monitor({output="HEADLESS-1",mode="1600x1000@60",position="0x0",scale=1})
hl.monitor({output="WAYLAND-1",mode="1600x1000@60",position="0x0",scale=1})
```
— i.e. the config *assumes* both backends attach successfully. None of the three
`nested_*.lua` files (`nested_caption.lua`, `nested_drag.lua`, `nested_pinned.lua`) set
`xwayland { enabled = ... }` or any aquamarine/backend override at all — the configs
rely entirely on whatever environment the launching process (not present in this
directory snapshot — it writes `/tmp/window-parity-nested-env.json`, consumed by
`live_drag_bridge_nested.py` and `run_pinned_modal_nested.py`) happened to hand it.

### 2. Xwayland `:1 -rootless` SIGABRT, `FatalError` in `InitOutput` (xwayland.c:456), "Failed to create ... mapping: Operation not permitted"
Xwayland is a *child* of the (now successfully nested, or host) Hyprland process, which
is itself a child of the sandboxed Bash command — so it inherits the same bwrap jail.
`InitOutput` needs to create its listening socket under `/tmp/.X11-unix` and shared
memory mappings (memfd/shm) under `$XDG_RUNTIME_DIR`; both are outside the sandbox's
default write allow-list, so the syscalls return `EPERM`, Xwayland's own X server
treats that as fatal (`FatalError`), and `OsAbort()` turns it into `SIGABRT`. This
matches the literal wording "Operation not permitted" character-for-character with how
the sandboxing doc describes the mount-namespace write-denial failure mode elsewhere
(e.g. the `git merge`/`unable to unlink old` case ends the same way on Linux: "Read-only
file system").

None of `nested_caption.lua`/`nested_drag.lua`/`nested_pinned.lua` disable Xwayland, so
every nested instance auto-spawns it even though the actual test surface (`foot`,
`wtype`, the quickshell test harness) is Wayland-native and doesn't need it.

### 3. qml tool (`qs -p ~/.local/share/hypr-window-controls`) aborted: "Failed to create wl_display (Operation not permitted)"
Same mechanism as #2: Qt's `QPA` Wayland platform plugin (and quickshell's own IPC
socket — see `omarchy-files.before-window-backend`, which launches the real production
instance the same way: `setsid qs -p "$APP" -d`) needs to `connect()`/`bind()` a Unix
socket under `$XDG_RUNTIME_DIR`. If that directory isn't in
`sandbox.filesystem.allowWrite` (and, if the seccomp filter is installed, the socket
path isn't in `sandbox.network.allowUnixSockets`), the connect/bind returns
`EPERM`, which Qt surfaces verbatim as "Operation not permitted."

### 4. Orca/AT-SPI probe segfault in `XKeysymToKeycode` via `libatspi`
`recovery-audit/keyboard-monitor/abi_client.py` asserts
`ROOT == Path(os.environ['XDG_RUNTIME_DIR'])` and
`str(ROOT).startswith('/tmp/kbd-')`, then drives `Atspi.Device` (libatspi), which talks
to the AT-SPI registry over the **session D-Bus socket** and, for keysym/keycode
mapping, over an **X11 connection** (`XKeysymToKeycode` is an Xlib call — AT-SPI's key
grabbing still goes through X even on Wayland via XTest/Xwayland). If Xwayland crashed
(failure #2) or the D-Bus session socket isn't reachable from inside the sandbox, the
Python process gets a dead/NULL `Display*` and libatspi's C code dereferences it
instead of checking for the error — segfault. This is a **downstream** crash, not an
independent sandbox denial: it only happens because Xwayland (or the AT-SPI
registry/dbus-daemon) already died out from under it.

### 5. test quickshell segfault in `QInputMethod::commit` during `QQuickItem` destruction
Same shape as #4: this is the Qt/QML scene graph tearing down while an input method
commit is in flight, which happens when the compositor connection the shell held (the
nested Hyprland Wayland socket) disappears mid-operation (because Hyprland itself was
killed or had already aborted per #1), rather than a clean, ordered shutdown. It's a
teardown-ordering bug in Qt triggered by an unclean compositor exit, not a sandbox
syscall denial on its own.

## Recommended configuration

### A. Treat nested-compositor launches as sandbox-incompatible, like Docker
The sandboxing docs' own guidance for `docker` applies almost verbatim: GUI compositors
need raw device (`/dev/dri`), seat (`logind`/`seatd`), and runtime-socket access that's
awkward and risky to allowlist piecemeal. Cleanest fix: add the actual launcher
commands to `sandbox.excludedCommands` (or have the other session's harness pass
`dangerouslyDisableSandbox: true` specifically for the commands that start/stop the
nested compositor, Xwayland, and `qs`), so they run outside bwrap entirely while
everything else (file edits, git, python unit tests like `fuzz_desktops.py`,
`test_windowctl.py`) stays sandboxed as normal:

```json
{
  "sandbox": {
    "enabled": true,
    "excludedCommands": [
      "Hyprland *",
      "Xwayland *",
      "qs *",
      "dbus-run-session *"
    ]
  }
}
```

### B. If it must stay sandboxed, explicitly widen both layers
```json
{
  "sandbox": {
    "filesystem": {
      "allowWrite": [
        "/run/user/1000/wqa",
        "/run/user/1000/bus",
        "/tmp/.X11-unix",
        "/tmp/kbd-*"
      ]
    },
    "network": {
      "allowUnixSockets": [
        "/run/user/1000/wqa/*",
        "/run/user/1000/bus",
        "/run/dbus/system_bus_socket",
        "/run/seatd.sock",
        "/tmp/.X11-unix/*"
      ]
    }
  }
}
```
This does *not* solve the `/dev/dri` device-node problem (bubblewrap's own default
device namespace, not a Claude Code setting) — so DRM will still fail inside the
sandbox. That's fine as long as a valid Wayland parent is guaranteed (next section),
since the Wayland backend doesn't need `/dev/dri` directly, only the parent compositor's
socket.

### C. Hyprland nested-config changes (orthogonal to sandboxing, should happen regardless)
1. **Disable Xwayland in every nested QA config that doesn't need X11.** None of
   `nested_caption.lua`, `nested_drag.lua`, `nested_pinned.lua` currently do this —
   add at the top of each:
   ```lua
   hl.config({xwayland={enabled=false}})
   ```
   This alone eliminates crash #2 (and transitively reduces the odds of #4, since
   Orca's `XKeysymToKeycode` calls have nothing to crash against if the probe is also
   adjusted to not require X/AT-SPI key-grab for Wayland-only test runs — see below).

2. **Always launch the nested Hyprland binary with a verified-live `WAYLAND_DISPLAY`.**
   The actual spawn code isn't in this directory (it writes
   `/tmp/window-parity-nested-env.json`, which `live_drag_bridge_nested.py` and
   `run_pinned_modal_nested.py` read back), so it lives in whatever orchestrator starts
   it. That orchestrator should: (a) pass `env=dict(os.environ, WAYLAND_DISPLAY=<parent
   socket>, XDG_RUNTIME_DIR=<dedicated dir>)` explicitly rather than relying on
   inheritance through `setsid`/`dbus-run-session`, and (b) probe the parent socket is
   connectable (e.g. `wayland-info` exit code, or just `socket.connect()` in Python)
   before spawning Hyprland, instead of discovering the failure only via Hyprland's own
   abort.

3. **Pick one `$XDG_RUNTIME_DIR` convention and use it everywhere.** Right now
   `live_drag_bridge_nested.py` hardcodes `/run/user/1000/wqa`,
   `run_pinned_modal_nested.py` inherits whatever `instance['wl_socket']` implies, and
   `abi_client.py` asserts a *different* runtime dir under `/tmp/kbd-*`. Three different
   runtime-dir schemes make it impossible to write one clean sandbox allow-list (or one
   clean `excludedCommands` rule) and increases the chance that some code path winds up
   pointed at the default `/run/user/1000` (which collides with the real, non-QA
   session) instead of an isolated QA directory.

4. **Don't rely on DRM/headless fallback succeeding silently.** Given
   hyprwm/Hyprland#7917 (headless mode regressions) and the fact that bubblewrap won't
   forward `/dev/dri` anyway, the only backend worth depending on for sandboxed nested
   runs is the Wayland backend against a real parent socket. Treat DRM/headless success
   as a bonus, not the primary path.

### D. Make a dead compositor fail quiet instead of loud
Once B/C are fixed the hard crashes should mostly disappear, but as a second layer: wrap
probe launches (`abi_client.py`, the `qs` test harness) so a vanished compositor socket
is detected and the client exits cleanly (catch the Wayland/X11 disconnect, don't let
libatspi/Qt dereference a dead `Display*`/connection). Concretely:
- In `abi_client.py`, check the AT-SPI registry/display connection succeeded before
  calling into `XKeysymToKeycode`-touching code paths (`device.add_key_grab`,
  `map_keysym_modifier`), and catch `Glib.Error`/connection failures rather than
  assuming they'll always be live.
- When tearing down a nested run, send the shutdown signal to clients first (quickshell,
  `foot`, Orca probe) and wait for them to exit before killing the nested Hyprland
  process, instead of killing the compositor and letting clients discover the dead
  socket mid-operation — this is what's producing the `QInputMethod::commit`
  destruction-order segfault.

## Files inspected (for reference)
- `/home/hoskinson/window-integration-qa/nested_caption.lua`
- `/home/hoskinson/window-integration-qa/nested_drag.lua`
- `/home/hoskinson/window-integration-qa/nested_pinned.lua`
- `/home/hoskinson/window-integration-qa/live_drag_bridge_nested.py`
- `/home/hoskinson/window-integration-qa/run_pinned_modal_nested.py`
- `/home/hoskinson/window-integration-qa/live_family_backend.py`
- `/home/hoskinson/window-integration-qa/fuzz_desktops.py`
- `/home/hoskinson/window-integration-qa/recovery-audit/keyboard-monitor/abi_client.py`
- `/home/hoskinson/.local/share/hypr-window-controls/` (shell.qml, qa/virtual-pointer*)
- `/home/hoskinson/window-integration-qa/omarchy-files.before-window-backend` (shows the
  production `qs -p ... -d` launch pattern the QA harness mirrors)
