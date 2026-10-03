module frontend {
 type Phase=Idle|Refused|Sending|Uncertain|Accepted|Rejected
 type Event=Validate(bool)|Send|Reply({peer:bool,eof:bool,frame:bool,ok:bool,accepted:bool})|Disconnect|Retry
 var phase:Phase
 var sends:int
 var allowed:bool
 var accepted:bool
 action init=all{phase'=Idle,sends'=0,allowed'=false,accepted'=false}
 action fire(e:Event):bool=all{
  allowed'=match e {|Validate(valid)=>valid|_=>allowed},
  sends'=if(e==Send and phase==Idle and allowed)sends+1 else sends,
  phase'=match e {
   | Validate(valid)=>if(phase==Idle and not(valid))Refused else phase
   | Send=>if(phase==Idle and allowed)Sending else phase
   | Reply(r)=>if(phase!=Sending)phase else if(not(r.peer and r.eof and r.frame))Uncertain else if(r.ok and r.accepted)Accepted else Rejected
   | Disconnect=>if(phase==Sending)Uncertain else phase
   | Retry=>phase
  },
  accepted'=match e {|Reply(r)=>if(phase==Sending and r.peer and r.eof and r.frame and r.ok and r.accepted)true else accepted|_=>accepted}
 }
 val atMostOneSubmit=sends<=1
 val onlyVerifiedAcceptance=accepted implies phase==Accepted and sends==1
 val refusedNeverSends=phase==Refused implies sends==0
 val allProps=atMostOneSubmit and onlyVerifiedAcceptance and refusedNeverSends
 action step={nondet good=Bool.oneOf();nondet e=Set(Validate(good),Send,Reply({peer:good,eof:good,frame:good,ok:good,accepted:good}),Disconnect,Retry).oneOf();fire(e)}
}
