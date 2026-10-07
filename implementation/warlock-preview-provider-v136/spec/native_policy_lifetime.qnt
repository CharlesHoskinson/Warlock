module native_policy_lifetime {
 type Event=Status|Malformed|WrongThreadInvoke|WrongThreadClose|Grant|ForeignClose|TrustedClose|Destroy
 type State={held:bool,controlled:bool,closed:bool,code:int,history:List[str]}
 var s:State
 pure def label(e:Event):str=match e{|Status=>"Status"|Malformed=>"Malformed"|WrongThreadInvoke=>"WrongThreadInvoke"|WrongThreadClose=>"WrongThreadClose"|Grant=>"Grant"|ForeignClose=>"ForeignClose"|TrustedClose=>"TrustedClose"|Destroy=>"Destroy"}
 pure def reduce(st:State,e:Event):State={
  val base={...st,code:0};
  if(not(st.held)){...base,code:1}
  else if(e==Malformed){...base,code:1}
  else if(e==WrongThreadInvoke or e==WrongThreadClose){...base,code:2}
  else if(e==Grant){...base,controlled:true}
  else if(e==TrustedClose and st.controlled){...base,closed:true}
  else if(e==Destroy){if(st.controlled and not(st.closed)){...base,code:5}else{...base,held:false}}
  else base
 }
 action init=s'={held:true,controlled:false,closed:false,code:0,history:[]}
 action fire(e:Event):bool={val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}}
 action step={nondet e=Set(Status,Malformed,WrongThreadInvoke,WrongThreadClose,Grant,ForeignClose,TrustedClose,Destroy).oneOf();fire(e)}
 val safety=all{s.closed implies s.controlled,(not(s.held) and s.controlled) implies s.closed,s.code>=0,s.code<=5}
}
