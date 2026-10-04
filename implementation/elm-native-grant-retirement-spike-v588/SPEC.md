# Lifetime-scoped native grant registry spike

This fresh component implements a standalone C++ registry and executable Quint abstraction before any authority behavior change. It does not alter current579/586, the compositor, shared shell or installed desktop. Actual authority integration belongs to a separately reviewed derivative.

The single serialized owner assigns session IDs monotonically within one nonzero native lifetime. A newly attached peer gets the next ID and frontend1. Same PID/start hello advances only its own frontend. PID removal, PID/start replacement and exact retirement never reset the allocator. UINT64_MAX may be issued once; further new sessions refuse. A frontend at UINT64_MAX refuses hello without changing its current grant. Sixteen retained peers bound the live table; ID history is represented by the monotonic allocation watermark, not an unbounded tombstone table.

Peer PID/start inputs are trusted integration inputs, never frontend wire arguments. Both exact retirement and read-only state require the caller's current PID/start and full lifetime/session/frontend binding. Retirement refuses the current caller's exact grant, foreign lifetime, missing or stale target. An admitted retirement erases exactly the other target grant; all subsequent effect admission must consult the same authoritative registry. A new attachment never revives the retired session ID.

## Read-only classification

| State | Required condition |
| --- | --- |
| Refused | Caller authentication inputs/binding mismatch, foreign target lifetime, zero target session/frontend |
| Registered | Exact target session/frontend currently present |
| Future | Target session exceeds last issued ID, or present target session has queried frontend greater than its current frontend |
| Retired | Allocated target session ID is absent forever, or present session has a greater current frontend than the queried one |

Querying the current caller's exact tuple returns Registered without mutation; retiring it returns CurrentCaller refusal. A disappeared allocated ID can safely classify all its nonzero frontend values as Retired because the ID can never be allocated again. A present ID's future frontend must return Future, including the caller's own ID. An exact-mutation TargetMissing result alone proves neither absence forever nor retirement; future IDs/frontends can subsequently become registered. Recovery must consume the explicit read-only classification rather than reinterpret a refusal.

The allocator starts at zero for a fresh native lifetime. The explicit seeded constructor exists for the actual uint64 boundary fixtures or separately verified continuity; production must not recreate/reseed a Registry within the same lifetime. Copy and move are disabled. The adapter must maintain one owner and serialize hello, retirement/query and native effects. The helper itself has no thread lock, kernel authentication, wire parser, process liveness probe or durable journal.

## Evidence scope and integration prerequisites

The small-domain Quint model exercises monotonic allocation, frontend progression, exact retirement, caller preservation, reattachment and pure classification. C++ exercises actual uint64 limits, table capacity, PID/start replacement, authentication input matching, future grant transitions and 1,000 retirement/reattachment iterations. Counted churn assertions are separate from unique boundary cases. Mutation controls must compile/typecheck and then fail their behavioral oracle.

Actual SO_PEERCRED and `/proc` start-time authentication, native lifetime entropy/uniqueness across authority restart, singleton/serialization integration, permission to retire another broker, complete native resource retirement and durable reservation release remain unproven. In particular, Retired is a registry classification under the helper assumptions; it is not a signed kernel certificate, durable fsync acknowledgement or authorization to clear Unknown automatically. Authority/native protocol and recovery integration must bind the result to current caller/target/lifetime, then satisfy the independent durable reservation and effect-boundary contracts.

Preserve `history/exact-mutation/packet-manifest.json` and its original source/evidence. The positive-query model was verified before its C++ implementation. Failed compiled query mutation construction remains in its own report; the corrected mutation compiles and fails its actual behavioral test.
