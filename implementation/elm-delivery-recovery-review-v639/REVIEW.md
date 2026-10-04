# V630 independent delivery-recovery review

Verdict: **changes required**. The persistence/anchor/wire design is consistent with V624, but repeated history delivery has a confirmed serial-scope liveness defect (`RECOVERY-639-001`, high).

## Confirmed counterexample

A retained frontend already accepted originA's release, while originB remains Unknown after a lost release. Both are historically Released in the broker. V630 announces the combined historical census A→B and serializes proof scopes. V619 `unknown` rejects an already locally released slot; `announce` requires an unreleased eligible slot. The first A proof therefore emits no `reconciliation-ready` or reads. Actual V630 stays ready=false, active=A and pending2; B remains unresolved and never receives its announced proof. Reversing the historical order so B comes first emits ready and demonstrates the source-specific obstruction.

New protected CPU evidence under qa:12 assertions, actual frozen V630 Reconciliation plus the held actual compiled V619 public controller. Baseline is a previously accepted A trajectory; we add a second exact-shaped origin with independent binding/intent and retain its UI Unknown across reconnect. Historical census and typed native proofs are synthetic fixtures. The compiled worker was hash-verified against V630's frozen manifest, reused and executed anew, not compiled anew. No actual store/native experiment is claimed by this counterexample.

Correction must let exact already released historical origins take an informational current proof/ready/read turn so the backend can advance, while retaining released status, Unknown history and all unrelated live reservations/counters. It must validate current/queried bindings, strictly newer proof sequence and exact current read correlation; proof/read/release must emit no automatic effect. Do not reorder or evict history as a correctness fix: any fixed ordering can encounter another already-delivered head on a later restart. A fresh frontend derivative is required; V619/V630 remain frozen.

## Confirmed bounded design properties by source review

V630 Reconciliation computes live entries plus Released historical records and refuses combined>64 before its first send or proof request. Every full Unknown precedes proof publication. Valid store snapshots guarantee record status/correlation; ordinary invalid synthetic snapshots are not a substitute for storage validation. The unchanged V626 publish_startup stages settlement/recovery/reconciliation before attached, releases storage locks, restores live callback, then flushes frames in preserved order. Thus the asynchronous C bind sees no startup filesystem lock held by Python.

For matching current accepted read domains/output, inherited release(join) returns only a durable Released disposition. Then exact V624 attest(join) conserves the original archive anchor and returns a new certificate after sidecar file/root synchronization. V630 wire includes precisely certificate id/proof/observation; anchorId stays local. The strict V619 decoder accepts a valid64-hex ID and correlated proof/contexts without expecting the original release ID. Invalid extra anchorId remains rejected. Current binding is checked after each persistence operation and before publication.

Neither release nor attestation invokes effects or changes Unknown to Committed. Attestation matches full record, not target alone, so a distinct live same-target origin remains live. Output failure after durable attestation does not undo archive truth; retry must acquire a fresh valid proof and accepted pair. Archived arrays and delivery sidecar remain bounded64/1MiB. Combined65 blocks even if each individual array has room; this is conservative fail-closed behavior, not S15 scalability.

## Source closure and evidence boundaries

V630's frozen manifest pins unchanged production sources to V626, added delivery_ledger.py exactly to V624, with only reconciliation.py/recovery_store.py changed. V630 explicitly has no complete GUI build. Its integration worker is compiled from held V619 source; copied GUI source differs at Desktop.elm. Source closure of each packet does not make those different frontends a coherent GUI release. Root's fresh640 derivative must merge the reviewed frontend with the backend and build one source tuple before native testing.

V630's existing C/filesystem/coordinator integration and compiled frontend controls are historical passes, not new639 filesystem/C runs. New639 executed only the counterexample trajectory and source/worker pins. Certificate durability fault coverage remains bounded; power loss, actual authenticated native transport, repeated real-daemon reconnects, same-view mixed delivered/lost histories and full coherent GUI behavior remain open. V629's proposed paged archive does not remove the current capacity limits or establish actual filesystem scaling.
