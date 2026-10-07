module imported_resources {
 type Event=OpenReader|Read|CloseReader|Reconcile|Poll|Lock|Unlock|Ack|Close
 type State={quarantined:bool,locked:bool,producer:bool,exported:bool,mapped:bool,reader:bool,known:bool,terminal:bool,bytes:int,proofs:int,offset:int,captures:int,transfers:int,last:int,history:List[str]}
 var s:State
 pure def label(e:Event):str=match e{|OpenReader=>"OpenReader"|Read=>"Read"|CloseReader=>"CloseReader"|Reconcile=>"Reconcile"|Poll=>"Poll"|Lock=>"Lock"|Unlock=>"Unlock"|Ack=>"Ack"|Close=>"Close"}
 pure def reduce(st:State,e:Event):State=
  if(e==OpenReader) {
   val allowed=st.known and st.mapped and not(st.quarantined)
   {...st,reader:allowed,offset:if(allowed)0 else st.offset,last:if(allowed)1 else -1}
  }
  else if(e==Read){...st,offset:if(not(st.quarantined) and st.offset<16)st.offset+1 else st.offset,last:if(st.quarantined)-1 else if(st.offset<16)1 else 0}
  else if(e==CloseReader){...st,reader:false,last:0}
  else if(e==Reconcile){...st,quarantined:true,last:0}
  else if(e==Lock){...st,locked:true,last:0}
  else if(e==Unlock){...st,locked:false,last:0}
  else if(e==Close){...st,last:-1}
  else if(e==Ack){...st,known:false,terminal:false,proofs:0,last:0}
  else {
   val producer=if(st.quarantined and not(st.locked))false else st.producer
   val done=st.known and not(st.terminal) and st.quarantined and not(producer) and not(st.reader)
   {...st,producer:producer,mapped:if(done)false else st.mapped,terminal:if(done)true else st.terminal,
     bytes:if(done)0 else st.bytes,proofs:if(done)2 else st.proofs,last:0}
  }
 action init=s'={quarantined:false,locked:false,producer:true,exported:false,mapped:true,reader:false,known:true,terminal:false,bytes:4096,proofs:0,offset:0,captures:1,transfers:1,last:0,history:[]}
 action fire(e:Event):bool=all{
  if(e==OpenReader)not(s.reader) else if(e==Read)s.reader else if(e==Lock)s.quarantined else if(e==Ack)s.known and s.terminal else true,
  val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}
 }
 action step={nondet e=Set(OpenReader,Read,CloseReader,Reconcile,Poll,Lock,Unlock,Ack,Close).oneOf();fire(e)}
 val safety=all{s.reader implies (s.mapped and s.known),s.terminal implies (not(s.mapped) and not(s.producer) and not(s.reader) and s.bytes==0 and s.proofs==2),
  s.mapped==(s.bytes==4096),not(s.known) implies (not(s.mapped) and s.proofs==0),s.captures==1,s.transfers==1,not(s.exported),s.offset>=0,s.offset<=16}
}
