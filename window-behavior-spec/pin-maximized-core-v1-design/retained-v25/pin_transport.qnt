module pin_transport {
 type Token={session:int,incarnation:int,epoch:int,generation:int,owner:int}
 type Event=Capture(Token)|ChangeLifetime|Reload|UnloadReload|SessionChange|Guard(bool)|Send|Reply({eof:bool,valid:bool,nativeOk:bool,after:bool})|ChangeAuthority|Idle
 pure val first={session:1,incarnation:1,epoch:1,generation:1,owner:1}
 var current:Token
 var captured:Token
 var hasCapture:bool
 var authority:bool
 var guarded:bool
 var sends:int
 var uncertain:bool
 var success:bool
 var refused:bool
 action init=all{current'=first,captured'=first,hasCapture'=false,authority'=true,guarded'=false,sends'=0,uncertain'=false,success'=false,refused'=false}
 action fire(e:Event):bool={
  val b=current
  all{current'=match e{|ChangeLifetime=>{...b,generation:b.generation+1}|Reload=>{...b,epoch:b.epoch+1}|UnloadReload=>{...b,incarnation:b.incarnation+1}|SessionChange=>{...b,session:b.session+1}|_=>b},
  captured'=match e{|Capture(t)=>if(sends==0)t else captured|_=>captured},
  hasCapture'=match e{|Capture(_)=>sends==0 or hasCapture|_=>hasCapture},
  authority'=(authority and e!=ChangeAuthority),
  guarded'=match e{|Guard(v)=>v and authority and hasCapture and captured==current and sends==0|ChangeLifetime=>false|Reload=>false|UnloadReload=>false|SessionChange=>false|ChangeAuthority=>false|_=>guarded},
  sends'=if(e==Send and guarded and authority and hasCapture and captured==current and sends==0)1 else sends,
  uncertain'=(uncertain or ((e==ChangeAuthority or e==ChangeLifetime or e==Reload or e==UnloadReload or e==SessionChange)and sends==1)or match e{|Reply(v)=>sends==1 and (not(v.eof and v.valid and v.after and authority)or captured!=current)|_=>false}),
  success'=match e{|Reply(v)=>sends==1 and not(uncertain)and v.eof and v.valid and v.nativeOk and v.after and authority and captured==current|ChangeAuthority=>false|ChangeLifetime=>false|Reload=>false|UnloadReload=>false|SessionChange=>false|_=>success},
  refused'=(refused or (e==Send and not(guarded and authority and hasCapture and captured==current and sends==0))or match e{|Guard(v)=>not(v and authority and hasCapture and captured==current and sends==0)|Reply(v)=>sends==1 and v.eof and v.valid and v.after and authority and captured==current and not(v.nativeOk)|_=>false})}
 }
 val allProps=sends>=0 and sends<=1 and (success implies sends==1 and authority and hasCapture and captured==current and not(uncertain))
 action step={nondet b=Set(true,false).oneOf();nondet e=Set(Capture(first),Capture({...first,owner:2}),ChangeLifetime,Reload,UnloadReload,SessionChange,ChangeAuthority,Guard(b),Send,Reply({eof:b,valid:true,nativeOk:true,after:true}),Idle).oneOf();fire(e)}
 action check(v:bool):bool=all{assert(v),current'=current,captured'=captured,hasCapture'=hasCapture,authority'=authority,guarded'=guarded,sends'=sends,uncertain'=uncertain,success'=success,refused'=refused}
 action prepared=fire(Capture(first)).then(fire(Guard(true)))
}
