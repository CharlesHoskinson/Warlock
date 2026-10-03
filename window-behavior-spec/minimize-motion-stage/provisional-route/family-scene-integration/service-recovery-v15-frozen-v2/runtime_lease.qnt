module runtime_lease {
 type Event=Acquire|RootChange|LockChange|OwnerChange|Unlock|Observe|Write|Listen
 type State={acquired:bool,root:bool,lock:bool,owner:bool,held:bool,fresh:bool,write:bool,listening:bool}
 var s:State
 action init=s'={acquired:false,root:false,lock:false,owner:false,held:false,fresh:false,write:false,listening:false}
 action fire(e:Event):bool={val b={...s,write:false,listening:false};s'=match e {
 | Acquire=>if(not(s.acquired)){...b,acquired:true,root:true,lock:true,owner:true,held:true} else b
 | RootChange=>{...b,root:false,fresh:false}
 | LockChange=>{...b,lock:false,fresh:false}
 | OwnerChange=>{...b,owner:false,fresh:false}
 | Unlock=>{...b,held:false,fresh:false}
 | Observe=>{...b,fresh:s.acquired and s.root and s.lock and s.owner and s.held}
 | Write=>if(s.fresh){...b,write:true} else b
 | Listen=>if(s.fresh){...b,listening:true} else b
 }}
 val allProps=(s.write or s.listening) implies(s.acquired and s.fresh and s.root and s.lock and s.owner and s.held)
 action step={nondet e=Set(Acquire,RootChange,LockChange,OwnerChange,Unlock,Observe,Write,Listen).oneOf();fire(e)}
}
