module recovery_cancel {
 type Binding={root:int,lock:int,session:int,owner:int,lifetime:int,receipt:int,observation:int}
 type Event=Acquire|Replace(int)|Observe({complete:bool,stable:bool,compatible:bool})|Terminal({helpers:bool,renderer:bool,uncertain:bool})|RetirePersist|RetirePersistFail|Acknowledge|DurabilityFail|Dispose|Write|Crash|Reload|Expose
 type State={current:Binding,witness:Binding,fresh:bool,owned:bool,helpers:bool,renderer:bool,retired:bool,uncertain:bool,compatible:bool,cancelled:bool,durable:bool,directory:bool,disposed:bool,write:bool,exposed:bool,crashed:bool}
 var s:State
 val binding={root:1,lock:1,session:1,owner:1,lifetime:1,receipt:1,observation:1}
 action init=s'={current:binding,witness:binding,fresh:false,owned:false,helpers:false,renderer:false,retired:false,uncertain:false,compatible:true,cancelled:false,durable:false,directory:true,disposed:false,write:false,exposed:false,crashed:false}
 pure def changed(b:Binding,i:int):Binding=if(i==0){...b,root:b.root+1} else if(i==1){...b,lock:b.lock+1} else if(i==2){...b,session:b.session+1} else if(i==3){...b,owner:b.owner+1} else if(i==4){...b,lifetime:b.lifetime+1} else if(i==5){...b,receipt:b.receipt+1} else {...b,observation:b.observation+1}
 val sameOriginal=s.current.root==binding.root and s.current.lock==binding.lock and s.current.session==binding.session and s.current.lifetime==binding.lifetime and s.current.receipt==binding.receipt
 val authorized=sameOriginal and s.owned and s.fresh and s.witness==s.current and s.helpers and s.renderer and s.retired and not(s.uncertain) and not(s.crashed)
 action fire(e:Event):bool={val b={...s,write:false,exposed:false};s'=match e {
 | Acquire=>if(not(s.crashed)){...b,owned:true} else b
 | Replace(i)=>{...b,current:changed(s.current,i),fresh:false,owned:false}
 | Observe(p)=>if(s.owned and not(s.crashed)){...b,witness:s.current,fresh:p.complete and p.stable,compatible:p.compatible} else b
 | Terminal(p)=>{...b,helpers:p.helpers,renderer:p.renderer,uncertain:s.uncertain or p.uncertain,fresh:false}
 | RetirePersist=>if(s.renderer and s.helpers and not(s.uncertain) and not(s.crashed)){...b,retired:true} else b
 | RetirePersistFail=>{...b,fresh:false}
 | Acknowledge=>if(authorized and not(s.compatible) and s.directory){...b,cancelled:true,durable:true} else b
 | DurabilityFail=>{...b,fresh:false}
 | Dispose=>if(authorized and s.cancelled and s.durable){...b,directory:false,disposed:true} else b
 | Write=>if(authorized and not(s.cancelled) and s.compatible){...b,write:true} else b
 | Crash=>{...b,crashed:true,owned:false,fresh:false,helpers:false,renderer:false}
 | Reload=>{...b,crashed:false,current:{...s.current,owner:s.current.owner+1},fresh:false,owned:false}
 | Expose=>if(authorized and s.cancelled and s.durable and not(s.directory)){...b,exposed:true} else b
 }}
 val allProps=(s.disposed implies(s.cancelled and s.durable)) and (s.write implies(authorized and not(s.cancelled))) and (s.exposed implies(authorized and s.cancelled and s.durable and not(s.directory))) and (s.cancelled implies s.durable)
 action step={nondet e=Set(Acquire,Replace(0),Replace(1),Replace(2),Replace(3),Replace(4),Replace(5),Replace(6),Observe({complete:true,stable:true,compatible:false}),Observe({complete:true,stable:true,compatible:true}),Observe({complete:false,stable:true,compatible:false}),Observe({complete:true,stable:false,compatible:false}),Terminal({helpers:true,renderer:true,uncertain:false}),Terminal({helpers:true,renderer:true,uncertain:true}),Terminal({helpers:false,renderer:true,uncertain:false}),Terminal({helpers:true,renderer:false,uncertain:false}),RetirePersist,RetirePersistFail,Acknowledge,DurabilityFail,Dispose,Write,Crash,Reload,Expose).oneOf();fire(e)}
}
