// Original ELM-UI-010: one policy actor over already-admitted native identities.
// Two opaque incarnations/requests; passive focus observation is not an effect.
// No native authentication, DOM/AT, clocks, threads, or output lifecycle proof.
module notificationRelevance {
 type State={live:Set[int],expired:Set[int],focus:int,pending:int,request:int,dnd:bool,
  expiry:int -> int,rejection:int -> int,permittedExpiry:Set[int],permittedRejection:Set[int],settled:Set[int],repeats:int,discarded:int}
 var s:State
 action init=s'={live:Set(1,2),expired:Set(),focus:0,pending:0,request:0,dnd:false,
  expiry:Set(1,2).mapBy(_=>0),rejection:Set(1,2).mapBy(_=>0),permittedExpiry:Set(),permittedRejection:Set(),settled:Set(),repeats:0,discarded:0}
 action focus(id:int):bool=all{id!=s.focus,s'={...s,focus:id}}
 action invoke(id:int):bool=all{s.live.contains(id),s.pending==0,s.request<2,s'={...s,pending:id,request:s.request+1}}
 pure def isRelevant(state:State,id:int):bool=state.focus==id or state.pending==id
 pure def expireResult(state:State,id:int):State={
  val allowed=isRelevant(state,id) and not(state.dnd)
  {...state,live:state.live.exclude(Set(id)),expired:state.expired.union(Set(id)),expiry:state.expiry.set(id,if(allowed)1 else 0),permittedExpiry:if(allowed)state.permittedExpiry.union(Set(id))else state.permittedExpiry}
 }
 action expire(id:int):bool=all{s.live.contains(id),s'=expireResult(s,id)}
 pure def canRefuse(state:State,req:int):bool=state.pending>0 and state.request==req and not(state.settled.contains(req))
 action refused(req:int):bool=all{canRefuse(s,req),
  s'={...s,pending:0,settled:s.settled.union(Set(req)),rejection:s.rejection.set(req,if(s.expired.contains(s.pending) and not(s.dnd))1 else 0),permittedRejection:if(s.expired.contains(s.pending) and not(s.dnd))s.permittedRejection.union(Set(req))else s.permittedRejection}}
 action dnd(value:bool):bool=all{value!=s.dnd,s'={...s,dnd:value}}
 action duplicate=all{s.expired.size()>0 or s.settled.size()>0,s'={...s,repeats:s.repeats+1}}
 action foreign=all{s'={...s,discarded:s.discarded+1}}
 val safety=s.expiry.keys().forall(id=>s.expiry.get(id)<=1 and (s.expiry.get(id)==1 implies s.permittedExpiry.contains(id))) and s.rejection.keys().forall(id=>s.rejection.get(id)<=1 and (s.rejection.get(id)==1 implies s.permittedRejection.contains(id))) and s.live.intersect(s.expired).size()==0
 val focusedExpiryWitness=s.expired.contains(s.focus) and s.permittedExpiry.contains(s.focus)
 val invokedExpiryWitness=s.pending>0 and s.expired.contains(s.pending) and s.permittedExpiry.contains(s.pending)
 val irrelevantWitness=s.expired.exists(id=>s.expiry.get(id)==0)
 val refusalWitness=s.permittedRejection.size()>0
 val repeatWitness=s.repeats>0
 action step={nondet id=Set(1,2).oneOf()
  any{focus(id),focus(0),invoke(id),expire(id),refused(s.request),dnd(true),dnd(false),duplicate,foreign}}
}
