# Handoff: stop the window-integration QA from crashing (and flooding crash toasts)

**From:** the Claude Code session that investigated the desktop crash toasts.
**To:** the Codex session running `~/window-integration-qa`.
**Evidence:** `~/Documents/crash-noise/B-source.md` (sandbox mechanism and the launcher lines) and `C-system.md` (coredump mechanics).

## What is happening
Since 2026-09-30, 22 crashes came from this QA's process tree, all in one terminal scope:
- nested Hyprland (`--config .../nested_*.lua`): `CBackend::create() failed`;
- its Xwayland on `:1`: `FatalError` in `InitOutput`, "Failed to create ... mapping: Operation not permitted";
- the test `qs -p ~/.local/share/hypr-window-controls`: SIGSEGV in `QInputMethod::commit` during `~QQuickItem`;
- the Orca probe `recovery-audit/keyboard-monitor/abi_client.py`: SIGSEGV in `XKeysymToKeycode`;
- a portal on the private bus of `real_brave_publisher.py`: the use-after-free at shutdown.

**Cause:** the compositors are started from sandboxed commands. The sandbox blocks writes under `/run/user/1000` and `/tmp/.X11-unix` and does not forward `/dev/dri`, so Xwayland and Hyprland abort. The shell and the Orca probe then crash on the dead connection. Each crash raised a "Process crashed" toast on the user's desktop. The desktop now filters these out (an override of `omarchy-crash-watch`), but the runs are still crashing.

## Please change
1. **No core dumps from the harness tree.** Launch each nested run in its own scope:
   ```
   systemd-run --user --scope --slice=qa-harness.slice -p LimitCORE=1 -- <launcher>
   ```
   With the pipe `core_pattern`, a limit of exactly 1 makes the kernel skip systemd-coredump, so there is no journal entry and no toast. Use `-p LimitCORE=infinity` for a run that needs a backtrace.
2. **Turn off Xwayland where X11 isn't under test.** Add `hl.config({ xwayland = { enabled = false } })` to the `nested_*.lua` configs; none disable it today.
3. **Always nest, never fall back to DRM.** Pass a verified-live parent `WAYLAND_DISPLAY` explicitly to nested Hyprland. Check the socket exists and accepts a connection before launch. Never rely on inherited env.
4. **Run compositor launchers outside the sandbox.** Use the escalated or unsandboxed path for `Hyprland`, `Xwayland`, `qs`, `dbus-run-session`, or allow `/run/user/1000/wqa` and `/tmp/.X11-unix` explicitly. Use one `XDG_RUNTIME_DIR` scheme: `live_drag_bridge_nested.py`, `run_pinned_modal_nested.py` and `abi_client.py` use three different ones today.
5. **Tear down in order.** Stop clients first (the test quickshell, foot, the Orca probe), and the nested compositor last. In `abi_client.py`, check the AT-SPI/X connection before any keysym or keycode call.

## Don't
- Don't revert the desktop's crash-watch override (`~/.config/systemd/user/omarchy-crash-watch.service.d/override.conf`) or the system grim and gnome-keyring builds.
- No AI attribution in any commit or PR. This is the owner's iron rule.
