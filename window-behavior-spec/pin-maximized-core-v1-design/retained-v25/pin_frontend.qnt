module pin_frontend {
 type Token={owner:int,generation:int,epoch:int}
 type Event=Open(int)|Capture({nonce:int,token:Token,authority:bool})|Dismiss|Invoke|Execute|Focus(int)|Close|NewLifetime|Reload|Ack(bool)
 type State={nonce:int,open:bool,target:int,captured:Token,pending:Token,ready:bool,queued:bool,sent:bool,complete:bool,generation:int,epoch:int,alive:bool,active:int,pinned:Set[int],lastWrite:int}
 var s:State
 pure val none={owner:0,generation:0,epoch:0}
 val current={owner:1,generation:s.generation,epoch:s.epoch}
 action init=s'={nonce:0,open:false,target:0,captured:none,pending:none,ready:false,queued:false,sent:false,complete:false,generation:1,epoch:1,alive:true,active:1,pinned:Set(2),lastWrite:0}
 action fire(e:Event):bool={
 val b={...s,lastWrite:0,complete:false}
 s'=match e{
 |Open(owner)=>{...b,nonce:s.nonce+1,open:true,target:owner,captured:none,ready:false}
 |Capture(reply)=>if(s.open and reply.authority and reply.nonce==s.nonce and reply.token.owner==s.target and reply.token==current and s.alive){...b,captured:reply.token,ready:true}else b
 |Dismiss=>{...b,open:false,captured:none,ready:false,nonce:s.nonce+1}
 |Invoke=>if(s.open and s.ready and not(s.queued)){...b,open:false,ready:false,pending:s.captured,queued:true,sent:false}else b
 |Execute=>if(s.queued and not(s.sent)){
 ...b,sent:true,pinned:if(s.alive and s.pending==current){if(s.pinned.contains(1))s.pinned.exclude(Set(1))else s.pinned.union(Set(1))}else s.pinned,lastWrite:if(s.alive and s.pending==current)1 else 0
 }else b
 |Ack(ok)=>{...b,complete:ok and s.queued and s.sent and s.alive and s.pending==current,queued:false}
 |Focus(owner)=>{...b,active:owner}
 |Close=>{...b,alive:false,generation:s.generation+1,pinned:s.pinned.exclude(Set(1))}
 |NewLifetime=>{...b,alive:true,generation:s.generation+1,pinned:s.pinned.exclude(Set(1))}
 |Reload=>{...b,epoch:s.epoch+1}
 }
 }
 val allProps=all{s.lastWrite==0 or (s.lastWrite==1 and s.alive and s.pending==current),s.pinned.contains(2),s.complete implies s.alive and s.pending==current,s.ready implies s.open}
 action step={nondet e=Set(Open(1),Open(2),Capture({nonce:s.nonce,token:current,authority:true}),Capture({nonce:s.nonce-1,token:current,authority:true}),Capture({nonce:s.nonce,token:current,authority:false}),Invoke,Execute,Dismiss,Focus(2),Close,NewLifetime,Reload,Ack(true),Ack(false)).oneOf();fire(e)}
 action check(v:bool):bool=all{assert(v),s'=s}
 action menu=fire(Open(1)).then(fire(Capture({nonce:1,token:{owner:1,generation:1,epoch:1},authority:true})))
}
