# Pin helper boundary refinement

This fresh derivative retains the original helper and its actual malformed
completion counterexample. It changes the caller boundary before any new native
test. The existing complete token and native pin transaction remain unchanged.

1. Before sending, verify the actual helper executable and final kernel argv,
   isolated/no-site interpreter flags, frozen entry, captured requester and
   compositor lifetimes, selected environment, mapped module and exact socket.
   The interpreter path and SHA are explicit configuration authority. An entry
   launch must work with the actual Linux shebang parser.
2. Use one absolute two-second transaction deadline. Authority checks, connect,
   send, all chunks, EOF and final checks consume the same deadline. Set each
   socket timeout from the remaining budget. No chunk, check or retry resets it.
3. Publish complete evidence with checked full writes and fsync before parsing
   a received reply and before reporting completion. A publication failure after
   a possible send is uncertain. No automatic retry or rollback is authorized.
4. After send has become possible, missing/malformed captured tokens, malformed
   JSON, duplicate object keys, nonfinite values, missing EOF, partial writes,
   peer/source/socket changes and deadline expiry are uncertain. They cannot
   become a pre-send refusal or be cleared by a later valid reply.
5. A well-formed explicit native validation refusal is allowed without a
   captured/before/after projection. Successful completion requires an actual
   invoked action, the full captured token, matching live normal owner
   projections, a boolean original pin state and its exact toggled final state.
6. Exactly one send is permitted. A durable final receipt is required before
   any completion claim. Native effects, stale-owner policy and UI feedback are
   separate integration requirements; this model and CPU tests do not prove
   those native behaviors.

The Quint model abstracts actual kernel authority and wall-clock observations
as supplied events. Kernel socket, argv, evidence and deadline tests must verify
the implementation separately. Existing frozen packets and results are immutable.
