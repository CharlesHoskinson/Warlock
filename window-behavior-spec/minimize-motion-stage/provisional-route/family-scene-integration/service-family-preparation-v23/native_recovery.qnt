module native_recovery {
 type Event=Load({session:bool,provenance:bool,receipt:int})|RetireResources(bool)|Prepare(bool)|Observe({exact:bool,family:bool,context:bool,receipt:int})|Settle|Revoke|Clear|Listen|Crash
 type State={loaded:bool,latest:int,resources:bool,durable:bool,observed:int,exact:bool,family:bool,context:bool,effect:bool,effectReceipt:int,settled:bool,cleared:bool,listening:bool}
 var s:State
 action init=s'={loaded:false,latest:0,resources:false,durable:false,observed:0,exact:false,family:false,context:false,effect:false,effectReceipt:0,settled:false,cleared:false,listening:false}
 action fire(e:Event):bool={val b={...s,effect:false};s'=match e {
  | Load(p)=>if(p.session and p.provenance and p.receipt>0){...b,loaded:true,latest:p.receipt,resources:false,durable:false,observed:0,settled:false,cleared:false,listening:false} else b
  | RetireResources(ok)=>if(s.loaded){...b,resources:ok,observed:0} else b
  | Prepare(ok)=>if(s.loaded and s.resources){...b,durable:ok,observed:0} else b
  | Observe(p)=>if(s.loaded and s.resources and s.durable){...b,observed:p.receipt,exact:p.exact,family:p.family,context:p.context} else b
  | Settle=>if(s.loaded and s.resources and s.durable and s.observed==s.latest and s.exact and s.family and s.context){...b,effect:true,effectReceipt:s.latest,settled:true} else b
  | Revoke=>{...b,observed:0,exact:false,family:false,context:false}
  | Clear=>if(s.loaded and s.resources and s.durable and s.settled and s.observed==s.latest and s.exact and s.family and s.context){...b,cleared:true} else b
  | Listen=>if(s.cleared){...b,listening:true} else b
  | Crash=>{...b,loaded:false,resources:false,durable:false,observed:0,settled:false,cleared:false,listening:false}
 }}
 val authority=s.effect implies(s.loaded and s.resources and s.durable and s.exact and s.family and s.context and s.observed==s.latest and s.effectReceipt==s.latest)
 val allProps=authority and (s.listening implies s.cleared)
 action step={nondet e=Set(Load({session:true,provenance:true,receipt:2}),Load({session:false,provenance:true,receipt:2}),Load({session:true,provenance:false,receipt:2}),RetireResources(true),RetireResources(false),Prepare(true),Prepare(false),Observe({exact:true,family:true,context:true,receipt:2}),Observe({exact:false,family:true,context:true,receipt:2}),Observe({exact:true,family:false,context:true,receipt:2}),Observe({exact:true,family:true,context:false,receipt:2}),Observe({exact:true,family:true,context:true,receipt:1}),Settle,Revoke,Clear,Listen,Crash).oneOf();fire(e)}
}
