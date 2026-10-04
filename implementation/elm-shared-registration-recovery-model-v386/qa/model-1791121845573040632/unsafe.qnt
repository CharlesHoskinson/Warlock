module recovery {
 type State={slots:Set[int],next:int,refused:bool,pending:bool,unknown:bool,sent:int,rejected:int,readNeeded:bool}
 var s:State
 action init=s'={slots:Set(),next:1,refused:false,pending:false,unknown:false,sent:0,rejected:0,readNeeded:false}
 action issue=s'=if(s.next<=5 and not(s.refused) and not(s.pending)){
   if(s.slots.size()<2){...s,slots:s.slots.union(Set(s.next)),next:s.next+1,pending:true,sent:s.sent+1}
   else {...s,next:s.next+1,refused:true,pending:false,rejected:s.rejected+1,readNeeded:false}
 }else s
 action finish=s'={...s,pending:false}
 action unknownReceipt=s'={...s,pending:false,unknown:true}
 action exactCertificate=if(s.slots.size()>0){nondet key=s.slots.oneOf();s'={...s,slots:s.slots.exclude(Set(key)),refused:false,readNeeded:s.readNeeded or s.refused}}else s'=s
 action wrongCertificate=s'={...s,refused:false}
 action step=any{issue,finish,unknownReceipt,exactCertificate,wrongCertificate}
 val safety=s.slots.size()<=2 and s.sent+s.rejected==s.next-1 and (not(s.refused) or not(s.pending))
 run capacityRefusalTest=init.then(issue).then(finish).then(issue).then(finish).then(issue).then(all{assert(s.refused and not(s.pending) and s.sent==2 and s.rejected==1),s'=s})
 run exactCapacityRecoveryTest=init.then(issue).then(finish).then(issue).then(finish).then(issue).then(exactCertificate).then(all{assert(not(s.refused) and s.readNeeded and s.sent==2 and not(s.pending)),s'=s})
 run wrongCertificateTest=init.then(issue).then(finish).then(issue).then(finish).then(issue).then(wrongCertificate).then(all{assert(s.refused and s.slots.size()==2 and s.sent==2),s'=s})
 run unknownSurvivesCapacityRecoveryTest=init.then(issue).then(unknownReceipt).then(issue).then(finish).then(issue).then(exactCertificate).then(all{assert(s.unknown and s.sent==2 and not(s.pending)),s'=s})
 run admittedCertificateNeverReplaysTest=init.then(issue).then(exactCertificate).then(all{assert(s.pending and s.sent==1 and not(s.readNeeded)),s'=s})
 run uncertainCertificateNeverSettlesTest=init.then(issue).then(unknownReceipt).then(exactCertificate).then(all{assert(s.unknown and s.sent==1),s'=s})
 run refusedNotificationsStayBoundedTest=init.then(issue).then(finish).then(issue).then(finish).then(issue).then(issue).then(issue).then(all{assert(s.next==4 and s.sent==2 and s.rejected==1),s'=s})
 run freshUserIntentAfterRecoveryTest=init.then(issue).then(finish).then(issue).then(finish).then(issue).then(exactCertificate).then(issue).then(all{assert(s.sent==3 and s.next==5 and s.pending),s'=s})
}
