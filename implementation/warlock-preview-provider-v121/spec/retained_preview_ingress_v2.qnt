module retained_preview_ingress_v2 {
 pure def minimum(a:int,b:int):int=if(a<b)a else b
 type Event=Quarantine|Seed|Terminal|Complete|Issue|WrongTicket|ForeignTicket|ForeignInnerTicket|Retry|ForeignRetry|Close|NextGrant|RepeatGrant
 type State={epoch:int,held:bool,known:bool,demand:bool,closing:bool,closed:bool,seeded:bool,ready:bool,terminalSeen:bool,processed:int,pending:List[str],deferred:List[str],commands:List[str],history:List[str]}
 var s:State
 pure def label(e:Event):str=match e{|Quarantine=>"Quarantine"|Seed=>"Seed"|Terminal=>"Terminal"|Complete=>"Complete"|Issue=>"Issue"|WrongTicket=>"WrongTicket"|ForeignTicket=>"ForeignTicket"|ForeignInnerTicket=>"ForeignInnerTicket"|Retry=>"Retry"|ForeignRetry=>"ForeignRetry"|Close=>"Close"|NextGrant=>"NextGrant"|RepeatGrant=>"RepeatGrant"}
 pure def staged(st:State,outputs:List[str]):State={
  val fresh=outputs.filter(x=>not(st.pending.contains(x)));
  val available=1-st.pending.length();
  val retained=st.pending.concat(fresh.slice(0,minimum(available,fresh.length())));
  {...st,pending:retained,deferred:fresh.slice(minimum(available,fresh.length()),fresh.length()),commands:retained}
 }
 pure def settle(st:State,outputs:List[str]):State=if(st.seeded and not(st.ready) and st.held and not(st.known))staged({...st,ready:true},outputs.append("detach-ready"))else staged(st,outputs)
 pure def reduce(st:State,e:Event):State={
  val base={...st,commands:[]};
  if(e==Issue){...base,pending:st.pending.slice(minimum(st.pending.length(),1),st.pending.length())}
  else if(e==WrongTicket or e==ForeignTicket or e==ForeignInnerTicket or e==ForeignRetry or e==RepeatGrant)base
  else if(e==Retry){
   val available=1-st.pending.length();
   val take=minimum(available,st.deferred.length());
   val retained=st.pending.concat(st.deferred.slice(0,take));
   {...base,pending:retained,deferred:st.deferred.slice(take,st.deferred.length()),commands:retained}
  }
  else if(e==Close){if(not(st.held) and st.pending.length()==0 and st.deferred.length()==0){...base,closing:true,closed:true}else base}
  else if(e==NextGrant){if(st.closed){...base,epoch:st.epoch+1,closing:false,closed:false,held:false,known:false,demand:false,seeded:false,ready:false,terminalSeen:false,processed:0}else base}
  else if(st.deferred.length()>0)base
  else if(st.closed)staged(base,[])
  else if(e==Quarantine and not(st.closing))staged({...base,closing:true,demand:false},if(st.known)["reconcile","cancel"]else["reconcile"])
  else if(e==Seed and st.held)settle({...base,closing:true,demand:false,seeded:true},if(not(st.closing) and st.known)["cancel"]else[])
  else if(e==Terminal and st.closing and st.held and (st.known or st.terminalSeen))settle({...base,known:false,terminalSeen:true},["acknowledge"])
  else if(e==Complete and st.processed==1)staged(base,["detach-delivery-ack"])
  else if(e==Complete and st.held and st.seeded and st.ready and not(st.known) and st.processed==0)staged({...base,held:false,demand:false,processed:1},["detach-delivery-ack"])
  else staged(base,[])
 }
 action init=s'={epoch:1,held:true,known:true,demand:true,closing:false,closed:false,seeded:false,ready:false,terminalSeen:false,processed:0,pending:["acquire"],deferred:[],commands:["acquire"],history:[]}
 action fire(e:Event):bool={val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}}
 action step={nondet e=Set(Quarantine,Seed,Terminal,Complete,Issue,WrongTicket,ForeignTicket,ForeignInnerTicket,Retry,ForeignRetry,Close,NextGrant,RepeatGrant).oneOf();fire(e)}
 val safety=all{s.pending.length()<=1,s.deferred.length()<=2,s.known implies s.held,s.closing implies not(s.demand),s.closed implies (not(s.held) and s.pending.length()==0 and s.deferred.length()==0),s.processed==1 implies not(s.held),s.ready implies (s.seeded and not(s.known))}
}
