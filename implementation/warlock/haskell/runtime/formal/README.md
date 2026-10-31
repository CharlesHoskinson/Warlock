# Current-registration correspondence model

This bounded model accompanies the current Haskell `CurrentSessions`, `ScopedPeer`
and `CredentialScopeGuard` integration. It separates peer checking from final
admission, ordered replacement from delayed old publication, and callback draining
from reaping. Two symbolic registration identities and generations 1–2 model the
monotone high-water rule and exhaustion without claiming full Word64 exploration.
The atomic replacement action abstracts the real authority→registration→Scope
lock order. Kernel credentials, process identity, owning thread, executable and
endpoint checks remain opaque premises; symbolic CrossUser is not an actual UID
trace. Callback completion is subsequent policy validation, never a native effect.

## Run the checks

Use the unchanged protected CPU launcher with pinned Quint 0.33.0. Typecheck both
files, then select the 23 named `run` tests individually with anchored `--match`.
Run `current_registration.qnt` using `--invariant safety --max-samples 10000
--max-steps 30 --seed 20261031`. Keep failures and full traces. No Apalache or
exhaustive model checking was run. `nearExhaustion` is an explicit bounded fixture
in the modeled step, not an observation of a real generation counter at maximum.

The qualification records 23 passing directed tests and a seeded sample, then a
stronger observer and four affected directed tests plus another seeded sample.
Root corrected an actual Quint zero-argument value/call type error before any
successful result. Root also found that the old invariant only constrained a
nonempty current registration: clearing current while a newer scope remained live
escaped that observer. `liveIsCurrent` now checks the converse; `oldCleanupMutant`
must violate the combined safety predicate. The production old-cleanup route had
already passed its real-child test; this was a model-observer defect.

## Read the evidence

[qualification.json](qualification.json) pins model sources and retained machine
reports. Public model headers differ only in comments from the qualified private
Rootv3 source; no transition or assertion changed. The five deliberate broken
policies are excluded from normal `step`; their directed assertions expose unsafe
states rather than asserting that actual production code contains those policies.

All 11 sampled aggregate state witnesses were nonzero, but only seven traces
reached a checked peer, three reached a claim and two reached callback delivery.
Those are aggregate state counts, not action coverage. Directed positive paths
are necessary alongside the sample. Idempotent retirement/presentation and the
bounded setup remain in the transition system; no fairness, progress, kernel,
full asynchronous teardown or persistent GUI proof is claimed. This is supporting
formal evidence, not original-scenario, native-effect or release acceptance.
