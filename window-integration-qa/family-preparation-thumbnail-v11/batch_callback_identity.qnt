module batch_callback_identity {
 type Callback={function:int,owner:int,source:bool}
 type Binding={moduleToken:int,ownerToken:int,callbacks:int->Callback}
 type Event=Link(Binding)|Original(bool)|Confirm(Binding)|Accept|Refuse
 type State={binding:Binding,linked:bool,original:bool,final:bool,accepted:bool,refused:bool}
 pure val roles=1.to(6)
 pure def expectedOwner(role:int):int=if(role==6)2 else 1
 pure val callbacks=roles.mapBy(role=>{function:role,owner:expectedOwner(role),source:true})
 pure val good={moduleToken:23,ownerToken:1,callbacks:callbacks}
 pure def valid(p:Binding):bool=p.moduleToken==23 and p.ownerToken==1 and p.callbacks.keys()==roles and roles.forall(role=>p.callbacks.get(role)==callbacks.get(role))
 var s:State
 action init=s'={binding:good,linked:false,original:false,final:false,accepted:false,refused:false}
 action fire(e:Event):bool=s'=if(s.refused)s else match e {
 |Link(p)=>if(valid(p) and (not(s.linked) or p==s.binding)){...s,binding:p,linked:true,final:false,accepted:false}else {...s,refused:true,accepted:false}
 |Original(ok)=>{...s,original:ok,accepted:false}
 |Confirm(p)=>if(s.linked and valid(p) and p==s.binding){...s,final:true}else {...s,refused:true,accepted:false}
 |Accept=>{...s,accepted:s.linked and s.original and s.final}
 |Refuse=>{...s,refused:true,accepted:false}
 }
 val allProps=s.accepted implies s.linked and s.original and s.final and valid(s.binding) and not(s.refused)
 action step={nondet role=roles.oneOf();nondet fn=roles.oneOf();nondet owner=Set(1,2,3).oneOf();nondet source=Set(true,false).oneOf();val p={...good,callbacks:callbacks.set(role,{function:fn,owner:owner,source:source})};nondet e=Set(Link(p),Original(source),Confirm(p),Accept,Refuse).oneOf();fire(e)}
}
