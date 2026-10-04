# Automatic roadmap continuation

The user requested a loop to build the entire system. The hosted goal is active
for the full mandatory Elm desktop roadmap and right-click amendment, including
qualification, failure recovery and authorized reversible deployment. See
[BUILD-LOOP.md](../../docs/elm-roadmap/BUILD-LOOP.md) for each iteration and its
completion gate. Automatic AI turns come from that goal; `loop.py` is a durable
checkpoint and native-QA coordinator, not a second AI daemon.

From the repository root:

```bash
python3 -B implementation/elm-build-loop-v1/loop.py status
python3 -B implementation/elm-build-loop-v1/loop.py checkpoint \
  --thread 01a101d3-cde7-7370-83b1-3170bdd0c9d1 \
  --slice implementation/elm-menu-lifecycle-v2 \
  --status active \
  --next 'Implement bounded providers and correlated outstanding menu receipts' \
  --evidence implementation/elm-context-menu-v1/qa/implementation-manifest.json
python3 -B implementation/elm-build-loop-v1/loop.py native \
  --runner /absolute/repository/path/to/reviewed/qa/native.py
```

Checkpoint publication is atomic and exclusive. Events record source lane,
next work and hashed evidence pointers, including failed reports. The CLI cannot
certify a completed requirement, cycle or goal. Existing primary integration
state and frozen acceptance inventories remain unchanged.

Native invocation holds a shared per-user lock across repository worktrees and
calls the original protected launcher with a literal argument vector. There is
no shell evaluation, arbitrary launcher override or core-limit bypass. A busy
coordinator or visible protected QA process refuses before starting a child,
with exit code 75. Unsafe paths return 2; child status and interruption propagate.
The conservative process check can also refuse an existing CPU QA scope. CPU
work may continue while a native slot is occupied.

All native workers must adopt the wrapper. Process scanning detects existing
uncoordinated campaigns but cannot prevent an uncoordinated future launch from
racing. The lock is not a source-review or ABI gate; the reviewed runner retains
responsibility for those original preflights, parent/socket/runtime validation,
private ownership, deadlines, and ordered normal teardown.

State files under `~/.local/state/elm-build-loop` contain no credentials. The
repository checkpoint journal persists across sessions. A new machine must
review/rebind the protected launcher and requalify its native source/ABI tuple;
an archived successful binary is not portable native acceptance.

`qa/test.py` runs synthetic orchestration checks through the unchanged protected
launcher. It exercises real concurrent checkpoint writers and lock contention,
path refusal, immutable evidence references, child exit/interruption handling,
and unchanged frozen roadmap inputs without launching a GUI. Final evidence and
scope are in `HANDOFF.md`.
