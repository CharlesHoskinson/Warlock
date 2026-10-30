# Final independent original ELM-DEL-015 disposition

Reviewer: roadmap-fidelity. **Accepted: all four original scenarios and the whole current implemented ELM-DEL-015 EARS**, on the exact source and observed store/protocol tuple identified below. This is original settings-storage acceptance, not GUI, AT, native window behavior, deployment or release acceptance. No QA was rerun; I read source, original oracles, actual retained outputs and root's model execution/correspondence review. Root owns canonical integration and ledger writes.

## Literal oracle dispositions

| Original scenario | Disposition | Decisive evidence |
| --- | --- | --- |
| `delivery-015`: old valid settings upgrade leaves valid new settings and recoverable original | **accepted** | Actual production schema1→2 save and fresh Store read recover the new validated revision; exact original formatting survives in private single-link backup before active rename. Later schema2 saves do not replace that original. Baseline defect is preserved, not relabeled passing. |
| `invalid-settings`: invalid fields refuse and active settings remain unchanged | **accepted** | Legacy47 and migration327 include real validators, schema/field/type limits, invalid flags/scales, stale CAS/no-op controls and 100 reproducible parameter sequences. Invalid proposals do not create a migration or overwrite active bytes. Source validation precedes publication. |
| `interrupted-settings`: interrupted atomic write recovers complete old or complete new, never partial | **accepted** | Injected syscall failures plus 11 actual abrupt child exits (exit85, no Python finally cleanup) and 56 assertions reopen the production Store and recover expected complete validated old/new state. Actual publication is fsynced-temp then atomic rename; no partial active bytes observed. |
| `migration-failure`: original remains recoverable and failed upgrade is not activated | **accepted** | Backup file/publish/unlink/directory barrier and active staging/rename failures preserve old active; original bytes remain recoverable. The two-link publication interruption is explicitly exercised through fresh-process reopening and later save refusal. No automatic cleanup or weakened hardlink guard is claimed. |

Whole EARS: versioned validated schemas, atomic writes, and preserved pre-migration original before the implemented upgrade are **accepted for the current implemented settings-storage boundary**. Final directory-sync error after active rename is an uncertain already-published outcome (`Unknown`), not a pre-commit failed migration or a false rollback guarantee. Its complete new active and original backup are explicitly checked. This disposition does not require an impossible rollback claim after the commit point.

## Actual settings scope, not an appearance-only redefinition

The tested schema upgrade is in `shell_preferences.Store`. I additionally inspected the other adopted settings stores: `taskbar_preferences`, `shortcut_preferences` and `motion_preferences` each validate and write schema1 only and reject unsupported versions. They have no existing alternate upgrade path that can bypass original preservation. Their source retains private-directory/flock discipline, validated CAS proposals, fsynced temporary bytes, atomic rename and post-rename Unknown. No currently implemented upgrade that overwrites a previous version was found outside the repaired route.

`recovery_profile.preference` invokes production validators but returns the original input body; `copy_state` and exclusive baseline creation write those bytes. Compatible legacy appearance validation therefore does not silently serialize schema2 or migrate a copied preference. This source-backed inventory closes the actual adopted migration boundary; hypothetical future schema upgrades are not a new acceptance gate. The 47/327/56 runtime results exercise the appearance Store, not newly rerun shortcut/motion/pin store matrices. The cross-store conclusion is source correspondence; retain that distinction.

## Source and execution checks performed by this reviewer

Current Store SHA702f110e matches the tested report and both reads are O_NOFOLLOW|O_NONBLOCK before regular-file/private/single-link validation. The earlier FIFO hang finding is addressed on both active and backup paths; both timeout-bounded subprocess controls are observed passing. Backup conflict/symlink/hardlink/shared-permission negatives do not overwrite active/original. Backup fsync and directory barrier precede active publication. CAS, no-op, max revision and current-schema behavior preserve the original.

The prior review71603ac9 and immutable baseline remain applicable to unchanged production source. I previously parsed actual47+327 outputs, checked their source pins and empty stderr. I now checked the canonical process-cut report218f4e39/stdouta521382d: passed=true, 11 distinct selected exits, 56 passing checks, current source/runner pins. No child normal exit86 can satisfy the abrupt-cut positive control.

For the model I applied the Quint review skill structurally and reviewed retained execution rather than rerunning QA. Public files equal canonical v2 model677962af/tests582737d7. One grouped State, sum-type phases/outcomes, guarded whole-state transitions, observable byte classes and explicit unsafe/foreign/no-op/current-schema routes support source correspondence. Nontrivial backup-before-activation, saved-after-barrier and no-overwrite invariants are not mere type bounds. A deliberately broken historical activation is excluded from normal `step` and has its own expected failing-property witness. V1's fixture-composition defect is retained without invented execution.

I independently checked all38 command stdout/stderr hashes against model/report.json; every recorded exit is0. These include version, two typechecks, executable init, 29 explicitly selected named tests (each actual stdout positively reports one test) and five sampled invariants, each1000 traces/max30steps/seed20261030. Positive success and fault/restart witnesses prevent vacuous safety from being mistaken for useful reachability. Public and frozen model bytes match. No counterexample was observed in these bounded runs; there is no exhaustive or universal proof claim. The source headers still say proposal/unrun; exact qualified hashes and retained runtime reports supersede that historical annotation only for this observed version, not all proposals.

