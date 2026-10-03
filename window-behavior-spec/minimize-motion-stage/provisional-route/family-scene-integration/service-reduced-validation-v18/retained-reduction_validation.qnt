module reduction_validation {
  type State = {receipt:int, token:int, validated:int, context:bool,
    reduced:bool, visual:bool, retiring:int, alive:bool, native:int,
    desired:int, commits:int, lastCommitReceipt:int, commitProved:bool,
    error:bool, sources:bool, fresh:bool}
  type Witness = {receipt:int,token:int}
  type Event = ReduceOn | ReduceOff | Watchdog | Context | Validate(Witness)
    | Ack(int) | NewRequest | StartVisual | Presented(Witness) | LoseScope
    | Deadline | OldReady(Witness)
  var s:State
  pure val initial = {receipt:1,token:1,validated:0,context:true,
    reduced:false,visual:false,retiring:0,alive:true,native:0,
    desired:1,commits:0,lastCommitReceipt:0,commitProved:true,
    error:false,sources:false,fresh:false}
  action init = s'=initial
  action existing = s'={...initial,receipt:2,token:2,native:1,desired:0,
    visual:true,sources:true}
  def mayCommit(x:State):bool = x.alive and not(x.error) and x.context
    and x.validated==x.receipt and x.fresh and x.retiring==0
  def commit(x:State):State = {...x,native:x.desired,commits:x.commits+1,
    lastCommitReceipt:x.receipt,commitProved:x.commitProved and mayCommit(x),
    alive:false,retiring:if(x.visual)x.token else 0}
  action fire(e:Event):bool = s'=(match e {
    | ReduceOn => {...s,reduced:true}
    | ReduceOff => {...s,reduced:false}
    | Watchdog => if(s.reduced and mayCommit(s))commit(s)
      else if(s.alive and not(s.error) and s.reduced and s.visual
        and s.validated!=s.receipt and s.retiring==0)
        {...s,retiring:s.token,validated:0,fresh:false} else s
    | Context => if(s.alive and not(s.error)){...s,context:true} else s
    | Validate(p) => if(s.alive and not(s.error) and s.context
        and s.retiring==0 and p.receipt==s.receipt and p.token==s.token)
        {...s,validated:p.receipt,fresh:true} else s
    | Ack(t) => if(t==s.retiring and t>0)
        if(s.alive and not(s.error)){...s,token:s.token+1,visual:false,
          sources:false,retiring:0,validated:0,fresh:false}
        else {...s,visual:false,sources:false,retiring:0}
      else s
    | NewRequest => {...s,receipt:s.receipt+1,token:s.token+1,
        desired:1-s.desired,context:false,validated:0,fresh:false,
        alive:true,error:false}
    | StartVisual => if(mayCommit(s) and not(s.reduced))
        {...s,visual:true,sources:true} else s
    | Presented(p) => if(mayCommit(s) and not(s.reduced) and s.visual
        and p.receipt==s.receipt and p.token==s.token)commit(s) else s
    | LoseScope => {...s,fresh:false,validated:0,error:true}
    | Deadline => if(s.alive and s.validated==0){...s,alive:false,error:true,
        retiring:if(s.visual and s.retiring==0)s.token else s.retiring} else s
    | OldReady(p) => s
  })
  val allProps = s.commitProved and s.lastCommitReceipt<=s.receipt
    and s.retiring<=s.token and (s.validated==0 or s.validated==s.receipt)
    and (s.retiring>0 implies s.sources)
  action step = {
    nondet e=Set(ReduceOn,ReduceOff,Watchdog,Context,Validate({receipt:s.receipt,token:s.token}),
      Validate({receipt:s.receipt-1,token:s.token-1}),Ack(s.retiring),Ack(s.token-1),NewRequest,
      StartVisual,Presented({receipt:s.receipt,token:s.token}),Presented({receipt:s.receipt-1,token:s.token-1}),
      LoseScope,Deadline,OldReady({receipt:s.receipt-1,token:s.token-1})).oneOf()
    fire(e)
  }
}
