module control_delivery {
 type Event=Packet1|Packet1Changed|Packet2|Packet3|Finish|WrongReceiver|WrongEpoch|WrongBinding|Reinitialize|Boundary|PacketMax|Wrap|Empty|Oversize|WrongFinish
 type State={delivered:int,pending:int,wire:int,latest:int,inFlight:bool,
  invoked:int,decision:int,receipt:int,history:List[str]}
 var s:State
 pure val maximum=18446744073709551615
 pure def label(e:Event):str=match e{
  |Packet1=>"Packet1"|Packet1Changed=>"Packet1Changed"|Packet2=>"Packet2"|Packet3=>"Packet3"|Finish=>"Finish"
  |WrongReceiver=>"WrongReceiver"|WrongEpoch=>"WrongEpoch"|WrongBinding=>"WrongBinding"|Reinitialize=>"Reinitialize"
  |Boundary=>"Boundary"|PacketMax=>"PacketMax"|Wrap=>"Wrap"|Empty=>"Empty"|Oversize=>"Oversize"|WrongFinish=>"WrongFinish"}
 pure def ordinal(e:Event):int=match e{|Packet1=>1|Packet1Changed=>1|Packet2=>2|Packet3=>3|PacketMax=>maximum|Wrap=>1|_=>0}
 pure def bytes(e:Event):int=match e{|Packet1=>1|Packet1Changed=>2|Packet2=>3|Packet3=>4|PacketMax=>5|Wrap=>1|_=>0}
 pure def reduce(st:State,e:Event):State=
  if(e==Boundary){...st,delivered:maximum-1,receipt:maximum-1}
  else if(e==Finish){...st,delivered:st.pending,latest:st.wire,inFlight:false,receipt:st.pending,decision:3}
  else if(e==WrongFinish or e==Reinitialize){...st,decision:0}
  else if(st.inFlight or ordinal(e)==0){...st,decision:0}
  else if(ordinal(e)==st.delivered and bytes(e)==st.latest){...st,decision:2}
  else if(st.delivered<maximum and ordinal(e)==st.delivered+1){...st,pending:ordinal(e),wire:bytes(e),inFlight:true,invoked:st.invoked+1,receipt:0,decision:1}
  else {...st,decision:0}
 action init=s'={delivered:0,pending:0,wire:0,latest:0,inFlight:false,invoked:0,decision:0,receipt:0,history:[]}
 action fire(e:Event):bool=all{
  if(e==Boundary)s.history.length()==0 else if(e==Finish or e==WrongFinish)s.inFlight else true,
  val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}
 }
 action step={nondet e=Set(Packet1,Packet1Changed,Packet2,Packet3,Finish,WrongReceiver,WrongEpoch,WrongBinding,Reinitialize,PacketMax,Wrap,Empty,Oversize,WrongFinish).oneOf();fire(e)}
 val safety=all{s.delivered>=0,s.delivered<=maximum,s.inFlight implies (s.delivered<maximum and s.pending==s.delivered+1 and s.receipt==0),not(s.inFlight) implies s.receipt==s.delivered,s.invoked>=0}
}
