# Optional Harness2 adapter

The contributor core remains standard-library Python 3.9+. Harness2 is optional.
The adapter does not install packages, launch an agent, change a guard, adopt a
candidate, merge a branch or grant acceptance.

The original project is [google-research/harness2](https://github.com/google-research/harness2).
This adapter pins commit `6868817518876de8fd170c6a8354daca273b6191`.
Its [package metadata](https://github.com/google-research/harness2/blob/6868817518876de8fd170c6a8354daca273b6191/pyproject.toml)
requires Python 3.12 or 3.13 and declares no runtime dependencies. Its recursive
Propose–Probe–Compose API can compare execution behavior and retain lessons.
That mechanism does not replace Warlock's original oracles or acceptance review.

## Place in the implementation loop

After each completed slice, the contributor core requires an RSI disposition for
the workflow plugin: `adopted`, `no-change` or `deferred-blocker`. Use that existing
record and handoff. This adapter supplies optional comparison evidence for that
step. It creates no second ledger or controller. An RSI record does not itself
start another recursive RSI obligation.

Choose a concrete workflow problem, such as an ambiguous prompt, wrong tool
sequence, ineffective task decomposition or incomplete handoff. Freeze the same
task and source inputs before comparing the baseline and candidate. Change only:

- `prompt`
- `toolGuidance`
- `taskDecomposition`
- `handoff`

Authorization, guards, tests, original oracles, task/source inputs and the baseline
plugin snapshot are immutable. A proposal to change another field is refused.
Guidance text has no authority to override those inputs. Root must review its
meaning before any adoption; matching file hashes cannot prove that prose obeys
a policy.

## Freeze a private context

Use a new owner-only directory (`0700`) containing explicitly selected, nonsecret
copies. Keep repository-relative names. Symlinks, paths outside the directory,
missing files, duplicate roles and files larger than 1 MiB are refused. Freeze
before running each comparison arm. No desktop, native provider or original QA
runs through this adapter.

A request has exactly these fields:

```json
{
  "schema": 1,
  "taskId": "handoff-probe-1",
  "taskFiles": ["task.txt"],
  "sourceFiles": ["implementation/example.txt"],
  "oracleFiles": ["oracle.json"],
  "guardFiles": ["guards.json"],
  "authorizationFiles": ["authorization.json"],
  "pluginBaselineFiles": ["plugins/warlock-contributor/README.md"],
  "checkNames": ["delivered", "original-oracle-retained"]
}
```

The short plugin list above illustrates the format. A real RSI comparison must
use the **complete baseline plugin files map from the contributor core**, with
exact names and hashes. Root/core must reject a different or incomplete baseline
snapshot. The adapter cannot infer which unlisted files belong to that snapshot.

The harness JSON contains the four editable fields. The first, second and fourth
are nonempty strings; `taskDecomposition` is a nonempty list of unique strings.

```sh
python3 -B plugins/warlock-contributor/scripts/harness2_adapter.py freeze \
  --context-root /private/context \
  --request request.json --harness baseline-harness.json --output baseline.json
```

Repeat with the candidate guidance and the same frozen inputs. Outputs must be
new files. Freeze does not execute or approve the proposed guidance.

## Compare retained observations

Each arm supplies a JSON observation:

```json
{
  "schema": 1,
  "taskId": "handoff-probe-1",
  "snapshotSha256": "FULL_SHA256_OF_THE_CANONICAL_ADAPTER_SNAPSHOT",
  "checks": [
    {"name": "delivered", "passed": true},
    {"name": "original-oracle-retained", "passed": true}
  ],
  "reportFiles": ["reports/task-probe.json"],
  "regressionFiles": ["reports/plugin-regression.json"]
}
```

Check names, order and booleans must match the frozen inventory exactly. Reports
must exist inside that arm's private context. A combined report may serve both
roles if it actually records both observations; its contents still require review.
The adapter hashes reports but does not independently certify their execution.

```sh
python3 -B plugins/warlock-contributor/scripts/harness2_adapter.py compare \
  --baseline /private/context/baseline.json \
  --candidate /private/context/candidate.json \
  --baseline-observation /private/context/baseline-observation.json \
  --candidate-observation /private/context/candidate-observation.json \
  --completed-candidate-sha EXACT_FULL_CORE_DELIVERY_CANDIDATE_SHA256 \
  --output /private/context/comparison.json
```

The explicit completed-candidate digest is opaque: copy it from the core delivery
candidate. Do not substitute a task source-map digest. Comparison refuses changed
immutable files, stale snapshots, a different task, omitted/reordered/duplicate
checks, or missing reports.

The comparison receipt has `kind: same-task-harness-comparison` and these core
bindings: `completedCandidateSha256`, `baselinePluginSha256`,
`baselineSnapshotSha256`, `candidateSnapshotSha256`, `immutableHashes`, `checks`
and `regression` (an exact retained candidate report `path` and `sha256`).
`sourceSnapshotSha256` is separate from the completed-candidate digest. The plugin
snapshot digest hashes the canonical `{path: sha256}` map, without size metadata
or a self-referential digest field. Canonical JSON uses sorted keys, no spacing
and ASCII escaping.

The receipt also retains both arms' probe and regression hashes. A positive
supplied check delta proposes `deferred-blocker` until independent improvement
and adoption review. No positive delta proposes `no-change`; an evidence-based
no-change is valid and does not force a cosmetic edit. Root/core owns the final
disposition. Only verified improvement, independent review and the exact installed
plugin snapshot can support `adopted`. Every adapter receipt keeps
`acceptanceAuthority` and `autoAdopt` false.

## Optional upstream API probe

Run this only with a separately installed, private Python 3.12 environment and a
clean checkout at the pinned commit. No optional render/bridge/benchmark packages
are needed. Package build artifacts must remain outside the checkout; any changed,
untracked or ignored checkout input is refused, including `.env`.

```sh
/private/python312/bin/python -B \
  plugins/warlock-contributor/scripts/harness2_adapter.py upstream-probe \
  --upstream-root /private/harness2-study \
  --output-root /private/empty-probe-context
```

This fixed probe calls the real `harness2.core.schedule.run_domain` API with
`DemoAdapter` and `DemoProposer`: two arithmetic tasks, one recursion step, both
parallel and sequential modes, seed 0. It uses no credentials or live agents.
The child receives a minimal environment. A Python audit hook refuses socket
operations and any subprocess except the current Python interpreter running the
fixed private `summarize.py`/`ledger.csv` pair. The original upstream code remains
unchanged. The subprocess has a 120-second outer limit; each arithmetic execution
has the upstream 10-second limit.

The upstream package imports substrate definitions, including Codex definitions;
this probe never instantiates or invokes the Codex executor. Its unrestricted
sandbox/approval flags are not suitable for this workflow. Do not run upstream
model-backed benchmarks or substitute their launchers here.

A successful probe establishes only this deterministic API capability. It does
not measure a Warlock improvement, authorize another worker, reopen a stopped
slice, change any original deadline, or grant original/native/release acceptance.
