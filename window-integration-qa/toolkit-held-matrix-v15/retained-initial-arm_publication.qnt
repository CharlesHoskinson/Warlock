module arm_publication {
 type State={now:int,deadline:int,helpers:int,locked:bool,proposed:bool,config:bool,authority:bool,bad:bool,published:int,publishQuiet:bool,failed:bool,lockWait:bool}
 type Event=Tick|Spawn|Finish|Propose|Acquire|Recheck|ConfigChanged|AuthorityChanged|BadTerminal|Malformed|OriginalImmediate
 var s:State
 pure val initial={now:0,deadline:8,helpers:0,locked:false,proposed:false,config:true,authority:true,bad:false,published:0,publishQuiet:false,failed:false,lockWait:false}
 action init=s'=initial
 action fire(e:Event):bool=s'=(if(s.failed or s.published>0)s else match e {
 |Tick=>if(s.locked)s else if(s.now+1>=s.deadline){...s,now:s.now+1,failed:true}else {...s,now:s.now+1}
 |Spawn=>{...s,helpers:s.helpers+1}
 |Finish=>if(s.helpers>0 and not(s.locked)){...s,helpers:s.helpers-1}else s
 |Propose=>if(not(s.locked) and s.helpers==0 and s.config and s.authority and not(s.bad)){...s,proposed:true}else s
 |Acquire=>if(s.proposed){...s,locked:true}else s
 |Recheck=>if(not(s.locked))s else if(not(s.config) or not(s.authority) or s.bad){...s,locked:false,failed:true}
   else if(s.helpers>0){...s,locked:false,proposed:false}
   else if(s.now>=s.deadline){...s,locked:false,failed:true}
   else {...s,published:1,publishQuiet:true,locked:false}
 |ConfigChanged=>{...s,config:false,failed:true,locked:false}
 |AuthorityChanged=>{...s,authority:false,failed:true,locked:false}
 |BadTerminal=>{...s,bad:true,failed:true,locked:false}
 |Malformed=>{...s,bad:true,failed:true,locked:false}
 |OriginalImmediate=>if(s.locked and s.helpers>0){...s,failed:true,locked:false}else s
 })
 val allProps=s.deadline==8 and s.published<=1 and not(s.lockWait)
   and (s.published==1 implies s.publishQuiet and s.config and s.authority and not(s.bad) and not(s.failed) and s.now<s.deadline)
 action step={nondet e=Set(Tick,Spawn,Finish,Propose,Acquire,Recheck,ConfigChanged,AuthorityChanged,BadTerminal,Malformed).oneOf();fire(e)}
}
