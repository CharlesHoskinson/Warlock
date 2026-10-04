module pipeline {
 var s: {pub:int,dom:int,view:int,epoch:int,lease:int,proofPub:int,proofView:int,proofEpoch:int,proofLease:int,age:int,pressed:bool,released:bool,available:bool,pending:bool,forwards:int,book:int}
 action init = s' = {pub:10,dom:10,view:1,epoch:1,lease:2,proofPub:0,proofView:0,proofEpoch:0,proofLease:0,age:0,pressed:false,released:false,available:false,pending:false,forwards:0,book:0}
 action press = s' = {...s,pressed:true,released:false,available:false,proofPub:s.pub,proofView:s.view,proofEpoch:s.epoch,proofLease:s.lease,age:0}
 action release = if(s.pressed) s' = {...s,pressed:false,released:true,available:true} else s'=s
 action redundantCommit = s' = {...s,pub:s.pub+1,book:s.book+1}
 action coalescedUpdate = s' = {...s,book:s.book+1}
 action render = s' = {...s,dom:s.pub}
 action replaceView = s' = {...s,view:s.view+1}
 action laterInput = s' = {...s,epoch:s.epoch+1}
 action expire = s' = {...s,age:501}
 val currentProof = s.proofPub==s.pub and s.proofEpoch==s.epoch and s.proofLease==s.lease and s.age<=500
 action callback = if(s.released and s.available and currentProof and s.dom==s.pub) s' = {...s,available:false,pending:true} else s'=s
 action finish = if(s.pending) s' = {...s,pending:false,forwards:s.forwards+(if(currentProof and s.dom==s.pub) 1 else 0)} else s'=s
 action step = any {redundantCommit,coalescedUpdate,render,replaceView,laterInput,expire,callback,finish}
 val safety = s.forwards<=1 and (not(s.pending) or not(s.available))
 run matchingOnceTest = init.then(press).then(release).then(callback).then(finish).then(all {assert(s.forwards==1),s'=s})
 run redundantCommitDropsOldCallbackTest = init.then(press).then(release).then(redundantCommit).then(callback).then(finish).then(all {assert(s.forwards==0 and s.pub==11),s'=s})
 run coalescedUpdateKeepsProofTest = init.then(press).then(release).then(coalescedUpdate).then(callback).then(finish).then(all {assert(s.forwards==1 and s.pub==10 and s.book==1),s'=s})
 run changedDuringVerificationTest = init.then(press).then(release).then(callback).then(redundantCommit).then(render).then(finish).then(all {assert(s.forwards==0),s'=s})
 run replacementViewRefusesTest = init.then(press).then(release).then(replaceView).then(callback).then(finish).then(all {assert(s.forwards==0),s'=s})
 run laterInputRefusesTest = init.then(press).then(release).then(laterInput).then(callback).then(finish).then(all {assert(s.forwards==0),s'=s})
 run expiryRefusesTest = init.then(press).then(release).then(expire).then(callback).then(finish).then(all {assert(s.forwards==0),s'=s})
 run newDomCannotRebaseProofTest = init.then(press).then(release).then(redundantCommit).then(render).then(callback).then(finish).then(all {assert(s.forwards==0),s'=s})
 run duplicateCallbackInertTest = init.then(press).then(release).then(callback).then(finish).then(callback).then(finish).then(all {assert(s.forwards==1),s'=s})
}
