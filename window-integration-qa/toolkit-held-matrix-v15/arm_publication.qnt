module arm_publication {
 type State={now:int,deadline:int,helpers:int,locked:bool,proposed:bool,config:bool,authority:bool,bad:bool,published:int,publishQuiet:bool,failed:bool,lockWait:bool,externalLock:bool,attempts:int,busyAttempts:int}
 type Event=Tick|Spawn|Finish|Propose|Acquire|Recheck|ConfigChanged|AuthorityChanged|BadTerminal|Malformed|HoldExternal|ReleaseExternal|OriginalBlocking|OriginalImmediate
 var s:State
 pure val initial={now:0,deadline:8,helpers:0,locked:false,proposed:false,config:true,authority:true,bad:false,published:0,publishQuiet:false,failed:false,lockWait:false,externalLock:false,attempts:0,busyAttempts:0}
 action init=s'=initial
 pure def advance(x:State,e:Event):State=(if(x.failed or x.published>0)x else match e {
 |Tick=>if(x.now+1>=x.deadline){...x,now:x.now+1,failed:true,locked:false,lockWait:false}else {...x,now:x.now+1}
 |Spawn=>{...x,helpers:x.helpers+1}
 |Finish=>if(x.helpers>0 and not(x.locked)){...x,helpers:x.helpers-1}else x
 |Propose=>if(not(x.locked) and x.helpers==0 and x.config and x.authority and not(x.bad)){...x,proposed:true}else x
 |Acquire=>if(x.proposed and not(x.locked)){...x,locked:not(x.externalLock),attempts:x.attempts+1,busyAttempts:x.busyAttempts+(if(x.externalLock)1 else 0)}else x
 |HoldExternal=>if(not(x.locked)){...x,externalLock:true}else x
 |ReleaseExternal=>{...x,externalLock:false}
 |OriginalBlocking=>if(x.proposed and x.externalLock){...x,lockWait:true}else x
 |Recheck=>if(not(x.locked))x else if(not(x.config) or not(x.authority) or x.bad){...x,locked:false,failed:true}
   else if(x.helpers>0){...x,locked:false,proposed:false}
   else if(x.now>=x.deadline){...x,locked:false,failed:true}
   else {...x,published:1,publishQuiet:true,locked:false}
 |ConfigChanged=>{...x,config:false,failed:true,locked:false}
 |AuthorityChanged=>{...x,authority:false,failed:true,locked:false}
 |BadTerminal=>{...x,bad:true,failed:true,locked:false}
 |Malformed=>{...x,bad:true,failed:true,locked:false}
 |OriginalImmediate=>if(x.locked and x.helpers>0){...x,failed:true,locked:false}else x
 })
 action fire(e:Event):bool=s'=advance(s,e)
 val allProps=s.deadline==8 and s.published<=1 and not(s.lockWait) and s.busyAttempts<=s.attempts
   and (s.locked implies not(s.externalLock) and s.now<s.deadline) and (s.failed implies not(s.locked))
   and (s.published==1 implies s.publishQuiet and s.config and s.authority and not(s.bad) and not(s.failed) and s.now<s.deadline)
 action step={nondet e=Set(Tick,Spawn,Finish,Propose,Acquire,Recheck,ConfigChanged,AuthorityChanged,BadTerminal,Malformed,HoldExternal,ReleaseExternal).oneOf();fire(e)}
}
