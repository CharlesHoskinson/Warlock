module stable {
 var s: { publication: int, lease: int, status: int, target: int, enabled: bool, mode: int, book: int, effects: int, proof: int, epoch: int, proofEpoch: int }
 action init = s' = {publication:10,lease:2,status:1,target:1,enabled:true,mode:0,book:0,effects:0,proof:10,epoch:1,proofEpoch:1}
 action commit(status:int,target:int,live:bool,mode:int,lease:int,commands:int): bool = {
  val same = status==s.status and target==s.target and live==s.enabled and mode==s.mode and lease==s.lease
  s' = {...s, status:status,target:target,enabled:live,mode:mode,lease:lease,book:s.book,effects:s.effects+commands,publication:if(same and commands==0) s.publication else s.publication+1}
 }
 action internal = commit(s.status,s.target,s.enabled,s.mode,s.lease,0)
 action statusChange = commit(2,s.target,s.enabled,s.mode,s.lease,0)
 action targetChange = commit(s.status,2,s.enabled,s.mode,s.lease,0)
 action disable = commit(s.status,s.target,false,s.mode,s.lease,0)
 action modeChange = commit(s.status,s.target,s.enabled,1,s.lease,0)
 action leaseChange = commit(s.status,s.target,s.enabled,s.mode,3,0)
 action command = commit(s.status,s.target,s.enabled,s.mode,s.lease,1)
 action focusLoss = s' = {...s,epoch:s.epoch+1}
 val proofCurrent = s.proof==s.publication and s.proofEpoch==s.epoch
 action step = any { internal,statusChange,targetChange,disable,modeChange,leaseChange,command,focusLoss }
 val safety = s.publication>=10 and s.effects<=s.publication-10 and s.book>=s.effects
 run internalPreservesProofTest = init.then(internal).then(all {assert(s.book==1 and s.publication==10 and proofCurrent),s'=s})
 run statusRevokesTest = init.then(statusChange).then(all {assert(s.publication==11 and not(proofCurrent)),s'=s})
 run targetRevokesTest = init.then(targetChange).then(all {assert(s.publication==11 and not(proofCurrent)),s'=s})
 run enabledRevokesTest = init.then(disable).then(all {assert(s.publication==11 and not(proofCurrent)),s'=s})
 run modeRevokesTest = init.then(modeChange).then(all {assert(s.publication==11 and not(proofCurrent)),s'=s})
 run leaseRevokesTest = init.then(leaseChange).then(all {assert(s.publication==11 and not(proofCurrent)),s'=s})
 run commandIsNotCoalescedTest = init.then(command).then(all {assert(s.effects==1 and s.publication==11 and not(proofCurrent)),s'=s})
 run focusStillRevokesTest = init.then(internal).then(focusLoss).then(all {assert(s.publication==10 and not(proofCurrent)),s'=s})
}
