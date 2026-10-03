module terminal_linearization {
 type State={selected:bool,lease:int,preparedLease:int,prepared:bool,normal:bool,fault:bool,pending:Set[int],overflow:bool,closed:int,pastLease:int,refused:bool,nonce:int,token:int,attemptNonce:int,attemptToken:int,attempted:bool,status:int,published:bool,failures:int,successes:int,launches:int,writes:int}
 type Event=Begin|Queue(int)|Overflow|Boundary|Commit|Replace|UiPrepare|UiRefuse|ChangeMenu|Dismiss
 var s:State
 action init=s'={selected:true,lease:1,preparedLease:0,prepared:false,normal:true,fault:false,pending:Set(),overflow:false,closed:0,pastLease:0,refused:false,nonce:1,token:10,attemptNonce:0,attemptToken:0,attempted:false,status:0,published:false,failures:0,successes:0,launches:0,writes:0}
 pure def invalidate(a:State):State={...a,fault:true,normal:false,refused:true}
 pure def drain(a:State):State={val bad=a.selected and (a.overflow or a.pending.contains(a.lease));val clean={...a,pending:Set(),overflow:false};if(bad)invalidate(clean)else clean}
 action fire(e:Event):bool={s'=match e {
 |Queue(n)=>if(n<0 or n>4)s else if(s.pending.size()>=4){...s,overflow:true}else {...s,pending:s.pending.union(Set(n))}
 |Overflow=>{...s,overflow:true}
 |Begin=>{val a=drain(s);if(a.selected and a.normal and not(a.fault)){...a,prepared:true,preparedLease:a.lease,refused:false}else {...a,prepared:false,refused:true}}
 |Boundary=>drain(s)
 |Commit=>if(not(s.prepared)or not(s.selected)or s.preparedLease!=s.lease){...s,refused:true}else if(s.pending.contains(s.lease)or s.overflow)invalidate(s)else if(s.fault or not(s.normal)){...s,refused:true}else {...s,selected:false,prepared:false,normal:true,closed:s.closed+1,pastLease:s.lease,refused:false}
 |Replace=>{val a=drain(s);if(a.selected and a.normal and not(a.fault)and a.lease<4){...a,lease:a.lease+1,closed:a.closed+1,pastLease:a.lease}else {...a,refused:true}}
 |UiPrepare=>if(s.status==0 and not(s.published)){...s,attempted:true,attemptNonce:s.nonce,attemptToken:s.token}else s
 |UiRefuse=>if(s.refused and s.attempted and s.attemptNonce==s.nonce and s.attemptToken==s.token and s.status==0 and not(s.published)){...s,status:2,published:true,failures:s.failures+1}else s
 |ChangeMenu=>if(s.nonce<4){...s,nonce:s.nonce+1,token:s.token+1,status:0,published:false}else s
 |Dismiss=>{...s,status:1}
 }}
 val allProps=all{s.closed>=0,s.closed<=4,s.pastLease<=s.lease,not(s.fault)or not(s.normal),s.successes==0,s.launches==0,s.writes==0,s.failures<=s.nonce,not(s.published)or s.status!=0}
 action step=nondet e=Set(Begin,Queue(0),Queue(1),Queue(s.lease),Queue(4),Overflow,Boundary,Commit,Replace,UiPrepare,UiRefuse,ChangeMenu,Dismiss).oneOf();fire(e)
 action check(v:bool):bool=all{assert(v),s'=s}
 run normalLinearizationPreservesExactPastTest=init.then(fire(Begin)).then(fire(Commit)).then(check(not(s.selected)and s.closed==1 and s.pastLease==1 and s.normal))
 run matchedFaultAtDisconnectBoundaryRefusesTest=init.then(fire(Begin)).then(fire(Queue(1))).then(fire(Boundary)).then(fire(Commit)).then(check(s.selected and s.fault and not(s.normal)and s.closed==0))
 run matchedFaultAfterFinalDrainRefusesTest=init.then(fire(Begin)).then(fire(Boundary)).then(fire(Queue(1))).then(fire(Commit)).then(check(s.selected and s.fault and s.closed==0))
 run overflowAfterFinalDrainRefusesTest=init.then(fire(Begin)).then(fire(Boundary)).then(fire(Overflow)).then(fire(Commit)).then(check(s.selected and s.fault and s.closed==0 and s.overflow))
 run preexistingMatchedQueueDrainedAtEntryTest=init.then(fire(Queue(1))).then(fire(Begin)).then(check(s.selected and not(s.prepared)and s.fault and s.closed==0))
 run oldPendingQueueDoesNotFaultSelectedRetirementTest=init.then(fire(Begin)).then(fire(Queue(0))).then(fire(Commit)).then(check(not(s.selected)and s.closed==1 and not(s.fault)))
 run oldCallbackAdmittedAfterCommitCannotAlterPastTest=init.then(fire(Begin)).then(fire(Commit)).then(fire(Queue(1))).then(fire(Boundary)).then(check(not(s.selected)and s.closed==1 and s.normal and not(s.fault)))
 run replacedRecordNeverErasedByOldRetireTest=init.then(fire(Begin)).then(fire(Replace)).then(fire(Commit)).then(check(s.selected and s.lease==2 and not(s.fault)and s.closed==1 and s.refused))
 run replacedRecordNeverFaultedByOldQueuedCallbackTest=init.then(fire(Begin)).then(fire(Replace)).then(fire(Queue(1))).then(fire(Boundary)).then(fire(Commit)).then(check(s.selected and s.lease==2 and s.normal and not(s.fault)and s.closed==1))
 run implicitSameCommandReuseStillDrainsCurrentFaultTest=init.then(fire(Queue(1))).then(fire(Replace)).then(check(s.lease==1 and s.selected and s.fault and s.closed==0))
 run visibleCurrentRetirementRefusalPublishesFailureOnlyTest=init.then(fire(UiPrepare)).then(fire(Begin)).then(fire(Queue(1))).then(fire(Commit)).then(fire(UiRefuse)).then(check(s.status==2 and s.failures==1 and s.successes==0 and s.launches==0))
 run repeatedRefusalCannotPublishOrLaunchTwiceTest=init.then(fire(UiPrepare)).then(fire(Begin)).then(fire(Overflow)).then(fire(Commit)).then(fire(UiRefuse)).then(fire(UiPrepare)).then(fire(UiRefuse)).then(check(s.status==2 and s.failures==1 and s.launches==0))
 action oldFailureInert={val before=s;fire(UiRefuse).then(check(s==before))}
 run changedMenuGetsNoOldRefusalPublicationTest=init.then(fire(UiPrepare)).then(fire(Begin)).then(fire(Queue(1))).then(fire(Commit)).then(fire(ChangeMenu)).then(oldFailureInert)
 run dismissedMenuGetsNoOldRefusalPublicationTest=init.then(fire(UiPrepare)).then(fire(Begin)).then(fire(Queue(1))).then(fire(Commit)).then(fire(Dismiss)).then(oldFailureInert)
 run successfulRetirementNeverPublishesPinSuccessTest=init.then(fire(UiPrepare)).then(fire(Begin)).then(fire(Commit)).then(fire(UiRefuse)).then(check(s.failures==0 and s.successes==0 and s.launches==0))
}
