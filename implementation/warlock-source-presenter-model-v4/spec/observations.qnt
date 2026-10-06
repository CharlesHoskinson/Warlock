module observations {
 type State={seeded:bool,open:bool,known:bool,capturing:bool,accepted:bool,retiring:bool,fresh:bool,revoked:bool,charged:bool,records:int,cleanup:bool,history:List[str],commands:List[str]}
 type Event=Seed|Request|Capture|Content|Scene|Stopped|Output|Privacy|Rendering|Locked|Absent|Gpu|Expire|Close|Drain|Ack|ClockOnly
 var s:State
 pure val initial={seeded:false,open:true,known:false,capturing:false,accepted:false,retiring:false,fresh:true,revoked:false,charged:false,records:0,cleanup:false,history:List("Init"),commands:List()}
 pure def label(e:Event):str=match e {
  | Seed=>"Seed" | Request=>"Request" | Capture=>"Capture" | Content=>"Content"
  | Scene=>"Scene" | Stopped=>"Stopped" | Output=>"Output" | Privacy=>"Privacy"
  | Rendering=>"Rendering" | Locked=>"Locked" | Absent=>"Absent" | Gpu=>"Gpu"
  | Expire=>"Expire" | Close=>"Close" | Drain=>"Drain" | Ack=>"Ack" | ClockOnly=>"ClockOnly"
 }
 pure def reduce(st:State,e:Event):State=match e {
  | Seed=>{...st,seeded:true}
  | Request=>{...st,known:true,capturing:true,charged:true,records:1,commands:List("acquire")}
  | Capture=>{...st,capturing:false,accepted:true}
  | Content=>{...st,fresh:false} | Scene=>{...st,fresh:false} | Stopped=>{...st,fresh:false}
  | Output=>revoke(st) | Privacy=>revoke(st) | Rendering=>revoke(st)
  | Locked=>revoke(st) | Absent=>revoke(st) | Gpu=>revoke(st)
  | Expire=>{...st,accepted:false,retiring:true,cleanup:true,commands:List("release")}
  | Close=>{...st,open:false}
  | Drain=>{...st,known:false,retiring:false,charged:false,commands:List("acknowledge")}
  | Ack=>{...st,records:0,cleanup:false}
  | ClockOnly=>st
 }
 pure def revoke(st:State):State={...st,revoked:true,accepted:false,retiring:true,cleanup:true,commands:List("release")}
 action init=s'=initial
 action fire(e:Event):bool={val cleared={...s,commands:List()};val updated=reduce(cleared,e);s'={...updated,history:s.history.append(label(e))}}
 pure def status(st:State):str=if(st.accepted and st.open) if(st.fresh) "live" else "historical" else if(st.capturing and st.open) "loading" else "unavailable"
 val safety=(s.records>=0 and s.records<=1) and (s.charged implies s.records==1) and (s.retiring implies s.known) and (s.accepted implies s.known)
}
