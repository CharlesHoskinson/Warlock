module enrollment_tests {
 import enrollment.* from "enrollment"
 run capacityExtendsSameReceiver=init.then(fire(Retry)).then(assert(s.status=="Capacity" and s.members==3 and not(s.issued) and s.receiver))
 run originalDeadlineAfterDrain=init.then(fire(Retry)).then(fire(Drain)).then(fire(Retry)).then(assert(s.status=="Started" and s.deadline==20 and s.issued and s.members==3))
 run changedDeadlineRefused=init.then(fire(Retry)).then(fire(Renew)).then(assert(s.status=="Conflict" and s.deadline==20 and not(s.issued)))
 run expiredIntentNotRevived=init.then(fire(Retry)).then(fire(Expire)).then(fire(Drain)).then(fire(Retry)).then(assert(s.status=="Expired" and not(s.issued) and s.deadline==20))
 run reusedReceiverCannotIssue=init.then(fire(ReplaceReceiver)).then(fire(Retry)).then(assert(s.status=="ReceiverRejected" and not(s.issued) and s.members==2))
 run replacementKeepsOldJobs=init.then(fire(Retry)).then(fire(ReplaceReceiver)).then(fire(Retry)).then(assert(s.status=="ReceiverRejected" and s.members==3 and s.charge==64 and s.records==2))
 run foreignIntentCannotJoin=init.then(fire(Foreign)).then(assert(s.status=="Invalid" and not(s.issued) and s.members==2))
 run changedPublicationRefused=init.then(fire(ChangeStamp)).then(assert(s.status=="Conflict" and s.deadline==20 and s.members==2))
}
