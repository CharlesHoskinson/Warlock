module adapterAnnouncementTests {
  import adapterAnnouncements.* from "./adapter-announcements"
  action assertState(condition:bool):bool=all{assert(condition),s'=s}
  run matchedFailureAnnouncesOnceTest=init.then(request(1)).then(receipt(1,1,true)).then(assertState(s.counts.get(1)==1 and s.focus==7))
  run repeatedFailureCannotReannounceTest=init.then(request(1)).then(receipt(1,1,true)).then(duplicateReceipt).then(assertState(s.counts.get(1)==1 and not(canRead(s,1,1))))
  run successfulReadIsSilentTest=init.then(request(2)).then(receipt(2,1,false)).then(assertState(s.counts.get(1)==0 and s.failures.size()==0))
  run foreignReceiptCannotSettleTest=init.then(request(1)).then(foreignReceipt).then(assertState(s.waiting.get(1)==1 and s.counts.get(1)==0 and not(canRead(s,1,2))))
  run wrongAdapterCannotSettleTest=init.then(request(1)).then(assertState(not(canRead(s,2,1)) and s.waiting.get(1)==1))
  run explicitRetryHasFreshIdentityTest=init.then(request(1)).then(receipt(1,1,true)).then(request(1)).then(receipt(1,2,true)).then(assertState(s.counts.get(1)==1 and s.counts.get(2)==1))
  run failedAndSuccessfulProvidersStayIndependentTest=init.then(request(1)).then(request(2)).then(receipt(2,2,false)).then(receipt(1,1,true)).then(assertState(s.counts.get(1)==1 and s.counts.get(2)==0 and s.focus==7))
  run recoveryReadDoesNotReplayFailureTest=init.then(request(1)).then(receipt(1,1,true)).then(request(1)).then(receipt(1,2,false)).then(assertState(s.counts.get(1)==1 and s.counts.get(2)==0 and s.successful==1))
}
