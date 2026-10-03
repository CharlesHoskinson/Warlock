module preview_admission {
 type Phase=Idle|Acquiring|Admitted|Refused
 type LockReply=Free|Busy|Unknown|Replaced
 type State={phase:Phase,now:int,deadline:int,receipt:int,current:int,required:Set[int],held:Set[int],receiptHeld:bool,keeperHeld:bool,lifecycleHeld:bool,slept:bool,publishedAt:int,authority:bool,launch:bool}
 type Event=Begin({count:int,receipt:int,deadline:int,exact:bool})|Tick(int)|ReceiptEnter|ReceiptLeave|KeeperEnter|LifecycleEnter|Acquire({address:int,reply:LockReply})|Sleep|Supersede(int)|GuardFailure|Commit|Launch
 var s:State
 pure val initial={phase:Idle,now:0,deadline:8,receipt:1,current:1,required:Set(1,2,3),held:Set(),receiptHeld:false,keeperHeld:false,lifecycleHeld:false,slept:false,publishedAt:-1,authority:true,launch:false}
 pure def refuse(x:State):State={...x,phase:Refused,held:Set(),receiptHeld:false,keeperHeld:false,lifecycleHeld:false,launch:false}
 pure def live(x:State):bool=x.now<x.deadline and x.current==x.receipt and x.authority
 pure def transition(x:State,e:Event):State=match e {
 | Tick(n)=>{val y={...x,now:x.now+n};if(n<0)refuse(x)else if(x.phase==Acquiring and not(live(y)))refuse(y)else y}
 | Begin(a)=>if(x.phase==Idle and a.exact and a.count>=1 and a.count<=64 and a.receipt==x.current and a.deadline==8 and x.now<a.deadline){...x,phase:Acquiring,receipt:a.receipt,required:1.to(a.count),deadline:a.deadline}else refuse(x)
 | ReceiptEnter=>if(x.phase==Acquiring and live(x) and x.held==Set()){...x,receiptHeld:true}else refuse(x)
 | ReceiptLeave=>{...x,receiptHeld:false}
 | KeeperEnter=>if(x.phase==Acquiring){...x,keeperHeld:true}else refuse(x)
 | LifecycleEnter=>if(x.phase==Acquiring){...x,lifecycleHeld:true}else refuse(x)
 | Acquire(a)=>if(x.phase!=Acquiring or not(live(x)) or x.receiptHeld or x.keeperHeld or x.lifecycleHeld or not(x.required.contains(a.address)) or x.held.contains(a.address))refuse(x)else match a.reply {
   | Free=>{...x,held:x.held.union(Set(a.address))}
   | Busy=>{...x,held:Set()}
   | Unknown=>refuse(x)
   | Replaced=>refuse(x)
 }
 | Sleep=>if(x.phase==Acquiring and live(x) and x.held==Set() and not(x.receiptHeld or x.keeperHeld or x.lifecycleHeld)){...x,slept:true}else refuse(x)
 | Supersede(receipt)=>refuse({...x,current:receipt})
 | GuardFailure=>refuse({...x,authority:false})
 | Commit=>if(x.phase==Acquiring and live(x) and x.held==x.required and not(x.receiptHeld or x.keeperHeld or x.lifecycleHeld)){...x,phase:Admitted,publishedAt:x.now}else refuse(x)
 | Launch=>if(x.phase==Admitted and live(x) and x.publishedAt>=0){...x,launch:true}else refuse(x)
 }
 action init=s'=initial
 action fire(e:Event):bool=s'=transition(s,e)
 val allProps=(s.phase==Admitted implies s.publishedAt>=0 and s.publishedAt<s.deadline and s.current==s.receipt and s.authority and s.held==s.required) and (s.phase==Refused implies s.held==Set() and not(s.launch)) and (s.launch implies s.phase==Admitted and s.publishedAt<s.deadline) and (s.phase==Acquiring and s.now>=s.deadline implies s.held==Set())
 action step={
  nondet a=Set(1,2,3,4).oneOf();nondet r=Set(Free,Busy,Unknown,Replaced).oneOf();nondet n=0.to(3).oneOf()
  nondet e=Set(Begin({count:3,receipt:1,deadline:8,exact:true}),Begin({count:65,receipt:1,deadline:8,exact:true}),Tick(n),ReceiptEnter,ReceiptLeave,KeeperEnter,LifecycleEnter,Acquire({address:a,reply:r}),Sleep,Supersede(2),GuardFailure,Commit,Launch).oneOf()
  fire(e)
 }
}
