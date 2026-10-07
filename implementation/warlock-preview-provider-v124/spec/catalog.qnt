module catalog {
 type State = {present:bool,scoped:bool,demand:bool,pending:bool,known:int,minimized:bool,request:int,cancels:int,history:List[str]}
 type Event = Catalog | Minimized | Remove | Stale | Foreign | Start | Receipt
 var s:State
 pure def label(event:Event):str=match event { |Catalog=>"Catalog" |Minimized=>"Minimized" |Remove=>"Remove" |Stale=>"Stale" |Foreign=>"Foreign" |Start=>"Start" |Receipt=>"Receipt" }
 pure def reduce(st:State,event:Event):State=match event {
  |Catalog=>if(st.scoped){...st,request:st.request+1} else {...st,present:true,minimized:false,request:st.request+1}
  |Minimized=>if(st.scoped){...st,request:st.request+1} else {...st,present:true,minimized:true,request:st.request+1}
  |Remove=>if(st.scoped){...st,demand:false,pending:st.pending or st.known>0,request:st.request+1,cancels:st.cancels+(if(st.known>0 and not(st.pending))1 else 0)} else {...st,present:false,minimized:false,request:st.request+1}
  |Start=>{...st,scoped:true,demand:true,known:1}
  |Receipt=>{...st,pending:false,known:0}
  |_=>st
 }
 action init=s'={present:false,scoped:false,demand:false,pending:false,known:0,minimized:false,request:0,cancels:0,history:[]}
 action fire(event:Event):bool=all {
  if(event==Start) s.present and not(s.scoped) and s.request>0 else if(event==Receipt) s.pending else if(event==Foreign) s.request>0 else true,
  val updated=reduce(s,event);s'={...updated,history:s.history.append(label(event))}
 }
 action step={nondet event=Set(Catalog,Minimized,Remove,Stale,Foreign,Start,Receipt).oneOf();fire(event)}
 val safety=s.known>=0 and s.known<=1 and s.cancels>=0 and s.cancels<=1 and (s.pending implies s.known==1) and (s.demand implies s.scoped) and (s.scoped implies s.present) and (not(s.scoped) implies s.known==0)
}
