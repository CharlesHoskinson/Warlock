# Exact compositor maintenance (offline contract before implementation)

V8's 296 frozen inputs remain unchanged. This future package does not authorize
main load, production build, installation, reader activation, config/autostart
changes, synthetic input or forced unload.

A reviewed manifest pins an immutable user-owned versioned library, SHA256,
exact Hyprland commit, package ID and plugin name/version. Native acceptance,
production acceptance and absence of the private Probe interface must be
separately approved. The initial manifest is unapproved; there is no bypass flag.

An explicit or environment instance signature is strict; an unavailable preferred
target fails without fallback. Without either, resolve exactly one current
instance. Persist UID/PID/process start/signature and IPC socket dev/inode.
Recheck identity before every IPC call and supply hyprctl -i plus the same
HYPRLAND_INSTANCE_SIGNATURE. Runtime/socket must belong to this UID. Ambiguity,
PID reuse, socket replacement, ABI/hash drift or duplicate bridge identities
refuse further action.

Production exposes no private Probe D-Bus interface. Narrow compositor-owned
Lua identity/prepare_unload(signature,packageID) functions hold maintenance
authority. Incorrect tokens fail before mutation. False PrepareUnload preserves
subscriptions, capture routes, pointer notes and virtual lock parity. True
requires the accepted captured-key and surviving virtual Caps/Num correction
quiescence predicate, then atomically retires interception and pointer work.
All later subscriptions fail. Only true permits normal exact-library unload.
Transport failure never permits raw unload; an unload error after retirement
leaves a passive retired bridge rather than reactivating it.

Exact primary source: plugin list JSON omits library path. A wrapper must check
unique name/version, actual /proc/PID/maps dev/inode/path, pinned library bytes
and Lua identity. Lua return values require hyprctl repl: ordinary eval discards
return text. Exit zero or an unstructured 'ok' cannot prove retirement.

The package never starts Orca, sets ScreenReaderEnabled, creates grabs, alters
permissions or injects releases. Main deployment requires its separate full
14-preservation snapshot, production ABI/maintenance native acceptance, backups
and reviewed rollback. Forced core unload/error ejection with captured keys
remains unsupported.
