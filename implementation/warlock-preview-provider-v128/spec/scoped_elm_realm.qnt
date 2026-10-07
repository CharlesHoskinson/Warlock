module scoped_elm_realm {
 type Event=Seed|WrongFloor|Terminal|ForeignTerminal|Complete|Gap|WrongEntry|ChangedComplete|Quarantine|Close|ForeignClose|NextGrant|Source|OldSource|Request|BareSource
 type State={epoch:int,held:bool,known:bool,demand:bool,closing:bool,closed:bool,floor:int,seeded:bool,ready:bool,terminalSeen:bool,processed:int,commands:List[str],history:List[str]}
 var s:State
 pure def label(e:Event):str=match e{|Seed=>"Seed"|WrongFloor=>"WrongFloor"|Terminal=>"Terminal"|ForeignTerminal=>"ForeignTerminal"|Complete=>"Complete"|Gap=>"Gap"|WrongEntry=>"WrongEntry"|ChangedComplete=>"ChangedComplete"|Quarantine=>"Quarantine"|Close=>"Close"|ForeignClose=>"ForeignClose"|NextGrant=>"NextGrant"|Source=>"Source"|OldSource=>"OldSource"|Request=>"Request"|BareSource=>"BareSource"}
 pure def settle(st:State):State=if(st.seeded and not(st.ready) and st.held and not(st.known) and not(st.demand)) {...st,ready:true,commands:st.commands.append("detach-ready")} else st
 pure def reduce(st:State,e:Event):State={
  val base={...st,commands:[]};
  if(e==Close and not(st.held)){...base,closing:true,closed:true}
  else if(e==NextGrant and st.closed){...base,epoch:st.epoch+1,closing:false,closed:false,held:false,known:false,demand:false,floor:0,seeded:false,ready:false,terminalSeen:false,processed:0}
  else if(st.closed)base
  else if(e==Quarantine and not(st.closing)){...base,closing:true,demand:false,commands:if(st.known)["reconcile","cancel"]else["reconcile"]}
  else if(e==Seed and st.held)settle({...base,closing:true,demand:false,seeded:true,commands:if(not(st.closing) and st.known)["cancel"]else[]})
  else if(e==Terminal and st.held and (st.known or st.terminalSeen))settle({...base,known:false,terminalSeen:true,commands:["acknowledge"]})
  else if(e==Complete and st.processed==1){...base,commands:["detach-delivery-ack"]}
  else if(e==Complete and st.held and st.seeded and st.ready and not(st.known) and st.processed==0){...base,held:false,demand:false,processed:1,commands:["detach-delivery-ack"]}
  else if(e==Source and not(st.closing)){...base,held:true,demand:true}
  else if(e==Request and st.held and not(st.closing) and st.floor==0 and st.demand){...base,known:true,floor:1,commands:["acquire"]}
  else base
 }
 action init=s'={epoch:1,held:true,known:true,demand:true,closing:false,closed:false,floor:1,seeded:false,ready:false,terminalSeen:false,processed:0,commands:[],history:[]}
 action fire(e:Event):bool={val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}}
 action step={nondet e=Set(Seed,WrongFloor,Terminal,ForeignTerminal,Complete,Gap,WrongEntry,ChangedComplete,Quarantine,Close,ForeignClose,NextGrant,Source,OldSource,Request,BareSource).oneOf();fire(e)}
 val safety=all{s.known implies s.held,s.closing implies not(s.demand),s.closed implies not(s.held),s.processed==1 implies not(s.held),s.ready implies (s.seeded and not(s.known) and not(s.demand))}
}
