module switcherFocus {
  // UX-014/UX-026 reconciliation of an already-admitted browsing chord.
  // Opaque IDs are native incarnations, never addresses or labels. Elm update
  // is atomic; existing admission, ordinal, mutation and native AT protocols
  // are outside this focus-request model and retain their original oracles.
  type State = {live:Set[int], selected:int, closed:bool, label:int, previous:int, target:int, focuses:int, changes:int}
  var s:State
  action init=s'={live:Set(1,2,3),selected:2,closed:false,label:0,previous:2,target:0,focuses:0,changes:0}
  pure def nextLive(live:Set[int], old:int):int =
    if (old.in(live)) old
    else if (old==3 and 2.in(live)) 2
    else if (old==2 and 1.in(live)) 1
    else if (old==1 and 3.in(live)) 3
    else if (1.in(live)) 1 else if (2.in(live)) 2 else if (3.in(live)) 3 else 0
  pure def reconcile(st:State, observed:Set[int], label:int):State =
    if (st.closed) st else {
      val live=st.live.intersect(observed)
      val selected=nextLive(live,st.selected)
      val changed=selected!=st.selected
      val target=if (changed and selected>0) selected else 0
      {...st,live:live,selected:selected,closed:selected==0,label:label,previous:st.selected,target:target,focuses:st.focuses+(if (target>0) 1 else 0),changes:st.changes+(if (changed) 1 else 0)}
    }
  action retireSelected=all {not(s.closed),s.selected.in(s.live),s'=reconcile(s,s.live.exclude(Set(s.selected)),s.label)}
  action observeSame=all {not(s.closed),s'=reconcile(s,s.live,s.label)}
  action relabel=all {not(s.closed),s'=reconcile(s,s.live,1)}
  action observe(live:Set[int]):bool=all {not(s.closed),s'=reconcile(s,live,s.label)}
  action step=any {retireSelected,observeSame,relabel,observe(Set(1,3,4)),observe(Set(4)),observe(Set())}
  val retirementFocusWitness=s.selected==1 and s.focuses==1 and s.target==1
  val quietLabelWitness=s.label==1 and s.selected==2 and s.focuses==0
  val emptyDismissalWitness=s.closed and s.selected==0 and s.target==0
  val safety=(s.selected==0 or s.selected.in(s.live)) and (s.target==0 or (s.target==s.selected and s.target!=s.previous)) and s.focuses<=s.changes
}
