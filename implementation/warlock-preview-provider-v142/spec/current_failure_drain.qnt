module current_failure_drain {
 type State={failed:bool,closing:bool,owned:bool,closed:bool,exited:bool,unknown:bool,epoch:int,policy:int}
 type Event=Fault|NativeSettled|StrictRetire|Exit|LaterIntent|StaleError|Unknown
 var s:State
 pure val initial={failed:false,closing:false,owned:true,closed:false,exited:false,unknown:false,epoch:1,policy:1}
 pure def earlyExit(st:State):State={...st,exited:true}
 pure def reduce(st:State,e:Event):State=match e {
  | Fault => if(st.exited)st else {...st,failed:true,closing:true}
  | NativeSettled => if(st.closing and not(st.unknown)){...st,owned:false} else st
  | StrictRetire => if(st.closing and not(st.owned) and not(st.unknown)){...st,closed:true,closing:false} else st
  | Exit => if(st.failed and st.closed and not(st.owned) and not(st.unknown)){...st,exited:true} else st
  | LaterIntent => st
  | StaleError => st
  | Unknown => if(st.exited or st.closed)st else {...st,failed:true,closing:true,unknown:true}
 }
 pure def safe(st:State):bool=all{st.epoch==1,st.policy==1,st.closed implies not(st.owned or st.unknown),st.exited implies (st.failed and st.closed and not(st.owned or st.unknown))}
 action init=s'=initial
 action fire(e:Event):bool=s'=reduce(s,e)
 action step={nondet e=Set(Fault,NativeSettled,StrictRetire,Exit,LaterIntent,StaleError,Unknown).oneOf();fire(e)}
 val safety=safe(s)
}
