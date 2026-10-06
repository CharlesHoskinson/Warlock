module next_intent {
 type State={now:int,deadline:int,publication:int,lease:int,previous:int,free:bool,issued:bool,status:str,charge:int,records:int,history:List[str]}
 type Event=Retry|Advance|Expire|Drain|OldStamp|Partial|Foreign|WrongClock|Renew
 var s:State
 pure def label(e:Event):str=match e{ |Retry=>"Retry" |Advance=>"Advance" |Expire=>"Expire" |Drain=>"Drain" |OldStamp=>"OldStamp" |Partial=>"Partial" |Foreign=>"Foreign" |WrongClock=>"WrongClock" |Renew=>"Renew" }
 pure def reduce(st:State,e:Event):State=match e{
  |Retry=>if(st.now>=st.deadline){...st,status:"Expired"}else if(st.free){...st,status:"Started",free:false,issued:true,charge:64,records:2}else{...st,status:"Capacity"}
  |Advance=>if(st.now>=st.deadline){...st,previous:st.deadline,deadline:st.now+20,publication:st.publication+1,lease:st.lease+1,status:"Admitted"}else{...st,status:"Conflict"}
  |Expire=>{...st,now:st.deadline+1,status:"ClockAdvanced"}
  |Drain=>{...st,free:true,charge:32,records:1,status:"CapacityReturned"}
  |OldStamp=>{...st,status:"Conflict"}
  |Partial=>{...st,status:"Conflict"}
  |Foreign=>{...st,status:"Invalid"}
  |WrongClock=>{...st,status:"Conflict"}
  |Renew=>{...st,status:"Conflict"}
 }
 action init=s'={now:3,deadline:20,publication:1,lease:1,previous:0,free:false,issued:false,status:"Admitted",charge:64,records:2,history:[]}
 action fire(e:Event):bool=all{
  not(s.issued),if(e==Drain)not(s.free)else true,
  val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}
 }
 action step={nondet e=Set(Retry,Advance,Expire,Drain,OldStamp,Partial,Foreign,WrongClock,Renew).oneOf();fire(e)}
 val safety=all{s.publication==s.lease,s.deadline>=20,s.previous==0 or s.previous<s.deadline,s.free==(s.charge==32),s.records==s.charge/32,s.issued implies s.status=="Started",s.status=="Expired" implies not(s.issued)}
}
