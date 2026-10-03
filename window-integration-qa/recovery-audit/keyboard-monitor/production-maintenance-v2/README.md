# Staged Omarchy accessibility production package

The original private full campaign passed185/185 (96 pointer,45 keyboard policy,36 lifecycle), all19 main preservation and all four strict helper gates. This package preserves its policy/source headers and signed coordinate compatibility but adds new production initialization and Lua management. It has **not been loaded**, installed, or accepted for main activation. `productionAccepted=false` blocks install/load/reader startup.

## Concrete review artifacts

- `native/accepted-to-production.diff`: narrow native runtime/initialization/Lua changes; no private Probe in production source or binary.
- `native/MaintenanceLua.hpp`: exact signature/package/per-load random nonce, read-only fresh capability query and normal retirement.
- `control.py`: exact compositor UID/PID/start/IPC peer/socket, version, immutable artifact/map and nonce validation; runtime flock; normal load/unload/reload. No reader start or property Set.
- `reader_bootstrap.py`, `launch_reader.py`: explicit user reader start, existing enabled-intent gate, real Orca user settings/speech, accepted public capability/reconnect adapters.
- `payload/`: complete self-contained versioned artifact, copied original signed reader prefix, clearly labeled signed-v3 mouse compatibility, source, packages/signatures/metadata and license text.
- `install.py`: reviewable plan/apply/guarded rollback, exact previous launcher byte backups, immutable versions. No autostart/config or permission edits.

## Review commands (offline)

Run from this directory:

```sh
python3 -m unittest -v test_control test_install
./native/test_lua
python3 install.py plan --payload ./payload > reviewed-install-plan.json
```

The plan targets `~/.local/lib/omarchy-a11y/omarchy-a11y-prod-v2` and fresh `~/.local/bin/omarchy-a11y-control` / `omarchy-orca` wrappers. Apply is intentionally refused until a separately reviewed fresh accepted payload exists. Do not edit a frozen package's manifest in place to turn its flag on; freeze a new approved candidate after native acceptance.

## Intended deployment/rollback after review and fresh native proof

```sh
python3 install.py apply --payload /absolute/reviewed/accepted/payload --plan /absolute/reviewed/install-plan.json
omarchy-a11y-control status --instance EXACT_CURRENT_SIGNATURE
omarchy-a11y-control load --instance EXACT_CURRENT_SIGNATURE
omarchy-a11y-control unload --instance EXACT_CURRENT_SIGNATURE
python3 install.py rollback --receipt /absolute/deployment-receipt.json
```

Normal reload captures/revalidates its load incarnation, prepares only when captured keys and surviving virtual lock corrections are clean, unloads by exact immutable path, then loads a fresh passive incarnation. False retirement preserves subscriptions. An API failure after retirement leaves a passive bridge. Forced raw core unload while held input is unsupported. An uncoordinated same-user raw swap after the wrapper's last validation is also outside the serialized normal-management guarantee.

Reader startup is a separate **explicit** `omarchy-orca` action. It requires preexisting ScreenReaderEnabled=true and never sets that property itself. Product speech remains Orca's real default/user selection; no silent QA factory, shared QA profile, no-portals or GIO local-VFS overrides are installed. The retained process-only Legacy modifier helper has a historical ORCA_QA option name internally but is scoped to this explicitly launched reader and inert for the official Manager backend.

## Remaining native production gates

Prove in the private headless Weston host before considering main activation: production plugin main-shaped runtime guard refusal/approved private scope, actual Lua namespace/structured return, no Probe introspection, per-load nonce across same-artifact reload, old nonce refusal preserving active policies, false retirement on held input/dirty locks, true retirement/API unload, exact-instance wrapper source guard failures, existing-reader owner churn and accepted command/pointer replay through the Lua capability check, existing enabled/disabled property preservation, real (non-silent) user speech/profile startup separately. Physical hardware/general keymaps and forced/error unload remain retained evidence limits.
