# Independent bounded settings migration review

Reviewer: roadmap-fidelity. Source and retained evidence read only; no QA rerun or public edits. Disposition: **approve the bounded source repair and observed production-store filesystem checks; no remaining blocking finding in the reviewed delta under the existing private-directory/cooperative-lock contract.** Root owns original scenario/requirement acceptance. Companion model is separate and was not reviewed here.

## Original contract and repaired defect

ELM-DEL-015 requires versioned validated schema, atomic writes and a preserved pre-migration copy before schema upgrade. Its scenarios cover valid upgrade/recoverable original, invalid writes leaving active unchanged, interrupted old-or-new complete settings, and failed migration retaining recoverable original without pre-commit activation. Baseline report records actual production Store Saved/schema2 with exactOriginalRecoverable=false. Current repair retains exact schema1 bytes including whitespace before explicit changed schema2 publication; read-only normalization is not a disk upgrade.

## Source disposition

Both active and existing backup opens now use O_NOFOLLOW|O_NONBLOCK. FIFO does not wait for a writer; inherited _private rejects nonregular paths, wrong owner, group/world permissions and multiple links. The existing private directory and shared nonblocking flock cover save/read. Same-user external mutation outside the cooperative lock remains outside these guarantees; no cross-UID security expansion is claimed.

Validation precedes acquisition/migration. Stale revision, no-op, revision exhaustion and current schema2 avoid new backup publication. Unknown/invalid schema does not get overwritten. Exact-byte existing backup equality is checked and synced; foreign/unsafe existing backups refuse. New backup is exclusive random 0600 temp, complete file fsync, no-overwrite link, temporary unlink and directory fsync before creating/replacing the active new schema. Active file is fsynced before rename, then directory synced. Pre-active-replacement failures leave old active intact. A post-rename final directory-fsync failure returns Unknown with complete new active, not false Refused/rollback. This distinction is necessary for truthful outcome handling; it is not an automatic retry contract.

Earlier FIFO hang finding is addressed on BOTH paths. The link-to-unlink crash edge remains deliberately fail-closed: two-link backup contains exact original and old active remains recoverable, but a restarted Store refuses migration. There is no automatic cleanup promise or weakening of the hardlink guard. This documented availability limitation is not a remaining blocker to the bounded preservation repair; do not claim every interrupted publication is automatically retryable. Actual sudden power-loss durability on a particular filesystem is not demonstrated.

## Actual retained evidence inspected

The summary report says passed=true with exitCode0 for both current QA sources and storeSHA matching current source. I independently rehashed those source files, parsed both stdout JSONs and counted 47 legacy plus 327 migration checks, all passed=true; both stderr files are empty. I did not observe the outer protected process directly or rerun it. Protected execution identity is root's claim unless separately supplied by its launcher receipt; the compact summary itself does not record the full imported dependency/tool/environment closure.

Migration test uses the actual Store and real temporary files, syscall faults at backup file sync/publish/unlink/directory sync and active file sync/rename/directory sync. It observes exact backup presence at active publication, formatting, private single-link state, later schema2 backup preservation, stale/no-op/invalid refusal, conflicts, symlink/hardlink/shared-copy refusal, and current2 behavior. Both FIFO cases execute actual Store.save in timeout-bounded subprocesses and return Refused. Two-link restart explicitly refuses and retains old active/original. Seed0xDE1015 generates100 parameterized invalid/valid/restart/stale sequences (300 of327 assertions); this is useful production sequence coverage, not arbitrary interleavings or power-loss testing. No test count is a native feature count.

The new reference accurately describes these semantics, including no automatic cleanup, post-rename Unknown and no native/power-loss claim. Its claims do not promise transparent recovery after every interruption. Retain original baseline/fault evidence and exact source hashes when canonicalizing. Parent _private/endpoint hashes below record the dependencies I actually inspected now; they are not retroactive proof that the runtime pinned them.

## Approval limits / next gate

No further source blocker identified in this delta. Canonical evidence should bind current source, test/log hashes, original oracle, actual protected execution and dependency context; keep baseline immutable. Root/independent original acceptance must distinguish pre-commit migration failure from post-publication Unknown and retain the two-link manual-recovery limit. Native settings/help/AT/restart presentation, reversible deployment, licensing and full release remain separate. No claim is made about concurrent hostile same-UID writers, physical power failure, all filesystems, model results or broader original requirements. Do not reset unrelated stopped investigations.

## Recomputed identities

- `/home/charles/Warlock/implementation/warlock/adapter/shell_preferences.py`: `702f110efc7db1c5ab45df0fc2910a06891eb0abce5fc4183271dd3538b2bdb4`
- `/home/charles/Warlock/implementation/warlock/adapter/taskbar_preferences.py`: `4fde83478c22f7173ef05727a3666ff7ce72076bc05fddfa4fd08705af9a57d2`
- `/home/charles/Warlock/implementation/warlock/adapter/endpoint.py`: `e254b870922a46b935de9d85db1de56129838ea2cf73eeb55c9fa16e8539d731`
- `/home/charles/Warlock/implementation/warlock/qa/check-settings.py`: `b39f26f170336599756aab3812c8c41ab1a71fcd6846590abea7b3557409ee5a`
- `/home/charles/Warlock/implementation/warlock/qa/check-settings-migration.py`: `3fe44bc9252e0a99ee5007d78221cf148c864cd9cb8dedb46da83a1786b7b184`
- `/home/charles/Warlock/docs/warlock/reference/settings-storage.md`: `3922cfcc31e1092834f838cd0d8a7f89caf0f4f3cbfdcc50d3799c20d8e2c8a0`
- `/home/charles/.local/state/warlock-team/20261028/settings-migration-root-v1/baseline-report.json`: `bf1d2f2bb4ce7ff704c6f0d98e6968752931837be32ade98a42d6140fec234b4`
- `/home/charles/.local/state/warlock-team/20261028/settings-migration-root-v1/checks-1793345705544487265/report.json`: `e140444f529b440f5b2da1756ae51b4d76107f109bf012bdd4b6d7b6e201b7ef`
- `/home/charles/.local/state/warlock-team/20261028/settings-migration-root-v1/checks-1793345705544487265/check-settings.py.stdout`: `6c0f49e8cbd9ff014a0c864df13919fe303bc6870fbd03168b8446afbeb355ed`
- `/home/charles/.local/state/warlock-team/20261028/settings-migration-root-v1/checks-1793345705544487265/check-settings-migration.py.stdout`: `ce65aa06ccf40b7c0d700e3d78128e1b1a6d226f54473341c0d19a636314c15b`
