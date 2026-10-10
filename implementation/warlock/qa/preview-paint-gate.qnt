module previewPaintGate {
  // UI-016 preview-states: renderer paint opportunity before original Acquire.
  // Full native job identity abstracts binding/context/request/origin/clock/
  // deadline, never just the window incarnation. Native admission stays outside.
  type State={pending:Set[(int,int)],sent:Set[(int,int)],issued:Set[int],painted:Set[(int,int)],cancelledBeforeSend:Set[int],cancelled:Set[int],controls:int,dispatches:int}
  var s:State
  action init=s'={pending:Set(),sent:Set(),issued:Set(),painted:Set(),cancelledBeforeSend:Set(),cancelled:Set(),controls:0,dispatches:0}
  action idle=s'=s
  action queue(ticket:int,job:int):bool=all{not(s.issued.contains(job)),s'={...s,pending:s.pending.union(Set((ticket,job))),issued:s.issued.union(Set(job))}}
  pure def callback(state:State,ticket:int):State={
    val ready=state.pending.filter(pair=>pair._1==ticket)
    {...state,pending:state.pending.exclude(ready),sent:state.sent.union(ready),painted:state.painted.union(ready),dispatches:state.dispatches+ready.size()}
  }
  action paint(ticket:int):bool=s'=callback(s,ticket)
  action cancel(job:int):bool={
    val unsent=s.pending.filter(pair=>pair._2==job)
    s'={...s,pending:s.pending.exclude(unsent),cancelled:s.cancelled.union(Set(job)),cancelledBeforeSend:if(unsent.size()>0) s.cancelledBeforeSend.union(Set(job)) else s.cancelledBeforeSend,controls:s.controls+1}
  }
  action control=s'={...s,controls:s.controls+1}
  action step=any{idle,queue(1,1),queue(2,2),paint(1),paint(2),paint(9),cancel(1),cancel(2),control}
  // Callback is supplied after the browser's paint opportunity, not hardware
  // proof. Native/current scope guards still validate the original command.
  val safety=s.pending.size()<=2 and s.dispatches==s.sent.size() and s.sent.subseteq(s.painted) and
    s.sent.forall(pair=>not(s.cancelledBeforeSend.contains(pair._2)))
  val paintDispatchWitness=s.sent.contains((1,1)) and s.dispatches>=1
  val cancelledUnsentWitness=s.cancelledBeforeSend.contains(1) and not(s.sent.contains((1,1))) and s.controls>0
  val independentDispatchWitness=s.cancelledBeforeSend.contains(1) and s.sent.contains((2,2))
}
