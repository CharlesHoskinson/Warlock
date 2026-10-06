module transfers {
 type Frame={captured:bool,producer:bool,exported:bool,charged:bool,mapped:bool,held:bool,cleanup:bool,terminal:bool,records:int,permitted:bool}
 type State={first:Frame,second:Frame,history:List[str]}
 type Event=Capture1|Capture2|Transfer1|Transfer2|Pending1|Fail1|Unknown1|Hold1|Hold2|Close1|Close2|Release1|Release2|Drain1|Drain2|Ack1|Ack2|Stop1|Lock1|Expire1|Foreign1
 var s:State
 pure val empty={captured:false,producer:false,exported:false,charged:false,mapped:false,held:false,cleanup:false,terminal:false,records:0,permitted:true}
 pure val captured={...empty,captured:true,producer:true,exported:true,charged:true,mapped:true,records:1}
 pure val initial={first:empty,second:empty,history:List("Init")}
 pure def label(e:Event):str=match e {
  | Capture1=>"Capture1" | Capture2=>"Capture2" | Transfer1=>"Transfer1" | Transfer2=>"Transfer2" | Pending1=>"Pending1" | Fail1=>"Fail1" | Unknown1=>"Unknown1"
  | Hold1=>"Hold1" | Hold2=>"Hold2" | Close1=>"Close1" | Close2=>"Close2" | Release1=>"Release1" | Release2=>"Release2" | Drain1=>"Drain1" | Drain2=>"Drain2"
  | Ack1=>"Ack1" | Ack2=>"Ack2" | Stop1=>"Stop1" | Lock1=>"Lock1" | Expire1=>"Expire1" | Foreign1=>"Foreign1"
 }
 pure def drain(f:Frame):Frame=if(f.cleanup and not(f.held) and not(f.producer)) {...f,charged:false,mapped:false,terminal:true} else f
 pure def ack(f:Frame):Frame=if(f.terminal) {...f,records:0,cleanup:false,terminal:false} else f
 pure def reduce(st:State,e:Event):State=match e {
  | Capture1=>{...st,first:captured}
  | Capture2=>if(st.first.producer) st else {...st,second:captured}
  | Transfer1=>{...st,first:{...st.first,producer:false,exported:false}}
  | Transfer2=>{...st,second:{...st.second,producer:false,exported:false}}
  | Pending1=>{...st,first:{...st.first,exported:false}}
  | Fail1=>st
  | Unknown1=>{...st,first:{...st.first,exported:false}}
  | Hold1=>{...st,first:{...st.first,held:true}}
  | Hold2=>{...st,second:{...st.second,held:true}}
  | Close1=>{...st,first:{...st.first,held:false}}
  | Close2=>{...st,second:{...st.second,held:false}}
  | Release1=>{...st,first:{...st.first,cleanup:true}}
  | Release2=>{...st,second:{...st.second,cleanup:true}}
  | Drain1=>{...st,first:drain(st.first)}
  | Drain2=>{...st,second:drain(st.second)}
  | Ack1=>{...st,first:ack(st.first)}
  | Ack2=>{...st,second:ack(st.second)}
  | Stop1=>st
  | Lock1=>{...st,first:{...st.first,permitted:false}}
  | Expire1=>{...st,first:{...st.first,permitted:false}}
  | Foreign1=>{...st,first:{...st.first,permitted:false}}
 }
 pure def slots(f:Frame):int=(if(f.producer) 1 else 0)+(if(f.exported) 1 else 0)
 pure def projection(f:Frame)={nativeSlots:slots(f),charged:f.charged,mapped:f.mapped,held:f.held,cleanup:f.cleanup,terminal:f.terminal,records:f.records,readable:f.captured and f.mapped and not(f.cleanup) and f.permitted}
 action init=s'=initial
 action fire(e:Event):bool={val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}}
 val safety=slots(s.first)+slots(s.second)<=2 and (s.first.charged implies s.first.records==1) and (s.second.charged implies s.second.records==1) and (s.first.held implies s.first.mapped) and (s.second.held implies s.second.mapped)
}
