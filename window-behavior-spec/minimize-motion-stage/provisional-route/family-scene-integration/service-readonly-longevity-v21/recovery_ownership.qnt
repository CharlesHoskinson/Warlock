module recovery_ownership {
 type Event=Reserve|Acquire(bool)|Gate({exact:bool,durable:bool})|Release|Crash|Observe({sameStart:bool,material:bool})|Signal|Gone|Directory({same:bool,private:bool})|Delete|Close
 type State={reserved:bool,acquired:bool,gated:bool,durable:bool,released:bool,crashed:bool,sameStart:bool,material:bool,gone:bool,directory:bool,private:bool,signal:bool,deleted:bool,closed:bool}
 var s:State
 action init=s'={reserved:false,acquired:false,gated:false,durable:false,released:false,crashed:false,sameStart:false,material:false,gone:false,directory:false,private:false,signal:false,deleted:false,closed:false}
 action fire(e:Event):bool={val b={...s,signal:false};s'=if(s.closed)b else match e {
 | Reserve=>{...b,reserved:true}
 | Acquire(ok)=>if(s.reserved and not(s.acquired)){...b,acquired:ok} else b
 | Gate(p)=>if(s.acquired and not(s.gated) and p.exact){...b,gated:true,durable:p.durable} else b
 | Release=>if(s.gated and s.durable){...b,released:true} else b
 | Crash=>if(s.deleted)b else {...b,crashed:true,sameStart:false,material:false,directory:false,private:false}
 | Observe(p)=>if(s.crashed and s.gated and s.durable and not(s.gone)){...b,sameStart:p.sameStart,material:p.material,gone:not(p.sameStart)} else b
 | Signal=>if(s.crashed and s.gated and s.durable and s.sameStart and s.material and not(s.gone)){...b,signal:true} else b
 | Gone=>if(s.crashed and s.gated and s.durable){...b,gone:true,sameStart:false} else b
 | Directory(p)=>if(s.crashed and s.acquired and not(s.deleted)){...b,directory:p.same,private:p.private} else b
 | Delete=>if(s.crashed and s.gone and s.acquired and s.directory and s.private){...b,deleted:true} else b
 | Close=>if(s.gone and s.deleted){...b,closed:true} else b
 }}
 val allProps=(s.released implies(s.gated and s.durable)) and (s.signal implies(s.crashed and s.gated and s.durable and s.sameStart and s.material and not(s.gone))) and (s.deleted implies(s.crashed and s.gone and s.acquired and s.directory and s.private)) and (s.closed implies(s.gone and s.deleted))
 action step={nondet e=Set(Reserve,Acquire(true),Acquire(false),Gate({exact:true,durable:true}),Gate({exact:true,durable:false}),Gate({exact:false,durable:true}),Release,Crash,Observe({sameStart:true,material:true}),Observe({sameStart:true,material:false}),Observe({sameStart:false,material:true}),Signal,Gone,Directory({same:true,private:true}),Directory({same:false,private:true}),Directory({same:true,private:false}),Delete,Close).oneOf();fire(e)}
}
