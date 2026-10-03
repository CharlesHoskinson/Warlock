# Bridge and native effect-boundary proof of concept

CPU-only executable Quint 0.33.0 model. The final run passed **18 explicitly selected named tests** and **2,000 sampled traces of 40 transitions**. Nine deliberately defective derivatives failed their targeted tests, with retained ITF counterexamples. These results establish bounded model behavior, not native execution, latency or completed Elm implementation.

Run `python3 run_bridge.py` from any directory. The runner wraps every Quint process with the protected QA launcher and records exact commands, seeds, version, source/log hashes, exit codes and ITF traces in `receipts/manifest.json`. Do not overwrite accepted evidence in later work: create a new output directory or preserve the existing campaign first. Each generated mutant is clearly separate from the correct `bridge.qnt`.

The model has one pending effect slot, two sampled request identities, native epoch, window incarnation, dependency revision, sequence watermark and gap barrier. A coherent snapshot releases the barrier; it never changes an existing captured request into a fresh request. Commit rechecks identities and the original monotonic deadline. Cancellation and commit each occupy one atomic linearization point: cancellation first prevents commit; commit first is final. Missing committed receipts become Unknown rather than permission to replay. Retired request identities remain tombstoned in the model. Dependent dispatch requires Committed with current epoch/incarnation/revision and no barrier.

Named cases cover fresh admission, separate incarnation/revision/epoch races, restart, missing sequence, snapshot recovery, both cancellation orders, deduplication, expiration, all five dependency outcomes, stale prerequisite identity and lost-receipt replay prevention. Mutation tests remove epoch, incarnation or revision checks, ignore gaps, drop cancellation, disable deduplication/deadlines, treat Unknown as permission or admit a stale prerequisite.

## Architecture correction discovered

The first experiment's incarnation mutation survived because `replaceWindow` also changed the global revision. Its stale-revision guard masked the missing incarnation guard. `attempt-1-masked-incarnation/` preserves original logs, manifest, ITFs and byte-exact original source/runner/mutants verified against its stored hashes. The corrected experiment changes the incarnation independently, modeling a reused address whose per-window revision can be equal. Both direct-effect and prerequisite-incarnation mutations now fail. An independent native epoch change also tests the effect boundary before a frontend restart receipt is observed.

This is a concrete reason to avoid making every race fixture change every identity at once: separate epoch, incarnation and dependency-revision fixtures are necessary for meaningful guard coverage.

## Mapping into Elm and modern FRP

Use immutable records and custom types: `Outcome = Pending | Committed | Refused Reason | Cancelled | Unknown`; wrap canonical string authority IDs in distinct `Epoch`, `Incarnation`, `Revision` and `RequestId` types. The model's integer identity tokens describe equality only; production JS/Elm transport must preserve canonical strings and reject JSON numeric identities.

Each model action maps to a typed `Msg` handled by pure `update : Msg -> Model -> ( Model, Cmd Msg )`. Model guards produce immutable next state and explicit effect descriptions. `Cmd` may publish a validated intent or request observation, but must never imply a successful native mutation. Native `Sub` observations/receipts update committed truth. Effect-boundary `commit` belongs to native authority; reproducing it inside the Elm reducer cannot establish native correctness. Ordered subscription events retain gap detection and cancellation/control order. Dependent commands are emitted only after matching committed prerequisite observations, never through an unordered batch.

Replay ITF counterexamples as typed Msg fixtures for the eventual Elm reducer, then compare states and effect descriptions. No Elm reducer is compiled by this prototype; that cross-language conformance proof remains an implementation task.

The `safety` invariant rejects recorded unsafe commits and dependencies and requires effect count to match unique committed identities. Named assertions additionally check exact statuses and no-effect obligations. Sampling is not exhaustive formal verification or a liveness proof. The model assumes coherent snapshots and authenticated receipt inputs; it does not prove decoders, socket authentication, bounded queue mechanics, native threading, GPU ownership or real timeout measurements. IDs are finite in sampling, while clocks/generations are abstract increasing integers. The real service needs bounded caches plus persistent retirement/monotonic identity rules; this model does not prove cache eviction behavior.
