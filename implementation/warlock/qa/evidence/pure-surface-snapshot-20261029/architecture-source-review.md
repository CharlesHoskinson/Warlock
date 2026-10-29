# SurfaceSnapshot proposal review

Disposition: source-only READY for selected implementation and proportional verification. No compiler, replay, fuzzer, model, native QA, or GUI acceptance was run by this reviewer. No product file was edited.

Reviewed the five private files and `proposal.json` against current `implementation/warlock/src/`. A read-only source comparison confirmed:

- Every proposed file SHA-256 matches proposal.json; the current renderer matches baseline `48e03f50fd509ea0e42e23d7a1aa26396122350ab824c8dc179952b5bfd28c63`.
- The function block from `strict` through `action`, including decoder, encoder, accessors and `pendingQuery`, moved byte-for-byte.
- The renderer's view code is identical after the sole expected change from destructuring the old opaque constructor to obtaining `SurfaceSnapshot.details current`.
- OutputController and Presentation contain exactly the module-name substitutions; Main contains exactly the unused renderer-import removal.

The new Snapshot constructor stays hidden. Details/Control expose immutable values but no function wraps arbitrary Details as an admitted Snapshot. The renderer compatibility alias resolves to the same opaque SurfaceSnapshot type; it does not introduce a second representation or decoder. Existing public function signatures and parameter order remain compatible by source inspection. The module's dependencies are JSON, Set, Settings and UInt64, with no new runtime/Html dependency. Actual compilation is still required.

No obvious Elm type, public API or intentional semantic change was found. Preserve two limits in implementation documentation and QA:

1. The existing `pendingQuery : String -> Snapshot -> Snapshot` is a display overlay, not fresh decoder validation; do not claim arbitrary overlay strings satisfy decoder text bounds. Normalization properties apply to appropriately decoded/valid inputs, not every unconstrained overlay.
2. Removing the direct controller/presentation renderer imports does not make the authority graph entirely Html-free. OutcomeAnnouncements still depends on Announcement's message value/encoding, and Announcement owns Html rendering.

Original stale-action refusal, localEdit same-lease exception, malformed presentation clearing, query/composition envelopes, preview labels/semantics, counters, action effects, native lifetimes and publication ownership remain unchanged by this source delta. This does not establish physical behavior or repair the existing WebKit delivery failure.

Before integration: select the original-scenario contributor record; recheck source freshness; compile Main/Bar/Popup and relevant production replays; run the selected original contracts and seeded positive/negative/sequence checks; preserve any divergence against the baseline instead of weakening expected behavior. T4/Q1 private exact-source/coverage review was requested through Sol. Root retains product integration and protected QA ownership.
