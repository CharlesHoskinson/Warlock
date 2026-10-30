# ELM-DEL-015 / delivery-015 — private model proposal

**SOURCE ONLY: UNTYPECHECKED AND UNRUN.** This is not a validated spec, source/binary proof, native filesystem proof, or DEL-015 acceptance. User explicitly prohibits worker Quint/compiler/QA execution; root owns protected execution and independent review. Incremental typecheck/run required by the modeling skill is deferred, so errors remain possible. No edits to existing `qa/settings.qnt`, baseline or requirements.

## Original and source pins

`docs/elm-roadmap/REQUIREMENTS.md:1661` SHA256 `0058972a8133d01689815d3b4148c5fed95d7a79f1a192d512328feeae51c825`: validated versioned schema, atomic writes and preserved pre-migration copy before any upgrade; inject invalid fields, interrupted writes and migration failure. `docs/elm-roadmap/contributions/delivery.json:269` SHA256 `1b8edf80efb1c126e3ca7bf2a348fa429a8bfcd63c91a75364aab8295bbe5f46` scenario: old valid settings, schema upgrade, valid new settings and recoverable original exist.

- `implementation/warlock/adapter/shell_preferences.py` SHA256 `702f110efc7db1c5ab45df0fc2910a06891eb0abce5fc4183271dd3538b2bdb4`: `snapshot` validates and normalizes schema 1 in memory; `_read_original` retains raw bytes; `_preserve_legacy` writes and file-fsyncs backup temporary, hard-links, unlinks, fsyncs directory, or checks/fsyncs an existing matching private original; `save` applies valid schema-2 proposal, revision CAS and no-op gate before backup, then stages/fsyncs active and renames/directory-fsyncs. Failure before rename propagates; error after rename returns `Unknown`. A read itself never migrates.
- `implementation/warlock/adapter/taskbar_preferences.py` SHA256 `4fde83478c22f7173ef05727a3666ff7ce72076bc05fddfa4fd08705af9a57d2`: `_private` demands owner/private/regular and one link; `read` calls `_read` only. `implementation/warlock/adapter/endpoint.py` SHA256 `e254b870922a46b935de9d85db1de56129838ea2cf73eeb55c9fa16e8539d731`: `Refused` is a raised `RuntimeError`, not an `OSError`.
- Actual production-route checker `implementation/warlock/qa/check-settings-migration.py` SHA256 `3fe44bc9252e0a99ee5007d78221cf148c864cd9cb8dedb46da83a1786b7b184` supplies positive, no-op/CAS/invalid, seven syscall failures, FIFO child and 100 seeded parameter sequences. User reports protected pass; this thread did not execute it. Retained pre-fix `settings-migration-root-v1/baseline-report.json` SHA256 `bf1d2f2bb4ce7ff704c6f0d98e6968752931837be32ade98a42d6140fec234b4` is historical. Existing `implementation/warlock/qa/settings.qnt` SHA256 `a171d177b09f2e31ee56e29f75d8bfa37c761bf76588cf942e43d4be3c16ba34` untouched.

## Scope and mapping

One writer/local shared filesystem with the application's existing exclusive lock; no distributed protocol, external writer races, OS scheduling or native policy. `active`, `old`, `backup` are opaque whole-byte identity classes: exact raw original=1, complete schema-2 image=2, foreign backup=3; hash collision resistance, validation and atomic rename are assumptions. Model fields distinguish existing/fresh backup, 0/1/2 links, safe file, backup file + directory sync, active file + directory sync, rename visibility, outcome and restart. The finite model abstracts values/revisions and unknown-field rejection into valid/invalid/CAS/no-op actions; it does not model arbitrary JSON, IDs, POSIX semantics, storage hardware or every choice.

