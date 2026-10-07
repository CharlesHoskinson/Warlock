module pins {
  // Bounded preference receipt/CAS abstraction; real filesystem and Elm proofs
  // are separate, and no whole-system refinement claim is made.
  var s: {version: int, captured: int, order: List[int], proposed: List[int], confirmed: List[int], pending: int, request: int, dispatched: Set[int]}
  action init = s'={version:1,captured:0,order:List(1,2),proposed:List(),confirmed:List(1,2),pending:0,request:0,dispatched:Set()}
  action propose = all { s.pending==0, s.request<4, s'={...s,captured:s.version,proposed:List(2,1),pending:s.request+1,request:s.request+1,dispatched:s.dispatched.union(Set(s.request+1))} }
  action save = all { s.pending>0, s'=if(s.captured==s.version) {...s,version:s.version+1,order:s.proposed,confirmed:s.proposed,pending:0} else {...s,confirmed:s.order,pending:0} }
  action externalSave = s'={...s,version:s.version+1,order:List(1)}
  action staleReceipt = s'=s
  action restart = s'={...s,pending:0,confirmed:s.order}
  action step = any {propose,save,externalSave,staleReceipt,restart}
  val safety = s.dispatched.size()==s.request
  run noReplayTest = init.then(propose).then(staleReceipt).then(staleReceipt).then(all {assert(s.dispatched==Set(1)),s'=s})
  run restartReadsWithoutReplayTest = init.then(propose).then(save).then(restart).then(all {assert(s.confirmed==List(2,1) and s.dispatched==Set(1)),s'=s})
  run staleCannotConfirmTest = init.then(propose).then(staleReceipt).then(all {assert(s.pending==1 and s.confirmed==List(1,2)),s'=s})
  run conflictingWriterCannotOverwriteTest = init.then(propose).then(externalSave).then(save).then(all {assert(s.order==List(1) and s.pending==0),s'=s})
}
