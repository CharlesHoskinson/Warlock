module batch_preview_lease {
 type Event=Stage(int)|Launch|Returned({closed:bool,outputs:bool})|Current(bool)|Publish|Release(int)|Dispose
 type State={pending:Set[int],active:bool,uncertain:bool,generated:bool,current:bool,published:bool,disposed:bool,refused:bool,launches:int}
 var s:State
 action init=s'={pending:Set(),active:false,uncertain:false,generated:false,current:true,published:false,disposed:false,refused:false,launches:0}
 action fire(e:Event):bool={s'=match e {
 | Stage(id)=>if(not(s.active) and not(s.uncertain) and not(s.disposed) and not(s.pending.contains(id))){...s,pending:s.pending.union(Set(id))} else {...s,refused:true}
 | Launch=>if(s.pending==Set(1,2,3) and s.current and not(s.disposed) and not(s.active) and not(s.uncertain) and s.launches==0){...s,active:true,launches:1} else {...s,refused:true}
 | Returned(p)=>if(s.active){...s,active:false,uncertain:not(p.closed),generated:p.closed and p.outputs} else {...s,refused:true}
 | Current(v)=>{...s,current:v}
 | Publish=>if(s.current and s.generated and not(s.active) and not(s.uncertain) and not(s.disposed) and s.pending==Set(1,2,3)){...s,published:true,pending:Set()} else {...s,refused:true}
 | Release(id)=>if(not(s.active) and not(s.uncertain)){...s,pending:s.pending.exclude(Set(id))} else {...s,refused:true}
 | Dispose=>if(s.pending==Set() and not(s.active) and not(s.uncertain)){...s,disposed:true} else {...s,refused:true}
 }}
 val allProps=s.launches<=1 and (s.generated implies not(s.uncertain) and not(s.active))
  and (s.disposed implies s.pending==Set() and not(s.active) and not(s.uncertain))
  and (s.published implies s.generated and not(s.uncertain) and not(s.active))
 action step={nondet id=1.to(3).oneOf();nondet e=Set(Stage(id),Launch,Returned({closed:true,outputs:true}),Returned({closed:true,outputs:false}),Returned({closed:false,outputs:true}),Current(true),Current(false),Publish,Release(id),Dispose).oneOf();fire(e)}
}
