# Provisional route presentation guard prototype

Offline only. The original unsafe prototype and root counterexample are preserved, plus v2 files before the bounded ledger correction. This version has27 actual JS scenarios,8 presentation formal named scenarios and5 handoff formal named scenarios and2000×100 randomized states. `offline-report.json` records commands, complete output and exact source hashes.

An output may present an earlier in-flight submission after a newer submission, provided its sequence and time exceed the last actually presented frame and its identity/token/topology/digest/rectangle match the retained submission. Each output retains128 submissions; safely evicted frames cannot authorize readiness. Presentation consumes that frame and all older submissions. Submission sequence/time high-water marks survive consumption. Explicit field equality permits reordered rectangle/native proof objects while requiring identical finite numeric geometry.

`submit` and `present` are internal trusted renderer probe interfaces, not external IPC shape validation. Observed frame metadata must be tied to the synchronized render submission and actual frame sequence. Neither a caller-provided digest nor these pure JS tests proves actual GPU pixels. Native pixel replay and Qt frame telemetry remain required before integration.

Run `node test_global_route.js`, `quint test presentation_test.qnt`, and `quint run presentation.qnt --max-samples=2000 --max-steps=100 --invariant=allProps --verbosity=0`. No service or QML integration/deployment has occurred.

## Visible origins and handoff

The source38ef and root visible-origin counterexample are preserved. A computed tick that has not been presented cannot become a reversal origin. `reserve` and visual rollback require a current matched presentation for each participant and an empty old in-flight submission ledger. The coordinator must atomically stop old submissions during the handoff; without that barrier or Wayland presentation observations, integration is incomplete. Missing/undrained participant evidence rejects reserve; it does not invent an origin or drop the native latest intent. A future service adapter must preserve that native intent while obtaining a current visual handoff.

Each fragment retains its own latest observed rectangle and interpolates from it using one shared progress clock. `rectForOutput(output)` is the expected geometry for that output; `current`/`from` are destination-output references, never evidence of all displayed fragments. Whole request token grammar is validated before parsing its strictly newer safe integer sequence. During asynchronous handoff, differing output origins may produce temporary fragment geometry differences; actual seam/cadence acceptance remains a native integration gate.
