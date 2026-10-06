module historical {
 type State={seeded:bool,open:bool,known:bool,capturing:bool,accepted:bool,retiring:bool,fresh:bool,revoked:bool,charged:bool,records:int,cleanup:bool,ready:bool,floor:int,held:bool,history:List[str],commands:List[str]}
 type Event=Seed|Request|Capture|Stop|Close|Reopen|Retain|OldLease|MissingPublication|ForeignScope|ChangedExpiry|Unknown|Expire|Hold|CloseReader|Drain|Ack
 var s:State
 pure val initial={seeded:false,open:true,known:false,capturing:false,accepted:false,retiring:false,fresh:true,revoked:false,charged:false,records:0,cleanup:false,ready:true,floor:0,held:false,history:List("Init"),commands:List()}
 pure def label(e:Event):str=match e {
  | Seed=>"Seed" | Request=>"Request" | Capture=>"Capture" | Stop=>"Stop" | Close=>"Close" | Reopen=>"Reopen"
  | Retain=>"Retain" | OldLease=>"OldLease" | MissingPublication=>"MissingPublication" | ForeignScope=>"ForeignScope"
  | ChangedExpiry=>"ChangedExpiry" | Unknown=>"Unknown" | Expire=>"Expire" | Hold=>"Hold" | CloseReader=>"CloseReader" | Drain=>"Drain" | Ack=>"Ack"
 }
 pure def reduce(st:State,e:Event):State=match e {
  | Seed=>{...st,seeded:true}
  | Request=>{...st,known:true,capturing:true,charged:true,records:1,floor:1,commands:List("acquire")}
  | Capture=>{...st,capturing:false,accepted:true}
  | Stop=>{...st,fresh:false}
  | Close=>{...st,open:false,seeded:false}
  | Reopen=>{...st,open:false,seeded:false}
  | Retain=>if(st.accepted and not(st.cleanup) and st.ready) {...st,seeded:true,open:true} else st
  | OldLease=>st | MissingPublication=>st | ForeignScope=>st | ChangedExpiry=>st
  | Unknown=>{...st,ready:false,accepted:false,retiring:true,revoked:true,cleanup:true,commands:List("release","reconcile")}
  | Expire=>{...st,accepted:false,retiring:true,revoked:true,cleanup:true,commands:List("release")}
  | Hold=>{...st,held:true}
  | CloseReader=>{...st,held:false}
  | Drain=>if(st.held) st else {...st,known:false,retiring:false,charged:false,commands:List("acknowledge")}
  | Ack=>{...st,records:0,cleanup:false}
 }
 action init=s'=initial
 action fire(e:Event):bool={val updated=reduce({...s,commands:List()},e);s'={...updated,history:s.history.append(label(e))}}
 val safety=(s.floor>=0 and s.floor<=1) and (s.records>=0 and s.records<=1) and (s.charged implies s.records==1) and (s.retiring implies (s.known and s.cleanup)) and (s.held implies s.charged)
}
