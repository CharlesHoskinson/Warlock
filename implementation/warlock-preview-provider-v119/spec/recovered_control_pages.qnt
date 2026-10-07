module recovered_control_pages {
 type Event=Issue|Retain|Duplicate|Advisory|Changed|Gap|Ack1|Ack2|Ack3|Ack4|Retry|FailPost|RecoverPost|FailConfirm|RecoverConfirm|WrongEpoch|WrongBinding|RecoverCold|RecoverWarm|RecoverEmpty|IncompleteRecovery|MixedPrefixRecovery|WrongPositionRecovery|GapTicketRecovery|ForeignEpochRecovery
 type State={native:int,through:int,delivered:int,pending:List[int],posted:List[int],confirmations:List[int],postFails:bool,confirmFails:bool,last:bool,history:List[str]}
 var s:State
 pure def label(e:Event):str=match e{|Issue=>"Issue"|Retain=>"Retain"|Duplicate=>"Duplicate"|Advisory=>"Advisory"|Changed=>"Changed"|Gap=>"Gap"|Ack1=>"Ack1"|Ack2=>"Ack2"|Ack3=>"Ack3"|Ack4=>"Ack4"|Retry=>"Retry"|FailPost=>"FailPost"|RecoverPost=>"RecoverPost"|FailConfirm=>"FailConfirm"|RecoverConfirm=>"RecoverConfirm"|WrongEpoch=>"WrongEpoch"|WrongBinding=>"WrongBinding"|RecoverCold=>"RecoverCold"|RecoverWarm=>"RecoverWarm"|RecoverEmpty=>"RecoverEmpty"|IncompleteRecovery=>"IncompleteRecovery"|MixedPrefixRecovery=>"MixedPrefixRecovery"|WrongPositionRecovery=>"WrongPositionRecovery"|GapTicketRecovery=>"GapTicketRecovery"|ForeignEpochRecovery=>"ForeignEpochRecovery"}
 pure def ack(e:Event):int=match e{|Ack1=>1|Ack2=>2|Ack3=>3|Ack4=>4|_=>0}
 pure def posted(st:State):List[int]=if(st.pending.length()>0)st.posted.append(st.pending.nth(0))else st.posted
 pure def confirmed(st:State):List[int]=if(st.delivered>0)st.confirmations.append(st.delivered)else st.confirmations
 pure def reduce(st:State,e:Event):State=
  if(e==RecoverCold){...st,native:2,through:2,delivered:0,pending:[1,2],posted:[],confirmations:[],last:true}
  else if(e==RecoverWarm){...st,native:2,through:2,delivered:1,pending:[2],posted:[],confirmations:[],last:true}
  else if(e==RecoverEmpty){...st,native:2,through:2,delivered:2,pending:[],posted:[],confirmations:[],last:true}
  else if(e==IncompleteRecovery or e==MixedPrefixRecovery or e==WrongPositionRecovery or e==GapTicketRecovery or e==ForeignEpochRecovery){...st,last:false}
  else if(e==Issue){...st,native:st.native+1,last:true}
  else if(e==FailPost){...st,postFails:true,last:true}
  else if(e==RecoverPost){...st,postFails:false,last:true}
  else if(e==FailConfirm){...st,confirmFails:true,last:true}
  else if(e==RecoverConfirm){...st,confirmFails:false,last:true}
  else if(e==Retain){
   if(st.through>=st.native or st.pending.length()>=2){...st,last:false}
   else {val ordinal=st.through+1;{...st,through:ordinal,pending:st.pending.append(ordinal),posted:if(st.pending.length()==0)st.posted.append(ordinal)else st.posted,last:true}}
  }else if(e==Duplicate or e==Advisory){
   if(st.pending.length()>0){...st,posted:posted(st),last:true}
   else if(st.delivered>0){...st,confirmations:confirmed(st),last:true}
   else {...st,last:false}
  }else if(e==Retry){...st,posted:posted(st),confirmations:confirmed(st),last:(st.pending.length()>0 and not(st.postFails)) or (st.delivered>0 and not(st.confirmFails))}
  else if(ack(e)>0 and ack(e)<=st.delivered){...st,confirmations:confirmed(st),last:true}
  else if(st.pending.length()>0 and ack(e)==st.pending.nth(0)){
   val remaining=st.pending.slice(1,st.pending.length());
   {...st,delivered:ack(e),pending:remaining,confirmations:st.confirmations.append(ack(e)),posted:if(remaining.length()>0)st.posted.append(remaining.nth(0))else st.posted,last:true}
  }else {...st,last:false}
 action init=s'={native:0,through:0,delivered:0,pending:[],posted:[],confirmations:[],postFails:false,confirmFails:false,last:false,history:[]}
 action fire(e:Event):bool={val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}}
 action step={nondet e=Set(Issue,Retain,Duplicate,Advisory,Changed,Gap,Ack1,Ack2,Ack3,Ack4,Retry,FailPost,RecoverPost,FailConfirm,RecoverConfirm,WrongEpoch,WrongBinding,RecoverCold,RecoverWarm,RecoverEmpty,IncompleteRecovery,MixedPrefixRecovery,WrongPositionRecovery,GapTicketRecovery,ForeignEpochRecovery).oneOf();fire(e)}
 val safety=all{s.pending.length()<=2,s.delivered<=s.through,s.through<=s.native,s.pending.length()==s.through-s.delivered,s.pending.length()>0 implies s.pending.nth(0)==s.delivered+1}
}
