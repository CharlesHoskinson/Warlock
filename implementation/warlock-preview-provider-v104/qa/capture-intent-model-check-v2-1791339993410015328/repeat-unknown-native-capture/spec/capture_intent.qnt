module capture_intent {
 type Event=Acquire|Cancel|Poll|Confirm|Close|RawRetry|BadJob|ForeignReceiver
 type State={issued:int,delivered:int,confirmed:int,intent:bool,captures:int,charge:int,terminal:bool,cancelled:bool,closed:bool,deadlineUnchanged:bool,wireUnchanged:bool,last:int,history:List[str]}
 var s:State
 pure def label(e:Event):str=match e{|Acquire=>"Acquire"|Cancel=>"Cancel"|Poll=>"Poll"|Confirm=>"Confirm"|Close=>"Close"|RawRetry=>"RawRetry"|BadJob=>"BadJob"|ForeignReceiver=>"ForeignReceiver"}
 pure def reduce(st:State,e:Event):State=
  if(e==Acquire)if(st.intent){...st,last:if(st.delivered==1)2 else 0}else if(st.cancelled){...st,last:-1}else{...st,issued:st.issued+1,delivered:st.delivered+1,intent:true,captures:1,last:3}
  else if(e==Cancel)if(st.cancelled){...st,last:2}else{...st,issued:st.issued+1,delivered:st.delivered+1,cancelled:true,charge:if(st.intent)4096 else 0,terminal:not(st.intent),last:1}
  else if(e==Confirm){...st,confirmed:st.delivered,last:if(st.delivered>0)1 else 0}
  else if(e==RawRetry or e==BadJob or e==ForeignReceiver){...st,last:-1}
  else{...st,last:0}
 action init=s'={issued:0,delivered:0,confirmed:0,intent:false,captures:0,charge:4096,terminal:false,cancelled:false,closed:false,deadlineUnchanged:true,wireUnchanged:true,last:0,history:[]}
 action fire(e:Event):bool=all{
  if(e==RawRetry)s.intent else true,
  val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}
 }
 action step={nondet e=Set(Acquire,Cancel,Poll,Confirm,Close,RawRetry,BadJob,ForeignReceiver).oneOf();fire(e)}
 val safety=all{s.confirmed<=s.delivered,s.delivered<=s.issued,s.captures<=1,s.intent==(s.captures==1),s.intent implies (s.charge==4096 and not(s.terminal)),s.deadlineUnchanged,s.wireUnchanged,not(s.closed)}
}
