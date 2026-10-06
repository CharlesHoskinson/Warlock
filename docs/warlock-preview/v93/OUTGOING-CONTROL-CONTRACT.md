The outgoing control channel must keep an exact packet until its original native
receiver confirms delivery. Delivery means the native dispatcher returned; it
does not mean an effect succeeded. Terminal proof, physical retirement, immutable
Elm settlement and unknown-outcome reconciliation remain separate.

EARS CONTROL-001: WHEN an original-binding, original-epoch packet is the next
contiguous ordinal, the dispatcher SHALL invoke its handler at most once and
retain its exact byte identity before issuing a delivery receipt. WHILE that
handler is in flight, repeated or later packets SHALL NOT enter it.

EARS CONTROL-002: WHEN the latest delivered packet is retried byte for byte under
the same binding and receiver epoch, the dispatcher SHALL repeat only its
delivery receipt. Different bytes under that ordinal, gaps, zero, noncanonical
or overflowing ordinals, and foreign receiver grants SHALL NOT invoke effects
or advance the prefix. Exhaustion SHALL NOT wrap or reset the namespace.

EARS CONTROL-003: WHILE delivery is unconfirmed, the renderer transport SHALL
retain immutable packets, retry their exact existing ordinals in order, and
accept a receipt only for its own outstanding packet and original grant. Retrying
transport SHALL NOT recreate a command, assign a new ordinal, infer effect
success, or replay an Unknown effect under another grant.

EARS CONTROL-004: BEFORE native admission can create a job or actor obligation,
the native owner SHALL reserve bounded queue capacity and remaining ordinals for
its maximum required original cleanup and acknowledgments. Admission lacking
that capacity SHALL remain backpressured or exhausted before physical issuance.
Cleanup reservations SHALL remain available during normal overload and SHALL NOT
be consumed by speculative admission. Duplicate idempotent acknowledgments may
coalesce only by exact original identity; effects remain in their original order.
Finite bounds must derive from the owning Broker/actor/journal/proof contracts,
with executable worst-case witnesses. A renderer queue alone cannot authorize
native admission or silently discard an already emitted Elm command.

EARS CONTROL-005: WHEN a receiver reloads, is replaced, or disappears with an
outstanding packet, the native owner SHALL preserve original obligations and
unknown outcomes. A new receiver SHALL require a fresh trusted grant and explicit
reconciliation; it SHALL NOT reset a prefix or reuse the old grant to replay
effects. Normal close SHALL retain outstanding transport and physical barriers.

First qualify the native receipt/deduplication primitive independently, with
constant bounded storage for the in-flight and latest delivered packet. It remains
inactive in WebKit until the actual renderer outbox, native admission cleanup
reservation, reload/reconciliation, and strict original-receiver routing are
implemented together. This staged qualification does not close the host or
release gate. Original native timeouts and S02 measured pacing/resource policy
remain unchanged.

EARS CONTROL-006: WHILE the native dispatcher lacks confirmation that its latest
delivery receipt reached the original frontend, it SHALL retain and retry that
receipt and SHALL keep its transport confirmation barrier open. The frontend
SHALL repeat an idempotent original-grant confirmation for a previously processed
receipt without recreating a packet or asserting effect success. Confirmation
SHALL be bounded by the native delivered prefix; it cannot confirm an in-flight
or future invocation. Cumulative confirmation may preserve a compact monotonic
prefix. Closing the native owner SHALL independently require this confirmation,
all admission cleanup reservations, all terminal/physical barriers and final
actor-delivery confirmation.

This additional close prerequisite follows from the transport audit: native
physical drain can precede delivery of the final outgoing-control receipt to
the frontend. The initial receipt/deduplication primitive does not yet represent
this confirmation barrier. That is a recorded integration gap, not an observed
failure in a deployed GUI or permission to close the full release gate.
