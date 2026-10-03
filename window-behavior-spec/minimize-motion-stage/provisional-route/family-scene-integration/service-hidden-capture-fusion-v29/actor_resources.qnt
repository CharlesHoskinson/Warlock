module actor_resources {
 type State={active:Set[int],retiring:Set[int],quarantined:Set[int],pending:Set[int],visible:Set[int],awaiting:Set[int],owners:Set[int],serial:int,limit:int,lastReceipt:int,closed:bool}
 var s:State
 action init=s'={active:Set(),retiring:Set(),quarantined:Set(),pending:Set(),visible:Set(),awaiting:Set(),owners:Set(),serial:0,limit:3,lastReceipt:0,closed:false}
 val capacity=s.active.size()+s.retiring.size()
 action admit=all{not(s.closed),capacity<s.limit,s'={...s,active:s.active.union(Set(s.serial+1)),owners:s.owners.union(Set(s.serial+1)),serial:s.serial+1,lastReceipt:s.lastReceipt+1}}
 action reverse(a:int):bool=all{not(s.closed),s.active.contains(a),s.owners.contains(a),s'={...s,lastReceipt:s.lastReceipt+1}}
 action markPending(a:int):bool=all{not(s.closed),s.active.contains(a),s'={...s,pending:s.pending.union(Set(a))}}
 action markVisual(a:int):bool=all{not(s.closed),s.active.contains(a),s'={...s,visible:s.visible.union(Set(a))}}
 action markAwaiting(a:int):bool=all{not(s.closed),s.active.contains(a),s'={...s,awaiting:s.awaiting.union(Set(a))}}
 action idle(a:int):bool=all{s.active.contains(a),s'={...s,pending:s.pending.exclude(Set(a)),visible:s.visible.exclude(Set(a)),awaiting:s.awaiting.exclude(Set(a))}}
 val removable=s.active.filter(a=>not(s.pending.contains(a) or s.visible.contains(a) or s.awaiting.contains(a)))
 action detach(a:int):bool=all{removable.contains(a),s'={...s,active:s.active.exclude(Set(a)),retiring:s.retiring.union(Set(a)),owners:s.owners.exclude(Set(a))}}
 action normalClose(a:int):bool=all{s.retiring.contains(a),not(s.quarantined.contains(a)),not(s.visible.contains(a) or s.awaiting.contains(a)),s'={...s,retiring:s.retiring.exclude(Set(a))}}
 action failedClose(a:int):bool=all{s.retiring.contains(a),s'={...s,quarantined:s.quarantined.union(Set(a))}}
 action shutdown=all{not(s.closed),s'={...s,closed:true,pending:Set(),owners:Set(),retiring:s.retiring.union(s.active),active:Set()}}
 // Native/cancel settlement and renderer drain must complete before local
 // shutdown records can become removable; shutdown itself supplies no ACK.
 action shutdownSettled(a:int):bool=all{s.closed,s.retiring.contains(a),s'={...s,visible:s.visible.exclude(Set(a)),awaiting:s.awaiting.exclude(Set(a))}}
 val shutdownRevokesAdmission=not(s.closed) or s.pending.size()==0 and s.owners.size()==0
 val boundedActors=capacity<=s.limit
 val retiredCannotOwn=s.owners.intersect(s.retiring).size()==0
 val activeProtected=s.closed or s.retiring.intersect(s.pending.union(s.visible).union(s.awaiting)).size()==0
 val quarantineStillOccupies=s.quarantined.subseteq(s.retiring)
 val allProps=shutdownRevokesAdmission and boundedActors and retiredCannotOwn and activeProtected and quarantineStillOccupies
 action step={nondet a=1.to(12).oneOf();any{admit,reverse(a),markPending(a),markVisual(a),markAwaiting(a),idle(a),detach(a),normalClose(a),failedClose(a),shutdown,shutdownSettled(a)}}
}
