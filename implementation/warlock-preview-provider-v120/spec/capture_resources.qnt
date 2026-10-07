module capture_resources {
 type Event=Observe|Release|Retire|LostRelease|LostRetire|BadReply|BadTransfer|BadSubject|FailPrepare|Lock|Unlock|OtherCapture|Confirm
 type State={producer:bool,exported:bool,other:bool,locked:bool,sequence:int,cursor:int,seenProducer:int,seenExport:bool,unknown:bool,status:int,last:int,history:List[str]}
 var s:State
 pure def label(e:Event):str=match e{|Observe=>"Observe"|Release=>"Release"|Retire=>"Retire"|LostRelease=>"LostRelease"|LostRetire=>"LostRetire"|BadReply=>"BadReply"|BadTransfer=>"BadTransfer"|BadSubject=>"BadSubject"|FailPrepare=>"FailPrepare"|Lock=>"Lock"|Unlock=>"Unlock"|OtherCapture=>"OtherCapture"|Confirm=>"Confirm"}
 pure def reduce(st:State,e:Event):State=
  if(e==Lock){...st,locked:true,last:0}
  else if(e==Unlock){...st,locked:false,last:0}
  else if(e==OtherCapture){...st,other:true,last:0}
  else if(e==Confirm){...st,last:0}
  else if(e==FailPrepare or (e==BadTransfer and st.exported) or (e==BadSubject and st.producer)){...st,last:-1}
  else {
   val release=e==Release or e==LostRelease or e==BadTransfer
   val retire=e==Retire or e==LostRetire
   val producer=if(retire and not(st.exported) and not(st.locked))false else st.producer
   val exported=if(release)false else st.exported
   val status=if(retire)if(st.exported)2 else if(st.producer and st.locked)3 else 1 else if(release)1 else 0
   val lost=e==LostRelease or e==LostRetire or e==BadReply or e==BadSubject
   { ...st,producer:producer,exported:exported,sequence:st.sequence+1,
      cursor:if(lost)st.cursor else st.sequence+1,
      seenProducer:if(lost)st.seenProducer else if(producer)4096 else 0,
      seenExport:if(lost)st.seenExport else exported,unknown:lost,status:if(lost)st.status else status,last:if(lost)2 else 1 }
  }
 action init=s'={producer:true,exported:true,other:false,locked:false,sequence:0,cursor:0,seenProducer:4096,seenExport:true,unknown:true,status:0,last:0,history:[]}
 action fire(e:Event):bool=all{
  if(e==OtherCapture)not(s.producer) and not(s.exported) and not(s.other) else true,
  val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}
 }
 action step={nondet e=Set(Observe,Release,Retire,LostRelease,LostRetire,BadReply,BadTransfer,BadSubject,FailPrepare,Lock,Unlock,OtherCapture,Confirm).oneOf();fire(e)}
 val safety=all{s.cursor<=s.sequence,s.exported implies s.producer,s.other implies not(s.producer),s.seenExport implies s.seenProducer>0,
  not(s.unknown) implies (s.seenProducer==(if(s.producer)4096 else 0) and s.seenExport==s.exported)}
}
