module actor_control {
 type Event=Ready|DeliverReady|ConfirmJob|Poll|FinalAck|DeliverFinal|UnknownFinal|ConfirmAll|Collect|Close|RawReady|RawFinal|WrongObservation|FutureFinal|ForeignReceiver
 type State={issued:int,delivered:int,confirmed:int,reserved:int,tickets:int,ready:bool,accepted:bool,removed:bool,final:bool,acked:bool,unknown:bool,actor:bool,closed:bool,journal:int,frames:int,jobs:int,previous:int,last:int,history:List[str]}
 var s:State
 pure def label(e:Event):str=match e{|Ready=>"Ready"|DeliverReady=>"DeliverReady"|ConfirmJob=>"ConfirmJob"|Poll=>"Poll"|FinalAck=>"FinalAck"|DeliverFinal=>"DeliverFinal"|UnknownFinal=>"UnknownFinal"|ConfirmAll=>"ConfirmAll"|Collect=>"Collect"|Close=>"Close"|RawReady=>"RawReady"|RawFinal=>"RawFinal"|WrongObservation=>"WrongObservation"|FutureFinal=>"FutureFinal"|ForeignReceiver=>"ForeignReceiver"}
 pure def reduce(st:State,e:Event):State=
  if(e==Ready)if(not(st.actor)){...st,last:-1}else if(st.ready){...st,last:1}else{...st,ready:true,issued:3,reserved:st.reserved-1,tickets:st.tickets+1,last:1}
  else if(e==DeliverReady)if(not(st.ready)){...st,last:0}else if(st.delivered==3){...st,last:2}else if(st.delivered>3){...st,last:0}else if(st.confirmed>=2){...st,accepted:true,delivered:3,removed:true,reserved:st.reserved-3,tickets:st.tickets-2,frames:0,jobs:0,previous:1,last:1}else{...st,accepted:true,delivered:3,last:1}
  else if(e==ConfirmJob){...st,confirmed:if(st.confirmed<2)2 else st.confirmed,last:1}
  else if(e==Poll)if(st.accepted and not(st.removed) and st.confirmed>=2){...st,removed:true,reserved:st.reserved-3,tickets:st.tickets-2,frames:0,jobs:0,previous:1,last:1}else{...st,last:if(st.removed and st.journal==1)1 else 0}
  else if(e==FinalAck)if(not(st.actor)){...st,last:-1}else if(st.final){...st,last:1}else if(not(st.removed)){...st,last:-1}else{...st,final:true,issued:4,reserved:st.reserved-1,tickets:st.tickets+1,last:1}
  else if(e==DeliverFinal or e==UnknownFinal)if(not(st.final)){...st,last:0}else if(st.delivered==4){...st,last:2}else if(st.delivered!=3){...st,last:0}else{...st,delivered:4,acked:e==DeliverFinal,unknown:e==UnknownFinal,journal:if(e==DeliverFinal)0 else st.journal,last:1}
  else if(e==ConfirmAll){...st,confirmed:st.delivered,last:1}
  else if(e==Collect)if(st.actor and st.removed and st.acked and st.confirmed==4){...st,actor:false,tickets:0,previous:0,last:1}else{...st,last:0}
  else if(e==Close)if(not(st.actor) and st.removed){...st,closed:true,reserved:0,last:1}else{...st,last:0}
  else {...st,last:-1}
 action init=s'={issued:2,delivered:2,confirmed:1,reserved:6,tickets:2,ready:false,accepted:false,removed:false,final:false,acked:false,unknown:false,actor:true,closed:false,journal:1,frames:1,jobs:1,previous:0,last:0,history:[]}
 action fire(e:Event):bool=all{
  if(e==RawReady)not(s.accepted) else if(e==UnknownFinal)s.final and s.delivered==3 else true,
  val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}
 }
 action step={nondet e=Set(Ready,DeliverReady,ConfirmJob,Poll,FinalAck,DeliverFinal,UnknownFinal,ConfirmAll,Collect,Close,RawReady,RawFinal,WrongObservation,FutureFinal,ForeignReceiver).oneOf();fire(e)}
 val safety=all{s.confirmed<=s.delivered,s.delivered<=s.issued,s.tickets>=0,s.reserved>=0,s.closed implies (not(s.actor) and s.journal==0 and s.confirmed==4),s.unknown implies (s.actor and s.journal==1 and not(s.acked)),s.removed implies (s.frames==0 and s.jobs==0),s.acked implies (s.removed and s.journal==0)}
}
