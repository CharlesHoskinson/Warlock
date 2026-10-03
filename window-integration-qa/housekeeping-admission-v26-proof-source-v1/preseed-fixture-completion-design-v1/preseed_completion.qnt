module preseed_completion {
 type State={now:int,history:bool,created:int,removed:int,seed:bool,deadlineFailure:bool,accepted:bool,checkedAt:int,timedOut:bool,finallyEntered:bool}
 type Event=Reject|EnterFinally|ReleaseLocal|Tick(int)|CheckTerminal
 var s:State
 pure val initial={now:0,history:false,created:3,removed:0,seed:false,deadlineFailure:false,accepted:false,checkedAt:-1,timedOut:false,finallyEntered:false}
 pure def oldReady(x:State):bool=x.history
 pure def ready(x:State):bool=x.history and x.removed==3
 pure def transition(x:State,e:Event):State=match e {
 | Reject=>{...x,history:true,deadlineFailure:true}
 | EnterFinally=>if(x.history){...x,finallyEntered:true}else x
 | ReleaseLocal=>if(x.finallyEntered){...x,removed:3}else x
 | Tick(n)=>if(n>=0){...x,now:x.now+n}else x
 | CheckTerminal=>if(x.accepted or x.timedOut)x else if(x.now>=3){...x,timedOut:true}else if(ready(x)){...x,accepted:true,checkedAt:x.now}else x
 }
 action init=s'=initial
 action fire(e:Event):bool=s'=transition(s,e)
 val allProps=(s.accepted implies s.history and s.removed==3 and s.deadlineFailure and not(s.seed)and s.checkedAt>=0 and s.checkedAt<3 and not(s.timedOut))and(s.removed==3 implies s.finallyEntered)
 action step={nondet n=0.to(3).oneOf();nondet e=Set(Reject,EnterFinally,ReleaseLocal,Tick(n),CheckTerminal).oneOf();fire(e)}
}
