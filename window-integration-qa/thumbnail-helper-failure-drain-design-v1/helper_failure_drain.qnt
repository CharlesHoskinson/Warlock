module helper_failure_drain {
 type Phase=Idle|Checking|Draining|Returned|Raised
 type State={now:int,deadline:int,phase:Phase,starts:Set[int],terminals:Set[int],gone:Set[int],counts:bool,firstError:bool,errorOrdinal:int,unsafe:bool,archived:bool,cleanupNormal:bool,campaignAccepted:bool,originalRaised:bool,locked:bool}
 type Event=Begin|Start({id:int,authorized:bool})|Terminal({id:int,normal:bool,identity:bool})|Gone(int)|Counts(bool)|Check|SnapshotLock|SnapshotUnlock|Tick(int)|Archive|Finish|Unknown
 var s:State
 pure val initial={now:0,deadline:-1,phase:Idle,starts:Set(),terminals:Set(),gone:Set(),counts:false,firstError:false,errorOrdinal:0,unsafe:false,archived:false,cleanupNormal:false,campaignAccepted:false,originalRaised:false,locked:false}
 pure def active(x:State):bool=x.phase==Checking or x.phase==Draining
 pure def complete(x:State):bool=x.starts==x.terminals and x.starts==x.gone and not(x.unsafe)
 pure def transition(x:State,e:Event):State=match e {
 | Begin=>if(x.phase==Idle){...x,phase:Checking,deadline:x.now+10}else x
 | Tick(n)=>if(n>=0){...x,now:x.now+n}else{...x,unsafe:true}
 | Start(r)=>if(active(x))if(r.authorized and not(x.starts.contains(r.id))){...x,starts:x.starts.union(Set(r.id)),archived:false,cleanupNormal:false}else{...x,unsafe:true}else x
 | Terminal(r)=>if(active(x))if(x.starts.contains(r.id) and not(x.terminals.contains(r.id)) and r.normal and r.identity){...x,terminals:x.terminals.union(Set(r.id)),archived:false,cleanupNormal:false}else{...x,unsafe:true}else x
 | Gone(id)=>if(active(x) and x.starts.contains(id)){...x,gone:x.gone.union(Set(id)),archived:false,cleanupNormal:false}else x
 | Counts(v)=>if(active(x)){...x,counts:v}else x
 | Unknown=>if(active(x)){...x,unsafe:true,archived:false,cleanupNormal:false}else x
 | SnapshotLock=>if(active(x) and x.now<x.deadline){...x,locked:true}else x
 | SnapshotUnlock=>{...x,locked:false}
 | Check=>if(x.phase==Checking and not(x.counts)){...x,phase:Draining,firstError:true,errorOrdinal:1}else x
 | Archive=>if(active(x) and not(x.locked)){...x,archived:true,cleanupNormal:complete(x) and x.now<x.deadline}else x
 | Finish=>if(active(x) and x.archived and not(x.locked))if(x.firstError){...x,phase:Raised,originalRaised:true,campaignAccepted:false}else if(x.counts and x.cleanupNormal and not(x.unsafe) and x.now<x.deadline){...x,phase:Returned,campaignAccepted:true}else{...x,phase:Raised,campaignAccepted:false}else x
 }
 action init=s'=initial
 action fire(e:Event):bool=s'=transition(s,e)
 val allProps=(s.deadline>=0 implies s.deadline==10)and(s.firstError implies s.errorOrdinal==1 and not(s.campaignAccepted))and(s.campaignAccepted implies s.phase==Returned and s.archived and s.cleanupNormal and not(s.unsafe)and s.counts)and(s.originalRaised implies s.firstError and s.archived and s.phase==Raised)and(s.cleanupNormal implies s.starts==s.terminals and s.starts==s.gone)and(s.phase==Raised or s.phase==Returned implies not(s.locked))
 action step={nondet id=1.to(3).oneOf();nondet n=0.to(12).oneOf();nondet e=Set(Begin,Start({id:id,authorized:true}),Start({id:id,authorized:false}),Terminal({id:id,normal:true,identity:true}),Terminal({id:id,normal:false,identity:true}),Terminal({id:id,normal:true,identity:false}),Gone(id),Counts(true),Counts(false),Check,SnapshotLock,SnapshotUnlock,Tick(n),Archive,Finish,Unknown).oneOf();fire(e)}
}
