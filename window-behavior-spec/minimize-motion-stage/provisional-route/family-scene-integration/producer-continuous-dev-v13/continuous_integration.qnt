module continuous_integration {
 type Frame={token:int,epoch:int,generation:int,order:int,output:int,pos:int,vel:int}
 type Event=Sample(Frame)|Submit(Frame)|Swap(bool)|Feedback({generation:int,epoch:int})|Retarget({token:int,lower0:int,upper0:int,lower1:int,upper1:int})|Promote|Start|Discard|OutputChange|Reduce|Cancel
 type State={token:int,epoch:int,generation:int,order:int,active:bool,promoted:bool,running:bool,starts:int,issued:Frame,hasIssue:bool,pending:Frame,hasPending:bool,swapped:bool,early:bool,accepted:Set[int],origins:List[Frame],originPos:List[int],originVel:List[int],carryPos:List[int],carryVel:List[int],carried:bool,duration:int}
 var s:State
 pure def frame(token:int,epoch:int,generation:int,output:int,pos:int,vel:int):Frame={token:token,epoch:epoch,generation:generation,order:1,output:output,pos:pos,vel:vel}
 pure val initial:State={token:1,epoch:1,generation:1,order:1,active:true,promoted:false,running:false,starts:0,issued:frame(1,1,1,0,0,0),hasIssue:false,pending:frame(1,1,1,0,0,0),hasPending:false,swapped:false,early:false,accepted:Set(),origins:List(frame(1,1,1,0,0,0),frame(1,1,1,1,0,0)),originPos:List(0,0),originVel:List(0,0),carryPos:List(0,0),carryVel:List(0,0),carried:false,duration:4}
 pure def current(b:State,f:Frame):bool=b.active and f.token==b.token and f.epoch==b.epoch and f.generation==b.generation and f.order==b.order and f.output>=0 and f.output<2
 pure def retire(b:State):State={...b,active:false,promoted:false,hasIssue:false,hasPending:false,accepted:Set()}
 pure def record(b:State):State=if(current(b,b.pending) and b.swapped){...b,origins:b.origins.replaceAt(b.pending.output,b.pending),accepted:b.accepted.union(Set(b.pending.output)),hasPending:false,early:false} else b
 action init=s'=initial
 action fire(e:Event):bool={
  s'=match e {
   | Sample(f)=>if(current(s,f) and not(s.hasPending)){...s,issued:f,hasIssue:true} else s
   | Submit(f)=>if(s.hasIssue and f==s.issued and current(s,f) and not(s.hasPending)){...s,pending:f,hasPending:true,hasIssue:false,swapped:false,early:false} else s
   | Swap(ok)=>if(s.hasPending){if(not(ok))retire(s) else if(s.early)record({...s,swapped:true}) else {...s,swapped:true}} else s
   | Feedback(f)=>if(s.hasPending and f.generation==s.pending.generation and f.epoch==s.pending.epoch and current(s,s.pending)){if(s.swapped)record(s) else {...s,early:true}} else s
   | Retarget(p)=>if(s.active and not(s.hasPending) and s.accepted==Set(0,1) and p.token>s.token){
      val lower=if(p.lower0>p.lower1)p.lower0 else p.lower1
      val upper=if(p.upper0<p.upper1)p.upper0 else p.upper1
      if(lower>0 and lower<=upper){...s,token:p.token,epoch:s.epoch+1,promoted:false,running:true,starts:1,hasIssue:false,accepted:Set(),originPos:List(s.origins.nth(0).pos,s.origins.nth(1).pos),originVel:List(s.origins.nth(0).vel,s.origins.nth(1).vel),carryPos:List(s.origins.nth(0).pos,s.origins.nth(1).pos),carryVel:List(s.origins.nth(0).vel,s.origins.nth(1).vel),carried:true,duration:upper} else retire(s)
     } else s
   | Promote=>if(s.active){...s,promoted:true} else s
   | Start=>if(s.active and s.promoted and s.accepted==Set(0,1) and not(s.running)){...s,running:true,starts:1} else s
   | Discard=>retire(s)
   | OutputChange=>{...retire(s),generation:s.generation+1}
   | Reduce=>retire(s)
   | Cancel=>retire(s)
  }
 }
 val exactOriginPair=s.carried implies s.originPos==s.carryPos and s.originVel==s.carryVel
 val oneStart=s.starts>=0 and s.starts<=1
 val pendingBound=s.hasPending implies current(s,s.pending)
 val positiveSharedDuration=s.active implies s.duration>0
 val noRetiredAuthority=not(s.active) implies not(s.promoted) and s.accepted==Set()
 val allProps=exactOriginPair and oneStart and pendingBound and positiveSharedDuration and noRetiredAuthority
 action step={
  val f=frame(s.token,s.epoch,s.generation,0,12,-4)
  nondet e=Set(Sample(f),Sample({...f,output:1,pos:23,vel:5}),Submit(s.issued),Submit({...s.issued,vel:99}),Swap(true),Swap(false),Feedback({generation:s.generation,epoch:s.epoch}),Feedback({generation:s.generation-1,epoch:s.epoch}),Retarget({token:s.token+1,lower0:1,upper0:8,lower1:2,upper1:5}),Retarget({token:s.token+1,lower0:6,upper0:8,lower1:1,upper1:5}),Promote,Start,Discard,OutputChange,Reduce,Cancel).oneOf()
  fire(e)
 }
}
