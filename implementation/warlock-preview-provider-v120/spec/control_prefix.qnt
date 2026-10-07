module control_prefix {
 type State={delivered:int,offered:int,begun:int,inFlight:bool,ordered:bool,history:List[str]}
 type Event=Begin1|Begin2|Begin3|Finish|Boundary|BeginMax|Wrap
 var s:State
 pure val maximum=18446744073709551615
 pure def label(e:Event):str=match e{|Begin1=>"Begin1"|Begin2=>"Begin2"|Begin3=>"Begin3"|Finish=>"Finish"|Boundary=>"Boundary"|BeginMax=>"BeginMax"|Wrap=>"Wrap"}
 pure def ordinal(e:Event):int=match e{|Begin1=>1|Begin2=>2|Begin3=>3|BeginMax=>maximum|Wrap=>1|_=>0}
 pure def reduce(st:State,e:Event):State=
  if(e==Boundary){...st,delivered:maximum-1,ordered:true}
  else if(e==Finish){...st,delivered:st.offered,inFlight:false}
  else if(not(st.inFlight) and st.delivered<maximum and ordinal(e)==st.delivered+1)
   {...st,inFlight:true,offered:ordinal(e),ordered:true,begun:st.begun+1}
  else st
 action init=s'={delivered:0,offered:0,begun:0,inFlight:false,ordered:false,history:[]}
 action fire(e:Event):bool=all{
  if(e==Finish)s.inFlight else if(e==Boundary)s.history.length()==0 else true,
  val next=reduce(s,e);s'={...next,history:s.history.append(label(e))}
 }
 action step={nondet e=Set(Begin1,Begin2,Begin3,Finish,Boundary,BeginMax,Wrap).oneOf();fire(e)}
 val safety=all{s.delivered>=0,s.delivered<=maximum,s.inFlight implies (s.delivered<maximum and s.offered==s.delivered+1),not(s.ordered) implies s.delivered==0}
}
