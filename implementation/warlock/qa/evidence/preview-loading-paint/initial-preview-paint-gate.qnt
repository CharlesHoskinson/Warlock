module previewPaintGate {
  // UI-016 preview-states: renderer paint opportunity before original Acquire.
  // Full native job identity abstracts binding/context/request/origin/clock/
  // deadline, never just the window incarnation. Native admission stays outside.
  type State={pending:Set[(int,int)],sent:Set[(int,int)],cancelled:Set[int],controls:int}
  var s:State
  action init=s'={pending:Set(),sent:Set(),cancelled:Set(),controls:0}
  action idle=s'=s
  action step=idle
  val safety=s.sent==Set()
}
