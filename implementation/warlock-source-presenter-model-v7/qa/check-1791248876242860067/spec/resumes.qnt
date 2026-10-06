module resumes {
 type State={seeded:bool,known:bool,capturing:bool,accepted:bool,retiring:bool,charged:bool,records:int,cleanup:bool,ready:bool,floor:int,history:List[str],commands:List[str]}
 type Event=Seed|Request|Capture|DenyLocked|Drain|Ack|Reopen|Reserve|Recapture|Expire|OldLease|StaleScope|ForeignScope|TooCostly|LateDenied|LateAck
 var s:State
 pure val initial={seeded:false,known:false,capturing:false,accepted:false,retiring:false,charged:false,records:0,cleanup:false,ready:true,floor:0,history:List("Init"),commands:List()}
 pure def label(e:Event):str=match e {
  | Seed=>"Seed" | Request=>"Request" | Capture=>"Capture" | DenyLocked=>"DenyLocked" | Drain=>"Drain" | Ack=>"Ack"
  | Reopen=>"Reopen" | Reserve=>"Reserve" | Recapture=>"Recapture" | Expire=>"Expire" | OldLease=>"OldLease"
  | StaleScope=>"StaleScope" | ForeignScope=>"ForeignScope" | TooCostly=>"TooCostly" | LateDenied=>"LateDenied" | LateAck=>"LateAck"
 }
 pure def reduce(st:State,e:Event):State=match e {
  | Seed=>{...st,seeded:true}
  | Request=>{...st,known:true,capturing:true,charged:true,records:1,floor:1,commands:List("acquire")}
  | Capture=>{...st,capturing:false,accepted:true}
  | DenyLocked=>{...st,accepted:false,retiring:true,cleanup:true,ready:false,commands:List("release")}
  | Drain=>{...st,known:false,retiring:false,charged:false,commands:List("acknowledge")}
  | Ack=>{...st,records:0,cleanup:false}
  | Reopen=>{...st,seeded:false}
  | Reserve=>if(st.records==0 and st.floor==1) {...st,seeded:true,ready:true,known:true,capturing:true,charged:true,records:1,floor:2,commands:List("acquire")} else st
  | Recapture=>{...st,capturing:false,accepted:true}
  | Expire=>{...st,accepted:false,retiring:true,cleanup:true,commands:List("release")}
  | OldLease=>st | StaleScope=>st | ForeignScope=>st | TooCostly=>st | LateDenied=>st
  | LateAck=>{...st,commands:List("acknowledge")}
 }
 action init=s'=initial
 action fire(e:Event):bool={val updated=reduce({...s,commands:List()},e);s'={...updated,history:s.history.append(label(e))}}
 val safety=(s.records>=0 and s.records<=1) and (s.floor>=0 and s.floor<=2) and (s.charged implies s.records==1) and (s.retiring implies (s.known and s.cleanup)) and (s.accepted implies (s.known and s.charged and s.ready))
}
