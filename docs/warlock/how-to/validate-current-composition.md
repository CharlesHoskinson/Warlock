# Validate a current frontend/native composition

Use this procedure to bind an already reviewed current frontend build to the recorded unchanged native host, retained objects, libraries and compositor tuple. This is a local prerequisite for a separately reviewed runtime fixture; it does not install or launch Warlock.

First follow [the current frontend build procedure](build-current-frontend.md). Keep its original report next to its actual assets, staged inputs, registry snapshots and logs. The copy under `qa/evidence/` preserves evidence but lacks the adjacent build workspace required for receipt validation.

Run the composition commands through the protected launcher after obtaining the successful AgentBus QA HOLD receipt and confirming that no other CPU/native campaign is running. For example, from the repository root:

```bash
env PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=/home/charles/Warlock/window-integration-qa \
  /usr/bin/python3 -B /home/charles/Warlock/window-integration-qa/qa_run.py -- \
  /usr/bin/python3 -B implementation/warlock/adapter/current_native.py capture \
    --frontend-report /absolute/private/build/report.json \
    --frontend-sha256 REVIEWED_FRONTEND_REPORT_SHA256 \
    --output /absolute/private/new-native-lock.json
```

Capture validates the frontend through `current_build.validate_report` and retains explicit current/historical source roles. The original native recipe, preflight, source inventory, object ordering, dependency/provider and ABI checks remain. Only the eight explicitly supported historical Elm files are resolved as old bytes from the pinned Git revision; current frontend bytes are checked separately. Unexpected source changes, additions, removals or native drift require a separately reviewed implementation/build change.

Review the new lock and its exact digest before consuming it. It is a proposal, and its existence does not establish runtime correctness. Consume the reviewed lock with:

```bash
env PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=/home/charles/Warlock/window-integration-qa \
  /usr/bin/python3 -B /home/charles/Warlock/window-integration-qa/qa_run.py -- \
  /usr/bin/python3 -B implementation/warlock/adapter/current_native.py validate \
    --frontend-report /absolute/private/build/report.json \
    --frontend-sha256 REVIEWED_FRONTEND_REPORT_SHA256 \
    --lock /absolute/private/new-native-lock.json \
    --sha256 REVIEWED_NATIVE_LOCK_SHA256
```

Poll each protected process to terminal and send the successful QA RELEASE receipt. Validation checks the lock's current file/resolution identities, explicit aliases and source/receipt roles again. Preserve immutable lock and report files while they are being read. It returns the selected native slots and current assets; a later runtime adapter must consume those values without silently selecting another host or asset directory.

This implementation deliberately supports the currently recorded unchanged native tuple and exact known frontend deltas. It depends on machine-local private artifacts, historical Git objects and workspace links. It is not a portable package recipe. The retained renderer failure, actual native attention pixels/AT export, complete native runtime compatibility, tool upstream-source closure, offline reproducibility, compliance and release acceptance remain separate. See [status and evidence](../reference/status-and-evidence.md) and [verification](verify-selected-change.md).

The [receipt-corrected composition qualification](../../../implementation/warlock/qa/evidence/receipt-current-composition-20261030/LIMITS.md) records the current a04 lock and fresh 80ab frontend receipt. The public `qa/check-current-native.py` now includes current role counts, the retained static/adapter negatives and explicit Effects history/current checks; use its `--mode capture` and `--mode test` with the reviewed frontend/lock arguments for proportional protected checks. Its historical receipts remain unchanged.
