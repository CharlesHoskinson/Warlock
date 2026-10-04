# Visible rename and durable release: corrected model derivative

V602 remains unchanged. Its crash abstraction restored only durable state and discarded unsynchronized publication, so it did **not** cover process restart retaining a visible Prepared or Released rename. That limitation masked the V600/V603 recovery-ordering defect found by root. V605 separates visible namespace state from synchronized journal state.

Protected CPU evidence: **36 exact named scenarios**, **2,000 bounded sampled traces of at most80 transitions**, and **9 typechecked negative controls**, each failing an actual assertion. No native or filesystem test ran. The initial mutation-selector cardinality failure and its source/logs are preserved under `qa/failed-selector/`.

## Model correction

`visibleStage` changes when a valid Prepared/Released record is renamed into the namespace. `stage` changes only after the journal root's synchronization operation. A process `Crash` retains visible renames and admission unlinks but clears the runtime's `rootReady` flag. A separate `PowerLoss` event restores the last synchronized namespace/file states. This distinction makes the previously omitted counterexample executable.

`RestartRootSync` synchronizes the visible journal and establishes the runtime root barrier. Recovered Prepared cannot unlink its admission before that barrier. Recovered Released cannot acknowledge release or admit a new explicit action before it. Even a previously durable Released record must pass the restart barrier; the reader cannot assume its recovered namespace is already synchronized.

The visible-Prepared scenario renames Prepared without its directory fsync, crashes, attempts unlink, and proves the admission remains present while `visibleStage=1`, `stage=0`, `rootReady=false`. Only explicit root synchronization permits subsequent unlink. The visible-Released scenario crashes after final rename but before directory fsync; acknowledgement and new action remain blocked until root synchronization. Matching power-loss scenarios demonstrate that those unsynchronized renames may instead disappear.

Original V602 safety properties remain: exact retired-key proof; separately correlated action/geometry observations beyond its barrier; synchronized proof and Prepared record before removal; admission unlink/directory fsync before Released publication; Unknown history separate from live reservation; no old-intent replay, Committed inference, released-key resurrection, history overwrite or frontend-generation wrapping. The prior31 scenarios retain their power-loss meanings with explicit recovery barriers; five new scenarios exercise surviving-visible publication and its contrast.

## Negative controls

1. Recovered Prepared uses visible stage and skips the root barrier before unlink.
2. Recovered Released uses visible stage and skips the root barrier before acknowledgement.
3. Already durable Released skips its restart barrier.
4. Prepared rename is incorrectly treated as durable synchronization.
5. Released rename is incorrectly treated as durable synchronization.
6. Power loss incorrectly preserves an unsynchronized rename.
7. Registered proof is accepted as Retired.
8. An old intent is replayed.
9. Prepared completion regresses a Released journal.

Each mutation typechecks, then its selected scenario fails by assertion. These witnesses establish the model's sensitivity to the intended ordering rules; they do not prove the implementation matches the model.

## Evidence and limits

`qa/report.json` records selected/executed identities, commands/seeds, output/source hashes and mutation outcomes. Passing named traces are retained as ITF. The predecessor's exact source and manifest are retained under `qa/ancestor602/`; they are ancestry rather than new execution.

This model assumes record contents were validly written and file-synchronized before rename, that a successful root-directory fsync commits the modeled namespace, and that the native authority epoch remains stable through daemon restart. It does not model corrupt/foreign files, symlinks, rename/IO errors, concurrent writers, actual kernel/storage durability, native-authority replacement, scene changes or application effects. Failed synchronization supplies no successful model transition; actual error handling needs implementation fault tests. Root V604's real filesystem implementation must qualify those independent obligations.

Reproduction, CPU only:

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B /home/hoskinson/omarchy-windows-parity/implementation/elm-durable-release-model-v605/qa/run.py
```

All writes are confined to V605. No shared ledger, V602 evidence, native session or Git state changed.
