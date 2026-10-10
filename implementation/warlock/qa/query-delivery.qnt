module query_delivery {
  // UI-005/search-race. Popup.Present can emit a retained query before the
  // adapter's two animation frames acknowledge presentation to the native
  // gate. Messages from the same WebKit handler are delivered in FIFO order.
  // Model pub/lease admission and one observational query slot. Text is an
  // opaque bounded integer. Actual DOM, GIO, AT and paint are native oracles.
  var s: {pub:int, lease:int, ack:int, pending:int, root:int,
    lastDelivered:int, lastDeliveredPub:int, lastDeliveredLease:int, deliveryAck:int}
  action init = s'={pub:1,lease:1,ack:0,pending:-1,root:0,
    lastDelivered:-1,lastDeliveredPub:0,lastDeliveredLease:0,deliveryAck:0}
  action present = all {s.pub<20,s'={...s,pub:s.pub+1,ack:0,pending:-1}}
  action edit(value:int,pub:int,lease:int): bool =
    if (pub==s.pub and lease==s.lease and value>=0 and value<=4)
      if (s.ack==s.pub) s'={...s,root:value,lastDelivered:value,
        lastDeliveredPub:pub,lastDeliveredLease:lease,deliveryAck:s.ack}
      else s'={...s,pending:value}
    else s'=s
  action acknowledge(pub:int,lease:int): bool =
    if (pub==s.pub and lease==s.lease)
      if (s.pending>=0) s'={...s,ack:pub,root:s.pending,
        lastDelivered:s.pending,lastDeliveredPub:pub,
        lastDeliveredLease:lease,deliveryAck:pub,pending:-1}
      else s'={...s,ack:pub}
    else s'=s
  action reopen = all {s.lease<10,s.pub<20,
    s'={...s,pub:s.pub+1,lease:s.lease+1,ack:0,pending:-1}}
  action step = any {present,reopen,edit(3,s.pub,s.lease),
    acknowledge(s.pub,s.lease)}
  val safety = s.pending>= -1 and s.pending<=4 and s.ack<=s.pub and
    (s.lastDelivered>=0 implies (s.lastDeliveredPub<=s.pub and
      s.lastDeliveredLease<=s.lease and s.root==s.lastDelivered and
      s.deliveryAck==s.lastDeliveredPub))
  val queued = s.pending>=0
  val delivered = s.lastDelivered>=0
  val retired = s.lease>1
  val advanced = s.pub>1
  action check(ok:bool): bool = all {assert(ok),s'=s}
}
