# Async authority fence contract before native repair

The actual obsolete epoch signal is retained in v7d attempt4 with causal root
classification. V8 changes only native pointer delivery/control integration.
The authoritative root PointerLocator State remains byte-identical.

Motion records the actual coordinate change and consumes an accepted pending
arm into a bounded deferred note. It performs no D-Bus RPC, blocking operation,
or direct signal emission. Each note captures the unique sender, principal epoch
and selected real registration name/revision. Any affected name change rotates
that pointer principal's epoch, including an alias change while another monitor
name remains owned. Keyboard observation/capture policy is unchanged.

Control dispatch remains bounded32 messages/tick. It starts at most16 concurrent
asynchronous GetNameOwner calls on the SAME bridge session connection, each
500ms timeout, total note deadline1500ms. The returned unique owner must equal
captured sender. Same-connection daemon FIFO orders preceding owner events ahead
of this reply. Ordinary bounded libdbus dispatch must process them; blocking
pending_call APIs are forbidden. Completion only marks a snapshot ready.
Final delivery waits for all locally known control messages to drain and validates
same current compositor/service/principal epoch/name revision before enqueue.

Authorization linearizes at the daemon lookup snapshot. An unseen owner change
AFTER that snapshot is a future external event and can make a valid packet
in-flight; it cannot retrospectively invalidate its prior authorization. Owner
history PRECEDING the snapshot, including sameunique loss/reclaim, must prevent
old-note delivery. A known later event before enqueue also cancels delivery.
Local backlog empty alone is never an authority fence.

At most512 deferred notes exist; in-flight AX query/pending-arm reservations
prevent motion overflow. Resource exhaustion rejects NEW queries with
LimitsExceeded/noarm, preserving accepted valid notes. Deadline/transport/error,
NoOwner, owner mismatch, old epoch/name revision, bus loss and retirement never
emit. Deadline cancellation runs on each bounded control tick even when the owner
queue is saturated; start/completion/delivery wait for drained control history.
A failed note is diagnosed and discarded; a subsequent fresh authorized
query can arm recovery. Retirement cancels every pending fence and clears notes;
a late completion cannot reactivate delivery. No forced/raw plugin unload.

Model budgets are scaled2 notes/1 in-flight fence and bounded wire queues; native
constants are512/16/32. Source replay must cover captured Query→remote owner
loss→sameunique reclaim→motion→async reply, alias churn, retirement/busloss after
completion, timeout/noowner/mismatch/saturation and fresh rearm. Native acceptance
retains exact old baseline and causal telemetry, adds repeated actual ownerchurn,
and preserves all existing fractional/GTK/officialReader/14preservation gates.
