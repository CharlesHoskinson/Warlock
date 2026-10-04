module recovery {
 type State={entries:Set[int],unknowns:Set[int],latest:int,request:int,submissions:int,poisoned:bool,corrected:bool}
 var s:State
 action init=s'={entries:Set(),unknowns:Set(),latest:0,request:0,submissions:0,poisoned:false,corrected:false}
 action admit(target:int):bool=s'=if(not(s.poisoned) and s.entries.size()<2 and not(s.entries.contains(target))){...s,entries:s.entries.union(Set(target)),latest:target,request:s.request+1,submissions:s.submissions+1} else s
 action unknown(target:int):bool=s'=if(not(s.poisoned) and s.entries.contains(target)){...s,unknowns:s.unknowns.union(Set(target))} else s
 action commit(target:int):bool=s'=if(not(s.poisoned) and s.entries.contains(target)){...s,entries:s.entries.exclude(Set(target)),unknowns:s.unknowns.exclude(Set(target))} else s
 action cold=s'=s
 action failure=s'={...s,poisoned:true,corrected:false}
 action correct=s'={...s,corrected:true}
 action reopen=s'=if(s.poisoned and s.corrected){...s,poisoned:false} else s
 action step=any{admit(1),admit(2),admit(3),unknown(1),unknown(2),commit(1),commit(2),cold,failure,correct,reopen}
 val safety=s.entries.size()<=2 and s.unknowns.subseteq(s.entries) and s.request==s.submissions and s.request>=0
 run coldPreservesEarlierUnknownTest=init.then(admit(1)).then(unknown(1)).then(admit(2)).then(commit(2)).then(cold).then(all{assert(s.entries==Set(1) and s.unknowns==Set(1) and s.request==2 and s.submissions==2),s'=s})
 run capacityNoEvictionTest=init.then(admit(1)).then(unknown(1)).then(admit(2)).then(admit(3)).then(all{assert(s.entries==Set(1,2) and s.unknowns==Set(1) and s.request==2),s'=s})
 run duplicateNoResubmitTest=init.then(admit(1)).then(unknown(1)).then(admit(1)).then(all{assert(s.entries==Set(1) and s.submissions==1),s'=s})
 run unrelatedCommitOnlyOneTest=init.then(admit(1)).then(admit(2)).then(commit(1)).then(all{assert(s.entries==Set(2) and s.latest==2),s'=s})
 run coldNeverReplaysTest=init.then(admit(1)).then(unknown(1)).then(cold).then(cold).then(all{assert(s.submissions==1 and s.entries==Set(1)),s'=s})
 run wrongReceiptInertTest=init.then(admit(1)).then(commit(2)).then(all{assert(s.entries==Set(1) and s.request==1),s'=s})
 run definitiveSettlementRetainsWatermarkTest=init.then(admit(1)).then(commit(1)).then(cold).then(admit(2)).then(all{assert(s.request==2 and s.entries==Set(2)),s'=s})
 run failurePoisonsWritesTest=init.then(admit(1)).then(failure).then(commit(1)).then(admit(2)).then(all{assert(s.poisoned and s.entries==Set(1) and s.request==1),s'=s})
 run explicitCorrectionOnlyTest=init.then(failure).then(reopen).then(admit(1)).then(correct).then(reopen).then(admit(1)).then(all{assert(not(s.poisoned) and s.entries==Set(1) and s.submissions==1),s'=s})
}
