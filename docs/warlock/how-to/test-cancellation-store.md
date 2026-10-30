# Test the optional cancellation store

Use this guide to check V7 storage independently of daemon or native routing.
The runner uses temporary files and strict native-response doubles. It never
opens windows, changes desktop configuration or enables cancellation in the daemon.

From the repository root on this configured host, obtain the team's serialized
QA HOLD through AgentBus and confirm no protected runner is active. Follow the
[verification guide](verify-selected-change.md) for those shared execution rules.
Then run the repository-owned entrypoint through the protected launcher:

```sh
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH="$PWD/window-integration-qa" \
/usr/bin/python3 -B window-integration-qa/qa_run.py -- \
/usr/bin/python3 -B implementation/warlock/qa/check-cancellation-store.py
```

The command prints a report path under `implementation/warlock/qa/runs/`.
Read `passed`, every command's exit code, retained stdout/stderr and input hashes.
Confirm each group reports its assertions passed; an incomplete run is not a
passing matrix. After the launcher is actually terminal, release the QA HOLD.

The groups cover ordinary and typed restart, immutable admission keys, attempt
prerequisites, certificate-before-retirement ordering, ACK gating, selected
syscall failures, reopening and funded byte capacity. The [protocol reference](../reference/cancellation-protocol.md)
and [recorded limits](../../../implementation/warlock/qa/evidence/cancellation-store-20261030/LIMITS.md)
identify the current scope. This runner does not qualify authenticated transport,
physical Escape, C/Elm recovery delivery, all-slot operation or hardware power loss.
