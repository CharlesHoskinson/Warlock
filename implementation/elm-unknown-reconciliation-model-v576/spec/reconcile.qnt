module reconcile {
 var s:{oldLive:bool,newBinding:bool,proof:bool,read:bool,scope:bool,durable:bool,reserved:bool,unknownHistory:bool,explicit:bool,submits:int}
 action init = s'={oldLive:true,newBinding:false,proof:false,read:false,scope:true,durable:false,reserved:true,unknownHistory:true,explicit:false,submits:0}
 action attach = s'={...s,newBinding:true}
 action retire = if(s.newBinding) s'={...s,oldLive:false,proof:true,read:false} else s'=s
 action observe = if(s.proof and not(s.oldLive)) s'={...s,read:true} else s'=s
 action persist = if(s.proof and s.read) s'={...s,durable:true} else s'=s
 action foreignScope = s'={...s,scope:false}
 action wrongGrantLive = s'={...s,oldLive:true}
 action disconnect = s'={...s,newBinding:false,explicit:false}
 val eligible = s.newBinding and s.proof and s.read and s.scope and s.durable and not(s.oldLive)
 action release = if(eligible) s'={...s,reserved:false} else s'=s
 action intent = if(eligible and not(s.reserved)) s'={...s,explicit:true} else s'=s
 action submit = if(eligible and not(s.reserved) and s.explicit and s.submits==0) s'={...s,submits:s.submits+1,explicit:false} else s'=s
 action step = any {attach,retire,observe,persist,foreignScope,wrongGrantLive,disconnect,release,intent,submit}
 val safety = s.submits<=1 and s.unknownHistory
 run liveBrokerAttachDoesNotReleaseTest = init.then(attach).then(observe).then(persist).then(release).then(intent).then(submit).then(all {assert(s.reserved and s.submits==0),s'=s})
 run snapshotBeforeProofDoesNotSealTest = init.then(attach).then(observe).then(retire).then(persist).then(release).then(all {assert(s.reserved),s'=s})
 run proofNeedsPostBarrierReadTest = init.then(attach).then(retire).then(all {s'={...s,durable:true}}).then(release).then(all {assert(s.reserved),s'=s})
 run readNeedsProofTest = init.then(attach).then(all {s'={...s,oldLive:false,read:true,durable:true}}).then(release).then(all {assert(s.reserved),s'=s})
 run persistenceRequiredTest = init.then(attach).then(retire).then(observe).then(release).then(all {assert(s.reserved),s'=s})
 run foreignScopeRefusedTest = init.then(attach).then(retire).then(observe).then(persist).then(foreignScope).then(release).then(all {assert(s.reserved),s'=s})
 run activeOldGrantRefusedTest = init.then(attach).then(retire).then(observe).then(persist).then(wrongGrantLive).then(release).then(all {assert(s.reserved),s'=s})
 run noAutomaticReplayTest = init.then(attach).then(retire).then(observe).then(persist).then(release).then(submit).then(all {assert(not(s.reserved) and s.submits==0 and s.unknownHistory),s'=s})
 run explicitNewIntentTest = init.then(attach).then(retire).then(observe).then(persist).then(release).then(intent).then(submit).then(submit).then(all {assert(s.submits==1 and s.unknownHistory),s'=s})
 run oldPreReconcileIntentNotQueuedTest = init.then(attach).then(intent).then(retire).then(observe).then(persist).then(release).then(submit).then(all {assert(s.submits==0),s'=s})
 run disconnectedProofCannotReleaseTest = init.then(attach).then(retire).then(observe).then(persist).then(disconnect).then(release).then(intent).then(submit).then(all {assert(s.reserved and s.submits==0),s'=s})
}
