module preparation_profile {
 type Event=Install(bool)|Begin(int)|End(int)|Fault|ReplaceSource|Stop|Persist(bool)
 type State={installed:bool,stopped:bool,active:Set[int],seen:Set[int],events:int,fault:bool,sourceStable:bool,durable:bool,complete:bool,nativeAuthority:bool}
 var s:State
 val limit=8
 action init=s'={installed:false,stopped:false,active:Set(),seen:Set(),events:0,fault:false,sourceStable:true,durable:false,complete:false,nativeAuthority:false}
 action fire(e:Event):bool={s'=match e {
 | Install(clear)=>if(not(s.installed) and not(s.stopped) and clear and not(s.fault)){...s,installed:true} else {...s,fault:true,complete:false}
 | Begin(id)=>if(s.installed and not(s.stopped) and not(s.fault)){if(s.events<limit and not(s.seen.contains(id))){...s,active:s.active.union(Set(id)),seen:s.seen.union(Set(id)),events:s.events+1} else {...s,fault:true,complete:false}} else s
 | End(id)=>if(s.installed and not(s.stopped) and not(s.fault)){if(s.events<limit and s.active.contains(id)){...s,active:s.active.exclude(Set(id)),events:s.events+1} else {...s,fault:true,complete:false}} else s
 | Fault=>{...s,fault:true,complete:false}
 | ReplaceSource=>{...s,sourceStable:false,complete:false}
 | Stop=>{...s,stopped:true,installed:false,complete:false}
 | Persist(ok)=>if(s.stopped and ok){...s,durable:true,complete:not(s.fault) and s.sourceStable and s.active.size()==0} else {...s,fault:true,complete:false}
 }}
 val allProps=not(s.nativeAuthority) and s.events<=limit and s.active.subseteq(s.seen) and (s.complete implies s.stopped and not(s.installed) and s.durable and s.sourceStable and not(s.fault) and s.active.size()==0)
 action step={nondet id=1.to(5).oneOf();nondet e=Set(Install(true),Install(false),Begin(id),End(id),Fault,ReplaceSource,Stop,Persist(true),Persist(false)).oneOf();fire(e)}
}
