module policy_realm_reuse {
 // Native driver lifetime/custody abstraction. Physical Terminal and Permanent
 // observations retain their independent original Native/C authority.
 type Event=Retain|Process|Acquire|Issue|Dispatch|Confirm|Terminal|Permanent|Retire|Reopen|OldEpoch|ForeignBinding|Unknown
 type State={epoch:int,policy:int,inputs:int,duty:bool,proposal:bool,ticket:bool,confirmation:bool,closed:bool,uncertain:bool,permanent:bool,code:int,history:List[str]}
 var s:State
 pure def label(e:Event):str=match e {|Retain=>"Retain"|Process=>"Process"|Acquire=>"Acquire"|Issue=>"Issue"|Dispatch=>"Dispatch"|Confirm=>"Confirm"|Terminal=>"Terminal"|Permanent=>"Permanent"|Retire=>"Retire"|Reopen=>"Reopen"|OldEpoch=>"OldEpoch"|ForeignBinding=>"ForeignBinding"|Unknown=>"Unknown"}
 pure def reduce(st:State,e:Event):State={
  val base={...st,code:0};
  if(st.uncertain){...base,code:1}
  else if(e==Unknown){...base,uncertain:true}
  else if(e==OldEpoch or e==ForeignBinding){...base,code:1}
  else if(e==Reopen){if(not(st.closed)){...base,code:1}else{...base,epoch:st.epoch+1,closed:false}}
  else if(st.closed){...base,code:1}
  else if(e==Retain){...base,inputs:st.inputs+1}
  else if(e==Process){if(st.inputs==0){...base,code:1}else{...base,inputs:st.inputs-1}}
  else if(e==Acquire){if(st.duty){...base,code:1}else{...base,duty:true,proposal:true}}
  else if(e==Issue){if(not(st.proposal) or st.ticket){...base,code:1}else{...base,proposal:false,ticket:true}}
  else if(e==Dispatch){if(not(st.ticket)){...base,code:1}else{...base,ticket:false,confirmation:true}}
  else if(e==Confirm){if(not(st.confirmation)){...base,code:1}else{...base,confirmation:false}}
  else if(e==Terminal){if(st.proposal or st.ticket or st.confirmation){...base,code:1}else{...base,duty:false}}
  else if(e==Permanent){...base,permanent:true}
  else if(e==Retire){if(st.inputs!=0 or st.duty or st.proposal or st.ticket or st.confirmation){...base,code:1}else{...base,closed:true}}
  else base
 }
 action init=s'={epoch:1,policy:1,inputs:0,duty:false,proposal:false,ticket:false,confirmation:false,closed:false,uncertain:false,permanent:false,code:0,history:[]}
 action fire(e:Event)={val next=reduce(s,e);s'={...next,history:s.history.append(label(e))}}
 action step={nondet e=Set(Retain,Process,Acquire,Issue,Dispatch,Confirm,Terminal,Permanent,Retire,Reopen,OldEpoch,ForeignBinding,Unknown).oneOf();fire(e)}
 val safety=all{s.policy==1,s.epoch>=1,s.inputs>=0,s.closed implies (s.inputs==0 and not(s.duty) and not(s.proposal) and not(s.ticket) and not(s.confirmation)),s.ticket implies s.duty,s.proposal implies s.duty,s.confirmation implies s.duty}
}
