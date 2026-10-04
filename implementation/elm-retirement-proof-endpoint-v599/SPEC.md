# Strict retirement proof endpoint

Fresh599 owns only this adapter and its CPU evidence. `GrantEndpoint` subclasses the byte-preserved current521 `effect_endpoint.Endpoint`; inherited `request`, attached/hello, snapshot, scene facts, context and effect methods remain unchanged. The underlying endpoint retains its selected native PID/start/executable, private socket ownership, SO_PEERCRED, duplicate-JSON and absolute transport checks. This component does not requalify those checks on a live connection.

`observe(request_id, queried_binding)` sends `binding-retirement-state-request`. `retire(...)` sends `binding-retire-request`. Both requests have exactly protocolVersion3, kind, current binding, requestId and queriedBinding. Request IDs and every lifetime/session/frontend/sequence counter are canonical nonzero uint64 strings. The current binding and queried identity are copied into frozen `NativeBinding` values before transport; changes to endpoint binding while the request is in flight refuse the reply. Foreign target lifetimes and explicit current-caller retirement refuse before dispatch.

Reply acceptance requires exactly protocolVersion3, retirementProtocol1, kind binding-retirement, matching observe/retire operation, exact captured caller and target, exact requestId, a strictly increasing nonzero sequence and Registered/Future/Retired state. Bool, numeric, zero, leading-zero, signed, whitespace and overflow counters refuse. Missing/extra reply and nested binding fields refuse. Malformed and uncorrelated replies do not advance the accepted watermark.

Sequence watermarks are native-lifetime scoped and retained across hello/frontend changes. At most16 lifetime histories are retained; a new history beyond this bound refuses before transport. Existing histories are never evicted to make a replay appear fresh. Recreating an endpoint is a separately authenticated lifecycle event, not a means to accept an old queued proof.

## Proof API for the durable consumer

The returned frozen `RetirementProof` has `binding: NativeBinding`, `queried_binding: NativeBinding`, `request_id`, `sequence`, `operation` and `grant_state`. `NativeBinding.as_dict()` and `RetirementProof.as_dict()` produce detached copies. `allows_release` is true only for Retired. Registered and Future are valid observe results with false release permission; retire returns a proof only when state is Retired. Authenticated native refusal remains the inherited exception and never becomes a proof.

This property expresses only the native-grant prerequisite. The durable consumer must additionally match the proof target to its original reservation, bind it to its current authenticated caller, enforce its journal/Unknown state machine and complete reviewed durable writes. It must obtain the proof from the endpoint call rather than construct it from untrusted JSON. A frozen Python value is not a cryptographic certificate, fsync receipt or permission to unlink a file. Endpoint599 performs no ledger, reservation, frontend or unlink operation.

## Evidence

Immutable native596 report is copied under `qa/fixtures/` with its original hash. Nine exact successful native proof exchanges are replayed through the actual decoder. Producer596's42 checks remain their original bounded private native scope. The new endpoint tests use an explicitly synthetic request method; they do not authenticate fresh sockets, launch a compositor or establish durable recovery acceptance.

625 assertions cover exact wire/request reconstruction, malformed fields/counters, Registered/Future nonrelease, retired-only mutation proof, current binding replacement and in-place changes during transport, caller input alias mutation, stale sequence rejection across frontend replacement, uint64 maximum, local pre-dispatch refusals and inherited method identity. Nine syntax-valid decoder mutations each fail a meaningful behavioral oracle. Preserve the earlier622-check run as history; it predates the pre-dispatch lifetime-history bound refinement.
