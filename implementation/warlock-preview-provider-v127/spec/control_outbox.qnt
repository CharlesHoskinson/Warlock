module control_outbox {
 type Event=Offer|Ack1|Ack2|Ack3|Retry|FailPost|RecoverPost|WrongEpoch|WrongBinding|GapAck|Boundary
 type State={issued:int,confirmed:int,pending:List[int],posted:List[int],fails:bool,last:bool,history:List[str]}
 var s:State
 pure val maximum=18446744073709551615
 pure def label(e:Event):str=match e{|Offer=>"Offer"|Ack1=>"Ack1"|Ack2=>"Ack2"|Ack3=>"Ack3"|Retry=>"Retry"|FailPost=>"FailPost"|RecoverPost=>"RecoverPost"|WrongEpoch=>"WrongEpoch"|WrongBinding=>"WrongBinding"|GapAck=>"GapAck"|Boundary=>"Boundary"}
 pure def ackOrdinal(e:Event):int=match e{|Ack1=>1|Ack2=>2|Ack3=>3|_=>0}
 pure def reduce(st:State,e:Event):State=
  if(e==Boundary){...st,issued:maximum-1,confirmed:maximum-1,last:true}
  else if(e==FailPost){...st,fails:true,last:true}
  else if(e==RecoverPost){...st,fails:false,last:true}
  else if(e==Offer){
   if(st.pending.length()>=2 or st.issued==maximum){...st,last:false}
   else {val ordinal=st.issued+1;{...st,issued:ordinal,pending:st.pending.append(ordinal),posted:if(st.pending.length()==0)st.posted.append(ordinal)else st.posted,last:true}}
  }else if(e==Retry){...st,posted:if(st.pending.length()>0)st.posted.append(st.pending.nth(0))else st.posted,last:st.pending.length()>0 and not(st.fails)}
  else if(st.pending.length()>0 and ackOrdinal(e)==st.pending.nth(0)){
   val remaining=st.pending.slice(1,st.pending.length());
   {...st,confirmed:st.pending.nth(0),pending:remaining,posted:if(remaining.length()>0)st.posted.append(remaining.nth(0))else st.posted,last:true}
  }else {...st,last:false}
 action init=s'={issued:0,confirmed:0,pending:[],posted:[],fails:false,last:false,history:[]}
 action fire(e:Event):bool=all{if(e==Boundary)s.history.length()==0 else true,val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}}
 action step={nondet e=Set(Offer,Ack1,Ack2,Ack3,Retry,FailPost,RecoverPost,WrongEpoch,WrongBinding,GapAck).oneOf();fire(e)}
 val safety=all{s.pending.length()<=2,s.confirmed<=s.issued,s.issued<=maximum,s.pending.length()==s.issued-s.confirmed,
  s.pending.length()>0 implies s.pending.nth(0)==s.confirmed+1}
}
