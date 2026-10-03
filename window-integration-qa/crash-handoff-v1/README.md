# Crash-noise handoff implementation

Read `~/Documents/crash-noise/HANDOFF-codex-window-qa.md` and its source/system
evidence before changes. Native launches were held throughout this work.

1. **Core limits and scope:** shared `qa_run.py` wraps the entire tree in a
   unique user scope under `qa-harness.slice`. This host rejects `LimitCORE` as
   a scope property; the failed command is retained in `verification.json`.
   Scope plus `prlimit --core=1:1` passed actual parent/child inheritance checks.
   Explicit `--backtrace` enables infinity.
2. **Xwayland:** disabled in current drag, caption, pinning, motion and restart
   configs, plus the next private raster config. The new private host also
   appends an explicit disabled setting. A separate pinned X11 config is selected
   only for an actual X11 case, checked against the compositor's effective option.
3. **Parent and backend:** shared socket checks require an explicit owned live
   socket, stable inode and peer credentials. The private host matches the peer
   to its captured Weston PID/start before nested Hyprland. Only the Wayland
   Aquamarine backend is supplied, with DRM override removed.
4. **Execution and runtime:** launches use the available unrestricted execution
   path; there is no approval or sandbox escalation. Actual render-node access
   and owned `0700` runtime checks passed. All active paths use the shared short
   `/run/user/$UID/wqa/<4-hex>` runtime scheme. Drag/pinning no longer use three
   hardcoded runtime conventions or a stale `/tmp` descriptor.
5. **Teardown and accessibility:** restart cleanup now stops clients before its
   compositor. Private host cleanup follows clients → Hyprland → Weston → bus,
   retains logs, and rejects unexpected survivors. Fresh `abi-safe-v3` checks
   transport, live owner/protocol and actual Manager backend before key APIs,
   refuses unexpected X11/Legacy fallback, and uses client-first cleanup.

Exact legacy source backups are in `before/` with `before-manifest.json`.
Prior frozen packets remain historical evidence. Future launches use new host
V2 and ABI V3; no compositor was launched for this handoff verification.

The desktop crash-watch override and installed grim/gnome-keyring builds were
not modified. No commit or PR was created. This work checks launch guards and
ordering; it does not prove that upstream client teardown bugs cannot occur.
