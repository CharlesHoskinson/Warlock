module authority_fence {
 type Event=Query|Motion|Lose|Claim|Alias|Replace|ReceiveOwner|Drain|StartFence|ProcessFence|ReceiveReply|CompleteFence|Emit|Timeout|NoOwner|Mismatch|Retire|BusLoss|Overflow
 var wireEpoch:int
 var wireOwner:int
 var cacheEpoch:int
 var cacheOwner:int
 var server:List[(int,int)]
 var local:List[(int,int)]
 var pending:int
 var notes:List[int]
 var retired:bool
 var point:int
 var replyPoint:int
 var fence:int
 var prior:int
 var snapshotEpoch:int
 var snapshotOwner:int
 var emissions:List[(int,int,int,int)]
 var refused:bool
 action init=all {wireEpoch'=1,wireOwner'=1,cacheEpoch'=1,cacheOwner'=1,server'=List(),local'=List(),pending'=0,notes'=List(),retired'=false,point'=0,replyPoint'=0,fence'=0,prior'=0,snapshotEpoch'=0,snapshotOwner'=0,emissions'=List(),refused'=false}
 action fire(e:Event):bool={
  val change=not(retired) and ((e==Lose and wireOwner!=0) or (e==Claim and wireOwner==0) or (e==Alias and wireOwner==1) or e==Replace)
  val stop=e==Retire or e==BusLoss or e==Overflow or (change and server.length()>=4)
  val newOwner=if(e==Lose) 0 else if(e==Replace) 2 else 1
  val changed=change and not(stop)
  val receive=e==ReceiveOwner and server.length()>0 and (fence!=2 or prior>0)
  val drain=e==Drain and local.length()>0
  val query=e==Query and not(retired) and local.length()==0 and cacheOwner==1 and notes.length()<2
  val move=e==Motion and not(retired)
  val capture=move and pending!=0 and 1-point!=replyPoint and notes.length()<2
  val start=e==StartFence and not(retired) and notes.length()>0 and fence==0
  val process=not(retired) and fence==1 and (e==ProcessFence or e==NoOwner or e==Mismatch)
  val received=e==ReceiveReply and not(retired) and fence==2 and prior==0
  val complete=e==CompleteFence and not(retired) and fence==3 and local.length()==0
  val emit=e==Emit and not(retired) and fence==4 and notes.length()>0 and local.length()==0
  val valid=emit and cacheOwner==1 and snapshotOwner==1 and notes.head()==snapshotEpoch and notes.head()==cacheEpoch
  val timeout=e==Timeout and not(retired) and notes.length()>0
  all {
   wireEpoch'=if(changed) wireEpoch+1 else wireEpoch,
   wireOwner'=if(changed) newOwner else wireOwner,
   cacheEpoch'=if(stop) 0 else if(drain and not(retired)) local.head()._1 else cacheEpoch,
   cacheOwner'=if(stop) 0 else if(drain and not(retired)) local.head()._2 else cacheOwner,
   server'=if(changed) server.append((wireEpoch+1,newOwner)) else if(receive) server.tail() else server,
   local'=if(receive) local.append(server.head()) else if(drain) local.tail() else local,
   pending'=if(stop or capture or (drain and local.head()._1!=pending)) 0 else if(query) cacheEpoch else pending,
   notes'=if(stop) List() else if(capture) notes.append(pending) else if(emit or timeout) notes.tail() else notes,
   retired'=(retired or stop),
   point'=if(move) 1-point else point,
   replyPoint'=if(query) point else replyPoint,
   fence'=if(stop or emit or timeout) 0 else if(start) 1 else if(process) 2 else if(received) 3 else if(complete) 4 else fence,
   prior'=if(stop or emit or timeout) 0 else if(process) server.length() else if(receive and fence==2 and prior>0) prior-1 else prior,
   snapshotEpoch'=if(process) wireEpoch else if(stop or emit or timeout) 0 else snapshotEpoch,
   snapshotOwner'=if(process) (if(e==NoOwner) 0 else if(e==Mismatch) 2 else wireOwner) else if(stop or emit or timeout) 0 else snapshotOwner,
   emissions'=if(valid) emissions.append((notes.head(),snapshotEpoch,cacheEpoch,snapshotOwner)) else emissions,
   refused'=(e==Query and not(query))
  }
 }
 pure val EVENTS=Set(Query,Motion,Lose,Claim,Alias,Replace,ReceiveOwner,Drain,StartFence,ProcessFence,ReceiveReply,CompleteFence,Emit,Timeout,NoOwner,Mismatch,Retire,BusLoss,Overflow)
 action step={nondet e=EVENTS.oneOf();fire(e)}
 val allProps=emissions.foldl(true,(ok,p)=>ok and p._1==p._2 and p._1==p._3 and p._4==1)
  and notes.length()+(if(pending!=0)1 else 0)<=2 and server.length()<=4
  and (retired implies pending==0 and notes.length()==0 and fence==0 and cacheOwner==0)
}
