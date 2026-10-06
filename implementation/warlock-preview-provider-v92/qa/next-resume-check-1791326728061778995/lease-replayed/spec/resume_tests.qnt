module resume_tests {
 import resume.* from "./resume"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run capacityKeepsOriginalFloor=init.then(fire(Retry)).then(check(s.status=="Capacity" and s.floor==1 and s.records==2 and not(s.known)))
 run retryKeepsOriginalCutoff=init.then(fire(Retry)).then(fire(Retry)).then(fire(Drain)).then(fire(Retry)).then(check(s.status=="Started" and s.deadline==2000000004 and s.floor==2))
 run expiryAfterCapacityReturn=init.then(fire(Retry)).then(fire(Expire)).then(fire(Drain)).then(fire(Retry)).then(check(s.status=="Expired" and s.floor==1 and s.records==1))
 run changedPendingStampConflicts=init.then(fire(Retry)).then(fire(ChangeStamp)).then(check(s.status=="Conflict" and s.deadline==2000000004 and s.floor==1))
 run replacedReceiverBeforeQuery=init.then(fire(ReplaceReceiver)).then(fire(Retry)).then(check(s.status=="ReceiverRejected" and s.queries==0 and s.deadline==0))
 run replacementPreservesPending=init.then(fire(Retry)).then(fire(ReplaceReceiver)).then(fire(Retry)).then(check(s.status=="ReceiverRejected" and s.queries==1 and s.deadline==2000000004 and s.records==2))
 run actualIssuedRejectionKnown=init.then(fire(Retry)).then(fire(Drain)).then(fire(RejectNative)).then(fire(Retry)).then(check(s.status=="NativeRejected" and s.known and s.floor==2 and s.charge==32 and s.records==2))
 run oldCapacityWithoutReceiver=init.then(fire(Retry)).then(fire(ReplaceReceiver)).then(fire(Drain)).then(fire(Retry)).then(check(s.status=="ReceiverRejected" and s.floor==1 and s.records==1 and s.queries==1))
}
