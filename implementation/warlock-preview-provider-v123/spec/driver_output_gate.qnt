module driver_output_gate {
 // One original native job, original issued ticket and independent confirmation.
 // Held/Open stand for a stricter QA reservation gate; no physical duty settles.
 type Event=Step|Held|Open|Quarantine|Foreign
 type State={issued:int,notified:int,delivered:int,confirmed:int,effects:int,held:bool,demand:bool,known:bool,refused:bool,code:int,history:List[str]}
 var s:State
 pure def label(e:Event):str=match e{|Step=>"Step"|Held=>"Held"|Open=>"Open"|Quarantine=>"Quarantine"|Foreign=>"Foreign"}
 pure def reduce(st:State,e:Event):State={
  val base={...st,refused:false,code:0};
  if(e==Foreign){...base,refused:true}
  else if(e==Held){...base,held:true}
  else if(e==Open){...base,held:false}
  else if(e==Quarantine){...base,demand:false}
  else if(st.issued==0){...base,issued:1}
  else if(st.notified==0){...base,notified:1}
  else if(st.delivered==0){if(st.held){...base,refused:true,code:27}else{...base,delivered:1,effects:1}}
  else if(st.confirmed==0){...base,confirmed:1}
  else base
 }
 action init=s'={issued:0,notified:0,delivered:0,confirmed:0,effects:0,held:false,demand:true,known:true,refused:false,code:0,history:[]}
 action fire(e:Event):bool={val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}}
 action step={nondet e=(if(s.confirmed==1)Set(Held,Open,Quarantine,Foreign)else Set(Step,Held,Open,Quarantine,Foreign)).oneOf();fire(e)}
 val safety=all{s.confirmed<=s.delivered,s.delivered<=s.notified,s.notified<=s.issued,s.issued<=1,s.effects==s.delivered,s.known}
}
