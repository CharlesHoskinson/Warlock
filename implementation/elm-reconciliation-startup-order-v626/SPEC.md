# Startup admission order v626

The v618 native journey failed before any behavioral case. Its webview received
watermarks but never logged an attached frame, displayed recovery-unavailable,
and observed a signalled backend exit. The archived V6 store is structurally
valid and empty. The C attached handler sends exactly that failure and SIGTERM
when its nonblocking `admission_bind` fails. No recorded errno identifies which
bind guard failed, so the native log alone does not prove lock contention.

The v616 startup path nevertheless contains an actual ordering defect:
`send(hello)` precedes `reconciliation.announce()`, which reacquires the broker's
short `host-writer.lock`. The C host binds that same namespace after asynchronously
receiving attached and requires its nonblocking lock. This conflicts with the
existing startup comment and can explain the observed failure. Deterministic CPU
controls reproduce actual compiled C refusal while that broker lock is held and
success when it is released.

Only `adapter/daemon.py` changes production behavior. `publish_startup` collects
settlement/recovery frames and stages all reconciliation announcements, including
proof acquisition, before publishing attached. It then restores the coordinator's
live send callback and emits attached, settlements, watermarks, full Unknown
records, the first serial proof and geometry negotiation in the original order.
No broker short-lock acquisition occurs during that publication phase. Later
frontend requests can still use the restored callback to announce later scopes
and publish independently correlated durable releases.

All v616 Elm, JavaScript, native and other adapter sources remain byte exact.
CPU controls exercise the actual helper, real private V6 store and compiled C
bind, with synthetic strictly decoded599 proofs. Public Elm controls and the full
host/Elm build are repeated. No native GUI is launched by this packet. A new
native campaign must determine whether this fix resolves the observed v618
failure and preserve the original six-second deadline and behavioral identities.

The initially copied `current-build.json` refers to v616 and was captured by the
first build. That compilation passed, but its pointer input becomes stale when
publishing a new pointer. It is retained as development compilation evidence.
The accepted final build runs without the generated pointer, then publishes its
new pointer, following the original initial-build procedure. Its source inputs,
binary, generated assets and owning dependency inventory must all validate.
