# Reconciliation ready acknowledgement and queued reads

V614 composes a pure typed protocol reducer (`protocol.qnt`) with the byte-identical V605 durable reducer (`release.qnt`). The V605 source, tests and manifest are retained under `qa/ancestor605`; V605 itself is unchanged. Integer tags represent the exact wire contract: version3, kind1=`reconciliation-ready`, current binding2, queried old binding1, and active proof request ID1..16. These are symbolic binding identities, not a wire parser test.

The frontend first receives an announced proof, enqueues its exactly correlated ready acknowledgement, then enqueues fresh action/geometry reads. Read entries retain their enqueue scope, session domain, output, unique ID and whether ready had already been enqueued. Backend processing is separate. Processing a ready acknowledgement enables qualifying subsequent backend registrations; a read queued before acknowledgement cannot qualify even when its backend processing occurs after ready. Its delivered reply remains an ordinary observation. Backend processing earlier than acknowledgement does not retroactively qualify a reply.

Next announced proof clears ready, delivery/enqueue state, both expected IDs and both accepted replies. A duplicate announcement or ready acknowledgement does not clear fresh accepted replies. Processing a newer request within either read domain replaces its expected ID and invalidates that domain's earlier acceptance; late replies cannot restore stale acceptance. Both domains must match their latest distinct IDs, current scope/session and output before the durability path can start. Release additionally requires V605's durable Released stage and runtime root fsync barrier.

An active scope can authorize the modeled cohort of up to64 Unknown records while at most16 unique proof request scopes can be announced. The cohort count abstracts away individual record identity: it tests capacity and shared-proof fanout, not64 independent filesystem journals, duplicate record accounting or persisted wire payload correlation. The unchanged V605 ledger represents one exact admission/retirement proof. Multi-scope filesystem records must be independently joined by the real coordinator; this abstraction does not establish journal reassociation correctness across scopes.

The production transition set `tick` includes protocol events and gated V605 durability events. The `raw` helpers are test-only setup/negative witnesses: they establish a pre-existing durably released journal to ensure unannounced protocol state still cannot emit a release, and exercise every fsync boundary while retaining protocol state. They are excluded from sampled transition selection.

Final protected campaign passed **55 actually executed named scenarios**, **2,000 sampled traces of at most80 transitions**, and **seven typechecked mutants**, each producing an actual assertion failure. This is newly executed V614 CPU evidence; the36 inherited scenarios also ran here, rather than being counted solely from prior receipts.

Parent reports the implementation transport preserves FIFO: native `surface_receive` enqueues request arrays in order via `g_queue_push_tail`, `write_next` serializes one active request and pops the head, and the single-threaded daemon handles `FrontendFrames` in newline-stream order. Frontend ready is emitted before fresh reads. These implementation facts were supplied by the owning integration lane; this component independently models the ordering requirement but did not re-execute that transport or its native journey. FIFO transport remains an explicit implementation correspondence assumption.

Evidence uses exact selectors for all36 V605 scenarios and19 new protocol scenarios; commands, Quint version, seeds, execution identities, source and log hashes appear in `qa/report.json`. Accepted named ITF traces are retained. Sampled traces use seed61402, max80 transitions, TypeScript backend. Typed mutants must fail actual assertions, not merely parsing or typechecking. Initial parser/typechecker and composite-wrapper failures are retained under `qa/failed-*` with their original sources and logs.

CPU abstract validation only: successful fsync is an assumed transition, and native proof structure/authentication/native sequences are inherited abstractions. This does not prove the actual frontend uses FIFO transport, that backend queue scheduling preserves enqueue provenance, that a particular parser rejects invalid JSON, or that real filesystem errors/restarts/native observations behave as modeled. No native campaign, shared source/ledger edit, desktop action or commit occurred.

Reproduce through the protected launcher:

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B /home/hoskinson/omarchy-windows-parity/implementation/elm-reconciliation-ready-model-v614/qa/run.py
```
