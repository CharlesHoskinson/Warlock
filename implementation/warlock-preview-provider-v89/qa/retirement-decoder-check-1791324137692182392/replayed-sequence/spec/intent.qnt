module intent {
 type State={now:int,free:bool,issued:bool,status:str,deadline:int,charge:int,records:int,history:List[str]}
 type Event=Retry|Renew|ChangeStamp|Expire|Drain|Foreign
 var s:State
 pure def label(e:Event):str=match e{ |Retry=>"Retry" |Renew=>"Renew" |ChangeStamp=>"ChangeStamp" |Expire=>"Expire" |Drain=>"Drain" |Foreign=>"Foreign" }
 pure def reduce(st:State,e:Event):State=match e{
  |Retry=>if(st.now>=st.deadline){...st,status:"Expired"} else if(st.free){...st,status:"Started",free:false,issued:true,charge:64,records:2} else {...st,status:"Capacity"}
  |Renew=>{...st,status:"Conflict"}
  |ChangeStamp=>{...st,status:"Conflict"}
  |Expire=>{...st,now:21,status:"ClockAdvanced"}
  |Drain=>{...st,free:true,charge:32,records:1,status:"CapacityReturned"}
  |Foreign=>{...st,status:"Invalid"}
 }
 action init=s'={now:3,free:false,issued:false,status:"Admitted",deadline:20,charge:64,records:2,history:[]}
 action fire(e:Event):bool=all{
  if(e==Retry or e==Expire)not(s.issued) else if(e==Drain)not(s.free) and not(s.issued) else true,
  val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}
 }
 action step={nondet e=Set(Retry,Renew,ChangeStamp,Expire,Drain,Foreign).oneOf();fire(e)}
 val safety=all{s.deadline==20,s.now==3 or s.now==21,s.charge==32 or s.charge==64,s.records==1 or s.records==2,s.free==(s.charge==32),s.issued implies s.now==3,s.status=="Expired" implies not(s.issued)}
}
