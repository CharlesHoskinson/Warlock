# Held grant retirement and retirement-state helper

Owned fresh588 only. No current579/586, shared source, native session or git changes.

`native/grant-registry.hpp` implements strict PID/start/caller-binding checks, exact other-grant retirement, caller preservation, lifetime-scoped monotonic session allocation, uint64 exhaustion refusal and read-only Registered/Future/Retired/Refused classification. `native/test.cpp` compiles the actual helper with C++20 strict warnings and undefined-behavior instrumentation. The helper contains no compositor headers or substitute native effects.

Accepted protected CPU evidence:

- `qa/model-1791145632834935758/report.json`: 22 explicitly selected Quint scenarios, 1,000 invariant samples × 40 steps, 10 typechecked behavioral mutation controls rejected.
- `qa/compiled-1791145728181070670/report.json`: 2,069 assertions including 1,000 deterministic retirement/reattachment iterations and actual uint64 boundaries; 11 compiled behavioral mutation controls rejected.
- `history/exact-mutation/packet-manifest.json`: hash-bound predecessor helper/model/test/evidence before the positive-query extension. Earlier successful scope and the malformed-query-mutant compile failure remain intact.

Do not treat a target-missing retirement refusal as retirement proof: future session IDs/frontends can later become live. Consume the explicit query state. A present session's older frontend and an absent allocated session ID cannot return under the monotonic helper contract; future IDs and present-session future frontends are never labeled Retired. Current-caller query is Registered, while its mutation is refused.

Next integration must use this registry as the authoritative binding state under the compositor's effect serialization domain, not maintain an independently drifting grant table. It must authenticate kernel peer credentials and start identity, keep one allocator owner through PID cleanup/reattach, maintain lifetime uniqueness across restarts, enforce native retirement permission, retire associated resources and separately settle durable reservations before acknowledging recovery. None of these integration/kernel/durable claims is established by this standalone spike.

`component-manifest.json` binds the held source and every retained packet. Root may review and copy into a new actual authority derivative; do not rewrite this packet or transfer its CPU results into native acceptance.
