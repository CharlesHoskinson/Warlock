# v641 preparation handoff

Protected CPU controls report:
`qa/controls-1791153465947021714/report.json`.
Native campaign remains unrun. Coherent target/preflight acceptance remains
pending the reviewed repeated-reconnect fix and full GUI build.

Root should create preflight/evidence paths in a fresh root-owned native campaign
packet, leaving this frozen preparation unchanged. Run the generator through
qa_run.py with explicit `--gui`, `--output` and `--native-output-directory`.
Then export `ELM_RELEASE_NATIVE_PREFLIGHT` to that generated JSON and use the
serialized build-loop native command with this packet's qa/runner.py. The runner
writes native evidence to the new path selected by the preflight JSON.

The exact GTK fixture and DOM inspection collector are copied from v627. The
CPU fixture adapter/native inputs are copied from v624, with provenance verified
by the freezer. They are not the target runtime daemon: runtime imports only the
selected GUI build's actual adapter files through the source-pinned QA wrapper.

All user actions use actual native pointer input. The wrapper suppresses one
release output only after verifying real persisted certificate/history. Explicit
user Reconnect performs all recovery. The first broker Pending interruption and
the intentionally failed release backend are expected abnormal exits; the
webview/final backend and fixture must exit normally and cleanup must pass.

Keep original135 and general behavior acceptance separate. This packet neither
rewrites their oracles nor claims they ran as part of this additive journey.
