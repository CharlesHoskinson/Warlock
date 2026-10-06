module denials {
 type State={seeded:bool,open:bool,known:bool,capturing:bool,accepted:bool,retiring:bool,fresh:bool,revoked:bool,charged:bool,records:int,cleanup:bool,ready:bool,unknown:bool,pending:bool,history:List[str],commands:List[str]}
 type Event=Seed|Request|Capture|DenyLocked|DenyGone|DenyOutput|DenyLayout|ForeignDenied|StaleDenied|UnknownDenial|RepeatDenied|PendingRetire|Resume|StaleScope|Unknown|Close|Drain|Ack
 var s:State
 pure val initial={seeded:false,open:true,known:false,capturing:false,accepted:false,retiring:false,fresh:true,revoked:false,charged:false,records:0,cleanup:false,ready:true,unknown:false,pending:false,history:List("Init"),commands:List()}
 pure def label(e:Event):str=match e {
  | Seed=>"Seed" | Request=>"Request" | Capture=>"Capture" | DenyLocked=>"DenyLocked" | DenyGone=>"DenyGone"
  | DenyOutput=>"DenyOutput" | DenyLayout=>"DenyLayout" | ForeignDenied=>"ForeignDenied" | StaleDenied=>"StaleDenied"
  | UnknownDenial=>"UnknownDenial" | RepeatDenied=>"RepeatDenied" | PendingRetire=>"PendingRetire"
  | Resume=>"Resume" | StaleScope=>"StaleScope" | Unknown=>"Unknown" | Close=>"Close" | Drain=>"Drain" | Ack=>"Ack"
 }
 pure def deny(st:State):State=if(st.accepted) {...st,accepted:false,retiring:true,cleanup:true,revoked:true,ready:false,commands:List("release")} else st
 pure def reduce(st:State,e:Event):State=match e {
  | Seed=>{...st,seeded:true}
  | Request=>if(st.ready and st.open and not(st.known)) {...st,known:true,capturing:true,charged:true,records:1,commands:List("acquire")} else st
  | Capture=>{...st,capturing:false,accepted:true}
  | DenyLocked=>deny(st) | DenyGone=>deny(st) | DenyOutput=>deny(st) | DenyLayout=>deny(st) | RepeatDenied=>deny(st)
  | ForeignDenied=>st | StaleDenied=>st | UnknownDenial=>st | StaleScope=>st
  | PendingRetire=>{...st,pending:true}
  | Resume=>{...st,ready:not(st.unknown)}
  | Unknown=>{...deny(st),unknown:true,commands:List("release","reconcile")}
  | Close=>{...st,open:false}
  | Drain=>{...st,known:false,retiring:false,charged:false,pending:false,commands:List("acknowledge")}
  | Ack=>{...st,records:0,cleanup:false}
 }
 action init=s'=initial
 action fire(e:Event):bool={val updated=reduce({...s,commands:List()},e);s'={...updated,history:s.history.append(label(e))}}
 val safety=(s.records>=0 and s.records<=1) and (s.charged implies s.records==1) and (s.pending implies (s.charged and s.cleanup and s.retiring and s.known)) and (s.retiring implies s.known) and (s.unknown implies not(s.ready))
}
