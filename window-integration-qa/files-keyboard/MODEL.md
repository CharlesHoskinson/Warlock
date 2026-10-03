# Files keyboard and action authority model

`keyboard_focus.qnt` requires prompt trapping, independent list/grid peers, captured path authority, hidden/disabled/stale action refusal, editing precedence and reload focus restoration. Random commands remain unfiltered; modal rejection occurs in the transition.

The final model passes 21 named scenarios and 2,000 samples of 100 steps with seed 20260930:

```sh
quint test keyboard_focus_test.qnt --seed 20260930
quint run keyboard_focus.qnt --invariant allProps --max-samples 2000 --max-steps 100 --seed 20260930
```

Four file peers retain separate paths and epochs independently of keyboard selection. Current and stale generations are generated dynamically after rebuilds. Sidebar/Home authority uses each peer's captured path; prompt payload is captured on opening. Media rebinding requires retirement of the previous logical peer, while a retained current QObject naturally exposes its current semantics.

Deferred restoration is tied to reload request and input/focus epochs. Named scenarios cover normal materialization, newer toolbar focus, Tab, modal focus, hidden windows and a superseding reload. The first delayed model missed prompt intent, allowing Materialize to restore background focus: the model/source, failure log and ITF trace are preserved as `model-delayed-invariant-*`. Its corrected transition counts focus-changing commands as newer intent and verifies current modal scope. Historical initial/review model versions remain available.

Model reports: `model-named.log` and `model-seeded.log`. Actual Qt replay is separate: `guard-stage/retained-probe/report.json` records ordinary and hidden same-PID reload plus newer toolbar/Tab/prompt cancellation. These offscreen observations do not prove physical compositor input or Orca compatibility. The copied native reader runner remains pending a root-coordinated slot.
