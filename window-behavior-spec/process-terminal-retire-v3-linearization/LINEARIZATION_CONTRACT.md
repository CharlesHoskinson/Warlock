# Matched pending fault and terminal commit

The 63-input V2 proposal remains immutable. This fresh refinement admits queued wrong-thread callbacks without prematurely setting the owner-only fault field. Owning-thread retirement drains at every reentrant source/getter/receipt/lifecycle/disconnect boundary. A different record/lease is never erased or invalidated by the retiring request.

The final linearization is one no-callback section under the same faultMutex used to admit off-thread callbacks. It checks exact selected record/tuple/lease, matched queued faults and overflow, and the original normal-closure flags before history insertion and exact registration removal. A matched queue entry or overflow already admitted before this section revokes only the selected record and refuses retirement. No getters, Qt disconnections, notification callback, child controls, waits or worker work run inside the mutex. History capacity is reserved and the reply is constructed before locking.

A callback blocked on faultMutex is admitted after the completed removal and is an old-lease callback; it cannot retrospectively authorize or invalidate a new lease. No statement about physical callback invocation time precedes its admitted queue ordering. Unmatched queued old callbacks are inert for the selected retirement. Overflow is not consumed locally: the existing global drain policy remains intact.

Actual normal same-command arm, event, worker, lifecycle and cancellation bodies stay unchanged. This correction applies only to the new proposed retirement operation. It supplies no new current native authority.

# Visible action retirement refusal

Before attempting retirement the frontend captures the current menu nonce and immutable native token. If retirement refuses, it leaves the old action command and lease unchanged, launches nothing, clears any displayed receipt, and changes only that still-open exact menu to the existing refused-or-uncertain status with operationFinished(false). It never emits success or calls Policy.invoke. Changed/dismissed menus get no old failure publication. Repeated refused activation is disabled by that status. Existing Policy, labels, keyboard/pointer paths, helper strings and original requested JSON remain unchanged.

After approval, a genuine Registry CPU case must enqueue a matched wrong-thread callback from a real Process disconnectNotify hook while a normal old helper registration is being retired; the owner must refuse, retain the old record, and never seal normal history. Another case must target the final mutex admission boundary with exact lease, plus unmatched old queue/reentrant replacement and visible current/old menu refusal cases. These future actual tests are not claimed by the model or source diff. No runtime application, compilation, helper transaction or GUI is authorized by this source packet.
