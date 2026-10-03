module preview_admission {
 type Phase=Idle|Acquiring|Admitted|Dispatched|Closed|Publishing|Published|Refused
 type LockReply=Free|Busy|Unknown|Replaced
 type State={phase:Phase,now:int,deadline:int,receipt:int,current:int,required:Set[int],held:Set[int],receiptHeld:bool,keeperHeld:bool,lifecycleHeld:bool,slept:bool,admittedAt:int,dispatchedAt:int,publishedAt:int,nextAddress:int,replaced:int,authority:bool,launch:bool,helperOwned:bool,helperClosed:bool,quarantined:bool}
 type Event=Begin({count:int,receipt:int,deadline:int,exact:bool})|Tick(int)|ReceiptEnter|ReceiptLeave|KeeperEnter|LifecycleEnter|Acquire({address:int,reply:LockReply})|Sleep|Supersede(int)|GuardFailure|Commit|Launch|NormalClosure|UnknownClosure|BeginPublication|ReplaceOne|FinishPublication|ReceiptWait
 var s:State
 pure val initial={phase:Idle,now:0,deadline:8,receipt:1,current:1,required:Set(1,2,3),held:Set(),receiptHeld:false,keeperHeld:false,lifecycleHeld:false,slept:false,admittedAt:-1,dispatchedAt:-1,publishedAt:-1,nextAddress:1,replaced:0,authority:true,launch:false,helperOwned:false,helperClosed:false,quarantined:false}
 pure def refuse(x:State):State={...x,phase:Refused,held:Set(),receiptHeld:false,keeperHeld:false,lifecycleHeld:false,launch:false}
 pure def live(x:State):bool=x.now<x.deadline and x.current==x.receipt and x.authority
 pure def transition(x:State,e:Event):State=match e {
 | Tick(n)=>{val y={...x,now:x.now+n};if(n<0)refuse(x)else if(x.phase==Acquiring and not(live(y)))refuse(y)else y}
 | Begin(a)=>if(x.phase==Idle and a.exact and a.count>=1 and a.count<=64 and a.receipt==x.current and a.deadline==8 and x.now<a.deadline){...x,phase:Acquiring,receipt:a.receipt,required:1.to(a.count),deadline:a.deadline}else refuse(x)
 | ReceiptEnter=>if(x.phase==Acquiring and live(x) and x.held==Set()){...x,receiptHeld:true}else refuse(x)
 | ReceiptLeave=>{...x,receiptHeld:false}
 | KeeperEnter=>if(x.phase==Acquiring){...x,keeperHeld:true}else refuse(x)
 | LifecycleEnter=>if(x.phase==Acquiring){...x,lifecycleHeld:true}else refuse(x)
 | Acquire(a)=>if(x.phase!=Acquiring or not(live(x)) or x.receiptHeld or x.keeperHeld or x.lifecycleHeld or not(x.required.contains(a.address)) or x.held.contains(a.address) or a.address!=x.nextAddress)refuse(x)else match a.reply {
   | Free=>{...x,held:x.held.union(Set(a.address)),nextAddress:x.nextAddress+1}
   | Busy=>{...x,held:Set(),nextAddress:1}
   | Unknown=>refuse(x)
   | Replaced=>refuse(x)
 }
 | Sleep=>if(x.phase==Acquiring and live(x) and x.held==Set() and not(x.receiptHeld or x.keeperHeld or x.lifecycleHeld)){...x,slept:true}else refuse(x)
 | Supersede(receipt)=>refuse({...x,current:receipt})
 | GuardFailure=>refuse({...x,authority:false})
 | Commit=>if(x.phase==Acquiring and live(x) and x.held==x.required and not(x.receiptHeld or x.keeperHeld or x.lifecycleHeld)){...x,phase:Admitted,admittedAt:x.now}else refuse(x)
 | Launch=>if(x.phase==Admitted and live(x) and x.admittedAt>=0){...x,phase:Dispatched,launch:true,helperOwned:true,dispatchedAt:x.now}else refuse(x)
 | NormalClosure=>if(x.helperOwned){...x,phase:if(x.phase==Refused)Refused else Closed,helperOwned:false,helperClosed:true}else refuse(x)
 | UnknownClosure=>refuse({...x,quarantined:true})
 | BeginPublication=>if(x.phase==Closed and live(x) and x.helperClosed and not(x.helperOwned or x.quarantined) and x.held==x.required){...x,phase:Publishing,receiptHeld:true}else refuse(x)
 | ReplaceOne=>if(x.phase==Publishing and live(x) and x.receiptHeld and x.replaced<x.required.size()*3){...x,replaced:x.replaced+1}else refuse(x)
 | FinishPublication=>if(x.phase==Publishing and live(x) and x.receiptHeld and x.helperClosed and not(x.helperOwned or x.quarantined) and x.replaced==x.required.size()*3){...x,phase:Published,publishedAt:x.now,receiptHeld:false}else refuse(x)
 | ReceiptWait=>if(live(x) and not(x.receiptHeld or x.keeperHeld or x.lifecycleHeld) and (x.held==Set() or x.held==x.required))x else refuse(x)
 }
 action init=s'=initial
 action fire(e:Event):bool=s'=transition(s,e)
 val allProps=(s.phase==Admitted implies s.admittedAt>=0 and s.admittedAt<s.deadline and s.current==s.receipt and s.authority and s.held==s.required) and (s.phase==Refused implies s.held==Set() and not(s.launch)) and (s.launch implies s.dispatchedAt>=s.admittedAt and s.dispatchedAt<s.deadline) and (s.phase==Acquiring and s.now>=s.deadline implies s.held==Set()) and (s.phase==Published implies s.publishedAt>=s.dispatchedAt and s.publishedAt<s.deadline and s.helperClosed and not(s.helperOwned or s.quarantined) and s.current==s.receipt and s.authority and s.replaced==s.required.size()*3)

 action step={
  nondet a=Set(1,2,3,4).oneOf();nondet r=Set(Free,Busy,Unknown,Replaced).oneOf();nondet n=0.to(3).oneOf()
  nondet e=Set(Begin({count:3,receipt:1,deadline:8,exact:true}),Begin({count:65,receipt:1,deadline:8,exact:true}),Tick(n),ReceiptEnter,ReceiptLeave,KeeperEnter,LifecycleEnter,Acquire({address:a,reply:r}),Sleep,Supersede(2),GuardFailure,Commit,Launch,NormalClosure,UnknownClosure,BeginPublication,ReplaceOne,FinishPublication,ReceiptWait).oneOf()
  fire(e)
 }
}
