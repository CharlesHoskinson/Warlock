# Final public opt-in cancellation store review

Reviewer: roadmap-fidelity. No QA, model, import or compiler execution; no public edits. **Disposition: APPROVE bounded optional source integration and the documented store-component observation. No remaining concrete blocking defect identified in the reviewed delta.** This is not original ARC007/008/012/013, daemon enablement, native cancellation integration, C/Elm delivery, physical Escape, resource or release acceptance.

## Exact public source and prerequisite repairs

Public cancellation ledger31316524 and helperad23d4e7 are AST-identical, excluding only module docstrings, to the previously source-reviewed private d42f464e/1e5ca372 versions. I independently compared both ASTs. RecoveryStore3257927 remains identical. Therefore the actual source includes both ordinary-restart normalization and the later durable-attempt provenance repair; this approval does not reuse the older pre-repair review as though the defect were absent.

Restart repair normalizes legacy custody only, preserving original typed Pending admission keys, evidence, frozen predecessor and no-old-attachment mutation rights. The provenance correction independently guards live observations and persisted state: durable prepare before native evidence; exact prepared receipt before commit/cancel attempt; durable commit marker before Committed. Known native-owned Cancelled after prepare does not incorrectly require a local Cancel attempt. Strict initial Refused need not claim commit. Attempt history is monotone, and repeated commit remains consumed even if later Prepared/Unknown observations occur. Authentication remains a coordinator responsibility; Python evidence wrappers are not signatures or a same-process security sandbox.

Capacity charges actual serialized envelope bytes plus every retained typed record's remaining maximal growth, using current exact wire schemas, counter widths and finite terminal reasons. Admission and every later V7 write preserve that headroom. Certificates are durable before exact admission unlink, admissions-directory barrier, local retirement and ACK permission. Poisoned instances fail closed and reopen can reestablish barriers; visible replacement is never called rollback merely because a subsequent fsync failed. No identified defect remains in these scoped contracts under the existing private directory/cooperative writer assumptions.

## Actual public evidence inspected

The public entrypoint requires protected scope, pins the12 named production adapter modules and all shared fixture/case sources, then executes seven separate actual subprocess groups and rechecks those sources afterward. Fixture imports prepend the repository's actual adapter directory; no inherited private-store path shadows the production implementation. `completeRuntimeClosureClaimed=false` correctly avoids pretending these pins enumerate every transitive Python/OS dependency.

I independently rehashed every input in public report4b0267b2 against current repository source, and every command stdout/stderr against that report; no mismatch. Canonical store/report.json equals the actual public QA report bytes. Every group exited0 and reported passed=true:36 base,9 typed restart,23 provenance/corruption positives,99 selected syscall-fault assertions,239 capacity assertions/26 terminal pairs, plus exact ordinary-restart and missing-attempt negative observations. The last two groups are retained as structured observations, not converted to invented aggregate counts. The provenance negative reports both former out-of-order cases rejected. The source and actual positive cases corroborate the negative isn't merely disabling all cancellation outcomes.

Fault/capacity cases exercise the actual Store and private filesystem with strict native-response doubles, not a compositor/host/Elm transport. Nine faults include zero-progress write, file sync, close, replacement, envelope sync, exact admission unlink, admissions sync, final retirement save and ACK-permission save. Reopen, immutable keys, no old live rights, certificate-before-removal and reserved exact-byte boundaries are observed. All64-slot concurrency, arbitrary compaction, real storage exhaustion and abrupt power failure remain outside this matrix.

Model report dada4a52 records37 commands, all exit0: version,2 typechecks/init,24 separately selected named tests and9 bounded invariant samples of1000 traces/max30steps/seed20261030. I checked all37 retained stdout/stderr hashes; no mismatch. Q2's source STOP and narrow repair review are retained, with both RED defects and reconstruction diffs. The model is a reduced two-target persistence/ownership abstraction, not actual Python list/hash/JSON/locking/64slot or native transport proof. No exhaustive correctness is inferred, and no model/source correspondence gap is hidden by a passing sample.

## Deployment and original acceptance boundaries

I read the how-to, protocol/status reference, ownership explanation, README and LIMITS. They consistently mark default legacy/V6, internal explicit opt-in, strict response doubles, missing consumers and no original/release acceptance. I verified current daemon imports RecoveryStore as Journal but constructs it without `cancellation=True`; it therefore remains on the legacy path. There is no UI request that selects V7.

