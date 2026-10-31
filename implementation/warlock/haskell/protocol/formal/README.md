# Handler admission model

These files preserve the reviewed, executed v9 model without modification. They
map the public gate's local callback admission and retirement to a shared-state
machine: 64 admitted callbacks, 128 retained reasons, normal/exception accounting,
retirement draining and the distinction between one's own lock and another
caller's lock. Tokens are ghost callback identities, never public capabilities.

Quint 0.33.0 typechecked both modules and executed all 23 individually selected
directed tests, including excluded broken variants that must demonstrate their
stated failures. A seed-20261031 run explored 10,000 traces of 200 steps without
observing a safety counterexample. This is sampled evidence, not a theorem.

The aggregate witnesses were observed in 5,034 traces for admission, 1,759 for
callback entry, 5,012 for draining, 1,782 for retirement after work, and all 10,000
for the reason bound. **Busy was observed in zero random traces.** Its saturation
path was exercised separately by directed model and actual Haskell 64-slot
controls. Do not label the random workload complete action coverage.

The model assumes decoded/current-binding input and finite state publication.
It does not prove Haskell heap behavior, actual lock scheduling, raw-byte parsing,
authentication, native effects, global epochs, original effect deadlines,
duplicate-request prevention or liveness. Own-lock safety is a guard/mutant
correspondence check, not independent scheduler instrumentation. The observer
proposal's stale prose about mode representation does not change the enum model.

Exact source and output hashes are recorded in [../qualification.json](../qualification.json).
The local immutable execution report is
`arc004-handler-quint-1793441133087543802/report.json`. Earlier v8 source and its
fidelity findings remain frozen; no earlier failure or native STOP2 is reset.
