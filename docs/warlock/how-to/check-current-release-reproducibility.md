# Check reproducibility with a reviewed current composition

Use this guide to prepare the existing release rebuild campaign against an explicitly reviewed current native composition. It does not install Warlock. Root owns serialized protected execution and the AgentBus HOLD/RELEASE gate described in [the verification guide](verify-selected-change.md).

## Select and review the inputs

Prepare a [validated current composition](validate-current-composition.md) and record its absolute path and complete SHA-256. A changed adapter, source, dependency or validator invalidates the applicable lock; preserve it and review a new capture rather than editing its old hashes. Current frontend assets and historical host-source provenance have distinct roles.

Review the current release catalogues against the selected artifacts. Their provenance references and expected payload identities must match actual source and reviewed build receipts. Preserve unresolved redistribution and notice decisions. A matching hash does not establish a license grant or clear the release audit.

## Run the protected campaign

From this checkout, after successful root coordination and source review:

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B window-integration-qa/qa_run.py -- \
  /usr/bin/python3 -B implementation/warlock/qa/check-release-repro.py \
  --native-tuple /absolute/path/to/reviewed/native-lock.json \
  --native-tuple-sha256 COMPLETE_REVIEWED_SHA256
```

Both selection arguments are required together. The checker rejects nonregular or relative paths, malformed hashes and actual digest mismatches before creating a run. Omit both only to select the existing legacy builder route; it does not infer a current composition. `--probe` checks isolation only and rejects tuple-selection arguments.

The full campaign checks namespace separation, blocked network, read-only inputs and hidden host source, captures the locked inputs, stages an isolated filesystem and attempts clean builds A and B. It retains the existing host and all-current-asset hash checks, package audit and distributable comparison. Successful builds then exercise actual archive, payload and alias mismatch detection and restore the originals.

## Classify the actual result

Read the top-level report, `pair/reproducibility-report.json`, each attempted build's environment and sandbox logs, compiler outputs and compliance report. Keep these distinctions explicit:

- A failed namespace probe reaches no input capture or build.
- A capture refusal reaches no clean build.
- A failed build A leaves build B unattempted in the current coordinator.
- Matching rebuilt host/assets is component evidence; it is not a completed distributable or a two-build comparison.
- A compliance block remains a release block even when compilation and byte identity checks pass.

The generic error “Two offline builds did not match” can describe an early A failure. It does not by itself demonstrate two differing archives. Check which builds and artifacts actually exist before updating the original DEL004 ledger.

The [current evidence](../../../implementation/warlock/qa/evidence/current-release-selection-20261030/LIMITS.md) records one isolated A reproducing the selected host and all 19 frontend assets, followed by a 19-decision compliance block. No archive or build B exists. Do not bypass that audit or call the original two-build obligation accepted.
