module shared_process_drain {
 type State={failed:bool,processFailed:bool,closing:bool,owned:bool,closed:bool,unknown:bool,recovery:bool,exited:bool,policy:int,epoch:int,navigation:int,snapshot:int}
 type Event=Signal|DeliveryError|NativeSettled|StrictRetire|Recovery|Exit|Unknown|LaterIntent|OldEvent
 var s:State
 pure val initial={failed:false,processFailed:false,closing:false,owned:true,closed:false,unknown:false,recovery:false,exited:false,policy:1,epoch:1,navigation:1,snapshot:1}
 pure def earlyRecovery(st:State):State={...st,recovery:true}
 pure def reduce(st:State,e:Event):State=match e {
  | Signal => if(st.exited)st else {...st,failed:true,processFailed:true,closing:if(st.closed)false else true}
  | DeliveryError => if(st.exited)st else {...st,failed:true,closing:if(st.closed)false else true}
  | NativeSettled => if(st.closing and not(st.unknown)){...st,owned:false} else st
  | StrictRetire => if(st.closing and not(st.owned or st.unknown)){...st,closed:true,closing:false} else st
  | Recovery => if(st.processFailed and st.closed and not(st.owned or st.unknown)){...st,recovery:true} else st
  | Exit => if(st.failed and st.closed and not(st.owned or st.unknown)){...st,exited:true} else st
  | Unknown => if(st.closed or st.exited)st else {...st,unknown:true,failed:true,closing:true}
  | LaterIntent => st
  | OldEvent => st
 }
 pure def safe(st:State):bool=all{st.policy==1,st.epoch==1,st.navigation==1,st.snapshot==1,st.closed implies not(st.owned or st.unknown),st.recovery implies (st.processFailed and st.failed and st.closed and not(st.owned or st.unknown)),st.exited implies (st.failed and st.closed and not(st.owned or st.unknown))}
 action init=s'=initial
 action fire(e:Event):bool=s'=reduce(s,e)
 action step={nondet e=Set(Signal,DeliveryError,NativeSettled,StrictRetire,Recovery,Exit,Unknown,LaterIntent,OldEvent).oneOf();fire(e)}
 val safety=safe(s)
}
