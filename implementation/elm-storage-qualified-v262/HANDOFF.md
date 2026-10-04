# Stale actions, busy/legacy recovery and original GUI regression

V255 reproduces a compiled Elm bug: a stale scoped action checked its captured
stamp before checking whether window actions were available. During a storage
failure it could replace the recovery explanation with "Choose again." The failed
replay and exact V248 compiler inputs remain preserved. V256 checks availability
first, so disabled actions leave the model and failure explanation unchanged.
Connected stale actions retain the existing changed-list feedback. No host,
broker, journal, native core or plugin implementation changed in this derivative.

V256 compiles the real host and optimized Elm programs, passes inherited replay
suites of 20/27/30 checks, and passes 47 new compiled stale-action checks plus the
55 storage presentation/retry checks. Stale revision, session and output scopes
are tested across all five typed recovery reasons. V260 extends the abstract Quint
contract with notice preservation and connected stale feedback: ten explicitly
selected named cases and 1,000 sampled invariant traces up to 40 steps pass. It is
not an automatic implementation-refinement proof.

V257 seals the actual V256 host/assets/broker in a 20-file capsule. V258 passes 22
native checks using an actual Journal writer lock held by the protected QA owner:
the broker refuses before publishing attached, the real bar explains that recovery
data is busy, releasing the lock causes no auto retry, and an explicit pointer
Reconnect keeps the same native host and permits a fresh committed minimize.
This demonstrates real lock contention, not two simultaneously running production
shells. V259 passes 23 native checks with a real typed legacy Pending record and
missing owner metadata. The failure precedes attached and the bar explains migration
ownership. The fixture explicitly provisions private owner metadata for this exact
authenticated instance/lifetime; the broker preserves the legacy record, migrates
it to informational Unknown and never replays it. A fresh explicit minimize commits.
This qualifies the metadata rule and its native recovery path, not an automatic
ownership inference or production migration provisioning UI/tool.

Both cases retain before/after screenshots, owned pointer exits, broker failure
exit, application identity/minimized state, no-retry observation, one surviving
native shell generation, empty owned cohort and normal cleanup. The old source
and original check/wait/click helper ASTs/deadlines are preserved. Tests compare
identity/state before normal bar reservation; reservation geometry is not treated
as an application-preservation failure.

V261 passes the full original 137-check V171 native workload on V256/V89, including
the original 91-check launcher/window integration sequence, renderer recovery,
shared bar/controller/renderer process identity, dual outputs, popup bounds,
resize/removal/replug and normal cleanup. The V171 check/wait call AST sequences and
five helper ASTs are exactly unchanged; only its GUI source target changes. This
regression uses the original fixture-owned host lifetime and recovery route, not
the production supervisor. Its source inventory checks the actual participating
host build, source and ABI pair. It does not qualify a newer geometry/menu pair,
GPU/device-loss/budgets, or the independent original restore38/recovery34/case34
animation/retained-frame deadlines.

V254's native unverified/unavailable cases, Python/filesystem/C checks and V247's
interrupted minimize/restore matrix remain retained on their original V248/V238
tuples; they are not rerun here. The actual changed source is the pure Elm
availability/stamp decision order. Do not combine counts into a distinct scenario
total or mark any whole requirement or sprint complete. No installed desktop,
main compositor or user drafts changed.

Next: native storage failure during settlement after a real committed window
effect, host binding failure, full/readonly storage and explicit correction without
replay; qualify a production legacy provisioning flow. Rerun the full interrupted
recovery matrix on the final source and integrate the reviewed newer geometry/menu
pair. Global old-live-broker revocation, original restore timing, coherent GPU,
AT/IME, hotplug/zero outputs, full operations, physical/human UX, budgets/soak, C00
and release remain open.
