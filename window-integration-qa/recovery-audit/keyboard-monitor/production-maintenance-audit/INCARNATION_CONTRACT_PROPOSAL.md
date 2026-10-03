# Proposed maintenance incarnation guard before production wiring

The actual v1 draft wrapper can query identity from an old bridge, then retire
and unload a new instance of the same artifact under the same compositor. UID,
PID/start, IPC socket, manifest hash, maps dev/inode/path and name/version all
remain valid. This is a staged maintenance prototype gap, not a native v8 bug.
Actual-source controlled replay is retained in incarnation-counterexample.json.

A future fresh revision should model/check BOTH compositor identity and plugin
incarnation. Each successful plugin load creates a fresh bounded random nonce;
compositor session signature and reviewed package ID remain independent static
identities. Public compositor Lua identity returns all three. PrepareUnload
requires expected signature, package and exact incarnation; wrong/stale nonce
fails before quiescence or retirement. Wrapper validates the same nonce in the
reply and before exact API unload. Maintenance serialization lock is also
required but cannot replace the native expected-incarnation check.

Retirement remains irreversible. False/stale Prepare preserves all subscriptions,
held captures, pointer notes and lock parity. Missing/wrong nonce never permits
raw unload. True plus a target/nonce change before API unload must refuse normal
wrapper action, leaving the retired OLD bridge harmless. Normal core plugin
unload still accepts only a path, so an uncoordinated raw third-party swap after
final verification cannot be made transactional by user wrappers. This remains
an explicit same-user raw-maintenance interference boundary unless exact native
atomic unload support is proved; do not claim a nonexistent lease.

This is offline review only. V1 draft is retained unchanged. No production native
wiring, whole production build, main load, reader activation or config changes.
Finish the complete private pointer/reader campaign before production wiring.
