# v617 handoff

Owned QA derivative of v615; production adapter/native sources are unchanged.
Run `qa/test.py` through the protected CPU launcher. The accepted report is
`qa/tests-1791150400922859665/report.json`.

The failure control deliberately stops at the first release frame, after its
durable write, so the other member remains Unknown. It then reopens the real
store and checks exact admissions, retained history and recovery frames. It does
not infer an effect outcome from failed delivery.

This is an implementation control packet, not native GUI acceptance. Future
integration must bind the reviewed authority/core ABI and frontend receiver to
one release tuple and repeat the supported recovery journeys there.

`qa/freeze.py` validates every copied production file against v615, binds the
passed report and inventories all regular source/evidence files. Preserve this
packet unchanged after freezing; use a fresh derivative for changes.
