# ARC007 output transition and exact late receipt: baseline disposition

Disposition: DEMONSTRATED CURRENT-PRODUCTION ELM RECEIPT BOOKKEEPING DEFECT supporting original ELM-ARC-007 / receipt-committed. This is an actual compiled production reducer/controller route with injected bridge messages, not evidence that native delivery occurred in this order and not original-scenario acceptance.

## Exact retained evidence

Baseline directory: native-rebuild/receipt-output-current-cpu-1793332444826191664.

- report.json: e458fbb9242bc5888ccf85bc24eef6981bf1b48857831b3c4037853535bb8577.
- receipt-output.json: d00e7ad6c5f0d788953d35a377c55b4a04c8bb8100cf99f3f6b083bc3bebbf4a.
- Private witness: 8bacc0a9f6d4eed8b6a6e26a1ffd374336812e320b37f3995e5eabde4a1aea2b.
- Private diagnostic driver: 45b17b2aa2ed896087e74702166c016eb8eef2b4f71c53e39b4aeae1c3bd6505.
- Existing three-root receipt, revalidated before/after rather than rebuilt: 65b909422a1866a9df8f118b134ea42778fd69564aed070bdb92c0975f3818d8.
- Effects.elm: 873e8824d90828a9927cfd89723c7b7299e11791e3779173815ba720b11a8547.
- Shell.elm: f14b7fe3bfbf1a57f335f98914c988938c235823ba4596c067cf744776c4a9ae.
- OutputController.elm: aaf1729287ff61595a237201b261e7c1ce11c8f2353c620171f48aff99d86f38.
- NativeOutcome.elm: ffb20d47827d29653552d9a5c7f552491473b8df1cd336e00cc036816ae8b396.

Report records passed=true, all six reachability controls true, coreLimit=1, and protected qa-harness-e9a42453172f4dab9959e764326c6cfe.scope. Root identifies terminal invocation 8d41f26bc09c4026a165bee8ede47bb7. This reviewer read sources and retained output and rehashed identities only; no QA or edit was performed.

## Reached production sequence and original oracle

The original receipt-committed scenario requires the uniquely correlated request to have exactly Committed and no other request to change. architecture-007 separately requires Unknown when final effect cannot be proven after a connection drop. These requirements distinguish request evidence from present scene authority.

The actual witness constructs valid Fixture.base, captures the current Shell stamp and issues Minimize incarnation1 through Outputs.Interaction → Desktop.Window → TaskbarShell.Native → Shell.Act. One actual window-effect is emitted and the exact request/generation1, incarnation1, protocol1, output1 transaction and unresolved entry are Pending; issued count is1.

Accepted newer topology removes selected output1 and keeps output2. OutputController dispatches SupersedeObservations True despite Pending. Fixture.reconcile sends the actual newly expected projection request under the same binding/lifetime/epoch with output2. The guard confirms output2 was admitted; current transaction becomes Unknown, its unresolved counterpart remains Pending, and issued remains1.

An exact original protocol/binding/full-intent Committed passes NativeOutcome and Shell.issued correlation. Actual late state is transaction Unknown, unresolved=[], issued=0, expected projection3. The positive same-authority control commits; wrong-request control preserves Effects; topology/late receipt emit no new window-effect.

This is not justified conservative Unknown retention: the route consumes the exact terminal outcome and removes its own reservation while refusing to record that outcome on the still-matching current transaction solely because present observed output differs. The current transaction continues to carry the old intent, so its status is request evidence, not an assertion that the current scene or output is committed. Effects' source comment explicitly says terminal receipts change request state only, while scene changes require snapshots. No false native commit, automatically replayed action, lost bytes, renderer defect or changed host authority is inferred.

## Minimal correction and preserved boundaries

In Effects.apply receipt handling only, use `transaction = Maybe.map settled model.transaction` instead of conditioning that map on observed sameAuthority. settled already checks both effectProtocol and complete intent equality. Retain found-in-unresolved, supported protocol and operation/protocol gates, Shell binding/issued correlation and NativeOutcome validation. No scene, identity, counter, snapshot, disconnect, recovery or transport changes are needed.

Do not normalize all unresolved Pending entries during snapshot in this correction. That adjacent representation difference is retained baseline evidence, but validated recoverUnknown has its own route and must not be changed incidentally. Do not admit Cancelled into NativeOutcome: its reported false shape result is a separate channel/owner question. No change to no-replay or current-output action eligibility.

## Model correspondence

Read actual qa/output-retirement.qnt, transfer-workspace.qnt and empty-workspace-navigation.qnt. The first has topology/popup ownership and mutation count but no receipt records. The second has a single pending/unknown abstract status and abstract commit, with no keyed current/unresolved split. The third has one navigation status and native recovery, not the Effects record set. Their existing passes cannot prove this correction. Quint2's preserved DELTA-REVIEW reaches the same bounded coverage conclusion.

A minimal two-key/two-output model should explicitly map current optional transaction, unresolved records, issued full key/binding/protocol, observed output/scene and emitted-effect count. Output change maps only a Pending current transaction to Unknown as production does now. Exact receipt updates/removes its own unresolved entry and updates current iff keys match, regardless of current observed output. A newer different current key stays unchanged. Wrong/duplicate receipts are no-ops; Unknown retains its reservation; validated proof release is distinct from a terminal receipt. Model receipt authority as an explicit assumed authenticated/exact envelope predicate; do not claim to prove native transport authentication or JSON decoding. Preserve a legacy-output-gated variant so the original reached sequence exposes the status defect. Run/verification belongs to root under the selected scope; this review claims no model execution.

## Expanded executable regression routes

- Same-output exact Committed, Refused and Unknown controls.
- Real topology/output transition plus exact late Committed and Refused: matching current status becomes the exact terminal status and only its unresolved/issued record is removed.
- Exact late Unknown: matching current and unresolved statuses are Unknown; issued reservation retained; no mutation replay.
- After output transition, issue a legitimate newer Minimize incarnation2 through Shell.capture/Act. Old incarnation1 Committed/Refused/Unknown affects only its old record; newer full transaction, its unresolved/issued record, observed scene and request/generation counters stay unchanged.
- Wrong binding, protocol, request, generation, incarnation, operation and each context field do not alter correlated Effects/issued state or emit a window mutation. Allow independent decoder-refusal diagnostics to change when testing invalid envelopes.
- Duplicate terminal receipt is inert after original resolution. Every receipt path preserves observed scene and effect watermarks; subsequent read-only projection requests are permitted.
- Disconnect with no authoritative terminal proof remains Unknown. Preserve the separately validated Unknown recovery/release route and no replay.

Use real Outputs/Desktop/Shell entry points, not manually edited Effects records. Capture outputs from projection admission as well as topology/receipt if asserting no effect across the complete trace. Keep source baseline evidence immutable; await reviewed private model and expanded tests before applying the one-line product correction. Fresh optimized roots and applicable current receipt/composition review are required after any product source change.
