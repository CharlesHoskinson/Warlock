module job_control {
 type Event=Cancel|Ack|DeliverCancel|DeliverAck|Confirm|Resume|OldAck|ChangedAck|WrongJob|WrongFamily|ForeignReceiver|Malformed
 type State={job:int,phase:int,cancel:int,ack:int,issued:int,delivered:int,confirmed:int,tickets:int,reserved:int,previous:int,records:int,charge:int,invocations:int,last:int,history:List[str]}
 var s:State
 pure def label(e:Event):str=match e{|Cancel=>"Cancel"|Ack=>"Ack"|DeliverCancel=>"DeliverCancel"|DeliverAck=>"DeliverAck"|Confirm=>"Confirm"|Resume=>"Resume"|OldAck=>"OldAck"|ChangedAck=>"ChangedAck"|WrongJob=>"WrongJob"|WrongFamily=>"WrongFamily"|ForeignReceiver=>"ForeignReceiver"|Malformed=>"Malformed"}
 pure def reduce(st:State,e:Event):State=
  if(e==Cancel)if(st.cancel>0){...st,last:1}else{...st,cancel:st.issued+1,issued:st.issued+1,tickets:st.tickets+1,reserved:st.reserved-1,last:1}
  else if(e==Ack)if(st.ack>0){...st,last:1}else if(st.phase!=1){...st,last:-1}else{...st,ack:st.issued+1,issued:st.issued+1,tickets:st.tickets+1,reserved:st.reserved-1,last:1}
  else if(e==DeliverCancel)if(st.cancel==0){...st,last:0}else if(st.cancel==st.delivered){...st,last:2}else if(st.cancel!=st.delivered+1){...st,last:0}else{...st,phase:1,charge:0,delivered:st.cancel,invocations:st.invocations+1,last:1}
  else if(e==DeliverAck)if(st.ack==0){...st,last:0}else if(st.ack==st.delivered){...st,last:2}else if(st.ack!=st.delivered+1){...st,last:0}else{...st,phase:2,records:0,delivered:st.ack,invocations:st.invocations+1,last:1}
  else if(e==Confirm)if(st.delivered==0){...st,last:0}else{...st,confirmed:st.delivered,last:1}
  else if(e==Resume)if(st.phase!=2 or st.confirmed!=st.issued){...st,last:0}else{...st,job:st.job+1,previous:st.job,phase:0,cancel:0,ack:0,tickets:0,reserved:8,records:1,charge:4096,last:1}
  else if(e==OldAck)if(st.previous>0){...st,last:2}else{...st,last:-1}
  else {...st,last:-1}
 action init=s'={job:1,phase:0,cancel:0,ack:0,issued:0,delivered:0,confirmed:0,tickets:0,reserved:8,previous:0,records:1,charge:4096,invocations:0,last:0,history:[]}
 action fire(e:Event):bool=all{
  if(e==ChangedAck)s.ack>0 or s.previous>0 else if(e==OldAck)s.previous>0 else true,
  val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}
 }
 action step={nondet e=Set(Cancel,Ack,DeliverCancel,DeliverAck,Confirm,Resume,OldAck,ChangedAck,WrongJob,WrongFamily,ForeignReceiver,Malformed).oneOf();fire(e)}
 val safety=all{s.job>=1,s.phase>=0,s.phase<=2,s.tickets>=0,s.tickets<=2,s.reserved+s.tickets==8,s.confirmed<=s.delivered,s.delivered<=s.issued,s.previous==0 or s.previous==s.job-1,s.records==if(s.phase==2)0 else 1,s.charge==if(s.phase==0)4096 else 0,s.invocations==2*(s.job-1)+s.phase}
}
