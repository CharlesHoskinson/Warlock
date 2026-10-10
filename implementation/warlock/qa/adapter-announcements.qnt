// ELM-UI-010: one Elm reducer over already authenticated matched read facts.
// Opaque bounded requests/sources; native/provider recovery and AT are separate.
module adapterAnnouncements {
  type State={next:int,waiting:int -> int,counts:int -> int,failures:Set[int],focus:int,repeats:int,discarded:int,successful:int}
  var s:State
  action init=s'={next:0,waiting:Set(1,2,3,4,5,6,7,8).mapBy(_=>0),counts:Set(1,2,3,4,5,6,7,8).mapBy(_=>0),failures:Set(),focus:7,repeats:0,discarded:0,successful:0}
  pure def canRequest(state:State, source:int):bool=state.next<8 and state.waiting.get(source)==0
  pure def requested(state:State, source:int):State={...state,next:state.next+1,waiting:state.waiting.set(source,state.next+1)}
  action request(source:int):bool=all{canRequest(s,source),s'=requested(s,source)}
  val requestWitness=s.next>0
  val safety=s.focus==7 and s.counts.keys().forall(id=>s.counts.get(id)<=1 and (s.counts.get(id)==1 implies s.failures.contains(id)))
  pure def canRead(state:State, source:int, requestId:int):bool=requestId>0 and state.waiting.get(source)==requestId
  pure def readResult(state:State, source:int, requestId:int, unavailable:bool):State={...state,waiting:state.waiting.set(source,0),counts:state.counts.set(requestId,if(unavailable)1 else 0),failures:if(unavailable)state.failures.union(Set(requestId))else state.failures,successful:state.successful+(if(unavailable)0 else 1)}
  action receipt(source:int, requestId:int, unavailable:bool):bool=all{canRead(s,source,requestId),s'=readResult(s,source,requestId,unavailable)}
  // Received duplicates/foreign receipts are real observations; only ghosts
  // change, never the business state, focus or announcement counts.
  action duplicateReceipt=all{s.failures.size()>0,s'={...s,repeats:s.repeats+1}}
  action foreignReceipt=all{s.waiting.keys().exists(source=>s.waiting.get(source)>0),s'={...s,discarded:s.discarded+1}}
  val failureWitness=s.failures.size()>0
  val successWitness=s.successful>0
  val repeatWitness=s.repeats>0
  val discardWitness=s.discarded>0
  action step={
    nondet source=Set(1,2,3,4,5,6,7,8).oneOf()
    any{request(source),receipt(source,s.waiting.get(source),true),receipt(source,s.waiting.get(source),false),duplicateReceipt,foreignReceipt}
  }
}
