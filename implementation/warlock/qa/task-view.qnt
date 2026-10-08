module taskView {
  // Bounded stale choice/refresh abstraction. It supplies no native or AT verdict.
  var s: {shown: int, open: bool, live: Set[int], pending: int, chosenAt: int, mutations: List[int]}
  action init = s'={shown:1,open:true,live:Set(1,2),pending:0,chosenAt:0,mutations:List()}
  action choose = all { s.open, s.pending==0, s.live.contains(1), s'={...s,open:false,pending:1,chosenAt:s.shown} }
  action staleClick = s'=s
  action retire = s'={...s,shown:s.shown+1,live:s.live.exclude(Set(1))}
  action refresh = all {s.pending==1,s'={...s,pending:0,mutations:if(s.live.contains(1) and s.chosenAt==s.shown) s.mutations.append(1) else s.mutations}}
  action dismiss = s'={...s,open:false}
  action step = any {choose,staleClick,retire,refresh,dismiss}
  val safety = s.mutations==List() or s.mutations==List(1)
  run currentChoiceRefreshesOnceTest = init.then(choose).then(refresh).then(staleClick).then(all {assert(s.mutations==List(1)),s'=s})
  run staleChoiceDoesNotDispatchTest = init.then(staleClick).then(all {assert(s.pending==0 and s.mutations==List()),s'=s})
  run retiredIdentityNeverSubstitutesTest = init.then(choose).then(retire).then(refresh).then(all {assert(s.mutations==List()),s'=s})
  run dismissalDoesNotMutateTest = init.then(dismiss).then(staleClick).then(all {assert(s.mutations==List()),s'=s})
}
