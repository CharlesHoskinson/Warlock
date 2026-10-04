# UI/UX budget preflight prototype

This independent CPU component validates a declared budget matrix before comparative evaluation. It never grants performance, graphics, host-selection or release acceptance. `performanceAccepted` is always false, including for a complete synthetic fixture whose measured values exceed an absolute budget.

The protected final CPU campaign passes **44 checks**. Its predecessor passes 42 checks and remains under `qa/initial-42-checks/`, including original source and evidence. No native GUI campaign runs, no measurements are acquired, and `docs/elm-roadmap/delivery/budgets.json` is unchanged.

The actual current budget document yields deterministic `calibration-only`, `completeness: incomplete`, `schemaReady: false`, `performanceAccepted: false`. Its diagnostics identify missing comparative baseline, frozen thresholds and instrumentation overhead, and the helper-to-DOM timing endpoint. See `qa/current-budgets-verdict.json` and `qa/legacy-cli.stdout`.

## Executable schema

Input discriminator: `schema: "elm-budget-preflight/1"`. A complete synthetic example is `qa/valid-synthetic-matrix.json`; its limits, devices and approval reference are test data, not product decisions or observed hardware.

Required matrix rows: cold-start, idle, catalog-refresh, switcher, minimized-preview, first-capture, reversible-motion, output-transfer, soak. Each row carries a fixture SHA-256, warm/cold identity and workload definition. Each row has latency, CPU, wakeups, memory, frame-misses, power and copy-transfer categories. A category may declare a reasoned exclusion with a review reference; the validator checks that declaration structurally, not whether the exclusion is acceptable.

Each measured category requires:

- Nonempty unit/definition, positive integer minimum sample count, and finite nonnegative absolute maximum, regression-percent maximum and instrumentation-overhead maximum. JSON booleans are not numbers.
- Baseline and candidate source/evidence identities, evidence hashes, adapter/driver/backend/engine/output metadata and matching measurement semantics. Different source tuples are allowed because baseline and candidate are different implementations.
- Explicit clock domain, start/end events and same-domain declaration or measured mapping hash. Native monotonic domain names are accepted; other domains require a mapping hash. Latency specifically declares native seat input to native presentation. These declarations require independent instrumentation review.
- Nonempty finite nonnegative samples, exact count, frozen minimum count, nearest-rank p50/p95/p99 computed consistently from samples, measured bounded instrumentation overhead and complete process-group accounting declaration.
- Timezone-aware freeze/measurement timestamps. Candidate acquisition follows the declared freeze time. Baseline acquisition may precede freeze to support calibration before setting thresholds.

Duplicate JSON fields and NaN/Infinity constants are rejected by the loader. Missing/incompatible rows, fields, samples, metadata and clock boundaries block structural readiness. A complete matrix returns `ready-for-evaluation`, which is permission to begin a separate evaluation, never a passing budget verdict.

## Running

CPU proof:

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B /home/hoskinson/omarchy-windows-parity/implementation/elm-ui-ux-budget-validator-v583/qa/test.py
```

Preflight CLI through the protected CPU launcher:

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B /home/hoskinson/omarchy-windows-parity/implementation/elm-ui-ux-budget-validator-v583/validator.py /home/hoskinson/omarchy-windows-parity/docs/elm-roadmap/delivery/budgets.json
```

Exit 0 means structural readiness only. Exit 2 means incomplete/calibration-only/invalid input; JSON provides the specific verdict. No integration ledger, runner, session or deployment decision is changed automatically.

## Evidence and limits

The design reads actual historical V160 and V164 measurement reports: they contain helper-to-DOM timing, whole-process sampling limitations and explicit nonacceptance. Input hashes are recorded in `qa/report.json`; those measurements were not rerun or imported as qualifying observations. The historical document format intentionally remains calibration-only until a new, reviewed matrix is prepared.

The validator does not authenticate evidence files, verify claimed process coverage/clock mapping/device identity, approve numerical budgets or exclusions, calculate budget pass/fail, establish representative workload adequacy, or replace GPU/physical-output/AT/human testing. A schema-valid lie remains unaccepted. Hardware acceleration and WebGPU qualification are separate gates.

The final protected report contains source hashes, actual unchanged budget hash and each named CPU check. `component-manifest.json` freezes owned source/evidence; `qa/freeze-receipt.json` binds the manifest and protected verification command. Preserve these records before preparing a changed derivative.
