module transferWorkspace {
  var s: {request: int, pending: bool, unknown: bool, displayed: int, native: int, accepted: bool, sends: int}
  action init = s'={request:0,pending:false,unknown:false,displayed:1,native:1,accepted:false,sends:0}
  action begin = all {s.request==0,s'={...s,request:1,pending:true,sends:1}}
  action nativeAhead = all {s.pending,s'={...s,native:2}}
  action staleReceipt = s'=s
  action commit = all {s.pending,s'={...s,pending:false,native:2,displayed:2,accepted:true}}
  action refuse = all {s.pending,s.native==1,s'={...s,pending:false}}
  action lost = all {s.pending,s'={...s,pending:false,unknown:true}}
  action observe = s'={...s,displayed:if(s.accepted) s.native else 1}
  action duplicate = s'=s
  action step = any {begin,nativeAhead,staleReceipt,commit,refuse,lost,observe,duplicate}
  val safety = s.sends<=1 and (s.displayed==1 or s.accepted)
  run pendingObservationCannotCommitTest = init.then(begin).then(nativeAhead).then(observe).then(all {assert(s.displayed==1),s'=s})
  run matchingCommitChangesMembershipTest = init.then(begin).then(commit).then(all {assert(s.displayed==2 and s.accepted),s'=s})
  run refusalRetainsSourceTest = init.then(begin).then(refuse).then(observe).then(all {assert(s.displayed==1 and s.native==1),s'=s})
  run wrongReceiptCannotCommitTest = init.then(begin).then(staleReceipt).then(observe).then(all {assert(s.pending and s.displayed==1),s'=s})
  run unknownNeverReplaysTest = init.then(begin).then(nativeAhead).then(lost).then(observe).then(duplicate).then(all {assert(s.unknown and s.displayed==1 and s.sends==1),s'=s})
}
