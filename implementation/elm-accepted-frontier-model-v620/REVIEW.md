# Accepted observation frontier: independent formal review V620

**V619's correction is confirmed in the bounded frontend protocol scope.** New requested IDs describe future replies. They must not erase the previous actually accepted post-proof action/geometry stamps, because the already-qualified backend release can be queued behind the final reply while that reply immediately emits a new batch. An actually accepted newer reply supersedes its domain stamp and makes an obsolete release refuse.

V614 remains frozen. Its `protocol.qnt:11` requires accepted IDs to equal latest requested IDs, while `ProcessRead` at line29 erases the matching domain acceptance. Those rules model backend latest-request registration but must not be reused as frontend release acceptance. The V614 `retryLatestActionInvalidatesTest` is historical evidence for that older rule, not evidence against V619's explicit replacement contract. V620 implements the amended frontend contract independently rather than silently changing that scenario.

Review of V619 `src/ReconciliationTracking.elm`:

- `requested` at line37 updates only the future request expectation, retaining `slot.action`/`slot.geometry`.
- `observed` at lines43–54 requires the previously expected request to be admitted by the public Shell reducer and matches the resulting observation/context. It does not require the resulting phase to be Ready; immediate dirty drain can legitimately leave it Reconciling.
- `release` at lines66–74 builds Expected using stored accepted IDs and complete contexts rather than pending IDs, and checks the announced proof independently.

V619's existing tiny model covers those nine bookkeeping trajectories. V620 adds explicit independently correlated per-domain IDs, revisions, output and proof stamps; separate future expectations; pending-domain availability; and an ordered bounded wire queue. Its16 selected scenarios cover final action/geometry drain, pending request preservation, actual newer acceptance in each domain, matching latest pair, stale inadmissible reply, exact context, different outputs, next/duplicate proof, durable prerequisite, missing geometry, explicit action gating and FIFO final reply→release→next reply.

The FIFO witness queues the final geometry reply and durably qualified old-pair release. Delivering the final reply accepts its stamp and drains notifications into new requests3/4. Even if a next reply is appended immediately, the already queued release is delivered first and removes only the live reservation. Pending reads still block a new explicit action. Once a genuinely new reply has been accepted, a separately tested obsolete release is rejected. Release, reads and drain emit no automatic effect; historical status remains symbolic Unknown0.

## Evidence and scope

Final protected CPU campaign passed **16 actually executed named scenarios**, **1,000 sampled traces bounded to40 transitions**, and **nine typechecked mutants**, all failing their targeted actual assertions. Mutants cover acceptance erased on request, release requiring pending IDs, final drain discarding acceptance, ignored newer action/geometry stamps, automatic release effects, pending explicit actions, context weakened to ID equality and reversed FIFO selection.

`qa/report.json` records exact selected/executed names, commands, version, seeds, source and output hashes. Accepted named ITF traces are retained. Model mutations must typecheck and fail by actual assertion. Initial reserved-name parser failures and the first mutation API error are retained with original sources/logs under `qa/failed-*`; their failures are not successful negative controls.

Transport FIFO and serial backend reply+release production are assumptions supplied by the integration owner: native request arrays enqueue via push-tail and are processed pop-head with one active request; the daemon consumes the newline stream serially. The integration owner reports native618 stopped at startup before any behavioral case because of the separate asynchronous C-bind/host-writer lock race; the626 startup correction and627 native rerun remain outside this scope. No claim here treats that failure or coordinator CPU controls as native FIFO acceptance. This component does not exercise the carrier or daemon, or compile/re-execute the51 V619 frontend cases and13 compiled mutants. Those results are historical ancestry, not new V620 execution.

The durable prerequisite is an explicit Boolean abstraction. V605 fsync/restart and V614 ready/enqueue rules remain separate unchanged components; V620 does not rerun them or establish whole-model composition. One symbolic exact reservation and proof scope are modeled, not64 per-record journals, multi-origin collision or binding/parser authentication. No delivery loss, reconnect recovery, restart/power-loss, native GUI, hardware, frontend JSON decoding or storage campaign is performed. In particular this work does not resolve the delivery-loss624 lane.

Reproduce CPU only:

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B /home/hoskinson/omarchy-windows-parity/implementation/elm-accepted-frontier-model-v620/qa/run.py
```
