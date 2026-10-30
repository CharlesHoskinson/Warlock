// Stage 1 proposed native-owned Restore cancellation. Unvalidated source.
module NativeCancellation {
  type Phase = Absent | Prepared | Committing | Committed | Refused | Cancelled | ExecutionUnknown
  type Front = NoRequest | Pending | TransportUnknown | FrontCommitted | FrontRefused | FrontCancelled
  type AdmissionRecord = {key:int, owner:int, seq:int, pid:int, deadline:int, phase:Phase, front:Front,
    token:bool, retired:int, mutations:int, acked:bool}
  type Audit = {active:bool, key:int, prior:Phase, peerToken:bool, peerRetired:int}
  type State = {old:AdmissionRecord, high:AdmissionRecord, peer:AdmissionRecord, slotA:int, slotB:int, cursorA:int, cursorB:int,
    now:int, waiterReleased:bool, audit:Audit}
  var s:State
  pure def rec(x:State,k:int):AdmissionRecord = if(k==1) x.old else if(k==3) x.high else x.peer
  pure def other(x:State,k:int):AdmissionRecord = if(k==2) (if(x.slotA==3) x.high else x.old) else x.peer
  pure def owner(k:int):int = if(k==2) 2 else 1
  pure def sequence(k:int):int = if(k==3) 2 else 1
  pure def slot(x:State,k:int):int = if(owner(k)==1) x.slotA else x.slotB
  pure def cursor(x:State,k:int):int = if(owner(k)==1) x.cursorA else x.cursorB
  pure def terminal(p:Phase):bool = p==Committed or p==Refused or p==Cancelled
  pure def marked(x:State,k:int):Audit = {active:true,key:k,prior:rec(x,k).phase,
    peerToken:other(x,k).token,peerRetired:other(x,k).retired}
  pure def replaceRecord(x:State,k:int,r:AdmissionRecord):State = if(k==1) {...x,old:r} else if(k==3) {...x,high:r} else {...x,peer:r}
  pure def change(x:State,k:int,r:AdmissionRecord):State = replaceRecord({...x,audit:marked(x,k)},k,r)
  pure def exact(x:State,k:int,o:int,p:int,d:int):bool = (k==1 or k==2 or k==3) and
    rec(x,k).key==k and rec(x,k).owner==o and rec(x,k).pid==p and p>0 and rec(x,k).deadline==d
  pure def retained(x:State,k:int):bool = cursor(x,k)==sequence(k) and rec(x,k).phase!=Absent
  pure def occupied(x:State):int = (if(x.slotA==0) 0 else 1)+(if(x.slotB==0) 0 else 1)
  pure def retire(r:AdmissionRecord):AdmissionRecord = {...r,token:false,retired:r.retired+1}
  action init = s' = {old:{key:1,owner:1,seq:1,pid:11,deadline:3,phase:Absent,front:NoRequest,token:false,retired:0,mutations:0,acked:false},
    high:{key:3,owner:1,seq:2,pid:33,deadline:5,phase:Absent,front:NoRequest,token:false,retired:0,mutations:0,acked:false},
    peer:{key:2,owner:2,seq:1,pid:22,deadline:4,phase:Absent,front:NoRequest,token:false,retired:0,mutations:0,acked:false},
    slotA:0,slotB:0,cursorA:0,cursorB:0,now:0,waiterReleased:false,audit:{active:false,key:0,prior:Absent,peerToken:false,peerRetired:0}}
  action prepare(k:int,o:int,p:int,d:int):bool = all {exact(s,k,o,p,d),rec(s,k).phase==Absent,
    slot(s,k)==0,occupied(s)<2,sequence(k)>cursor(s,k),s.now<d,
    s'={...change(s,k,{...rec(s,k),phase:Prepared,front:Pending,token:true}),
      slotA:if(o==1) k else s.slotA,slotB:if(o==2) k else s.slotB,
      cursorA:if(o==1) sequence(k) else s.cursorA,cursorB:if(o==2) sequence(k) else s.cursorB}}
  // Duplicate prepare and query return the same retained reply; older cursor cannot resurrect.
  action retry(k:int,o:int,p:int,d:int):bool = all {exact(s,k,o,p,d),retained(s,k),s'=change(s,k,rec(s,k))}
  action query(k:int,o:int,p:int,d:int):bool = all {exact(s,k,o,p,d),retained(s,k),s'=change(s,k,rec(s,k))}
  action cancel(k:int,o:int,p:int,d:int):bool = all {exact(s,k,o,p,d),slot(s,k)==k,rec(s,k).phase==Prepared,
    s'=change(s,k,{...retire(rec(s,k)),phase:Cancelled})}
  // Atomic event-thread guard + first mutation; Committing has no yielding transition.
  action commit(k:int,o:int,p:int,d:int,uncertain:bool):bool = all {exact(s,k,o,p,d),slot(s,k)==k,
    rec(s,k).phase==Prepared,s.now<d,
    s'=change(s,k,if(uncertain) {...rec(s,k),phase:ExecutionUnknown,mutations:rec(s,k).mutations+1}
      else {...retire(rec(s,k)),phase:Committed,mutations:rec(s,k).mutations+1})}
  action expire(k:int,o:int,p:int,d:int):bool = all {exact(s,k,o,p,d),slot(s,k)==k,rec(s,k).phase==Prepared,s.now>=d,
    s'=change(s,k,{...retire(rec(s,k)),phase:Refused})}
  action invalid(k:int,o:int,p:int,d:int):bool = all {exact(s,k,o,p,d),slot(s,k)==k,rec(s,k).phase==Prepared,
    s'=change(s,k,{...retire(rec(s,k)),phase:Refused})}
  action lateDecision(k:int,o:int,p:int,d:int):bool = all {exact(s,k,o,p,d),retained(s,k),
    terminal(rec(s,k).phase) or rec(s,k).phase==ExecutionUnknown,s'=change(s,k,rec(s,k))}
  // Durable retention is an input assumption, not a fact invented by native.
  action ack(k:int,o:int,p:int,d:int,durable:bool):bool = all {exact(s,k,o,p,d),durable,slot(s,k)==k,terminal(rec(s,k).phase),
    s'={...change(s,k,{...rec(s,k),acked:true}),slotA:if(o==1) 0 else s.slotA,slotB:if(o==2) 0 else s.slotB}}
  action loseAck(k:int):bool = all {(k==1 or k==2 or k==3),slot(s,k)==k,
    s'=change(s,k,{...rec(s,k),front:TransportUnknown})}
  action recover(k:int,o:int,p:int,d:int):bool = all {exact(s,k,o,p,d),retained(s,k),
    s'=change(s,k,{...rec(s,k),front:if(rec(s,k).phase==Committed) FrontCommitted else if(rec(s,k).phase==Refused) FrontRefused else if(rec(s,k).phase==Cancelled) FrontCancelled else if(rec(s,k).phase==ExecutionUnknown) TransportUnknown else Pending})}
  action tick = all {s.now<6,s'={...s,now:s.now+1,audit:{...s.audit,active:false}}}
  // Observable refusal of a higher/direct/geometry request before allocation cursor moves.
  action busy(k:int):bool = all {(k==1 or k==2 or k==3),slot(s,k)!=0,s'={...s,audit:{...s.audit,active:false}}}
  action direct(k:int):bool = all {(k==1 or k==2 or k==3),slot(s,k)==0,s'={...s,audit:{...s.audit,active:false}}}
  // Proposed dependency owner: waiter is fixed to full key 1 (includes generation/incarnation).
  action releaseWaiter(k:int):bool = all {k==1,retained(s,k),rec(s,k).phase==Committed,not(s.waiterReleased),
    s'={...s,waiterReleased:true,audit:{...s.audit,active:false}}}
  action brokenLateCancel = all {s.old.phase==Committed,s'=change(s,1,{...s.old,phase:Cancelled})}
  action brokenWrongRelease = all {s.old.phase==Prepared,s.peer.token,
    s'={...s,old:{...s.old,phase:Cancelled},peer:retire(s.peer),audit:marked(s,1)}}
  action step = any {prepare(1,1,11,3),prepare(2,2,22,4),prepare(3,1,33,5),retry(1,1,11,3),retry(2,2,22,4),retry(3,1,33,5),
    cancel(1,1,11,3),cancel(2,2,22,4),cancel(3,1,33,5),commit(1,1,11,3,false),commit(1,1,11,3,true),commit(2,2,22,4,false),commit(3,1,33,5,false),
    expire(1,1,11,3),expire(2,2,22,4),expire(3,1,33,5),invalid(1,1,11,3),loseAck(1),recover(1,1,11,3),query(1,1,11,3),
    lateDecision(1,1,11,3),ack(1,1,11,3,true),ack(2,2,22,4,true),ack(3,1,33,5,true),tick,busy(1),busy(2),direct(1),direct(2),releaseWaiter(1)}
  val cancelledNoMutation = (s.old.phase==Cancelled implies s.old.mutations==0) and (s.high.phase==Cancelled implies s.high.mutations==0) and (s.peer.phase==Cancelled implies s.peer.mutations==0)
  val peerUntouched = s.audit.active implies other(s,s.audit.key).token==s.audit.peerToken and other(s,s.audit.key).retired==s.audit.peerRetired
  val terminalImmutable = s.audit.active and terminal(s.audit.prior) implies rec(s,s.audit.key).phase==s.audit.prior
  val noDuplicateWork = s.old.mutations<=1 and s.high.mutations<=1 and s.peer.mutations<=1 and s.old.retired<=1 and s.high.retired<=1 and s.peer.retired<=1
  val fixedMetadata = s.old.deadline==3 and s.high.deadline==5 and s.peer.deadline==4 and s.old.pid==11 and s.high.pid==33 and s.peer.pid==22
  val capacity = occupied(s)<=2 and (s.slotA==0 or s.slotA==1 or s.slotA==3) and (s.slotB==0 or s.slotB==2)
  val dependencySafe = s.waiterReleased implies s.old.phase==Committed
}
