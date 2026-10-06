module source {
 type State={domain:int,now:int,open:bool,known:bool,history:List[str],commands:List[str]}
 type Event=Client|Monitor|Legacy|NextClient|NextMonitor|NextLegacy|Request|Close|Malformed|Foreign|WrongStamp
 var s:State
 pure val initial={domain:-1,now:0,open:true,known:false,history:List("Init"),commands:List()}
 pure def label(e:Event):str=match e {
  | Client=>"Client" | Monitor=>"Monitor" | Legacy=>"Legacy"
  | NextClient=>"NextClient" | NextMonitor=>"NextMonitor" | NextLegacy=>"NextLegacy"
  | Request=>"Request" | Close=>"Close" | Malformed=>"Malformed" | Foreign=>"Foreign" | WrongStamp=>"WrongStamp"
 }
 pure def seed(st:State,domain:int,now:int):State=
  if(st.open and (st.domain == -1 or st.domain == domain)) {...st,domain:domain,now:if(now>st.now) now else st.now} else st
 pure def reduce(st:State,e:Event):State=match e {
  | Client=>seed(st,1,0) | Monitor=>seed(st,2,0) | Legacy=>seed(st,0,0)
  | NextClient=>seed(st,1,1) | NextMonitor=>seed(st,2,1) | NextLegacy=>seed(st,0,1)
  | Request=>if(st.domain != -1 and st.open and not(st.known)) {...st,known:true,commands:List("acquire")} else st
  | Close=>{...st,open:false,commands:if(st.known and st.open) List("cancel") else List()}
  | Malformed=>st | Foreign=>st | WrongStamp=>st
 }
 action init=s'=initial
 action fire(e:Event):bool={val cleared={...s,commands:List()};val updated=reduce(cleared,e);s'={...updated,history:s.history.append(label(e))}}
 val safety=(s.domain>=-1 and s.domain<=2) and (s.now>=0 and s.now<=1) and (s.known implies s.domain != -1)
}
