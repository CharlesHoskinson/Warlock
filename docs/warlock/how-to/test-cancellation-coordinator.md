# Test cancellation coordinator wiring

Use this guide to check the coordinator with real V6/V7 stores and controlled
native-schema replies. The suite also runs the daemon's mode selection and
cleanup with inert service/event objects. It does not connect to a compositor,
activate a desktop mode or establish C/Elm interoperability.

From the repository root on this configured host, obtain the shared AgentBus QA
HOLD and confirm no other protected runner is active. Follow the
[verification guide](verify-selected-change.md), then run:

```sh
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH="$PWD/window-integration-qa" \
/usr/bin/python3 -B window-integration-qa/qa_run.py -- \
/usr/bin/python3 -B implementation/warlock/qa/check-cancellation-coordinator.py
```

Inspect the printed report path under `implementation/warlock/qa/runs/`.
Require `passed: true`, three completed command groups, successful exits and
matching retained output/input hashes. The groups cover lifecycle ordering,
daemon selection/unwinding, and historical startup/direct dispatch. Release the
QA HOLD after the launcher is actually terminal.

The tests create internal true/false/malformed configurations in temporary
private directories. This is not an instruction to enable `cancellationOptIn` in
a live host configuration. The normal host still uses the existing default;
its C/Elm messages and host-issued deadline admission are not integrated.
See [the protocol reference](../reference/cancellation-protocol.md) and
[recorded evidence limits](../../../implementation/warlock/qa/evidence/cancellation-coordinator-20261030/LIMITS.md).


For the paired admission, settlement-cache and orphan-regression controls, use
the same protected invocation with
`implementation/warlock/qa/check-cancellation-host-cache.py` as the entry point.
Require six completed groups and matching source/output hashes. The tests use
explicit durable C-cache writer and native-response doubles; they do not qualify
the actual owning C consumer, physical Escape or native resource retirement.
See the [paired backend evidence](../../../implementation/warlock/qa/evidence/cancellation-host-cache-20261030/LIMITS.md).
