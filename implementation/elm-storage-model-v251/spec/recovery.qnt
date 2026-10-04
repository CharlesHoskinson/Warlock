module recovery {
 type State={phase:str,status:str,reason:str,retries:int,binding:int,effects:int,users:int}
 var s:State
 action init=s'={phase:"Ready",status:"Empty",reason:"",retries:0,binding:1,effects:0,users:0}
 action userEffect=s'=if(s.phase=="Ready" and s.status!="Pending"){...s,status:"Pending",effects:s.effects+1,users:s.users+1} else s
 action failure(reason:str):bool=s'=if(Set("unavailable","full","busy","unverified","legacy-owner").contains(reason)){...s,phase:"Detached",status:if(s.status=="Pending")"Unknown" else s.status,reason:reason} else s
 action disconnect=s'={...s,phase:"Detached",status:if(s.status=="Pending")"Unknown" else s.status}
 action correct=s'=s
 action retry=s'=if(s.phase=="Detached"){...s,phase:"Retrying",retries:s.retries+1} else s
 action attached=s'=if(s.phase=="Retrying"){...s,phase:"Awaiting",binding:s.binding+1,reason:""} else s
 action snapshot=s'=if(s.phase=="Awaiting"){...s,phase:"Ready"} else s
 action receipt(binding:int):bool=s'=if(s.phase=="Ready" and s.status=="Pending" and binding==s.binding){...s,status:"Committed"} else s
 action step=any{userEffect,failure("unavailable"),failure("legacy-owner"),failure("unverified"),failure("invented"),disconnect,correct,retry,attached,snapshot,receipt(s.binding),receipt(s.binding-1)}
 val safety=s.effects==s.users and s.binding>=1 and s.retries>=0 and (s.reason!="" implies Set("Detached","Retrying").contains(s.phase))
 run storageDisablesEffectsTest=init.then(failure("full")).then(userEffect).then(all{assert(s.effects==0 and s.phase=="Detached" and safety),s'=s})
 run pendingBecomesUnknownTest=init.then(userEffect).then(failure("unavailable")).then(all{assert(s.status=="Unknown" and s.effects==1 and safety),s'=s})
 run disconnectKeepsExplanationTest=init.then(failure("busy")).then(disconnect).then(all{assert(s.reason=="busy" and s.phase=="Detached"),s'=s})
 run correctionDoesNotRetryTest=init.then(failure("legacy-owner")).then(correct).then(all{assert(s.phase=="Detached" and s.retries==0 and s.effects==0),s'=s})
 run explicitRetryOnlyOnceTest=init.then(failure("unverified")).then(retry).then(retry).then(all{assert(s.retries==1 and s.phase=="Retrying" and safety),s'=s})
 run newSnapshotDoesNotReplayTest=init.then(userEffect).then(failure("full")).then(correct).then(retry).then(attached).then(snapshot).then(all{assert(s.phase=="Ready" and s.status=="Unknown" and s.effects==1 and s.reason==""),s'=s})
 run malformedReasonIgnoredTest=init.then(failure("invented")).then(all{assert(s.phase=="Ready" and s.reason=="" and safety),s'=s})
 run staleReceiptCannotClearUnknownTest=init.then(userEffect).then(failure("unavailable")).then(retry).then(attached).then(snapshot).then(receipt(1)).then(all{assert(s.status=="Unknown" and s.binding==2 and s.effects==1 and safety),s'=s})
}
