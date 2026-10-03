module retained_family_scope {
 type Member={address:int,stableId:int,pid:int}
 type Worker={receipt:int,generation:int}
 type State={receipt:int,generation:int,expected:Set[Member],actual:Set[Member],observed:Set[Member],freshRead:bool,contextPending:bool,visual:bool,cancelQueued:bool,acked:bool,fresh:bool,validated:bool,failed:bool,effects:int,effectProved:bool}
 type Event=Cancel|Ack|OldClearAck|FamilyChanged(Set[Member])|Observe(Worker)|Validate(Worker)|Effect|NewReceipt|Context(int)
 pure val a={address:1,stableId:11,pid:41}
 pure val b={address:2,stableId:12,pid:42}
 pure val c={address:3,stableId:13,pid:43}
 pure val original=Set(a,b,c)
 pure val closed=Set(a,b)
 pure val reused=Set(a,b,{...c,pid:99})
 pure val added=Set(a,b,c,{address:4,stableId:14,pid:44})
 pure val initial={receipt:2,generation:2,expected:original,actual:original,observed:Set(),freshRead:false,contextPending:false,visual:true,cancelQueued:false,acked:false,fresh:false,validated:false,failed:false,effects:0,effectProved:true}
 var s:State
 action init=s'=initial
 pure def current(x:State,w:Worker):bool=w.receipt==x.receipt and w.generation==x.generation
 pure def covered(x:State):bool=x.freshRead and (x.expected.isEmpty() or x.observed==x.expected)
 pure def mayValidate(x:State,w:Worker):bool=current(x,w) and x.fresh and x.acked and not(x.visual) and not(x.contextPending) and not(x.failed) and covered(x)
 pure def advance(x:State,e:Event):State=match e {
 | Cancel=>if(x.visual and not(x.cancelQueued)){...x,cancelQueued:true}else x
 | Ack=>if(x.cancelQueued and not(x.acked)){...x,visual:false,cancelQueued:false,acked:true,fresh:true,generation:x.generation+1,observed:Set(),freshRead:false,validated:false}else x
 | OldClearAck=>if(x.cancelQueued and not(x.acked)){...x,visual:false,cancelQueued:false,acked:true,fresh:true,generation:x.generation+1,expected:Set(),observed:Set(),freshRead:false,validated:false}else x
 | FamilyChanged(m)=>{...x,actual:m}
 | Observe(w)=>if(current(x,w) and x.fresh and not(x.failed)){...x,observed:x.actual,freshRead:true}else x
 | Validate(w)=>if(mayValidate(x,w)){...x,validated:true}else if(current(x,w) and x.fresh and x.freshRead and not(covered(x))){...x,failed:true}else x
 | Effect=>if(x.validated and not(x.failed) and not(x.contextPending) and x.actual==x.observed){...x,effects:x.effects+1,effectProved:x.effectProved and x.actual==original}else x
 | NewReceipt=>{...x,receipt:x.receipt+1,contextPending:true,validated:false,freshRead:false,observed:Set()}
 | Context(r)=>if(r==x.receipt){...x,contextPending:false}else x
 }
 action fire(e:Event):bool=s'=advance(s,e)
 val allProps=s.expected==original and s.effectProved and (s.validated implies covered(s))
 action step={nondet e=Set(Cancel,Ack,FamilyChanged(original),FamilyChanged(closed),FamilyChanged(reused),FamilyChanged(added),Observe({receipt:s.receipt,generation:s.generation}),Observe({receipt:s.receipt-1,generation:s.generation-1}),Validate({receipt:s.receipt,generation:s.generation}),Validate({receipt:s.receipt-1,generation:s.generation-1}),Effect,NewReceipt,Context(s.receipt),Context(s.receipt-1)).oneOf();fire(e)}
}
