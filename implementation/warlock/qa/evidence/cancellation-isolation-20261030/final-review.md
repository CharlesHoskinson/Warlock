# Expanded final cancellation isolation / namespace-owner review

Reviewer: roadmap-fidelity. **APPROVE bounded opt-in source integration of the exact six-module tuple below; no remaining concrete source blocker identified in the reviewed fixes and retained component evidence.** This fresh review expands and supersedes the applicable scope of prior4dcc7329; that older approval alone did not cover these repairs. No QA/model/import/compiler/native action was run and no public file was edited. Root owns staging, canonical evidence, documentation reconciliation and publication. No original ARC007/008/012/013 or native/release acceptance is granted.

## Exact current source and previously reproduced defects

Independently rehashed current ledger94dc5b03, helpera1190f6b, reconciliation6cd8c55f, journalba70923c, coordinatordda41b74 and daemon609d43. Both actual prior REDs remain relevant: typed cancellation admission could enter legacy proof/read release and be unlinked before V7 save rejected missing typed custody; defaultV6 opening a V7 namespace could import typed Pending into the supposedly frozen predecessor, making later V7 reopen fail. These are observed store/strict-proof-double defects, not demonstrated compositor mutations or arbitrary forged-proof exploits.

I read the changed source and the new real production-route case files. The fixes address side-effect order rather than merely catching a late validation error.

## Full-key cross-lane isolation

`CancellationLedger.release` validates the real ObservationJoin and checks the legacy record key against ALL retained typed admissions under host_guard BEFORE `_sync`, saving Prepared release or unlink. The key is actual effectProtocol+binding+full intent; the deadline/certificate have additional typed validation but are not falsely described as extra components of the legacy key. Same-window/different-full-key legacy work remains possible.

The `_remove_admission` override independently rejects typed full keys before calling the inherited unlink. This covers parent `_finish`/legacy `_sync` and intentional parent-method bypass. The helper's V7 validator rejects ANY legacy Prepared/Released release whose key collides with a typed record before restart cleanup. Therefore a corrupt persisted Prepared collision cannot reach unlink merely because the public entrypoint was bypassed. This is defense at admission, validation and side-effect boundary, not a broad rejection of all work on the same incarnation.

`legacy_reconciliation_records` excludes typed keys from the legacy projection; `Reconciliation.announce` uses that method where available and preserves the original V6 fallback otherwise. Consequently typed records do not elicit legacy grant-retirement announcements. They remain available to the separate cancellation recovery DTO. Genuine legacy release still follows exact proof/read joins and original historical evidence. Typed certificate finishing remains the explicit active-V7 certificate path and does not invoke this prohibited legacy retirement route. No alternative inherited delivery path creating a Released typed anchor was identified; attestation requires an existing valid Released anchor, while collision validation now rejects such typed anchors.

## Under-lock namespace ownership

The Journal guard runs after actual namespace writer.lock verification/flock and BEFORE `migrate` or mutable legacy constructors. A non-supporting class refuses if EITHER ledger-v7.json OR initialized marker exists. Non-following stat means dangling symlinks and nonregular names count as ownership presence and fail closed; malformed/partial state does not silently select a legacy migration. Only the explicit internal CancellationLedger class advertises support. This is internal source capability selection, not an arbitrary user/JSON authorization or cryptographic class assertion.

The guard preserves V7 predecessor/admission state on omitted or false mode, while clean V6 and a separate lifetime namespace remain usable. It adds no relock gap, old-constructor dictionary graft or automatic cleanup/downgrade. V7 constructor still holds its writer lock and explicit host guard for bootstrap/current-state validation.

## Actual latest evidence checked

Store actual report23bc4259 has nine exit0 groups: base36, typedrestart9, positive provenance23, faults99, capacity239, new legacy isolation33 and namespace ownership33, plus structured ordinary-restart and provenance-negative outcomes rather than invented aggregate counts. I independently checked EVERY report input against current source and all18 stdout/stderr hashes; no mismatch. Read actual33 isolation checks include genuine V6 and V7 legacy positives, same-window/different-full-key positive, direct typed release and central unlink negatives, parent bypass and corrupted Prepared restart. Exact typed Pending bytes and V7 bytes remain preserved on rejection. Namespace33 checks use real V7 Prepared/reopen/default and explicitfalse attempts with full file-byte snapshots, successful V7 reopening, direct Journal bypass refusal, file-only/marker-only/symlink/directory/FIFO controls, clean V6 and separate-lifetime positives.

