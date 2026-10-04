module accepted {
 type State = { proof: bool, requestedA: int, requestedG: int, acceptedA: int, acceptedG: int, dirty: bool, phase: str, reserved: bool, history: str, effects: int, request: int, generation: int, releaseA: int, releaseG: int }
 type Event = Proof | ActionReply | GeometryReply | Dirty | NextBatch | Release((int,int)) | Noop
 var s: State
 pure val initial = {proof:false,requestedA:0,requestedG:0,acceptedA:0,acceptedG:0,dirty:false,phase:"Ready",reserved:true,history:"Unknown",effects:0,request:12,generation:15,releaseA:0,releaseG:0}
 pure def nextBatch(state:State):State = {...state,requestedA:state.requestedA+1,requestedG:state.requestedG+1,dirty:false,phase:"Reconciling"}
 pure def drain(state:State):State = if (state.dirty and state.acceptedA>0 and state.acceptedG>0) nextBatch(state) else state
 pure def reduce(state:State,event:Event):State = match event {
  | Proof => if (not(state.proof)) {...state,proof:true,requestedA:1,requestedG:1,acceptedA:0,acceptedG:0} else state
  | ActionReply => if (state.proof and state.requestedA>0) drain({...state,acceptedA:state.requestedA,phase:"Ready"}) else state
  | GeometryReply => if (state.proof and state.requestedG>0) drain({...state,acceptedG:state.requestedG}) else state
  | Dirty => state.with("dirty",true)
  | NextBatch => if (state.proof) nextBatch(state) else state
  | Release(pair) => { val (a,g)=pair
      if (state.proof and state.reserved and a>0 and g>0 and true) {...state,reserved:false,releaseA:a,releaseG:g} else state }
  | Noop => state
 }
 action init = s'=initial
 action fire(event) = s'=reduce(s,event)
 action boundedNext = all {s.requestedA<3,s.requestedG<3,fire(NextBatch)}
 action step = any {fire(Proof),fire(ActionReply),fire(GeometryReply),fire(Dirty),boundedNext,fire(Release((1,1))),fire(Release((1,2))),fire(Release((2,1))),fire(Release((2,2))),fire(Noop)}
 val safety = s.history=="Unknown" and s.effects==0 and s.request==12 and s.generation==15 and (s.reserved or (s.releaseA>0 and s.releaseG>0 and s.proof))
 action checkReleased = all {assert(not(s.reserved) and safety),fire(Noop)}
 action checkBlocked = all {assert(s.reserved and safety),fire(Noop)}
 run noProofTest = init.then(fire(Release((1,1)))).then(checkBlocked)
 run missingGeometryTest = init.then(fire(Proof)).then(fire(ActionReply)).then(fire(Release((1,1)))).then(checkBlocked)
 run completedPairTest = init.then(fire(Proof)).then(fire(ActionReply)).then(fire(GeometryReply)).then(fire(Release((1,1)))).then(checkReleased)
 run pendingBatchTest = init.then(fire(Proof)).then(fire(ActionReply)).then(fire(GeometryReply)).then(fire(NextBatch)).then(fire(Release((1,1)))).then(checkReleased)
 run finalGeometryDrainTest = init.then(fire(Proof)).then(fire(ActionReply)).then(fire(Dirty)).then(fire(GeometryReply)).then(fire(Release((1,1)))).then(checkReleased)
 run finalActionDrainTest = init.then(fire(Proof)).then(fire(GeometryReply)).then(fire(Dirty)).then(fire(ActionReply)).then(fire(Release((1,1)))).then(checkReleased)
 run acceptedNewActionTest = init.then(fire(Proof)).then(fire(ActionReply)).then(fire(GeometryReply)).then(fire(NextBatch)).then(fire(ActionReply)).then(fire(Release((1,1)))).then(checkBlocked)
 run acceptedNewGeometryTest = init.then(fire(Proof)).then(fire(ActionReply)).then(fire(GeometryReply)).then(fire(NextBatch)).then(fire(GeometryReply)).then(fire(Release((1,1)))).then(checkBlocked)
 run latestPairTest = init.then(fire(Proof)).then(fire(ActionReply)).then(fire(GeometryReply)).then(fire(NextBatch)).then(fire(ActionReply)).then(fire(GeometryReply)).then(fire(Release((2,2)))).then(checkReleased)
}
