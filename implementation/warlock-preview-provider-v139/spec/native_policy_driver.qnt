module native_policy_driver {
 // Driver custody only. The original Elm lifecycle and native resource/terminal
 // authorities remain external; Proposal and Terminal represent their facts.
 type Event=Queue|Fill|Process|Proposal|Issue|Notify|Dispatch|Confirm|Quarantine|Terminal|Foreign|WrongEpoch|Malformed|Unknown|Close
 type State={inputs:int,proposal:bool,issued:int,notified:int,delivered:int,confirmed:int,posted:bool,obligation:bool,quarantined:bool,uncertain:bool,closed:bool,code:int,history:List[str]}
 var s:State
 pure val capacity=1065
 pure def label(e:Event):str=match e{|Queue=>"Queue"|Fill=>"Fill"|Process=>"Process"|Proposal=>"Proposal"|Issue=>"Issue"|Notify=>"Notify"|Dispatch=>"Dispatch"|Confirm=>"Confirm"|Quarantine=>"Quarantine"|Terminal=>"Terminal"|Foreign=>"Foreign"|WrongEpoch=>"WrongEpoch"|Malformed=>"Malformed"|Unknown=>"Unknown"|Close=>"Close"}
 pure def reduce(st:State,e:Event):State={
  val base={...st,code:0};
  if(st.closed or st.uncertain){...base,code:1}
  else if(e==Foreign or e==WrongEpoch or e==Malformed){...base,code:1}
  else if(e==Unknown){...base,uncertain:true}
  else if(e==Queue){if(st.inputs==capacity){...base,code:27}else{...base,inputs:st.inputs+1}}
  else if(e==Fill){...base,inputs:capacity}
  else if(e==Process){if(st.inputs==0){...base,code:1}else{...base,inputs:st.inputs-1}}
  else if(e==Proposal){if(st.proposal or st.posted){...base,code:1}else{...base,proposal:true,obligation:true}}
  else if(e==Issue){if(not(st.proposal) or st.posted or st.issued!=st.confirmed){...base,code:1}else{...base,issued:st.issued+1,posted:true}}
  else if(e==Notify){if(not(st.posted) or st.notified==st.issued){...base,code:1}else{...base,notified:st.issued,proposal:false}}
  else if(e==Dispatch){if(not(st.posted) or st.notified!=st.issued){...base,code:1}else{...base,delivered:st.issued,posted:false}}
  else if(e==Confirm){if(st.confirmed==st.delivered){...base,code:1}else{...base,confirmed:st.delivered}}
  else if(e==Quarantine){...base,quarantined:true}
  else if(e==Terminal){if(st.proposal or st.posted or st.confirmed!=st.issued){...base,code:1}else{...base,obligation:false}}
  else if(e==Close){if(st.inputs!=0 or st.proposal or st.posted or st.confirmed!=st.issued or st.obligation){...base,code:1}else{...base,closed:true}}
  else base
 }
 action init=s'={inputs:0,proposal:false,issued:0,notified:0,delivered:0,confirmed:0,posted:false,obligation:false,quarantined:false,uncertain:false,closed:false,code:0,history:[]}
 action fire(e:Event):bool={val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}}
 action step={nondet e=Set(Queue,Fill,Process,Proposal,Issue,Notify,Dispatch,Confirm,Quarantine,Terminal,Foreign,WrongEpoch,Malformed,Unknown,Close).oneOf();fire(e)}
 val safety=all{s.inputs>=0,s.inputs<=capacity,s.confirmed<=s.delivered,s.delivered<=s.notified,s.notified<=s.issued,s.issued-s.confirmed<=1,s.posted implies s.issued>s.delivered,s.closed implies (s.inputs==0 and not(s.obligation) and not(s.proposal) and not(s.posted) and s.confirmed==s.issued)}
}
