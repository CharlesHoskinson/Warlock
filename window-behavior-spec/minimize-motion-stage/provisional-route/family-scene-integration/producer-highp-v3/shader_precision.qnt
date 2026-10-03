module shader_precision {
 type Capability={epoch:int,vertex:int,fragment:int,error:bool}
 type Event=Context|Inspect(Capability)|Compile(bool)|Upload|Ready
 type State={epoch:int,checked:int,compiled:int,uploaded:int,ready:bool}
 var s:State
 action init=s'={epoch:1,checked:0,compiled:0,uploaded:0,ready:false}
 action fire(e:Event):bool={val b={...s,ready:false};s'=match e {
  | Context=>{...b,epoch:s.epoch+1,checked:0,compiled:0,uploaded:0}
  | Inspect(c)=>if(c.epoch==s.epoch and c.vertex>=23 and c.fragment>=23 and not(c.error)){...b,checked:c.epoch} else {...b,checked:0,compiled:0,uploaded:0}
  | Compile(ok)=>if(ok and s.checked==s.epoch){...b,compiled:s.epoch} else {...b,compiled:0,uploaded:0}
  | Upload=>if(s.checked==s.epoch and s.compiled==s.epoch){...b,uploaded:s.epoch} else b
  | Ready=>if(s.checked==s.epoch and s.compiled==s.epoch and s.uploaded==s.epoch){...b,ready:true} else b
 }}
 val allProps=s.ready implies (s.checked==s.epoch and s.compiled==s.epoch and s.uploaded==s.epoch)
 action step={nondet e=Set(Context,Inspect({epoch:s.epoch,vertex:23,fragment:23,error:false}),Inspect({epoch:s.epoch,vertex:23,fragment:10,error:false}),Inspect({epoch:s.epoch-1,vertex:23,fragment:23,error:false}),Inspect({epoch:s.epoch,vertex:23,fragment:23,error:true}),Compile(true),Compile(false),Upload,Ready).oneOf();fire(e)}
}
