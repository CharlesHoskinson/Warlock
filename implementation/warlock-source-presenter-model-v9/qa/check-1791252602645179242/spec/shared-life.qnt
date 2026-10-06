module shared_life {
 type Frame={job:int,floor:int,deadline:int,expires:int,lease:int,records:int,charged:bool,mapped:bool,held:bool,cleanup:bool,terminal:bool,live:bool}
 type Projection={job:int,floor:int,deadline:int,expires:int,lease:int,records:int,charged:bool,mapped:bool,held:bool,cleanup:bool,terminal:bool,live:bool,readable:bool}
 type State={first:Frame,second:Frame,nextProof:int,accepted:bool,history:List[str]}
 type Event=Reserve1|Reserve2|Capture1|Capture2|Hold1|Hold2|Close1|Close2|Release1|Release2|Drain1|Drain2|Ack1|Ack2|Resume1|ResumeOld1|ResumeMissing1|ResumeForeign1|ResumeStopped1|ResumeCostly1|Stop2|Present2|PresentOld2|PresentForeign2|OldAck1
 var s:State
 pure val empty={job:0,floor:0,deadline:0,expires:0,lease:1,records:0,charged:false,mapped:false,held:false,cleanup:false,terminal:false,live:true}
 pure val initial={first:empty,second:empty,nextProof:1,accepted:false,history:List("Init")}
 pure def label(e:Event):str=match e {
  | Reserve1=>"Reserve1" | Reserve2=>"Reserve2" | Capture1=>"Capture1" | Capture2=>"Capture2" | Hold1=>"Hold1" | Hold2=>"Hold2" | Close1=>"Close1" | Close2=>"Close2"
  | Release1=>"Release1" | Release2=>"Release2" | Drain1=>"Drain1" | Drain2=>"Drain2" | Ack1=>"Ack1" | Ack2=>"Ack2" | Resume1=>"Resume1" | ResumeOld1=>"ResumeOld1" | ResumeMissing1=>"ResumeMissing1" | ResumeForeign1=>"ResumeForeign1" | ResumeStopped1=>"ResumeStopped1" | ResumeCostly1=>"ResumeCostly1" | Stop2=>"Stop2" | Present2=>"Present2" | PresentOld2=>"PresentOld2" | PresentForeign2=>"PresentForeign2" | OldAck1=>"OldAck1"
 }
 pure def reserve(f:Frame,deadline:int):Frame={...f,job:1,floor:1,deadline:deadline,records:1,charged:true}
 pure def capture(f:Frame):Frame={...f,mapped:true,expires:f.deadline+3000000000}
 pure def canDrain(f:Frame):bool=f.cleanup and f.mapped and not(f.held)
 pure def drain(f:Frame):Frame=if(canDrain(f)) {...f,charged:false,mapped:false,terminal:true} else f
 pure def ack(f:Frame):Frame=if(f.terminal) {...f,records:0,cleanup:false,terminal:false} else f
 pure def reduce(st:State,e:Event):State=match e {
  | Reserve1=>{...st,first:reserve(st.first,2000000001)}
  | Reserve2=>{...st,second:reserve(st.second,2000000002)}
  | Capture1=>{...st,first:capture(st.first),nextProof:st.nextProof+2}
  | Capture2=>{...st,second:capture(st.second),nextProof:st.nextProof+2}
  | Hold1=>{...st,first:{...st.first,held:true}}
  | Hold2=>{...st,second:{...st.second,held:true}}
  | Close1=>{...st,first:{...st.first,held:false}}
  | Close2=>{...st,second:{...st.second,held:false}}
  | Release1=>{...st,first:{...st.first,cleanup:true}}
  | Release2=>{...st,second:{...st.second,cleanup:true}}
  | Drain1=>{...st,first:drain(st.first),nextProof:st.nextProof+(if(canDrain(st.first)) 1 else 0)}
  | Drain2=>{...st,second:drain(st.second),nextProof:st.nextProof+(if(canDrain(st.second)) 1 else 0)}
  | Ack1=>{...st,first:ack(st.first)}
  | Ack2=>{...st,second:ack(st.second)}
  | Resume1=>if(st.first.records==0 and st.first.floor==1) {...st,first:{...empty,job:2,floor:2,lease:2,deadline:2000000004,records:1,charged:true},accepted:true} else st
  | ResumeOld1=>st | ResumeMissing1=>st | ResumeForeign1=>st | ResumeStopped1=>st | ResumeCostly1=>st | OldAck1=>st
  | Stop2=>{...st,second:{...st.second,live:false}}
  | Present2=>if(st.second.mapped and not(st.second.cleanup) and not(st.second.terminal) and st.second.lease<2) {...st,second:{...st.second,lease:2},accepted:true} else st
  | PresentOld2=>st | PresentForeign2=>st
 }
 pure def projection(f:Frame):Projection={job:f.job,floor:f.floor,deadline:f.deadline,expires:f.expires,lease:f.lease,records:f.records,charged:f.charged,mapped:f.mapped,held:f.held,cleanup:f.cleanup,terminal:f.terminal,live:f.live,readable:f.mapped and not(f.cleanup)}
 action init=s'=initial
 action fire(e:Event):bool={val updated=reduce({...s,accepted:false},e);s'={...updated,history:s.history.append(label(e))}}
 val safety=(s.first.records>=0 and s.first.records<=1 and s.second.records>=0 and s.second.records<=1) and
  (s.first.floor<=2 and s.second.floor<=1) and (s.first.charged implies s.first.records==1) and (s.second.charged implies s.second.records==1) and
  (s.first.held implies s.first.mapped) and (s.second.held implies s.second.mapped) and
  (s.first.terminal implies (s.first.records==1 and not(s.first.charged))) and (s.second.terminal implies (s.second.records==1 and not(s.second.charged)))
}
