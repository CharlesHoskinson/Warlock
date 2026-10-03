module frontend {
 type Phase=Idle|Refused|Sending|VerifiedAccepted|Uncertain|Accepted|Rejected
 type Receipt={peer:bool,eof:bool,frame:bool,ok:bool,accepted:bool,completedFalse:bool,receiptValid:bool}
 type Event=Validate(bool)|Send|Reply(Receipt)|CommitLog(bool)|Disconnect|Retry
 var phase:Phase
 var sends:int
 var allowed:bool
 var accepted:bool
 var verifiedReceipt:bool
 pure def valid(r:Receipt):bool=r.peer and r.eof and r.frame and r.ok and r.accepted and r.completedFalse and r.receiptValid
 action init=all{phase'=Idle,sends'=0,allowed'=false,accepted'=false,verifiedReceipt'=false}
 action fire(e:Event):bool=all{
  allowed'=match e {|Validate(good)=>if(phase==Idle)good else allowed|_=>allowed},
  sends'=if(e==Send and phase==Idle and allowed)sends+1 else sends,
  phase'=match e {
   | Validate(good)=>if(phase==Idle and not(good))Refused else phase
   | Send=>if(phase==Idle and allowed)Sending else phase
   | Reply(r)=>if(phase!=Sending)phase else if(valid(r))VerifiedAccepted else if(r.peer and r.eof and r.frame and not(r.ok) and not(r.accepted))Rejected else Uncertain
   | CommitLog(good)=>if(phase==VerifiedAccepted)if(good)Accepted else Uncertain else phase
   | Disconnect=>if(phase==Sending or phase==VerifiedAccepted)Uncertain else phase
   | Retry=>phase
  },
  verifiedReceipt'=match e {|Reply(r)=>if(phase==Sending and valid(r))true else verifiedReceipt|_=>verifiedReceipt},
  accepted'=match e {|CommitLog(good)=>if(phase==VerifiedAccepted and good)true else accepted|_=>accepted}
 }
 val atMostOneSubmit=sends<=1
 val onlyVerifiedAcceptance=accepted implies phase==Accepted and sends==1 and verifiedReceipt
 val refusedNeverSends=phase==Refused implies sends==0
 val receiptsOnlyAfterOneSend=verifiedReceipt implies sends==1
 val allProps=atMostOneSubmit and onlyVerifiedAcceptance and refusedNeverSends and receiptsOnlyAfterOneSend
 action step={
  nondet p=Bool.oneOf();nondet e=Bool.oneOf();nondet f=Bool.oneOf();nondet o=Bool.oneOf();nondet a=Bool.oneOf();nondet c=Bool.oneOf();nondet r=Bool.oneOf();nondet good=Bool.oneOf()
  nondet event=Set(Validate(good),Send,Reply({peer:p,eof:e,frame:f,ok:o,accepted:a,completedFalse:c,receiptValid:r}),CommitLog(good),Disconnect,Retry).oneOf();fire(event)
 }
}
