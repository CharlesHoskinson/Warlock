module context_completion_fixture {
 type State={pending:Set[int],active:bool,validated:bool,failed:bool,latest:int,finishedReceipt:int,effects:Set[int],superseded:bool,rendererUsed:bool,elapsed:int,timedOut:bool,accepted:bool}
 type Event=Context(int)|Validate(int)|Finish(int)|Fail(int)|Tick|Inspect
 pure val original=Set(1,2,3)
 pure val initial={pending:Set(1,2),active:false,validated:false,failed:false,latest:2,finishedReceipt:0,effects:Set(),superseded:false,rendererUsed:false,elapsed:0,timedOut:false,accepted:false}
 var s:State
 action init=s'=initial
 pure def cue(x:State):bool=x.pending.size()==0
 pure def ready(x:State):bool=cue(x) and not(x.active)
 pure def exactOutcome(x:State):bool=ready(x) and not(x.failed) and x.finishedReceipt==x.latest and x.effects==original and x.superseded and not(x.rendererUsed)
 pure def advance(x:State,e:Event):State=match e {
 | Context(r)=>if(x.pending.contains(r)){...x,pending:x.pending.exclude(Set(r)),active:x.active or r==x.latest,superseded:x.superseded or r!=x.latest}else x
 | Validate(r)=>if(x.active and r==x.latest and not(x.failed)){...x,validated:true}else x
 | Finish(r)=>if(x.active and x.validated and r==x.latest and not(x.failed)){...x,active:false,finishedReceipt:r,effects:original}else x
 | Fail(r)=>if(x.active and r==x.latest){...x,active:false,failed:true}else x
 | Tick=>{...x,elapsed:x.elapsed+1,timedOut:x.timedOut or x.elapsed+1>=20}
 | Inspect=>{...x,accepted:exactOutcome(x) and not(x.timedOut) and x.elapsed<20}
 }
 action fire(e:Event):bool=s'=advance(s,e)
 val allProps=s.accepted implies exactOutcome(s)
 action step={nondet e=Set(Context(1),Context(2),Validate(1),Validate(2),Finish(1),Finish(2),Fail(1),Fail(2),Tick,Inspect).oneOf();fire(e)}
}
