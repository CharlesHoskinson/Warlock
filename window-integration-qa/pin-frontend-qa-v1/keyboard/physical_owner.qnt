module physical_owner {
 type Witness={life:bool,peer:bool,seat:bool,surface:bool,core:bool,selector:bool}
 type Event=Observe(Witness)|Begin|End(int)|Change
 var ready:bool
 var running:bool
 var ended:bool
 var accepted:bool
 var failed:bool
 pure val good={life:true,peer:true,seat:true,surface:true,core:true,selector:true}
 pure def valid(w:Witness):bool=w.life and w.peer and w.seat and w.surface and w.core and w.selector
 action init=all{ready'=false,running'=false,ended'=false,accepted'=false,failed'=false}
 action fire(e:Event):bool=all{
  ready'=match e{|Observe(w)=>valid(w) and not(failed)|_=>false},
  running'=if(e==Begin and ready and not(failed)and not(running)and not(ended))true else if(match e{|End(_)=>true|_=>false})false else running,
  ended'=(ended or (match e{|End(_)=>running|_=>false})),
  accepted'=match e{|Observe(w)=>ended and valid(w)and not(failed)|_=>false},
  failed'=(failed or e==Change or (match e{|Observe(w)=>not(valid(w))|Begin=>not(ready)or running or ended|End(code)=>not(running)or code!=0|_=>false}))
 }
 val allProps=all{accepted implies ended and ready and not(failed)and not(running),running implies not(ended)}
 action step={nondet b=Set(true,false).oneOf();nondet e=Set(Observe({...good,life:b}),Observe({...good,peer:b}),Observe({...good,seat:b}),Observe({...good,surface:b}),Observe({...good,core:b}),Observe({...good,selector:b}),Begin,End(0),End(1),Change).oneOf();fire(e)}
 action check(v:bool):bool=all{assert(v),ready'=ready,running'=running,ended'=ended,accepted'=accepted,failed'=failed}
}
