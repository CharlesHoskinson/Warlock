module enrollment {
 type State={now:int,free:bool,issued:bool,status:str,deadline:int,charge:int,records:int,history:List[str],receiver:bool,members:int}
 type Event=Retry|Renew|ChangeStamp|Expire|Drain|Foreign|ReplaceReceiver
 var s:State
 pure def label(e:Event):str=match e{ |Retry=>"Retry" |Renew=>"Renew" |ChangeStamp=>"ChangeStamp" |Expire=>"Expire" |Drain=>"Drain" |Foreign=>"Foreign" |ReplaceReceiver=>"ReplaceReceiver" }
 pure def reduce(st:State,e:Event):State=if(not(st.receiver) and (e==Retry or e==Renew or e==ChangeStamp or e==Foreign)){...st,status:"ReceiverRejected"} else match e{
  |Retry=>if(st.now>=st.deadline){...st,status:"Expired"} else if(st.free){...st,status:"Started",members:3,free:false,issued:true,charge:64,records:2} else {...st,status:"Capacity",members:3}
  |Renew=>{...st,status:"Conflict"}
  |ChangeStamp=>{...st,status:"Conflict"}
  |Expire=>{...st,now:21,status:"ClockAdvanced"}
  |Drain=>{...st,free:true,charge:32,records:1,status:"CapacityReturned"}
  |Foreign=>{...st,status:"Invalid"}
  |ReplaceReceiver=>{...st,receiver:false,status:"ReceiverReplaced"}
 }
 action init=s'={now:3,free:false,issued:false,status:"Admitted",deadline:20,charge:64,records:2,history:[],receiver:true,members:2}
 action fire(e:Event):bool=all{
  if(e==Retry or e==Expire)not(s.issued) else if(e==Drain)not(s.free) and not(s.issued) else if(e==ReplaceReceiver)s.receiver else true,
  val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}
 }
 action step={nondet e=Set(Retry,Renew,ChangeStamp,Expire,Drain,Foreign,ReplaceReceiver).oneOf();fire(e)}
 val safety=all{s.deadline==20,s.members==2 or s.members==3,s.status=="ReceiverRejected" implies not(s.receiver),s.now==3 or s.now==21,s.charge==32 or s.charge==64,s.records==1 or s.records==2,s.free==(s.charge==32),s.issued implies s.now==3,s.status=="Expired" implies not(s.issued)}
}
