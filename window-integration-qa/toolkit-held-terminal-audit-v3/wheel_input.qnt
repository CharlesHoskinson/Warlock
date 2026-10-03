module wheel_input {
 type State={held:bool,auth:bool,kind:bool,pending:bool,failed:bool,wheels:int,accepted:int,safe:bool}
 var s:State
 action init=s'={held:false,auth:true,kind:true,pending:false,failed:false,wheels:0,accepted:0,safe:true}
 action configure(held:bool,auth:bool,kind:bool):bool=s'={...s,held:held,auth:auth,kind:kind}
 action wheel(literal:bool):bool=s'=if(s.failed)s else if(not(s.pending) and literal and s.auth and s.kind and not(s.held)){...s,pending:true,wheels:s.wheels+1,safe:s.safe and literal and s.auth and s.kind and not(s.held)} else {...s,failed:true}
 action sync(exact:bool):bool=s'=if(s.failed)s else if(s.pending and not(exact)){...s,failed:true} else {...s,pending:false,accepted:if(s.pending)s.accepted+1 else s.accepted}
 action other=s'=if(s.pending){...s,failed:true} else s
 action finish=s'=if(s.pending){...s,failed:true} else s
 val invariant=s.safe and s.accepted<=s.wheels and (s.accepted==s.wheels or s.pending or s.failed)
 action step=any{nondet h=Set(true,false).oneOf();nondet a=Set(true,false).oneOf();nondet k=Set(true,false).oneOf();configure(h,a,k),wheel(true),wheel(false),sync(true),sync(false),other,finish}
}
