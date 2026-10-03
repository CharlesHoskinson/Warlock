module recovery_constant {
 type Event=Accept(int)|Claim({complete:bool,newer:bool})|Prepare(bool)|NativeWrite|DurableResult|Endpoint(bool)|Crash|Reload|Clear
 type State={receipt:int,owned:bool,prepared:bool,operation:bool,latched:bool,effect:bool,result:bool,endpoint:bool,crashed:bool,cleared:bool}
 var s:State
 action init=s'={receipt:0,owned:false,prepared:false,operation:false,latched:false,effect:false,result:false,endpoint:false,crashed:false,cleared:false}
 action fire(e:Event):bool={val b={...s,effect:false};s'=if(s.cleared)b else match e {
 | Accept(r)=>if(r>s.receipt and not(s.prepared)){...b,receipt:r,owned:false} else b
 | Claim(p)=>if(s.receipt>0 and p.complete and not(p.newer)){...b,owned:true} else b
 | Prepare(op)=>if(s.owned and not(s.prepared) and not(s.crashed)){...b,prepared:true,operation:op,latched:op} else b
 | NativeWrite=>if(s.owned and s.prepared and not(s.crashed)){...b,effect:true} else b
 | DurableResult=>if(s.effect){...b,result:true} else b
 | Endpoint(ok)=>if(s.result and not(s.crashed)){...b,endpoint:ok} else b
 | Crash=>{...b,owned:false,crashed:true}
 | Reload=>{...b,crashed:false}
 | Clear=>if(s.owned and s.prepared and s.result and s.endpoint and not(s.crashed)){...b,cleared:true} else b
 }}
 val allProps=(s.prepared implies s.operation==s.latched) and (s.effect implies(s.owned and s.prepared and not(s.crashed))) and (s.cleared implies(s.result and s.endpoint and s.prepared))
 action step={nondet e=Set(Accept(1),Accept(2),Claim({complete:true,newer:false}),Claim({complete:false,newer:false}),Claim({complete:true,newer:true}),Prepare(true),Prepare(false),NativeWrite,DurableResult,Endpoint(true),Endpoint(false),Crash,Reload,Clear).oneOf();fire(e)}
}
