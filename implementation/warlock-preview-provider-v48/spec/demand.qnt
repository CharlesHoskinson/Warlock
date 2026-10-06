module demand {
 type State = {latest:int,captured:int,issuedLease:int,busy:bool,owners:int,visible:bool,now:int,lastStart:int,lease:int,floor:int,history:List[str]}
 type Event = Content | Tick | Start | Finish | Drain | Close | Reopen
 var s:State
 pure val initial={latest:1,captured:0,issuedLease:0,busy:false,owners:0,visible:true,now:1,lastStart:0,lease:1,floor:0,history:List("Init")}
 pure def label(e:Event):str=match e { | Content=>"Content" | Tick=>"Tick" | Start=>"Start" | Finish=>"Finish" | Drain=>"Drain" | Close=>"Close" | Reopen=>"Reopen" }
 pure def reduce(st:State,e:Event):State=match e {
  | Content=>{...st,latest:st.latest+1}
  | Tick=>{...st,now:st.now+1}
  | Start=>if(st.visible and not(st.busy) and (st.latest!=st.captured or st.lease!=st.issuedLease) and (st.lastStart==0 or st.now-st.lastStart>=2) and st.owners<2) {...st,captured:st.latest,issuedLease:st.lease,busy:true,owners:st.owners+1,lastStart:st.now,floor:st.floor+1} else st
  | Finish=>{...st,busy:false}
  | Drain=>{...st,owners:if(st.busy) 1 else 0}
  | Close=>{...st,visible:false}
  | Reopen=>{...st,visible:true,lease:st.lease+1}
 }
 action init=s'=initial
 action fire(e:Event):bool={val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}}
 action step={nondet e=Set(Content,Tick,Start,Finish,Drain,Close,Reopen).oneOf();fire(e)}
 val safety=s.owners>=0 and s.owners<=2 and (s.busy implies s.owners>=1) and s.captured<=s.latest and s.issuedLease<=s.lease and s.lastStart<=s.now and s.floor>=0
}