## Scope and limitations

No remaining decisive original settings-store oracle gap identified. The two-link interrupted backup remains manually recoverable but automatic retry is refused; this is documented and does not lose the required original. POSIX atomic rename/fsync semantics and a cooperative single writer are assumptions. The process cuts are real process interruption with fresh reopening, not sudden power-loss experiments, every filesystem or hostile same-UID concurrent edits. The model uses opaque complete-byte classes and is not JSON/parser or OS implementation proof; real production filesystem/validation tests provide that complementary evidence.

Outer protected scope/invocation terminal observations are root's reported executions with retained cgroup/command/output receipts; I did not independently launch them. Tool hashes are bounded to the report's explicit pins, not exhaustive Node/Quint/OS dependency closure. Root's reference and LIMITS accurately retain Unknown/manual cleanup and non-native limits. Original native UI020 guidance/restart/AT, reversible Omarchy trials, licenses, hardware/resources/journeys and release obligations remain separate. All original242 requirements/417 scenarios remain intact; this closes only ELM-DEL-015, without resetting stopped investigations or accepting other settings UX.

## Recomputed identities

- `/home/charles/Warlock/docs/elm-roadmap/requirements.json`: `a0c2093cc7769e05b70cc81aa3c001dbcbffe936cc17d1c494d7ab2fdc8b3b1b`
- `/home/charles/Warlock/implementation/warlock/adapter/shell_preferences.py`: `702f110efc7db1c5ab45df0fc2910a06891eb0abce5fc4183271dd3538b2bdb4`
- `/home/charles/Warlock/implementation/warlock/adapter/taskbar_preferences.py`: `4fde83478c22f7173ef05727a3666ff7ce72076bc05fddfa4fd08705af9a57d2`
- `/home/charles/Warlock/implementation/warlock/adapter/shortcut_preferences.py`: `2a8cc047ebfb5040c7dda4f9fd0f9e80a9b1207245458beda3ac26ff2251c185`
- `/home/charles/Warlock/implementation/warlock/adapter/motion_preferences.py`: `ec75685d52f81d5d28f82155b92580015dc897bee6488892c2a8f98e0ffa3633`
- `/home/charles/Warlock/implementation/warlock/adapter/recovery_profile.py`: `ace346503b5afd2c691748e7c2e1c25394fd81cc0a90be60525ff6cd85a78142`
- `/home/charles/Warlock/implementation/warlock/adapter/endpoint.py`: `e254b870922a46b935de9d85db1de56129838ea2cf73eeb55c9fa16e8539d731`
- `/home/charles/Warlock/docs/warlock/reference/settings-storage.md`: `f70107e9ebc02edf4861a18df5638d8398e1cd9b7c68ed699a1aa0caebf944c1`
- `/home/charles/Warlock/implementation/warlock/qa/evidence/settings-migration-verification-20261030/model-source/settings-migration.qnt`: `677962afa6ff53346c4b033efcb7f89a9b8c3bfd98d1ad300715901ba859ddb2`
- `/home/charles/Warlock/implementation/warlock/qa/evidence/settings-migration-verification-20261030/model-source/settings-migration_test.qnt`: `582737d73c186e4b6a6a5b2346bb90beec02817262e878a84e9252f36d8ca575`
- `/home/charles/Warlock/implementation/warlock/qa/evidence/settings-migration-verification-20261030/model/report.json`: `8bce6f17df2b3ffdba520a4f2bdd866f0edb8c517644e35bfacf9a9cbde839bb`
- `/home/charles/Warlock/implementation/warlock/qa/evidence/settings-migration-verification-20261030/model-review.md`: `92f4acdfa7ad4fb42bd4cc61c0940664332c1fae8a255d056d7f7b014fed0ad7`
- `/home/charles/Warlock/implementation/warlock/qa/evidence/settings-migration-verification-20261030/process-cuts/report.json`: `218f4e39d5b55b024292706ccc186c9201b5fc4491f68d6bdd50e03851db9443`
- `/home/charles/Warlock/implementation/warlock/qa/evidence/settings-migration-verification-20261030/process-cuts/stdout`: `a521382d02747a9d1fcbd6c83a82bf998b02fd3b2c38a65ccb1e5a567d8111c5`
- `/home/charles/Warlock/implementation/warlock/qa/evidence/settings-migration-verification-20261030/LIMITS.md`: `bcba453a74d523fac40e61b356122fc0c2f58888a1e8c3782cd04b4cf2db626e`
- `/home/charles/.local/state/warlock-team/20261028/settings-migration-root-v1/review.md`: `71603ac9b5106fe2b290d49baa3fc38c55a7820f487edab729d6880930dc219a`
- `/home/charles/.local/state/warlock-team/20261028/settings-migration-root-v1/checks-1793345705544487265/report.json`: `e140444f529b440f5b2da1756ae51b4d76107f109bf012bdd4b6d7b6e201b7ef`
