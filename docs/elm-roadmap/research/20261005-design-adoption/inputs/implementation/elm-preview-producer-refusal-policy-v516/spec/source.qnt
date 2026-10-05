module source {
 type State={phase:int,bytes:int,physical:int,cancelled:bool,seq:int,proof:List[int],deadline:int,now:int}
 type Event=Admit | Allocate | Cancel | Refuse | Tick
 var s:State
 pure val initial={phase:0,bytes:0,physical:0,cancelled:false,seq:1,proof:List(),deadline:3,now:1}
 pure def reduce(st:State,e:Event):State=match e {
  | Admit=>if(st.phase==0) {...st,phase:1,bytes:1} else st
  | Allocate=>if(st.phase==1 and st.now<st.deadline) {...st,phase:2,physical:1} else st
  | Cancel=>if(st.phase==1 or st.phase==2) {...st,cancelled:true} else st
  | Refuse=>if(st.phase==1 and st.physical==0 and st.seq+(if(st.cancelled) 1 else 0)<=2) {...st,phase:3,bytes:0,seq:st.seq+(if(st.cancelled) 2 else 1),proof:if(st.cancelled) List(st.seq,st.seq+1) else List(st.seq)} else st
  | Tick=>{...st,now:st.now+1}
 }
 action init=s'=initial
 action fire(e:Event):bool=s'=reduce(s,e)
 action exhaust:bool=s'={...s,seq:3}
 action step={nondet e=Set(Admit,Allocate,Cancel,Refuse,Tick).oneOf();fire(e)}
 val safety=s.bytes>=0 and s.bytes<=1 and s.physical>=0 and s.physical<=1 and (s.phase==3 implies s.physical==0 and s.bytes==0) and s.deadline==3
}
