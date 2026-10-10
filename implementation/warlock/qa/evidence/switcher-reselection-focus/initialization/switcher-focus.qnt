module switcherFocus {
  // UX-014/UX-026 reconciliation of an already-admitted browsing chord.
  // Opaque IDs are native incarnations, never addresses or labels. Elm update
  // is atomic; existing admission, ordinal, mutation and native AT protocols
  // are outside this focus-request model and retain their original oracles.
  type State = {live:Set[int], selected:int, closed:bool, label:int, previous:int, target:int, focuses:int, changes:int}
  var s:State
  action init=s'={live:Set(1,2,3),selected:2,closed:false,label:0,previous:2,target:0,focuses:0,changes:0}
  action observeSame=s'={...s,previous:s.selected,target:0}
  action step=observeSame
  val safety=(s.selected==0 or s.selected.in(s.live)) and (s.target==0 or (s.target==s.selected and s.target!=s.previous)) and s.focuses<=s.changes
}
