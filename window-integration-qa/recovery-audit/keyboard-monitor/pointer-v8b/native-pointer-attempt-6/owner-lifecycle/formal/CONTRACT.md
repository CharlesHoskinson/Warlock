# Notification delivery integration contract before implementation

The authoritative root PointerLocator State/helper remains unchanged. This
separate model describes owner messages and deferred delivery around that helper.
It proposes a repair; the current candidate remains unchanged for causal testing.

Actual daemon ownership and compositor cached ownership are distinct. Owner
messages are ordered and must be processed within a bounded compositor control
budget. Motion may record a real coordinate change and capture the existing
pending request's epoch, but may not emit using cached authority while known
control messages remain undrained. Delivery requires nonretired service, live
bus, current validated registration epoch and an empty known control backlog.
An older queued notification is discarded when its epoch is no longer current.
The model never admits stale delivery to accommodate the old direct-emission path.

Control drain is bounded per tick. Budget exhaustion defers delivery. Notification
and control queues have explicit limits; overflow fails closed/retire, or refuses
new queries without replacing accepted state. No synchronous D-Bus operation is
permitted in the motion path. A native implementation must prove its real control
ordering and bounded resource behavior independently of this model.

Successful/authorized Unknown replies still arm after actual reply queueing.
Repeated queries before the next motion coalesce. A real move consumes one arm;
further moves without a query cannot create another notification. Motion away
and back remains a captured actual change even if the current point equals the
reply point by delivery time. A later explicit query may arm a later change;
accepted deferred notes are preserved within the bounded queue.

Owner loss/reclaim uses a new epoch even when the same unique connection reclaims
its registration. Retirement/bus loss clears pending and deferred notifications
and is irreversible. Owner callbacks cannot reactivate the retired service.
A signal already validly emitted before owner loss cannot be recalled from the
caller's main-context callback queue. Causal telemetry must distinguish that
in-flight history from a notification newly emitted from an obsolete epoch.

This stage does not prove the cause of native attempt 3 and does not change the
product. Causal testing must run the unchanged candidate before policy repair.
