module enrollment_tests {
 import enrollment.* from "enrollment"
 run capacityExtendsSameReceiver=init.then(fire(Retry)).then(assert(all{s.status=="Capacity",s.members==3,not(s.issued),s.receiver}))
 run originalDeadlineAfterDrain=init.then(fire(Retry)).then(fire(Drain)).then(fire(Retry)).then(assert(all{s.status=="Started",s.deadline==20,s.issued,s.members==3}))
 run changedDeadlineRefused=init.then(fire(Retry)).then(fire(Renew)).then(assert(all{s.status=="Conflict",s.deadline==20,not(s.issued)}))
 run expiredIntentNotRevived=init.then(fire(Retry)).then(fire(Expire)).then(fire(Drain)).then(fire(Retry)).then(assert(all{s.status=="Expired",not(s.issued),s.deadline==20}))
 run reusedReceiverCannotIssue=init.then(fire(ReplaceReceiver)).then(fire(Retry)).then(assert(all{s.status=="ReceiverRejected",not(s.issued),s.members==2}))
 run replacementKeepsOldJobs=init.then(fire(Retry)).then(fire(ReplaceReceiver)).then(fire(Retry)).then(assert(all{s.status=="ReceiverRejected",s.members==3,s.charge==64,s.records==2}))
 run foreignIntentCannotJoin=init.then(fire(Foreign)).then(assert(all{s.status=="Invalid",not(s.issued),s.members==2}))
 run changedPublicationRefused=init.then(fire(ChangeStamp)).then(assert(all{s.status=="Conflict",s.deadline==20,s.members==2}))
}
