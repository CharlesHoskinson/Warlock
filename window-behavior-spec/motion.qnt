/** Qualitative motion contract. Tick is a progress step, not a wall-clock bound.
 * Native presentation measurements separately establish observed timing.
 */
module motion {
  type Event = Animate(int) | Tick(int) | Reduce(bool) | Close | Open | Submit | Present
  type Frame = {valid:bool, position:int, target:int, reduced:bool}
  type State = {live:bool, identity:int, reduced:bool, position:int, target:int,
    epoch:int, running:bool, beforePosition:int, beforeTarget:int,
    lastTick:bool, tickAccepted:bool, pending:Frame, displayed:Frame}
  var s:State
  pure val emptyFrame={valid:false,position:0,target:0,reduced:false}
  action init=s'={live:true,identity:1,reduced:false,position:0,target:0,epoch:0,running:false,
    beforePosition:0,beforeTarget:0,lastTick:false,tickAccepted:false,
    pending:emptyFrame,displayed:emptyFrame}
  pure def advance(position:int,target:int):int =
    if(position<target)position+1 else if(position>target)position-1 else position
  pure def distance(a:int,b:int):int=if(a>b)a-b else b-a
  action fire(event:Event):bool = {
    val base={...s,beforePosition:s.position,beforeTarget:s.target,lastTick:false,tickAccepted:false}
    s'=match event {
      | Animate(target) => if(not(s.live))base else {...base,target:target,epoch:s.epoch+1,
          position:if(s.reduced)target else s.position,running:not(s.reduced) and target!=s.position}
      | Tick(epoch) => if(s.live and s.running and epoch==s.epoch and not(s.reduced)) {
          val advanced=advance(s.position,s.target)
          {...base,lastTick:true,tickAccepted:true,position:advanced,running:advanced!=s.target}
        } else {...base,lastTick:true}
      | Reduce(isReduced) => {...base,reduced:isReduced,epoch:s.epoch+1,
          position:if(isReduced)s.target else s.position,running:if(isReduced)false else s.running}
      | Close => {...base,live:false,running:false,position:s.target,epoch:s.epoch+1,pending:emptyFrame,displayed:emptyFrame}
      | Open => if(s.live)base else {...base,live:true,identity:s.identity+1,position:0,target:0,running:false,epoch:s.epoch+1}
      | Submit => if(not(s.live) or s.pending.valid)base else {...base,
          pending:{valid:true,position:s.position,target:s.target,reduced:s.reduced}}
      | Present => if(not(s.pending.valid))base else {...base,displayed:s.pending,pending:emptyFrame}
    }
  }
  action step = {
    nondet target=0.to(16).oneOf()
    nondet event=Set(Animate(target),Tick(s.epoch),Tick(s.epoch-1),Reduce(true),Reduce(false),Close,Open,Submit,Present).oneOf()
    fire(event)
  }
  val reducedSettles=s.reduced implies (not(s.running) and s.position==s.target)
  val staleTicksSafe=(s.lastTick and not(s.tickAccepted)) implies (s.position==s.beforePosition and s.target==s.beforeTarget)
  val tickProgress=s.tickAccepted implies (distance(s.target,s.position)<distance(s.beforeTarget,s.beforePosition))
  val noOvershoot=s.tickAccepted implies (if(s.beforePosition<=s.target)
    (s.position>=s.beforePosition and s.position<=s.target) else (s.position>=s.target and s.position<=s.beforePosition))
  val submittedReducedSettled=(s.pending.valid and s.pending.reduced) implies s.pending.position==s.pending.target
  val displayedReducedSettled=(s.displayed.valid and s.displayed.reduced) implies s.displayed.position==s.displayed.target
  val noDeadMotion=not(s.live) implies (not(s.running) and not(s.pending.valid) and not(s.displayed.valid))
  val bounded=0<=s.position and s.position<=16 and 0<=s.target and s.target<=16
  val allProps=reducedSettles and staleTicksSafe and tickProgress and noOvershoot
    and submittedReducedSettled and displayedReducedSettled and noDeadMotion and bounded
}
