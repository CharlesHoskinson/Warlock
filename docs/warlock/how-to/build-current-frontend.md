# Build a reviewed current frontend

Use this procedure when qualifying current Elm changes. It produces Main, Bar and Popup assets from a reviewed current input lock. It does not qualify a native host/core/plugin tuple, build an installable release, establish offline reproducibility or authorize deployment.

The implementation is `implementation/warlock/adapter/current_build.py`. It requires this checkout's held `implementation/warlock-preview-provider-v143` compiler/package cache, the protected QA launcher and a fresh private output location on the current machine. Locks and receipts use absolute paths. Existing historical build and native receipts remain immutable.

1. Capture a proposed lock into a new private file:

   ```bash
   python3 -B implementation/warlock/adapter/current_build.py capture \
     --output /absolute/private/current-lock.json
   ```

   Inspect the reported SHA-256 and review its exact current Elm/project inputs, static assets, compiler/package cache, Python interpreter and recipe identity. Capture hashes the current files; it does not establish their correctness or provenance. Retain the reviewed lock and digest separately. A source or recipe change requires a fresh reviewed lock.

2. Obtain the successful AgentBus QA HOLD receipt and confirm no other CPU/native campaign is running. Build through the existing protected launcher, replacing the digest with the reviewed value:

   ```bash
   env PYTHONDONTWRITEBYTECODE=1 \
     PYTHONPATH=/home/charles/Warlock/window-integration-qa \
     /usr/bin/python3 -B /home/charles/Warlock/window-integration-qa/qa_run.py -- \
     /usr/bin/python3 -B implementation/warlock/adapter/current_build.py build \
       --lock /absolute/private/current-lock.json \
       --sha256 REVIEWED_LOCK_SHA256 \
       --output /absolute/private/new-build-directory
   ```

   The parent directory must exist and the output directory must be new. All three optimized roots must succeed. The recipe stages only declared compiler inputs for this build, checks staged bytes, records compiler commands/logs and retains failure/partial output evidence. The exact private package registry is a mutable compiler cache seeded from the lock: each root retains before/after registry bytes and hashes in a checked chain. Other staged source/cache bytes stay strict, and undeclared cache files are rejected. This workspace is a build artifact, not a new source version. Poll the same process until terminal, then send the successful QA RELEASE receipt.

3. Review `new-build-directory/report.json` and its SHA-256. Consumers validate that exact receipt before using its assets:

   ```bash
   python3 -B implementation/warlock/adapter/current_build.py validate \
     --report /absolute/private/new-build-directory/report.json \
     --sha256 REVIEWED_REPORT_SHA256
   ```

   Validation checks the current source/lock identity, exact successful commands/environment, static and compiled asset inventory/hashes, compiler logs and frontend-only acceptance flags. Keep the lock, report and build assets in their recorded locations. A successful validation is an input/output custody check, not GUI acceptance.

For an actual native campaign, separately review the owning ABI tuple, host objects/providers/dependencies, current frontend composition and original scenario runner. This recipe does not replace historical native guards or solve the pending attention fixture's AT export association. Complete tool upstream source provenance, Python/runtime dependency closure, isolated offline rebuilds, redistribution review and release gates remain separate obligations. See [verification](verify-selected-change.md) and [status and evidence](../reference/status-and-evidence.md).
