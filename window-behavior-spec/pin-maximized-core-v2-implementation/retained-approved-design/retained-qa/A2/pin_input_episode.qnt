module pin_input_episode {
 type Key={code:int,state:int}
 type Row={code:int,state:int,owner:bool,scope:bool,typed:bool,fresh:bool}
 type Event=Plan(int)|Begin|Write|DriverExit|Deliver(Row)|Finish|Receipt(bool)|Observe(bool)|Accept
 type State={route:int,begun:bool,count:int,valid:bool,delivered:bool,receipt:bool,observed:bool,accepted:bool}
 pure def plan(route:int):List[Key]=if(route==1)List({code:272,state:1},{code:272,state:0})else if(route==2)List({code:125,state:1},{code:25,state:1},{code:25,state:0},{code:125,state:0})else List({code:125,state:1},{code:29,state:1},{code:20,state:1},{code:20,state:0},{code:29,state:0},{code:125,state:0})
 var s:State
 action init=s'={route:0,begun:false,count:0,valid:true,delivered:false,receipt:false,observed:false,accepted:false}
 action fire(e:Event):bool={val b={...s,accepted:false};s'=match e {
 |Plan(route)=>if(s.route==0 and Set(1,2,3).contains(route)){...b,route:route}else {...b,valid:false,delivered:false}
 |Begin=>if(s.route>0 and not(s.begun)){...b,begun:true}else {...b,valid:false,delivered:false}
 |Write=>b
 |DriverExit=>b
 |Deliver(row)=>if(s.begun and s.count<plan(s.route).length() and not(s.delivered)){...b,count:s.count+1,valid:s.valid and row.owner and row.scope and row.typed and row.fresh and {code:row.code,state:row.state}==plan(s.route).nth(s.count)}else {...b,valid:false,delivered:false}
 |Finish=>{...b,delivered:s.begun and s.route>0 and s.valid and s.count==plan(s.route).length()}
 |Receipt(ok)=>{...b,receipt:ok}
 |Observe(ok)=>{...b,observed:ok}
 |Accept=>{...b,accepted:s.delivered and s.valid and s.receipt and s.observed}
 }}
 val allProps=s.accepted implies s.route>0 and s.begun and s.valid and s.delivered and s.count==plan(s.route).length() and s.receipt and s.observed
 action step={nondet code=Set(272,125,25,29,20,0).oneOf();nondet state=Set(0,1,2).oneOf();nondet ok=Set(true,false).oneOf();nondet route=Set(0,1,2,3,4).oneOf();nondet e=Set(Plan(route),Begin,Write,DriverExit,Deliver({code:code,state:state,owner:ok,scope:ok,typed:ok,fresh:ok}),Finish,Receipt(ok),Observe(ok),Accept).oneOf();fire(e)}
}
