module known_renderer_reload {
 type State={owned:bool,closing:bool,closed:bool,unknown:bool,failed:bool,initialized:bool,replaced:bool,dom:bool,epoch:int,policy:int,lease:int,navigation:int,snapshot:int}
 type Event=Reload|NativeSettled|StrictRetire|Replace|DOMReady|Admit|Capture|OldCallback|Unknown|Failure|LaterIntent
 var s:State
 pure val initial={owned:true,closing:false,closed:false,unknown:false,failed:false,initialized:true,replaced:false,dom:true,epoch:1,policy:1,lease:1,navigation:1,snapshot:1}
 pure def legacyReload(st:State):State={...st,unknown:true,failed:true,navigation:st.navigation+1}
 pure def reduce(st:State,e:Event):State=match e {
  | Reload => if(st.closed or st.failed)st else {...st,closing:true,initialized:false,dom:false,navigation:st.navigation+1}
  | NativeSettled => if(st.closing and not(st.unknown)){...st,owned:false} else st
  | StrictRetire => if(st.closing and not(st.owned or st.unknown)){...st,closed:true,closing:false,initialized:false} else st
  | Replace => if(st.closed and not(st.owned or st.unknown or st.failed or st.replaced)){...st,replaced:true,dom:false,navigation:st.navigation+1} else st
  | DOMReady => if(st.replaced and st.closed){...st,dom:true} else st
  | Admit => if(st.closed and st.replaced and st.dom and not(st.unknown or st.failed)){...st,epoch:st.epoch+1,closed:false,owned:true,initialized:true,replaced:false} else st
  | Capture => if(st.initialized and not(st.closed or st.closing or st.unknown or st.failed)){...st,snapshot:st.snapshot+1} else st
  | OldCallback => st
  | LaterIntent => st
  | Unknown => {...st,unknown:true,initialized:false,closing:if(st.closed)false else true}
  | Failure => {...st,failed:true,initialized:false,closing:if(st.closed)false else true}
 }
 pure def safe(st:State):bool=all{st.policy==1,st.lease==1,st.epoch>=1,st.navigation>=st.epoch,st.snapshot>=1,st.closed implies not(st.owned),st.initialized implies not(st.closing or st.closed or st.unknown or st.failed),st.replaced implies (st.closed and not(st.owned))}
 action init=s'=initial
 action fire(e:Event):bool=s'=reduce(s,e)
 action step={nondet e=Set(Reload,NativeSettled,StrictRetire,Replace,DOMReady,Admit,Capture,OldCallback,Unknown,Failure,LaterIntent).oneOf();fire(e)}
 val safety=safe(s)
}
