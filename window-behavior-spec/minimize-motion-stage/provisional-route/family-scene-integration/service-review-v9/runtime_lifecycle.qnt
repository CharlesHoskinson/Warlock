module runtime_lifecycle {
 type Event=Start({lease:bool,private:bool,unresolved:bool})|Receive|Persist(bool)|Acknowledge|Validate|Commit|JournalFail|Stop|IdleStop
 type State={running:bool,receipt:int,durable:int,validated:int,ack:bool,ackReceipt:int,effect:bool,effectReceipt:int,failed:bool,actors:int}
 var s:State
 action init=s'={running:false,receipt:0,durable:0,validated:0,ack:false,ackReceipt:0,effect:false,effectReceipt:0,failed:false,actors:0}
 action fire(e:Event):bool={val b={...s,ack:false,effect:false};s'=match e {
  | Start(p)=>if(not(s.running) and p.lease and p.private and not(p.unresolved)){...b,running:true,failed:false} else b
  | Receive=>if(s.running and not(s.failed)){...b,receipt:s.receipt+1,validated:0} else b
  | Persist(ok)=>if(ok and s.running and not(s.failed)){...b,durable:s.receipt} else {...b,failed:true}
  | Acknowledge=>if(s.running and not(s.failed) and s.receipt>0 and s.durable==s.receipt){...b,ack:true,ackReceipt:s.receipt} else b
  | Validate=>if(s.running and not(s.failed) and s.durable==s.receipt and s.receipt>0){...b,validated:s.receipt} else b
  | Commit=>if(s.running and not(s.failed) and s.validated==s.receipt and s.durable==s.receipt and s.receipt>0){...b,effect:true,effectReceipt:s.receipt} else b
  | JournalFail=>{...b,failed:true,validated:0}
  | Stop=>{...b,running:false,validated:0,actors:0}
  | IdleStop=>b
 }}
 val allProps=(s.ack implies (s.running and not(s.failed) and s.ackReceipt==s.receipt and s.durable==s.receipt)) and (s.effect implies(s.running and not(s.failed) and s.effectReceipt==s.receipt and s.durable==s.receipt and s.validated==s.receipt))
 action step={nondet e=Set(Start({lease:true,private:true,unresolved:false}),Start({lease:false,private:true,unresolved:false}),Start({lease:true,private:false,unresolved:false}),Start({lease:true,private:true,unresolved:true}),Receive,Persist(true),Persist(false),Acknowledge,Validate,Commit,JournalFail,Stop,IdleStop).oneOf();fire(e)}
}