The distinct `host-cancellation-recovery` DTO preserves original record ownership under a current outer delivery binding and denies execution authority. Current host/Elm consumers are absent. Do not route nested historical certificates as ordinary fresh effect outcomes or native commands; these missing consumers and authenticated live coordination are still required before enabling the workflow. Store read/parse/attempt APIs alone do not prove native custody or per-generation resource retirement.

The protected how-to command names the actual public entrypoint, proper QA scope and serialized HOLD; no main-session change is proposed. Source navigation tutorial remains unaffected and the other Diátaxis quadrants describe the delivered boundary without calling it a complete feature. Previous accepted scenarios and stopped investigations are unchanged; all242requirements/417scenarios remain in scope.

No source integration blocker identified for this opt-in stage. Root should retain this exact review and final source/output hashes with the canonical manifest, complete its staged ownership gate and publish only owned reviewed paths. Do not upgrade any original ledger acceptance from this review.

## Recomputed identities

- `/home/charles/Warlock/implementation/warlock/adapter/cancellation_ledger.py`: `313165249e35ccf5f0f68bac7acb868d181a4bbd5daa1626c39c79b53b327981`
- `/home/charles/Warlock/implementation/warlock/adapter/cancellation_legacy.py`: `ad23d4e7c856120885625e8621887a4517acfcfc4d78b21a96986bd160a1ce86`
- `/home/charles/Warlock/implementation/warlock/adapter/recovery_store.py`: `3257927b706471357d7461b1f71935cb46dfe44b8f4e112418816eb49aaa22f5`
- `/home/charles/Warlock/implementation/warlock/adapter/daemon.py`: `a593494e4ca89ef467dced5cd946bc5eca9a88db21c591597c19eb2a80cdca31`
- `/home/charles/Warlock/implementation/warlock/qa/check-cancellation-store.py`: `20d07be554662f6f8399415c46865941474bd7a699f7ac3a27ab2096066ef1b9`
- `/home/charles/Warlock/implementation/warlock/qa/evidence/cancellation-store-20261030/store/report.json`: `4b0267b23650838302ec08a1741b9c790ff01429325f1d7c0dba8457f4210f62`
- `/home/charles/Warlock/implementation/warlock/qa/evidence/cancellation-store-20261030/model/report.json`: `dada4a52eec60fdabc67b951dc0d4f2956456906d03b885d51fa47a52b0f4056`
- `/home/charles/Warlock/implementation/warlock/qa/evidence/cancellation-store-20261030/provenance-repair-review.md`: `2bba0e722ada23ab357d7b7b7f4c2e711e29b3dd8ca410717afdaa5f1e92243d`
- `/home/charles/Warlock/implementation/warlock/qa/evidence/cancellation-store-20261030/provenance-stop.md`: `05bad8c2556865deb36985fb3598d547af30d674d8142b3127e311d68bac1bb5`
- `/home/charles/Warlock/implementation/warlock/qa/evidence/cancellation-store-20261030/LIMITS.md`: `8701b8c3d9693599c1ea6d2818b88e1f821ece154cf391ce7011417b827c6a62`
- `/home/charles/Warlock/docs/warlock/how-to/test-cancellation-store.md`: `54fe0486e03f591117086c6d9fcfba3764b2ccccc220fab00950bcbeda51a85b`
- `/home/charles/Warlock/docs/warlock/reference/cancellation-protocol.md`: `b5c4ac42488123f97c4dc7fa851fc5413d5c72a2b97ee7f73a53f4028e0c859a`
- `/home/charles/Warlock/docs/warlock/reference/status-and-evidence.md`: `2802a84ca36f75ebd3030e578318499884c6f3dd80abc074cf6eaf8b82cb6894`
- `/home/charles/Warlock/docs/warlock/explanation/ownership-and-lifetimes.md`: `815f3e64fe17ca1734cea1da70219817b5bedb58326e4ac7c36fe95452ac90ab`
- `/home/charles/Warlock/implementation/warlock/README.md`: `5026b3486a0a4a53fe84f5859909e2861ac18b66343a9024366e2656f88616a3`
