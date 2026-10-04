module recovery {
 type State={phase:str,epoch:int,journal:str,status:str,submissions:int,lastSubmitEpoch:int,replays:int}
 var s:State
 action init=s'={phase:"Ready",epoch:1,journal:"Empty",status:"Idle",submissions:0,lastSubmitEpoch:0,replays:0}
 action begin=s'=if(s.phase=="Ready" and s.status!="Pending"){...s,journal:"Pending",status:"Pending",submissions:s.submissions+1,lastSubmitEpoch:s.epoch} else s
 action settle=s'=if(s.phase=="Ready" and s.status=="Pending"){...s,journal:"Committed",status:"Committed"} else s
 action fail=s'={...s,phase:"Stopped"}
 action restart=s'=if(s.phase=="Stopped"){...s,phase:"Reconciling",epoch:s.epoch+1,status:if(s.journal=="Pending")"Unknown" else "Idle"} else s
 action snapshot=s'=if(s.phase=="Reconciling"){...s,phase:"Ready"} else s
 action oldReceipt(epoch:int):bool=s'=if(epoch==s.epoch and s.phase=="Ready" and s.status=="Pending"){...s,status:"Committed",journal:"Committed"} else s
 action step=any{begin,settle,fail,restart,snapshot,oldReceipt(s.epoch-1)}
 val safety=s.replays==0 and (s.status=="Pending" implies s.journal=="Pending") and (s.status=="Unknown" implies s.journal=="Pending") and s.lastSubmitEpoch<=s.epoch
 run unknownSurvivesRestartTest=init.then(begin).then(fail).then(restart).then(snapshot).then(all{assert(s.status=="Unknown" and s.submissions==1 and safety),s'=s})
 run committedDoesNotBecomeUnknownTest=init.then(begin).then(settle).then(fail).then(restart).then(all{assert(s.status=="Idle" and s.journal=="Committed"),s'=s})
 run noSubmissionBeforeSnapshotTest=init.then(begin).then(fail).then(restart).then(begin).then(all{assert(s.phase=="Reconciling" and s.submissions==1),s'=s})
 run oldReceiptCannotResolveUnknownTest=init.then(begin).then(fail).then(restart).then(snapshot).then(oldReceipt(1)).then(all{assert(s.status=="Unknown" and s.submissions==1),s'=s})
 run explicitFreshActionTest=init.then(begin).then(fail).then(restart).then(snapshot).then(begin).then(all{assert(s.status=="Pending" and s.submissions==2 and s.lastSubmitEpoch==2 and safety),s'=s})
 run duplicateSubmissionBlockedTest=init.then(begin).then(begin).then(all{assert(s.submissions==1 and safety),s'=s})
}
