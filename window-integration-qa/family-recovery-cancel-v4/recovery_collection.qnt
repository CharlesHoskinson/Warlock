module recovery_collection {
 type Event=Baseline(bool)|Archive({receipt:int,scope:int,source:int})|OldClosure({service:bool,keeper:bool,renderer:bool,uncertain:bool})|Observe({receipt:int,scope:int,source:int,complete:bool,stable:bool})|Ack({receipt:int,durable:bool,capturesPresent:bool})|Dispose|NewHelpers(bool)|Api|Lifecycle({main:bool,normal:bool,source:bool,unload:bool})|Report|Quarantine
 type State={baseline:bool,receipt:int,scope:int,source:int,oldClosed:bool,uncertain:bool,fresh:bool,ack:bool,ackWithFiles:bool,disposed:bool,helpers:bool,api:bool,main:bool,normal:bool,sourceExact:bool,unload:bool,report:bool,quarantine:bool}
 var s:State
 action init=s'={baseline:false,receipt:0,scope:0,source:0,oldClosed:false,uncertain:false,fresh:false,ack:false,ackWithFiles:false,disposed:false,helpers:false,api:false,main:false,normal:false,sourceExact:false,unload:false,report:false,quarantine:false}
 action fire(e:Event):bool={val b={...s,report:false};s'=match e {
 | Baseline(ok)=>{...b,baseline:ok}
 | Archive(p)=>if(s.receipt==0 and p.receipt>0 and p.scope>0 and p.source>0){...b,receipt:p.receipt,scope:p.scope,source:p.source} else b
 | OldClosure(p)=>{...b,oldClosed:p.service and p.keeper and p.renderer,uncertain:s.uncertain or p.uncertain,fresh:false,api:false}
 | Observe(p)=>{...b,api:false,fresh:s.oldClosed and not(s.uncertain) and p.receipt==s.receipt and p.scope==s.scope and p.source==s.source and p.complete and p.stable}
 | Ack(p)=>if(s.fresh and p.receipt==s.receipt and p.durable and p.capturesPresent and not(s.quarantine)){...b,ack:true,ackWithFiles:true} else b
 | Dispose=>if(s.ack and s.ackWithFiles and s.fresh and not(s.uncertain) and not(s.quarantine)){...b,disposed:true} else b
 | NewHelpers(ok)=>{...b,helpers:ok,api:s.api and ok}
 | Api=>if(s.ack and s.disposed and s.helpers and s.oldClosed and s.fresh and not(s.uncertain) and not(s.quarantine)){...b,api:true} else b
 | Lifecycle(p)=>{...b,main:p.main,normal:p.normal,sourceExact:p.source,unload:p.unload}
 | Report=>if(s.baseline and s.api and s.ackWithFiles and s.main and s.normal and s.sourceExact and s.unload and not(s.uncertain) and not(s.quarantine)){...b,report:true} else b
 | Quarantine=>{...b,quarantine:true,api:false,fresh:false}
 }}
 val allProps=(s.report implies(s.baseline and s.ackWithFiles and s.disposed and s.helpers and s.main and s.normal and s.sourceExact and s.unload and not(s.uncertain) and not(s.quarantine))) and (s.api implies(s.ack and s.disposed and s.helpers and s.oldClosed and s.fresh and not(s.uncertain) and not(s.quarantine)))
 action step={nondet e=Set(Baseline(true),Baseline(false),Archive({receipt:1,scope:1,source:1}),OldClosure({service:true,keeper:true,renderer:true,uncertain:false}),OldClosure({service:true,keeper:true,renderer:true,uncertain:true}),OldClosure({service:true,keeper:false,renderer:true,uncertain:false}),Observe({receipt:1,scope:1,source:1,complete:true,stable:true}),Observe({receipt:2,scope:1,source:1,complete:true,stable:true}),Observe({receipt:1,scope:2,source:1,complete:true,stable:true}),Observe({receipt:1,scope:1,source:2,complete:true,stable:true}),Observe({receipt:1,scope:1,source:1,complete:false,stable:true}),Ack({receipt:1,durable:true,capturesPresent:true}),Ack({receipt:1,durable:false,capturesPresent:true}),Ack({receipt:1,durable:true,capturesPresent:false}),Dispose,NewHelpers(true),NewHelpers(false),Api,Lifecycle({main:true,normal:true,source:true,unload:true}),Lifecycle({main:false,normal:true,source:true,unload:true}),Lifecycle({main:true,normal:false,source:true,unload:true}),Report,Quarantine).oneOf();fire(e)}
}
