# v630 handoff

Accepted protected integration report:
`qa/integration-1791152781571263529/report.json` — 36 checks.
Accepted public v619 replay report:
`qa/tests-1791152811827803535/report.json` — 51 checks.
The earlier integration development run is retained as superseded evidence.

The packet copies v626 production sources and adds exact v624 delivery_ledger.py.
Only adapter/reconciliation.py and adapter/recovery_store.py change existing
production files. The copied GUI stays v626; the CPU frontend probes explicitly
compile held v619 source. This is a broker integration prerequisite, not a native
GUI release tuple.

`qa/integration.py` tests C-produced admissions, lost output, explicit store reopen,
same-controller reservation recovery, actual durable certificate publication,
unrelated live reservation conservation and a sidecar fsync failure. Its full
event sequences, controller rows, original release, lost wire and fresh
certificate are preserved. `qa/public619.py` is the owned replay driver; its input
selection targets v619 source. Its retained `run-source.py` is the copied baseline
driver reference, while the executing driver itself is bound by this component's
source inventory.

Before a future GUI/native campaign, build one coherent accepted frontend/backend
tuple and revalidate ABI, process ownership and all original behavioral oracles.
Do not load this copied GUI as a claim of that qualification. Do not rewrite old
proof records or outcome history to deliver a new certificate.