Coordinator actual report0c441c24 has three exit0 groups140/52/110 on the expanded current dependency tuple. I independently checked every input and all six stdout/stderr hashes; no mismatch. This retains actual store ordering/grant/duplicate/fault checks and daemon default/explicit mode selection, detach-before-store-close, historical startup/direct dispatch. Strict native-schema responses and inert services/events remain doubles. The daemon main checks stop at startup publication; a full event-loop/EOF/native session is not inferred. Poisoned coordinator calls stay fail-closed, with standalone close obligation and actual daemon ExitStack cleanup intact.

Q5 FINAL-CORRESPONDENCE was read. Root cross-lane model report83100c6b has21 exit0 commands:13 explicitly selected named witnesses, executable init/typecheck and four bounded invariant samples1000traces/max30steps/seed20261030 (plus tool version). I rehashed every retained command stdout/stderr; no mismatch. The model separates legacy versus typed certificate unlink and witnesses the intentionally broken ordering outside normal step. It abstracts three opaque keys/proofs/filesystem state; it does NOT establish real proof production, actual schema/JSON/locks, transport, native no-replay or the constructor downgrade fix. Downgrade correspondence is separately source plus actual namespace checks, not retroactively attributed to that model.

## Approval limits and publication gate

No remaining concrete blocker found for this optional internal stage. Final canonical packet must pin these new source/reports/reviews, not reuse old4dcc7329 as complete approval. Documentation should state V6 default is only for a legacy-compatible namespace: any V7 ownership file/marker requires its owner and refuses downgrade before migration. Explain full-key legacy exclusion and retain both REDs and byte-preserving negatives. Root is refreshing these docs separately; this source review does not assert unseen final prose is correct.

Normal-host C deadline origin/companion admission, distinct typed settled/recovery DTO consumption, Elm lifecycle, actual native transport, per-generation custody/resources and physical Escape remain open. No generic legacy admission-retire may serve typed companion keys. Strict retired-grant/read doubles are not evidence that actual native cancellation was still Prepared simultaneously; the store safety rule applies even if a valid native retirement occurs before its certificate is observed. No power-loss/all-filesystem/hostile-writer/universal proof is claimed. Full242requirements/417scenarios and retained stopped investigations remain unchanged. No original ledger acceptance follows.

## Recomputed identities

- `/home/charles/Warlock/implementation/warlock/adapter/cancellation_ledger.py`: `94dc5b03dd3e513703dec2a705271178b4ff45ea319d0831a70517613fee7a05`
- `/home/charles/Warlock/implementation/warlock/adapter/cancellation_legacy.py`: `a1190f6bcf47790ab5b447296836c94bec1df5ee5d061f146cad7d2c3aa2e6d0`
- `/home/charles/Warlock/implementation/warlock/adapter/reconciliation.py`: `6cd8c55f627528e6197e4bda4cff2e21776991833a78ec8ed29a400b22f3aceb`
- `/home/charles/Warlock/implementation/warlock/adapter/recovery_journal.py`: `ba70923c01e9dabaca4d4cf1ae9c4e57f6227c9eb414d4a212c486f21edfbfe7`
- `/home/charles/Warlock/implementation/warlock/adapter/cancellation_coordinator.py`: `dda41b74eeb6f350a598b19f1c2022a117f63c71316144f7488873e79fc904f2`
- `/home/charles/Warlock/implementation/warlock/adapter/daemon.py`: `609d43a35c5f32e1354cdca4744f876fe4d462328826dadfff66cfb581690884`
- `/home/charles/Warlock/implementation/warlock/qa/runs/cancellation-store-1793353307927602074/report.json`: `23bc4259f840952a39c319637e40cb6deb16140f4a45f41f556f030c8689a489`
- `/home/charles/Warlock/implementation/warlock/qa/runs/cancellation-coordinator-1793353462114971926/report.json`: `0c441c24b455f533004b4a372a83e9a67e4b365e538c27c48adf1cfe161fbccd`
- `/home/charles/Warlock/implementation/warlock/qa/cancellation-store-cases/legacy_isolation.py`: `f7e087249291d73e5acaebe3b4c48b6f6b45c7e6791b36b445e9d5444bbb773f`
- `/home/charles/Warlock/implementation/warlock/qa/cancellation-store-cases/namespace_ownership.py`: `5b6030351b54e0ba0926e637827e62fc7917aa30a4c7a67d19dc7493ac731b0f`
- `/home/charles/.local/state/warlock-team/20261028/native-rebuild/model-review/quint-5/cancellation-crosslane-current/FINAL-CORRESPONDENCE.md`: `7270da0d1e526b006c0ae13120c038d3a003df18a71fdf6c9fabfbe581c66fc3`
- `/home/charles/.local/state/warlock-team/20261028/native-rebuild/cancellation-crosslane-root-v2/model-1793352464256569445/report.json`: `83100c6bd7da6e7784ff4929abe89a98b0c0ed757c3c03082a57d53934e7914c`
