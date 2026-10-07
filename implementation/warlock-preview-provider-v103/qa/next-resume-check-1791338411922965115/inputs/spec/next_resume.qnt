module next_resume {
 type State={now:int,deadline:int,previous:int,publication:int,lease:int,free:bool,records:int,charge:int,floor:int,receiver:bool,status:str,known:bool,fault:bool,queries:int,history:List[str]}
 type Event=Retry|Next|PartialPublication|PartialLease|OldStamp|Expire|Drain|ReplaceReceiver|RejectNative|MissingPredecessor
 var s:State
 pure def label(e:Event):str=match e{
  |Retry=>"Retry" |Next=>"Next" |PartialPublication=>"PartialPublication" |PartialLease=>"PartialLease" |OldStamp=>"OldStamp" |Expire=>"Expire" |Drain=>"Drain" |ReplaceReceiver=>"ReplaceReceiver" |RejectNative=>"RejectNative" |MissingPredecessor=>"MissingPredecessor"
 }
 pure def attempt(st:State):State=if(st.now>=st.deadline){...st,status:"Expired"}else if(not(st.free)){...st,status:"Capacity"}else if(st.fault){...st,status:"NativeRejected",known:true,floor:2,records:2}else{...st,status:"Started",known:true,floor:2,records:2,charge:64,free:false}
 pure def reduce(st:State,e:Event):State=match e{
  |Retry=>if(not(st.receiver)){...st,status:"ReceiverRejected"}else{
   val cutoff=if(st.deadline==0)st.now+2000000000 else st.deadline
   attempt({...st,deadline:cutoff,publication:if(st.deadline==0)2 else st.publication,lease:if(st.deadline==0)2 else st.lease,queries:st.queries+1})
  }
  |Next=>if(not(st.receiver)){...st,status:"ReceiverRejected"}else if(st.now<st.deadline){...st,status:"Conflict",queries:st.queries+1}else{
   attempt({...st,previous:st.deadline,deadline:st.now+2000000000,publication:st.publication+1,lease:st.lease+1,queries:st.queries+1})
  }
  |PartialPublication=>if(not(st.receiver)){...st,status:"ReceiverRejected"}else{...st,status:"Conflict",queries:st.queries+1}
  |PartialLease=>if(not(st.receiver)){...st,status:"ReceiverRejected"}else{...st,status:"Conflict",queries:st.queries+1}
  |OldStamp=>if(not(st.receiver)){...st,status:"ReceiverRejected"}else{...st,status:"Conflict",queries:st.queries+1}
  |MissingPredecessor=>if(not(st.receiver)){...st,status:"ReceiverRejected"}else{...st,status:"Invalid",queries:st.queries+1}
  |Expire=>{...st,now:st.deadline+1,status:"ClockAdvanced"}
  |Drain=>{...st,free:true,records:1,charge:32,status:"CapacityReturned"}
  |ReplaceReceiver=>{...st,receiver:false,status:"ReceiverReplaced"}
  |RejectNative=>{...st,fault:true,status:"Incoherent"}
 }
 action init=s'={now:4,deadline:0,previous:0,publication:0,lease:0,free:false,records:2,charge:64,floor:1,receiver:true,status:"Ready",known:false,fault:false,queries:0,history:[]}
 action fire(e:Event):bool=all{
  not(s.known),
  if(e==Next or e==PartialPublication or e==PartialLease or e==OldStamp or e==MissingPredecessor or e==Expire)s.deadline!=0 else if(e==Drain)not(s.free)else if(e==ReplaceReceiver)s.receiver else if(e==RejectNative)not(s.fault)else true,
  val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}
 }
 action step={nondet e=Set(Retry,Next,PartialPublication,PartialLease,OldStamp,Expire,Drain,ReplaceReceiver,RejectNative,MissingPredecessor).oneOf();fire(e)}
 val safety=all{s.floor==1 or s.floor==2,s.known==(s.floor==2),s.free==(s.charge==32),s.records==1 or s.records==2,s.publication==s.lease,s.previous==0 or s.previous<s.deadline,s.status=="Expired" implies not(s.known),s.status=="NativeRejected" implies s.known and s.fault,s.status=="ReceiverRejected" implies not(s.receiver)}
}
