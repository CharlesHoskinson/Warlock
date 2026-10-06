module resume {
 type State={now:int,deadline:int,free:bool,records:int,charge:int,floor:int,receiver:bool,status:str,known:bool,fault:bool,queries:int,history:List[str]}
 type Event=Retry|ChangeStamp|Expire|Drain|ReplaceReceiver|RejectNative
 var s:State
 pure def label(e:Event):str=match e{|Retry=>"Retry"|ChangeStamp=>"ChangeStamp"|Expire=>"Expire"|Drain=>"Drain"|ReplaceReceiver=>"ReplaceReceiver"|RejectNative=>"RejectNative"}
 pure def reduce(st:State,e:Event):State=match e{
  |Retry=>if(not(st.receiver)){...st,status:"ReceiverRejected"}else{
   val cutoff=if(st.deadline==0)st.now+2000000000 else st.deadline
   val updated={...st,deadline:cutoff,queries:st.queries+1}
   if(st.now>=cutoff){...updated,status:"Expired"}else if(not(st.free)){...updated,status:"Capacity"}else if(st.fault){...updated,status:"NativeRejected",known:true,floor:2,records:2}else{...updated,status:"Started",known:true,floor:2,records:2,charge:64,free:false}
  }
  |ChangeStamp=>if(not(st.receiver)){...st,status:"ReceiverRejected"}else{...st,status:"Conflict",queries:st.queries+1}
  |Expire=>{...st,now:2000000005,status:"ClockAdvanced"}
  |Drain=>{...st,free:true,records:1,charge:32,status:"CapacityReturned"}
  |ReplaceReceiver=>{...st,receiver:false,status:"ReceiverReplaced"}
  |RejectNative=>{...st,fault:true,status:"Incoherent"}
 }
 action init=s'={now:4,deadline:0,free:false,records:2,charge:64,floor:1,receiver:true,status:"Ready",known:false,fault:false,queries:0,history:[]}
 action fire(e:Event):bool=all{
  not(s.known),
  if(e==ChangeStamp or e==Expire)s.deadline!=0 else if(e==Drain)not(s.free) else if(e==ReplaceReceiver)s.receiver else if(e==RejectNative)not(s.fault) else true,
  val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}
 }
 action step={nondet e=Set(Retry,ChangeStamp,Expire,Drain,ReplaceReceiver,RejectNative).oneOf();fire(e)}
 val safety=all{s.deadline==0 or s.deadline==2000000004,s.floor==1 or s.floor==2,s.known==(s.floor==2),s.free==(s.charge==32),s.records==1 or s.records==2,s.status=="Expired" implies not(s.known),s.status=="NativeRejected" implies s.known and s.fault,s.status=="ReceiverRejected" implies not(s.receiver)}
}