| Original obligation / source route | Model actions / observations |
| --- | --- |
| Observation only; invalid, CAS conflict and no-op do not migrate | `readLegacy`, `invalid`, `casConflict`, `noChange` and named witnesses |
| Existing schema-2 write needs no new legacy backup | `currentSchema`, normal active phases, `currentSchemaWitness` |
| Existing backup immutable and exact/private or refuse | `existingExact`, `existingForeign`, `existingUnsafe`, `syncExistingFile`, `rejectBackup`; `backupNeverOverwritten` and three witnesses |
| Original complete file before activation | `flushBackup`, `linkBackup`, `unlinkBackupTemp`, `syncBackupDirectory`, then `writeActive`, `flushActive`, `renameActive`; `originalBeforeActivation`, `completeActive`, `successWitness` |
| Real boundary failures, no fabricated rollback | `preRenameFault`, `linkedInterrupt`, `postRenameFault`, `crashBeforeBarrierOld`; named failure/restart witnesses |
| Post-rename directory fsync failure | `postRenameFault` returns Unknown with complete new active visible and original retained; `activeBarrierUnknownWitness` |
| Unsafe active type/mode/link/schema | `unsafeActiveFixture`, `invalidSchemaFixture`, `rejectActive`; `restartRead` requires active-safe/schema-valid; no scheduler/no-hang proof |
| Source bug illustration | `brokenActivate` is NOT in `step` and explicitly violates `originalBeforeActivation`; `brokenWitness` |

`Refused` in the model is an observable rejection class: CAS/no-op correspond to the actual `('Refused', old)` result; invalid proposal, bad type/schema or unsafe/mismatched backup can raise `Refused` instead. `Raised` covers injected pre-rename OSError; `Unknown` corresponds to actual `('Unknown', None)` on an OSError after rename. No general assumption makes an exception restore old bytes after rename.

A real interruption after backup link and before temp unlink can leave two links. `twoLinkFailClosedWitness` retains exact old bytes, then reads the still-valid active file on restart; a subsequent save fails private-backup validation. **Ordinary restart read does not inspect the backup.** This is recoverable bytes with availability requiring manual recovery, not all-restart idempotence or automatic repair. On actual fsync-failure return the visible renamed active is new; modeled `crashBeforeBarrierOld` separately allows an old complete active after a crash before the directory barrier. The model assumes the old/new images and fsync semantics; it does not prove actual power-loss outcomes.

`completeActive`, `originalBeforeActivation`, `savedAfterBarrier`, `backupNeverOverwritten`, `twoLinkRecoverable` are proposed safety properties over independent transitions. They are not a proof of actual implementation, and the model excludes races with untrusted external mutation, hardware lies, storage exhaustion timing, unknown schemas beyond rejection, durable state after arbitrary crash and first-use/native/AT behaviors. The model assumes the settings lock and FS operations behave according to modeled boundaries. `existingUnsafe` abstracts symlink, FIFO, wrong owner/mode or hardlink as a refused unsafe backup, not a scheduler model; no FIFO no-hang guarantee is inferred.

## Deferred root execution after independent review

Set `P=/home/charles/.local/state/warlock-team/20261028/native-rebuild/settings-migration-quint3-v1`, `Q=/home/charles/.local/state/warlock-team/20261028/tooling/node_modules/.bin/quint`, `L=/home/charles/Warlock/window-integration-qa/qa_run.py`. Run from repo root through unchanged protected launcher, retaining every raw output; use no Apalache. Typecheck errors, witness coverage and failures are evidence, not permission to weaken invariants:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/charles/Warlock/window-integration-qa /usr/bin/python3 -B "$L" -- "$Q" typecheck "$P/settings-migration.qnt"
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/charles/Warlock/window-integration-qa /usr/bin/python3 -B "$L" -- "$Q" typecheck "$P/settings-migration_test.qnt"
for name in readOnlyWitness successWitness existingExactWitness invalidWitness casWitness noopWitness currentSchemaWitness unsafeActiveWitness invalidSchemaWitness foreignBackupWitness unsafeBackupWitness backupFaultWitness backupPublishFaultWitness backupDirectoryFaultWitness activeFileFaultWitness activeRenameFaultWitness activeBarrierUnknownWitness twoLinkFailClosedWitness crashOldWitness brokenWitness refuseInvalidActivation refuseForeignStart; do
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/charles/Warlock/window-integration-qa /usr/bin/python3 -B "$L" -- "$Q" test "$P/settings-migration_test.qnt" --main settings_migration_test --match "^${name}$"
done
for invariant in completeActive originalBeforeActivation savedAfterBarrier backupNeverOverwritten twoLinkRecoverable; do
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/charles/Warlock/window-integration-qa /usr/bin/python3 -B "$L" -- "$Q" run "$P/settings-migration.qnt" --invariant "$invariant" --max-samples=1000 --max-steps=20 --backend=typescript --seed=20261030
done
```

Examine actual selected test count and positive trace reachability, not exit code alone. `fail()` negatives are terminal and have no successor transition. Broken action is deliberately absent from sampled normal `step`. Preserve root's source-level fault tests and exact baseline; tests of this model do not substitute for them.
