module historical_closure {
 type State={lease:int,current:bool,actors:bool,source:bool,budget:bool,started:bool,proof:bool,proofLease:int,provedLive:bool,joined:bool,historical:bool,authority:bool,exit:bool,normal:bool,out:bool,err:bool,gone:bool,receipt:bool,accepted:bool,fault:bool,notifications:int,normalLife:bool,nativeWrites:int,retries:int}
 type Event=Start|WorkerProof(int)|Join|Result(int)|Cancel|CurrentLost|ActorsLost|SourceLost|Expire|Exit(bool)|Out|Err|Gone|Receipt(bool)|Verify|Rearm|Notify(int)|Poll|OldCallback(int)
 var s:State
 action init=s'={lease:1,current:true,actors:true,source:true,budget:true,started:false,proof:false,proofLease:0,provedLive:false,joined:false,historical:false,authority:false,exit:false,normal:false,out:false,err:false,gone:false,receipt:false,accepted:false,fault:false,notifications:0,normalLife:false,nativeWrites:0,retries:0}
 pure def actor(a:State):bool=all{a.actors,a.source,not(a.fault)}
 pure def normalClosure(a:State):bool=all{actor(a),a.started,a.historical,a.proofLease==a.lease,a.provedLive,a.joined,a.exit,a.normal,a.out,a.err,a.gone,a.receipt}
 pure def bad(a:State):State={...a,fault:true,authority:false,accepted:false,normalLife:false}
 action fire(e:Event):bool={s'=match e {
 |Start=>if(s.started)bad(s)else {...s,started:true}
 |WorkerProof(n)=>if(n!=s.lease)s else if(all{s.started,s.budget,not(s.proof)}){...s,proof:true,proofLease:n,provedLive:true}else bad(s)
 |Join=>if(s.started){...s,joined:true}else bad(s)
 |Result(n)=>if(n!=s.lease)s else if(all{actor(s),s.budget,s.proof,s.provedLive,s.proofLease==s.lease,s.joined,not(s.historical)}){...s,historical:true,authority:s.current}else bad(s)
 |Cancel=>{...s,current:false,authority:false,accepted:false}
 |CurrentLost=>{...s,current:false,authority:false,accepted:false}
 |ActorsLost=>bad({...s,actors:false})
 |SourceLost=>bad({...s,source:false})
 |Expire=>bad({...s,budget:false})
 |Exit(n)=>if(s.exit)bad(s)else if(n){...s,exit:true,normal:true}else bad({...s,exit:true,normal:false})
 |Out=>if(s.out)bad(s)else {...s,out:true}
 |Err=>if(s.err)bad(s)else {...s,err:true}
 |Gone=>if(s.exit){...s,gone:true}else bad(s)
 |Receipt(n)=>if(all{actor(s),s.historical,s.joined,s.exit,s.normal,s.out,s.err,s.gone,n}){...s,receipt:true}else bad(s)
 |Verify=>{...s,normalLife:normalClosure(s),accepted:all{normalClosure(s),s.current,s.authority}}
 |Rearm=>if(normalClosure(s)){lease:s.lease+1,current:true,actors:true,source:true,budget:true,started:false,proof:false,proofLease:0,provedLive:false,joined:false,historical:false,authority:false,exit:false,normal:false,out:false,err:false,gone:false,receipt:false,accepted:false,fault:false,notifications:0,normalLife:false,nativeWrites:s.nativeWrites,retries:s.retries}else bad(s)
 |Notify(n)=>if(n!=s.lease)s else if(s.notifications!=0 or not(s.proof))bad(s)else {...s,notifications:1}
 |Poll=>s
 |OldCallback(n)=>if(n!=s.lease)s else bad(s)
 }}
 val allProps=all{not(s.accepted)or all{normalClosure(s),s.current,s.authority},not(s.authority)or all{actor(s),s.current,s.historical,s.provedLive,s.proofLease==s.lease,s.joined},not(s.normalLife)or normalClosure(s),s.nativeWrites==0,s.retries==0,s.notifications<=1}
 action step=nondet e=Set(Start,WorkerProof(s.lease),WorkerProof(0),Join,Result(s.lease),Result(0),Cancel,CurrentLost,ActorsLost,SourceLost,Expire,Exit(true),Exit(false),Out,Err,Gone,Receipt(true),Receipt(false),Verify,Rearm,Notify(s.lease),Notify(0),Poll,OldCallback(0),OldCallback(s.lease)).oneOf();fire(e)
 action check(v:bool):bool=all{assert(v),s'=s}
 action witness=fire(Start).then(fire(WorkerProof(s.lease))).then(fire(Join))
 action deliver=fire(Result(s.lease))
 action close=fire(Exit(true)).then(fire(Out)).then(fire(Err)).then(fire(Gone)).then(fire(Receipt(true))).then(fire(Verify))
 action accepted=witness.then(deliver).then(close)
 run currentPositiveAuthorityTest=init.then(accepted).then(check(s.accepted and s.normalLife and s.authority))
 run originalPendingCancelGapCorrectedTest=init.then(witness).then(fire(Cancel)).then(deliver).then(close).then(check(s.historical and s.normalLife and not(s.authority)and not(s.accepted)))
 run cancelBeforeWorkerProofRetainsActorClosureTest=init.then(fire(Start)).then(fire(Cancel)).then(fire(WorkerProof(1))).then(fire(Join)).then(deliver).then(close).then(check(s.normalLife and not(s.accepted)))
 run currentConsumerLostStillCannotAuthorizeTest=init.then(witness).then(fire(CurrentLost)).then(deliver).then(close).then(check(s.normalLife and not(s.authority)))
 run cancelAfterCurrentAcceptanceRetainsNormalLifeTest=init.then(accepted).then(fire(Cancel)).then(fire(Verify)).then(check(s.normalLife and not(s.accepted)))
 run actorContextRetiredBeforeResultRefusesTest=init.then(witness).then(fire(ActorsLost)).then(deliver).then(check(not(s.historical)and not(s.authority)))
 run sourceRetiredBeforeResultRefusesTest=init.then(witness).then(fire(SourceLost)).then(deliver).then(check(not(s.historical)))
 run sourceRetiredAfterProofRevokesClosureTest=init.then(accepted).then(fire(SourceLost)).then(fire(Verify)).then(check(not(s.normalLife)and not(s.accepted)))
 run expiredHistoricalResultRefusesTest=init.then(witness).then(fire(Expire)).then(deliver).then(check(not(s.historical)))
 run wrongLeaseProofNeverHistoricalTest=init.then(fire(Start)).then(fire(WorkerProof(0))).then(fire(Join)).then(deliver).then(check(not(s.historical)))
 run unjoinedProofNeverActorClosureTest=init.then(fire(Start)).then(fire(WorkerProof(1))).then(deliver).then(check(not(s.historical)))
 run missingStdoutRefusesClosureTest=init.then(witness).then(deliver).then(fire(Exit(true))).then(fire(Err)).then(fire(Gone)).then(fire(Receipt(true))).then(check(not(s.normalLife)and s.fault))
 run missingStderrRefusesClosureTest=init.then(witness).then(deliver).then(fire(Exit(true))).then(fire(Out)).then(fire(Gone)).then(fire(Receipt(true))).then(check(not(s.normalLife)and s.fault))
 run missingGoneRefusesReceiptTest=init.then(witness).then(deliver).then(fire(Exit(true))).then(fire(Out)).then(fire(Err)).then(fire(Receipt(true))).then(check(not(s.normalLife)))
 run crashRefusesNormalActorClosureTest=init.then(witness).then(deliver).then(fire(Exit(false))).then(check(s.fault and not(s.normalLife)))
 run uncertainReceiptRefusesNormalLifeTest=init.then(witness).then(deliver).then(fire(Exit(true))).then(fire(Out)).then(fire(Err)).then(fire(Gone)).then(fire(Receipt(false))).then(check(s.fault and not(s.normalLife)))
 run rearmPendingRefusesTest=init.then(witness).then(fire(Cancel)).then(fire(Rearm)).then(check(s.lease==1 and s.fault))
 run canceledActorOnlyRearmsAfterEveryConditionTest=init.then(witness).then(fire(Cancel)).then(deliver).then(close).then(fire(Rearm)).then(check(s.lease==2 and not(s.started)and not(s.fault)))
 run duplicateCurrentResultFaultsTest=init.then(witness).then(deliver).then(deliver).then(check(s.fault and not(s.authority)))
 run firstNativeNotificationAfterPollIsHarmlessTest=init.then(witness).then(deliver).then(close).then(fire(Poll)).then(fire(Notify(1))).then(check(s.accepted and s.normalLife and s.notifications==1))
 run duplicateCurrentNativeNotificationFaultsTest=init.then(witness).then(deliver).then(close).then(fire(Notify(1))).then(fire(Notify(1))).then(check(s.fault and not(s.accepted)))
 action oldSignalPreserves={val before=s;fire(Notify(1)).then(check(s==before))}
 run actualOldNotificationAfterRearmInertTest=init.then(accepted).then(fire(Rearm)).then(oldSignalPreserves)
 run prematureNativeNotificationRefusesTest=init.then(fire(Start)).then(fire(Notify(1))).then(check(s.fault))
 run actorReplacementCannotRearmUnclosedTest=init.then(accepted).then(fire(ActorsLost)).then(fire(Rearm)).then(check(s.lease==1 and s.fault))
}
