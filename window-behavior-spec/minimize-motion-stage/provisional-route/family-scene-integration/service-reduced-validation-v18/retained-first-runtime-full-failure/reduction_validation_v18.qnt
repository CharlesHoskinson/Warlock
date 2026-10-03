module reduction_validation_v18 {
  type Binding={token:int,root:int,session:int,transport:int,members:int,sources:int}
  type Worker={receipt:int,token:int,generation:int}
  type State={receipt:int,token:int,generation:int,contextPending:bool,ingressGeneration:int,
    reduced:bool,alive:bool,scopeAlive:bool,validatedReceipt:int,validatedGeneration:int,
    visualToken:int,sources:bool,retirement:Binding,cancelQueued:bool,cancelCount:int,
    acked:bool,error:bool,uncertain:bool,commits:int,lastCommitReceipt:int,
    commitProved:bool,desired:int,nativeDirection:int,releases:int,releaseProved:bool,
    elapsed:int,receiptDeadline:int}
  type Event=ReduceOn|ReduceOff|Watchdog|Request|Context(int)|Validate(Worker)
    | StartVisual|Ready(Worker)|Endpoint(Worker)|Ack(Binding)|QueueFailure
    | TransportFailure|LoseScope|Deadline|Tick|OldWorker(Worker)
  pure val none={token:0,root:1,session:2,transport:3,members:4,sources:5}
  pure val initial={receipt:1,token:1,generation:1,contextPending:false,ingressGeneration:0,
    reduced:false,alive:true,scopeAlive:true,validatedReceipt:0,validatedGeneration:0,
    visualToken:0,sources:false,retirement:none,cancelQueued:false,cancelCount:0,
    acked:false,error:false,uncertain:false,commits:0,lastCommitReceipt:0,
    commitProved:true,desired:1,nativeDirection:0,releases:0,releaseProved:true,
    elapsed:0,receiptDeadline:10}
  var s:State
  action init=s'=initial
  action moving=s'={...initial,receipt:2,token:2,generation:2,visualToken:2,sources:true,desired:0,nativeDirection:1}
  action pendingContext=s'={...initial,receipt:2,token:2,generation:2,contextPending:true,ingressGeneration:2,
    visualToken:2,sources:true,desired:0,nativeDirection:1}
  def bound(x:State):Binding={...none,token:x.visualToken}
  def current(x:State,w:Worker):bool=w.receipt==x.receipt and w.token==x.token
    and w.generation==x.generation
  def mayPrepare(x:State):bool=x.alive and x.scopeAlive and not(x.error)
    and not(x.uncertain) and not(x.contextPending) and x.retirement.token==0
    
  def mayCommit(x:State):bool=mayPrepare(x) and x.validatedReceipt==x.receipt
    and x.validatedGeneration==x.generation
  def commit(x:State):State={...x,commits:x.commits+1,lastCommitReceipt:x.receipt,
    commitProved:x.commitProved and mayCommit(x),nativeDirection:x.desired,alive:false}
  def suppress(x:State):State=if(x.visualToken>0 and x.retirement.token==0)
    {...x,retirement:bound(x),cancelQueued:true,cancelCount:x.cancelCount+1,
      validatedReceipt:0,validatedGeneration:0} else x
  action fire(e:Event):bool=s'=(match e {
    | ReduceOn=>{...s,reduced:true}
    | ReduceOff=>{...s,reduced:false}
    | Watchdog=>if(s.reduced and mayCommit(s))commit(s)
      else if(s.alive and not(s.error) and s.reduced and not(mayCommit(s)))suppress(s) else s
    | Request=>{...s,receipt:s.receipt+1,token:s.token+1,generation:s.generation+1,
      contextPending:true,ingressGeneration:s.generation+1,validatedReceipt:0,desired:1-s.desired,
      validatedGeneration:0,alive:true,error:s.uncertain,acked:if(s.retirement.token>0)s.acked else false,
      visualToken:if(s.visualToken>0 and s.retirement.token==0)s.token+1 else s.visualToken,
      elapsed:0,receiptDeadline:10}
    | Context(r)=>if(r==s.receipt and s.alive and not(s.error))
      {...s,contextPending:false,ingressGeneration:0} else s
    | Validate(w)=>if(current(s,w) and mayPrepare(s))
      {...s,validatedReceipt:s.receipt,validatedGeneration:s.generation} else s
    | StartVisual=>if(mayCommit(s) and not(s.reduced))
      {...s,visualToken:s.token,sources:true} else s
    | Ready(w)=>if(current(s,w) and mayCommit(s) and not(s.reduced)
      and s.visualToken==s.token)commit(s) else s
    | Endpoint(w)=>if(current(s,w) and mayCommit(s) and not(s.reduced)
      and s.visualToken==s.token)commit(s) else s
    | Ack(b)=>if(b==s.retirement and b.token>0 and s.cancelQueued and not(s.acked))
      if(s.uncertain){...s,visualToken:0,acked:true}
      else if(s.alive and not(s.error))
        {...s,token:s.token+1,generation:s.generation+1,visualToken:0,sources:false,
          retirement:none,cancelQueued:false,acked:true,validatedReceipt:0,
          validatedGeneration:0,ingressGeneration:if(s.contextPending)s.generation+1 else 0,
          releases:s.releases+1,releaseProved:s.releaseProved and b==s.retirement}
      else {...s,visualToken:0,sources:false,retirement:none,cancelQueued:false,acked:true,
        releases:s.releases+1,releaseProved:s.releaseProved and b==s.retirement}
      else s
    | QueueFailure=>if(s.retirement.token>0)
      {...s,error:true,uncertain:true,cancelQueued:false} else s
    | TransportFailure=>{...s,error:true,uncertain:true}
    | LoseScope=>{...s,scopeAlive:false,error:true,validatedReceipt:0,validatedGeneration:0}
    | Deadline=>if(s.elapsed>=s.receiptDeadline and s.alive)
      {...suppress(s),alive:false,error:true} else s
    | Tick=>{...s,elapsed:s.elapsed+1}
    | OldWorker(w)=>if(current(s,w) and mayPrepare(s))
      {...s,validatedReceipt:s.receipt,validatedGeneration:s.generation} else s
  })
  val allProps=s.commitProved and s.releaseProved and s.lastCommitReceipt<=s.receipt
    and (s.validatedReceipt==0 or s.validatedReceipt==s.receipt)
    and (s.validatedGeneration==0 or s.validatedGeneration==s.generation)
    and (s.retirement.token>0 implies s.sources)
    and (s.retirement.token>0 implies s.visualToken==s.retirement.token or (s.acked and s.visualToken==0))
    and (s.retirement.token>0 implies s.validatedReceipt==0)
    and (s.contextPending implies s.ingressGeneration==s.generation)
    and (s.uncertain implies s.error)
  action step={
    nondet e=Set(ReduceOn,ReduceOff,Watchdog,Request,Context(s.receipt),Context(s.receipt-1),
      Validate({receipt:s.receipt,token:s.token,generation:s.generation}),
      Validate({receipt:s.receipt,token:s.token,generation:s.generation-1}),
      StartVisual,Ready({receipt:s.receipt,token:s.token,generation:s.generation}),
      Endpoint({receipt:s.receipt-1,token:s.token-1,generation:s.generation-1}),
      Ack(s.retirement),Ack({...s.retirement,members:99}),Ack({...s.retirement,session:99}),
      QueueFailure,TransportFailure,LoseScope,Tick,Deadline,
      OldWorker({receipt:s.receipt,token:s.token,generation:s.generation-1})).oneOf()
    fire(e)
  }
}
