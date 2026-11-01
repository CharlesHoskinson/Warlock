# Correlated desktop receipt states

The running Elm path represents `Pending`, `Committed`, `Refused`, `Cancelled` and `Unknown` separately. A valid, exactly correlated `Cancelled` outcome now reaches the existing menu cancellation state; it retires only that request's local issued, unresolved and menu reservation entries. It does not establish that a native operation was physically prevented or its helpers retired.

`Pending` is created by local request admission. It is not accepted as a terminal native wire outcome. A connection loss with no proven final effect leaves the request `Unknown`; reading current observations does not authorize replay. A matching terminal for an older request leaves the current unrelated request unchanged.

## Source contract

`NativeOutcome.elm` retains its strict protocol-3 schema, protocol/operation check, canonical positive counters and bounded reason. `ReceiptRouter.elm` retains full native binding, effect protocol and full intent correlation, then maps `Cancelled` to the existing `Menu.Cancellation`. `Shell.elm`, `Effects.elm` and `Menu.elm` remain the existing state/ownership authorities. JSON parsing does not authenticate a sender or issue a native execution certificate; callers still require the authenticated bounded channel.

The changed source is `01ad95b87c7550c8179fd13e907625a5a9b57cb4`. [Original ARC007 acceptance](../../warlock-build-loop/v2/receipt-state-acceptance-20261031.json) and [independent review](../../warlock-build-loop/v2/receipt-state-review-20261031.json) bind the complete tested source tuple.

## Verification reference

[The preserved report](../../../implementation/warlock/qa/evidence/receipt-state-20261031/report.json) and its compressed raw trace retain the mixed fixture failure, corrected cancellation-only RED, passing candidate, compiled fixture bytes, matching bridge scenario receipts, model output and exact source/artifact hashes. All three actual GUI roots compile; 2,451 assertions cover the five original scenarios, two simultaneous retained requests, both effect protocols, 18 invalid receipt categories, duplicates, late outcomes, disconnect and bounded observation reconciliation without mutation replay. Eight seeded matrices vary distinct full-width authority values above 2^53.

The existing local receipt model now includes `Cancelled`, terminal reservation retirement and two directed cancellation tests. Fourteen distinct named tests pass (two also repeat through the imported module), plus 10,000 sampled 50-step traces with seed 20261031 and seven positive reachability witnesses. Its opaque exact-key/validation assumptions do not prove native interleavings, physical effects, authority issuance, liveness or resource retirement.

Root can reproduce this exact fixed CPU mode on the recorded host using `tools/qa_cpu.py --review implementation/warlock/qa/evidence/receipt-state-20261031/cpu-review.json --sha256 <that packet's SHA256>`. The wrapper requires its complete unchanged input closure and protected scope/core/serial lock. A changed checkout needs a newly reviewed packet. This is development verification, not a native campaign.

## Haskell boundary

The [current Haskell preparation record](../../warlock-build-loop/v2/haskell-toolchain-readiness-20261031.json) records a private GHC 9.6.7/Cabal 3.12.1.0 SDK and actual offline production build plus all 24 controlled suites (36 fixture invocations). The SDK, dependency sources/revisions, full build plans, fixture binaries and failures are hash-bound. The library bootstrap still handles one frame; it is not a persistent GUI backend, native effect issuer or original ARC007 port acceptance.

The next implementation must connect an owned persistent authenticated Haskell session and an explicit reviewed schema bridge to the existing Elm policy. Keep actual native operations empty until genuine issuer/admission/effect/certificate qualification. ARC012's native commit/cancellation and resource observations, UI007 native/keyboard/AT, original hardware/resource budgets, deployment/rollback and release acceptance remain separate. Preserve HOSTSTOP2; this work authorizes no renamed probe or main desktop change.
