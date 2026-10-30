# Native Restore cancellation protocol

Implementation stage: native source compiled against its owning ABI and exercised by a strict client on an isolated real GTK fixture. The client is inherited by the production effect endpoint, but the daemon/Elm workflow is not routed to it. The plugin is unloaded after testing; no main-session deployment is implied. See [evidence and remaining gates](../../../implementation/warlock/qa/evidence/native-restore-cancellation-20261030/LIMITS.md). Existing consumers retain their three-status legacy interface; do not add Cancelled to that interface by assuming native execution.

## Admission and identity

A caller authenticates through the existing peer/start and grant binding. `effect-cancellation-negotiate` uses protocolVersion 3, binding, requestId and cancellationProtocol 1. The response advertises effectProtocol 1, operations `["restore"]`, maxPreparedPerSession 1, maxPreparedGlobal 64 and deadlineClock `CLOCK_MONOTONIC`. It is separate from the unchanged legacy hello capabilities.

Each lifecycle request carries protocolVersion 3, cancellationProtocol 1, effectProtocol 1, binding, full immutable intent and deadlineMonotonicNs. The intent contains request, generation, incarnation, operation `restore`, and context lifetime/epoch/output/revision. Binding lifetime/epoch must agree with intent context and the current grant. Counters are positive canonical decimal strings. Raw requests reject duplicate members, embedded NUL, excessive depth/size and unexpected fields.

| Kind | Additional field | Native meaning |
| --- | --- | --- |
| `effect-prepare` | None | Reserve one logical full-key slot; return `effect-prepared` with authority-generated preparedId. No effect outcome is implied. |
| `effect-commit` | preparedId | Revalidate and execute through the serialized owner if still Prepared and before the original deadline. |
| `effect-cancel` | preparedId | If Prepared, fix Cancelled before formatting/delivery and retire its token; a later commit cannot execute. |
| `effect-decision-request` | preparedId | Query the retained exact decision without replay. |
| `effect-decision-ack` | preparedId | Transfer a complete known terminal decision to the session cache and free its slot. The future adapter must durably retain the decision first. |

All five preserve the same intent, preparedId and original absolute deadline. Same-session live or unacknowledged slots block direct/geometry effects before their cursor writes. Other sessions have independent ownership. Unknown and terminal-unacknowledged slots consume capacity; uncertainty is never evicted to admit new work.

## Outcomes and custody

Opt-in outcomes include the full identity and cancellation certificate metadata. Cancelled means the native owner ordered cancellation before its commit boundary; it is distinct from local withdrawal or a refused legacy request. Native Unknown cannot be turned into Cancelled by asking again. Frontend transport uncertainty can coexist with native Prepared, so querying/cancelling that exact preparation may resolve it.

Typed observed Committed/Refused proof survives later formatting failure separately from wire state. Until a complete terminal reply is encoded, queries return the retained complete Unknown fallback; encoding retries never rerun work. A transport failure after complete terminal caching does not erase that terminal decision. Only an exact complete terminal record is acknowledgeable. ACK response construction allocates before freeing the owner slot; fixed record/string ownership transfers follow. Successful higher admission supersedes the old cache; a rejected attempt does not. Native retirement hooks retire unexecuted Prepared tokens while retaining unknown custody.

## Limits for callers

The opt-in Python API is available through `effect_endpoint.Endpoint`: `cancellation_negotiate`, `prepare_effect`, `commit_effect`, `cancel_effect`, `query_effect_decision` and `ack_effect_decision`. Its in-memory correlation cache does not implement durable recovery. Calls must be sequential on an instance. There is no routed daemon/Elm workflow for this channel yet. Native source does not establish host deadline origin, durable storage, scoped Escape transport, actual dependency scheduling or full resource retirement. A new native source tuple and runtime qualification must precede deployment. The [ownership explanation](../explanation/ownership-and-lifetimes.md) and [status reference](status-and-evidence.md) distinguish implementation stages from original acceptance.


## Current client and native observations

The [strict-client/native evidence](../../../implementation/warlock/qa/evidence/native-cancellation-client-20261030/LIMITS.md) records 533 codec assertions with 200 seeded reply-parameter cases, unchanged pointer regression, and 34 actual native checks on the owning compositor-only tuple. Cancel-first/commit-first and the subsequent late opposing requests preserve the appropriate real window state and exact receipt. Original ARC012 cases remain partial because generation retirement and physical Escape witnesses are missing.

Methods take the full validated prepared/outcome dictionary, preserve its original absolute deadline and return fresh validated native dictionaries. An exact repeated Prepare may recover a prior terminal; it does not execute. Unknown and Prepared cannot be ACKed. The caller must durably retain a known terminal before ACK; the client cannot inspect its storage. A `Refused` exception from validation/transport is not a native Refused certificate and must not be used to guess whether submission happened. See [the protected QA how-to](../how-to/test-native-cancellation.md).
