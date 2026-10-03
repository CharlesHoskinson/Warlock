module ownership {
 type State={barState:int,identity:int,request:int,pending:bool,dragOwner:int,borrowed:bool,success:bool,retired:bool,promotions:int,releaseSuppressed:bool}
 var s:State
 action init=s'={barState:0,identity:1,request:1,pending:false,dragOwner:0,borrowed:false,success:false,retired:false,promotions:0,releaseSuppressed:true}
 action reset(barState:int,identity:int,pending:bool,dragOwner:int):bool=s'={...s,barState:barState,identity:identity,pending:pending,dragOwner:dragOwner,borrowed:false,success:false,retired:false}
 action retire(request:int):bool={
  val valid=request==s.identity
  val live=s.barState==0
  val held=valid and s.dragOwner==s.identity
  val intent=valid and live and s.pending
  s'={...s,request:request,borrowed:valid and live,success:valid,retired:held or intent,pending:if(valid and live) false else s.pending,dragOwner:if(held) 0 else s.dragOwner}
 }
 action finishBorrow=s'={...s,borrowed:false}
 val noSharedPromotion=s.promotions==0
 val noDestroyingBorrow=not(s.borrowed) or s.barState==0
 val exactIdentity=not(s.success) or s.request==s.identity
 val noIntentRevival=not(s.borrowed) or not(s.pending)
 val preserveGenuineRelease=s.releaseSuppressed
 val allProps=noSharedPromotion and noDestroyingBorrow and exactIdentity and noIntentRevival and preserveGenuineRelease
 action step={nondet state=0.to(2).oneOf();nondet id=1.to(2).oneOf();nondet pending=Set(false,true).oneOf();nondet drag=0.to(2).oneOf();nondet request=1.to(3).oneOf();any{reset(state,id,pending,drag),retire(request),finishBorrow}}
}
