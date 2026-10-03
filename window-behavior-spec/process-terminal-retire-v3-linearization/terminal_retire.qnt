module terminal_retire {
 type State={active:bool,lease:int,next:int,command:int,boundCommand:int,actors:bool,source:bool,current:bool,idle:bool,started:bool,worker:bool,joined:bool,budget:bool,historical:bool,authority:bool,exited:bool,normal:bool,code:int,out:bool,err:bool,gone:bool,receipt:bool,normalLife:bool,accepted:bool,fault:bool,closed:int,pastLease:int,pastCommand:int,lastRefused:bool,nativeWrites:int,retries:int}
 type Event=Arm|SetCommand(int)|Start(int)|WorkerProof(int)|Join|Result(int)|ExitSuccess|ExitRefusal|ExitCrash|Out|Err|Gone|Receipt(bool)|Verify|Cancel|ActorsLost|SourceLost|WorkerExpired|Retire(int)|OldCallback(int)|ForeignLive
 var s:State
 action init=s'={active:false,lease:0,next:1,command:1,boundCommand:0,actors:true,source:true,current:true,idle:true,started:false,worker:false,joined:false,budget:true,historical:false,authority:false,exited:false,normal:false,code:-1,out:false,err:false,gone:false,receipt:false,normalLife:false,accepted:false,fault:false,closed:0,pastLease:0,pastCommand:0,lastRefused:false,nativeWrites:0,retries:0}
 pure def denied(a:State):State={...a,lastRefused:true}
 pure def bad(a:State):State={...a,fault:true,authority:false,accepted:false,normalLife:false,lastRefused:true}
 pure def actor(a:State):bool=all{a.active,a.actors,a.source,not(a.fault),a.command==a.boundCommand}
 pure def closure(a:State):bool=all{actor(a),a.started,a.worker,a.historical,a.joined,a.exited,a.normal,a.out,a.err,a.gone,a.idle,a.receipt}
 action fire(e:Event):bool={s'=match e {
 |Arm=>if(all{not(s.active),s.actors,s.source,s.idle,s.command>=1,s.command<=3,s.next<=4,s.closed<4}){...s,active:true,lease:s.next,next:s.next+1,boundCommand:s.command,current:true,started:false,worker:false,joined:false,budget:true,historical:false,authority:false,exited:false,normal:false,code:-1,out:false,err:false,gone:false,receipt:false,normalLife:false,accepted:false,fault:false,lastRefused:false}else denied(s)
 |SetCommand(n)=>if(n<1 or n>3)bad(s)else if(s.active and n!=s.boundCommand)bad({...s,command:n})else {...s,command:n,lastRefused:false}
 |Start(n)=>if(n!=s.lease or not(s.active))s else if(not(actor(s))or s.started)bad(s)else {...s,started:true,idle:false}
 |WorkerProof(n)=>if(n!=s.lease or not(s.active))s else if(all{actor(s),s.started,s.budget,not(s.worker)}){...s,worker:true}else bad(s)
 |Join=>if(not(s.active))s else if(all{s.started,s.worker}){...s,joined:true}else bad(s)
 |Result(n)=>if(n!=s.lease or not(s.active))s else if(all{actor(s),s.started,s.worker,s.joined,s.budget,not(s.historical)}){...s,historical:true,authority:s.current}else bad(s)
 |ExitSuccess=>if(all{actor(s),s.started,not(s.exited)}){...s,exited:true,normal:true,code:0}else bad(s)
 |ExitRefusal=>if(all{actor(s),s.started,not(s.exited)}){...s,exited:true,normal:true,code:2}else bad(s)
 |ExitCrash=>bad({...s,exited:true,normal:false,code:9})
 |Out=>if(all{actor(s),s.started,not(s.out)}){...s,out:true}else bad(s)
 |Err=>if(all{actor(s),s.started,not(s.err)}){...s,err:true}else bad(s)
 |Gone=>if(all{actor(s),s.exited}){...s,gone:true,idle:true}else bad(s)
 |Receipt(v)=>if(all{actor(s),s.historical,s.joined,s.exited,s.normal,s.out,s.err,s.gone,v}){...s,receipt:true}else bad(s)
 |Verify=>if(actor(s)){...s,normalLife:closure(s),accepted:all{closure(s),s.current,s.authority,s.code==0}}else if(s.active)bad(s)else s
 |Cancel=>if(s.active){...s,current:false,authority:false,accepted:false}else s
 |ActorsLost=>if(s.active)bad({...s,actors:false})else {...s,actors:false}
 |SourceLost=>if(s.active)bad({...s,source:false})else {...s,source:false}
 |WorkerExpired=>if(s.active and not(s.historical))bad({...s,budget:false})else s
 |Retire(n)=>if(n!=s.lease or not(s.active))denied(s)else if(not(actor(s)))bad(s)else if(closure(s)){...s,active:false,current:false,authority:false,accepted:false,normalLife:true,closed:s.closed+1,pastLease:s.lease,pastCommand:s.boundCommand,lastRefused:false}else denied(s)
 |OldCallback(n)=>if(n!=s.lease or not(s.active))s else bad(s)
 |ForeignLive=>if(s.active)bad({...s,idle:false})else {...s,idle:false}
 }}
 val allProps=all{not(s.authority)or all{actor(s),s.current,s.historical,s.joined},not(s.accepted)or all{closure(s),s.current,s.authority,s.code==0},s.active or all{not(s.authority),not(s.accepted)},s.pastLease<s.next,s.closed>=0,s.closed<=4,s.next<=5,s.nativeWrites==0,s.retries==0,not(s.fault)or all{not(s.authority),not(s.accepted),not(s.normalLife)}}
 action step=nondet e=Set(Arm,SetCommand(1),SetCommand(2),SetCommand(3),Start(s.lease),Start(0),WorkerProof(s.lease),WorkerProof(0),Join,Result(s.lease),Result(0),ExitSuccess,ExitRefusal,ExitCrash,Out,Err,Gone,Receipt(true),Receipt(false),Verify,Cancel,ActorsLost,SourceLost,WorkerExpired,Retire(s.lease),Retire(0),OldCallback(s.lease),OldCallback(0),ForeignLive).oneOf();fire(e)
 action check(v:bool):bool=all{assert(v),s'=s}
 action live=fire(Start(s.lease)).then(fire(WorkerProof(s.lease))).then(fire(Join)).then(fire(Result(s.lease)))
 action finish=fire(ExitSuccess).then(fire(Out)).then(fire(Err)).then(fire(Gone)).then(fire(Receipt(true))).then(fire(Verify))
 action positive=fire(Arm).then(live).then(finish)
 action retired=positive.then(fire(Retire(s.lease)))
 run positiveOriginalCommandTest=init.then(positive).then(check(s.accepted and s.command==1))
 run exactTerminalRetireSealsPastNoCurrentTest=init.then(retired).then(check(not(s.active)and s.closed==1 and s.pastLease==1 and s.pastCommand==1 and s.normalLife and not(s.authority)and not(s.accepted)))
 run changeCommandWithoutRetireRefusesTest=init.then(positive).then(fire(SetCommand(2))).then(fire(Verify)).then(check(s.active and s.fault and not(s.accepted)))
 run wrongLeaseRetirePreservesCurrentAuthorityTest=init.then(positive).then(fire(Retire(0))).then(check(s.active and s.accepted and s.authority and s.lastRefused and s.closed==0))
 run pendingRetireLeavesRegisteredOldActorTest=init.then(fire(Arm)).then(fire(Retire(1))).then(check(s.active and s.lease==1 and not(s.fault)and s.lastRefused and s.closed==0))
 run armWithoutExplicitRetireRefusesTest=init.then(positive).then(fire(Arm)).then(check(s.active and s.lease==1 and s.accepted and s.lastRefused))
 run sameCommandStillNeedsFreshProofTest=init.then(retired).then(fire(Arm)).then(check(s.lease==2 and not(s.started)and not(s.worker)and not(s.historical)and not(s.out)and not(s.err)and not(s.receipt)and not(s.accepted)))
 run changedCommandFreshArmResetsProofTest=init.then(retired).then(fire(SetCommand(2))).then(fire(Arm)).then(check(s.lease==2 and s.boundCommand==2 and not(s.started)and not(s.historical)and not(s.out)and not(s.err)and not(s.receipt)and not(s.accepted)))
 run changedCommandIndependentNewPositiveTest=init.then(retired).then(fire(SetCommand(2))).then(positive).then(check(s.lease==2 and s.accepted and s.boundCommand==2 and s.pastCommand==1))
 action oldPreserves={val before=s;fire(OldCallback(1)).then(check(s==before))}
 run oldCallbackAfterNewArmEntireSnapshotInertTest=init.then(retired).then(fire(SetCommand(2))).then(fire(Arm)).then(oldPreserves)
 run oldCallbackAfterNewAcceptanceEntireSnapshotInertTest=init.then(retired).then(fire(SetCommand(2))).then(positive).then(oldPreserves)
 run oldProofDoesNotSupplyNewReceiptTest=init.then(retired).then(fire(SetCommand(2))).then(fire(Arm)).then(fire(Receipt(true))).then(check(s.fault and not(s.accepted)))
 run missingStdoutRetireRefusesTest=init.then(fire(Arm)).then(live).then(fire(ExitSuccess)).then(fire(Err)).then(fire(Gone)).then(fire(Retire(1))).then(check(s.active and s.closed==0 and s.lastRefused))
 run missingStderrRetireRefusesTest=init.then(fire(Arm)).then(live).then(fire(ExitSuccess)).then(fire(Out)).then(fire(Gone)).then(fire(Retire(1))).then(check(s.active and s.closed==0 and s.lastRefused))
 run missingGoneRetireRefusesTest=init.then(fire(Arm)).then(live).then(fire(ExitSuccess)).then(fire(Out)).then(fire(Err)).then(fire(Retire(1))).then(check(s.active and s.closed==0))
 run missingReceiptRetireRefusesTest=init.then(fire(Arm)).then(live).then(fire(ExitSuccess)).then(fire(Out)).then(fire(Err)).then(fire(Gone)).then(fire(Retire(1))).then(check(s.active and s.closed==0))
 run unjoinedRetireRefusesTest=init.then(fire(Arm)).then(fire(Start(1))).then(fire(WorkerProof(1))).then(fire(ExitSuccess)).then(fire(Out)).then(fire(Err)).then(fire(Gone)).then(fire(Retire(1))).then(check(s.active and s.closed==0))
 run crashCannotSealNormalPastTest=init.then(fire(Arm)).then(live).then(fire(ExitCrash)).then(fire(Retire(1))).then(check(s.active and s.fault and s.closed==0))
 run malformedReceiptCannotRetireTest=init.then(positive).then(fire(Receipt(false))).then(fire(Retire(1))).then(check(s.active and s.fault and s.closed==0))
 run observedActorRetirementCannotSealTest=init.then(positive).then(fire(ActorsLost)).then(fire(Retire(1))).then(check(s.active and s.fault and s.closed==0))
 run observedSourceChangeCannotSealTest=init.then(positive).then(fire(SourceLost)).then(fire(Retire(1))).then(check(s.active and s.fault and s.closed==0))
 run currentDuplicateCannotRetireTest=init.then(positive).then(fire(Out)).then(fire(Retire(1))).then(check(s.active and s.fault and s.closed==0))
 run cancelledActorNormalClosureCanRetireTest=init.then(fire(Arm)).then(fire(Cancel)).then(live).then(finish).then(fire(Retire(1))).then(check(not(s.active)and s.closed==1 and not(s.accepted)))
 run normalRefusalCanRetireNeverAcceptsTest=init.then(fire(Arm)).then(live).then(fire(ExitRefusal)).then(fire(Out)).then(fire(Err)).then(fire(Gone)).then(fire(Receipt(true))).then(fire(Verify)).then(check(s.normalLife and not(s.accepted))).then(fire(Retire(1))).then(check(s.closed==1 and not(s.active)))
 run duplicateRetireCannotDuplicatePastTest=init.then(retired).then(fire(Retire(1))).then(check(s.closed==1 and s.lastRefused and not(s.active)))
 run changedSourceAfterRetireCannotArmTest=init.then(retired).then(fire(SourceLost)).then(fire(SetCommand(2))).then(fire(Arm)).then(check(not(s.active)and s.pastLease==1 and not(s.accepted)and s.lastRefused))
 run changedContextAfterRetireCannotArmTest=init.then(retired).then(fire(ActorsLost)).then(fire(Arm)).then(check(not(s.active)and s.pastLease==1 and s.lastRefused))
 run newUnregisteredLivePIDCannotArmTest=init.then(retired).then(fire(ForeignLive)).then(fire(Arm)).then(check(not(s.active)and s.lastRefused))
 run expiredWorkerCannotRetireTest=init.then(fire(Arm)).then(fire(Start(1))).then(fire(WorkerExpired)).then(fire(Retire(1))).then(check(s.active and s.closed==0 and s.fault))
 run finiteLeaseHistoryLimitNeverWrapsTest=init.then(retired).then(positive).then(fire(Retire(2))).then(positive).then(fire(Retire(3))).then(positive).then(fire(Retire(4))).then(fire(Arm)).then(check(s.closed==4 and s.next==5 and s.lease==4 and not(s.active)and s.lastRefused))
}
