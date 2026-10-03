# Window integration QA launch contract

Every new native or nested run must use the shared launcher:

```bash
python3 ~/window-integration-qa/qa_run.py -- python3 <reviewed-runner> <arguments>
```

It starts a unique user scope in `qa-harness.slice`, then applies
`prlimit --core=1:1` before the runner. This systemd version rejects the handoff's
`-p LimitCORE=1` on a scope (`Unknown assignment`); applying the inherited
soft/hard limit before execution preserves the required value. Normal launcher
and subprocess limits and cgroup membership were checked on this machine.
Use `qa_run.py --backtrace -- ...` only for an intentional diagnostic run.
Process exit status and logs remain QA evidence when core collection is disabled.

The current execution environment is unrestricted. Use the ordinary execution
tool without a sandbox override. Preflight requires writable, owned user runtime
directories and an accessible DRM render node; fail before launching if absent.

## Mandatory nested-run checks

- Use `qa_launch.private_runtime()` for an owned `0700`
  `/run/user/$UID/wqa/<4-hex>` runtime. The short name keeps Hyprland's long
  instance IPC paths within the Unix-socket path limit. The private bus and all
  test clients use that runtime.
- Use frozen `private-weston-aq-host-v4.PrivateHyprSession` for upcoming private campaigns.
  It verifies its live Weston parent socket and exact peer process before
  launching Hyprland with an explicit display and `AQ_BACKENDS=wayland`.
  No DRM or standalone headless-Hyprland fallback is permitted.
- Disable Xwayland for Wayland tests. `nested_pinned_x11.lua` is the explicit
  exception for an actual X11 test. The private host disables Xwayland in its
  effective config; preserve both caller and effective config hashes.
- Stop test clients, input probes, private accessibility services and motion
  producers before the nested compositor; stop Weston and the private bus last.
  Archive logs before runtime deletion. Record forced shutdown or survivors as
  failures rather than normal cleanup.
- Use the guarded Manager-only ABI revision at
  `recovery-audit/keyboard-monitor/abi-safe-v3`. It validates private transport,
  live owner/protocol and actual backend before any public key operation.
  Unexpected X11/Legacy fallback is rejected before keysym conversion.

The legacy drag/pinning cases attach only with `QA_NESTED_DESCRIPTOR` naming an
owned current session descriptor (`runtime`, `pid`, `start`, `config`,
`signature`, `env`). The target must be in a QA scope. PID/start, config,
private-bus routing, socket credentials and descriptor bytes are checked before
each explicit instance IPC call. There is no stale `/tmp` environment-file or
first-instance fallback.

Frozen prior packets and attempts are historical evidence and must not be used
as future launch paths. Make a fresh revision when migrating a frozen runner.
The old `abi_client.py` and `private_abi_proof.py` are retired in favor of
`abi-safe-v3`; their exact original bytes remain retained for provenance.

The crash-watch override and installed grim/gnome-keyring builds are untouched.
The handoff corrections are recorded under `crash-handoff-v1`. No new nested
execution is accepted merely because these launch guards pass; the hardware
renderer, DMA-BUF, fixture behavior and complete cleanup still need runtime QA.

## Actual follow-up launch evidence

The handoff38-check report predates native runs. The later foundationV3 proved
Intel GL/DMA-BUF and mappings/cleanup, but did not prove healthy ongoing parent
transport. First full rasterV2 failed before image comparison: the parent rejected
an unconfigured xdg_surface, and actual Aquamarine logs showed AQ_BACKENDS was
ignored and DRM/libseat attempted. All15main state checks and normal private
cleanup passed; frozen failed evidence is retained. Do not reuse adapterV2 for
future launches. Fresh private AQ lifecycleV1/adapterV3 enforce mandatory nesting
and ACK before announcement/render, and new rasterV3 adds actual parent feedback,
protocol/selection and host cleanup gates. Runtime proof is pending that fresh run.

Mutable content/restart launchers additionally use qa_nested_backend.command to
verify the entire frozen privateAQ library and select it only for the compositor
exec. This closes the ignored-environment hole in direct legacy launchers too.
Legacy attach also checks actual mapped backend identity from the same hashed
file descriptor; it cannot accept a scoped installed-AQ child solely from env.
The seven guard tests pass; prior source bytes are retained in crash-handoff-v2.
The frozen hostV4 fixes the private IPC readiness probe with a bounded read-only
`j/version` reply. Subsequent Qt, raster and pointer campaigns verified its live
private parent, exact core limit and clients-first host cleanup. Their retained
product failures remain failures; launch safeguards do not establish window
behavior acceptance. Existing V3 failed reports remain unchanged, including
their conservative transport acceptance flag.
