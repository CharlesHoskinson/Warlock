module next_resume_tests {
 import next_resume.* from "./next_resume"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run capacityKeepsOldRequest=init.then(fire(Retry)).then(check(s.floor==1 and s.status=="Capacity" and not(s.known)))
 run pendingCannotSucceed=init.then(fire(Retry)).then(fire(Next)).then(check(s.status=="Conflict" and s.deadline==2000000004 and s.previous==0))
 run sameExpiredIntentCannotRenew=init.then(fire(Retry)).then(fire(Expire)).then(fire(Retry)).then(check(s.status=="Expired" and s.floor==1 and s.deadline==2000000004))
 run explicitSuccessorKeepsFloor=init.then(fire(Retry)).then(fire(Expire)).then(fire(Next)).then(check(s.status=="Capacity" and s.floor==1 and s.previous==2000000004 and s.deadline==4000000005))
 run successorRetryKeepsCutoff=init.then(fire(Retry)).then(fire(Expire)).then(fire(Next)).then(fire(Retry)).then(check(s.deadline==4000000005 and s.floor==1))
 run capacityReturnsNextOriginalJob=init.then(fire(Retry)).then(fire(Expire)).then(fire(Next)).then(fire(Drain)).then(fire(Retry)).then(check(s.status=="Started" and s.floor==2 and s.deadline==4000000005 and s.known))
 run partialPublicationRefused=init.then(fire(Retry)).then(fire(Expire)).then(fire(PartialPublication)).then(check(s.status=="Conflict" and s.publication==2 and s.previous==0))
 run partialLeaseRefused=init.then(fire(Retry)).then(fire(Expire)).then(fire(PartialLease)).then(check(s.status=="Conflict" and s.lease==2 and s.previous==0))
 run oldStampCannotReplaceSuccessor=init.then(fire(Retry)).then(fire(Expire)).then(fire(Next)).then(fire(OldStamp)).then(check(s.status=="Conflict" and s.publication==3 and s.deadline==4000000005))
 run repeatedSuccessorsStayBounded=init.then(fire(Retry)).then(fire(Expire)).then(fire(Next)).then(fire(Expire)).then(fire(Next)).then(check(s.previous==4000000005 and s.deadline==6000000006 and s.publication==4 and s.floor==1))
 run receiverReplacementPreventsQuery=init.then(fire(Retry)).then(fire(Expire)).then(fire(ReplaceReceiver)).then(fire(Next)).then(check(s.status=="ReceiverRejected" and s.queries==1 and s.previous==0))
 run genuineRejectedSuccessorStaysKnown=init.then(fire(Retry)).then(fire(Expire)).then(fire(Drain)).then(fire(RejectNative)).then(fire(Next)).then(check(s.status=="NativeRejected" and s.known and s.floor==2 and s.charge==32))
 run missingPredecessorRejected=init.then(fire(Retry)).then(fire(Expire)).then(fire(MissingPredecessor)).then(check(s.status=="Invalid" and s.floor==1 and s.previous==0))
}
