module async_witness {
 type State={started:bool,alive:bool,budget:bool,source:bool,root:int,root0:int,declared:int,declared0:int,owner:int,owner0:int,context:int,context0:int,lease:int,lease0:int,epoch:int,frame:int,beforeEpoch:int,afterEpoch:int,beforeFrame:int,afterFrame:int,beforeSeen:bool,afterSeen:bool,discarded:Set[int],proof:bool,proofEpoch:int,provedWhileLive:bool,resultQueued:bool,workerLive:bool,workerDone:bool,workerJoined:bool,kernel:bool,accepted:bool,fault:bool,exitSeen:bool,normalExit:bool,outEOF:bool,errEOF:bool,gone:bool,receipt:bool,launches:int,jobs:int,nativeRetries:int,workerQObject:int,workerWrites:int}
 type Event=Start|Before|After|Verify(int)|ExplainedChange|HardFault|RootChange|DeclaredChange|OwnerChange|ContextChange|Retire|Expire|NormalExit|CrashExit|OutEOF|ErrEOF|Gone|Receipt|WorkerDone|Join|Result(int)|Finalize|WrongThreadCommit|CallerProof|OldExit(int)|OldEOF(int)|OldReceipt(int)
 var s:State
 action init=s'={started:false,alive:true,budget:true,source:true,root:1,root0:0,declared:1,declared0:1,owner:1,owner0:1,context:1,context0:1,lease:1,lease0:0,epoch:1,frame:1,beforeEpoch:0,afterEpoch:0,beforeFrame:0,afterFrame:0,beforeSeen:false,afterSeen:false,discarded:Set(),proof:false,proofEpoch:0,provedWhileLive:false,resultQueued:false,workerLive:false,workerDone:false,workerJoined:false,kernel:false,accepted:false,fault:false,exitSeen:false,normalExit:false,outEOF:false,errEOF:false,gone:false,receipt:false,launches:0,jobs:0,nativeRetries:0,workerQObject:0,workerWrites:0}
 pure def uiOriginal(a:State):bool=all{a.started,a.budget,a.source,not(a.fault),a.lease==a.lease0,a.root==a.root0,a.declared==a.declared0,a.owner==a.owner0,a.context==a.context0}
 pure def collecting(a:State):bool=all{uiOriginal(a),a.alive,a.workerLive,not(a.proof)}
 pure def complete(a:State):bool=all{collecting(a),a.beforeSeen,a.afterSeen,a.beforeEpoch==a.epoch,a.afterEpoch==a.epoch,a.beforeFrame==a.frame,a.afterFrame==a.frame,not(a.discarded.contains(a.epoch))}
 pure def historic(a:State):bool=all{a.proof,a.provedWhileLive,a.proofEpoch==a.epoch,not(a.discarded.contains(a.proofEpoch)),a.beforeSeen,a.afterSeen,a.beforeEpoch==a.proofEpoch,a.afterEpoch==a.proofEpoch,a.beforeFrame==a.frame,a.afterFrame==a.frame}
 pure def terminal(a:State):bool=all{uiOriginal(a),historic(a),a.kernel,a.workerDone,a.workerJoined,not(a.workerLive),a.exitSeen,a.normalExit,a.outEOF,a.errEOF,a.gone,a.receipt}
 pure def bad(a:State):State={...a,fault:true,kernel:false,accepted:false}
 pure def discard(a:State):State=if(collecting(a)and a.epoch<16){...a,epoch:a.epoch+1,frame:a.frame+1,beforeSeen:false,afterSeen:false,proof:false,proofEpoch:0,provedWhileLive:false,resultQueued:false,kernel:false,accepted:false,discarded:a.discarded.union(Set(a.epoch))}else bad(a)
 action fire(e:Event):bool={s'=match e {
 |Start=>if(s.started)bad(s)else {...s,started:true,root0:s.root,lease0:s.lease,launches:s.launches+1,jobs:s.jobs+1,workerLive:true}
 |Before=>if(collecting(s)){...s,beforeSeen:true,afterSeen:false,beforeEpoch:s.epoch,beforeFrame:s.frame}else bad(s)
 |After=>if(collecting(s)){...s,afterSeen:true,afterEpoch:s.epoch,afterFrame:s.frame}else bad(s)
 |Verify(n)=>if(n!=s.epoch)s else if(complete(s)){...s,proof:true,proofEpoch:s.epoch,provedWhileLive:true,resultQueued:true}else bad(s)
 |ExplainedChange=>discard(s)
 |HardFault=>bad({...s,source:false})
 |RootChange=>bad({...s,root:s.root+1})
 |DeclaredChange=>bad({...s,declared:s.declared+1})
 |OwnerChange=>bad({...s,owner:s.owner+1})
 |ContextChange=>bad({...s,context:s.context+1})
 |Retire=>{...s,lease:s.lease+1,kernel:false,accepted:false}
 |Expire=>{...s,budget:false,kernel:false,accepted:false}
 |NormalExit=>if(s.exitSeen)bad(s)else {...s,alive:false,exitSeen:true,normalExit:true}
 |CrashExit=>bad({...s,alive:false,exitSeen:true,normalExit:false})
 |OutEOF=>if(s.outEOF)bad(s)else {...s,outEOF:true}
 |ErrEOF=>if(s.errEOF)bad(s)else {...s,errEOF:true}
 |Gone=>if(s.exitSeen){...s,gone:true}else bad(s)
 |Receipt=>if(s.receipt)bad(s)else {...s,receipt:true}
 |WorkerDone=>if(s.workerLive){...s,workerLive:false,workerDone:true}else bad(s)
 |Join=>if(s.workerDone){...s,workerJoined:true}else bad(s)
 |Result(n)=>if(n!=s.lease or not(s.budget))s else if(all{uiOriginal(s),historic(s),s.resultQueued,s.workerDone,not(s.kernel)}){...s,kernel:true,resultQueued:false}else bad(s)
 |Finalize=>if(terminal(s)){...s,accepted:true}else {...s,accepted:false}
 |WrongThreadCommit=>bad(s)
 |CallerProof=>s
 |OldExit(n)=>if(n!=s.lease)s else bad(s)
 |OldEOF(n)=>if(n!=s.lease)s else bad(s)
 |OldReceipt(n)=>if(n!=s.lease)s else bad(s)
 }}
 val allProps=all{not(s.kernel)or all{uiOriginal(s),historic(s),s.workerDone},not(s.accepted)or terminal(s),s.launches<=1,s.jobs<=1,s.nativeRetries==0,s.workerQObject==0,s.workerWrites==0,s.epoch<=16,not(s.workerJoined)or all{s.workerDone,not(s.workerLive)}}
 action step=nondet e=Set(Start,Before,After,Verify(s.epoch),Verify(1),Verify(2),ExplainedChange,HardFault,RootChange,DeclaredChange,OwnerChange,ContextChange,Retire,Expire,NormalExit,CrashExit,OutEOF,ErrEOF,Gone,Receipt,WorkerDone,Join,Result(s.lease),Result(0),Finalize,WrongThreadCommit,CallerProof,OldExit(0),OldEOF(0),OldReceipt(0)).oneOf();fire(e)
 action check(v:bool):bool=all{assert(v),s'=s}
 action start=fire(Start)
 action before=fire(Before)
 action after=fire(After)
 action verify=fire(Verify(s.epoch))
 action done=fire(WorkerDone)
 action join=fire(Join)
 action result=fire(Result(s.lease))
 action normal=fire(NormalExit)
 action finishHelper=fire(OutEOF).then(fire(ErrEOF)).then(fire(Gone)).then(fire(Receipt))
 action witness=before.then(after).then(verify)
 action accept=fire(Finalize)
 action selectEpoch15=s'={...s,epoch:15,frame:15}
 run positiveNormalProcessWorkerTest=init.then(start).then(witness).then(done).then(join).then(result).then(normal).then(finishHelper).then(accept).then(check(s.accepted))
 run actualLiveProofMayDeliverAfterObservedExitTest=init.then(start).then(witness).then(normal).then(finishHelper).then(done).then(join).then(result).then(accept).then(check(s.accepted and s.provedWhileLive))
 run receiptBeforeResultCannotAuthorizeTest=init.then(start).then(witness).then(normal).then(finishHelper).then(accept).then(check(not(s.accepted)))
 run workerDoneAloneDoesNotCreateProofTest=init.then(start).then(done).then(join).then(result).then(check(not(s.kernel)))
 run callerCannotCreateProofTest=init.then(start).then(fire(CallerProof)).then(result).then(check(not(s.kernel)))
 run beforeWithoutAfterNeverProofTest=init.then(start).then(before).then(verify).then(check(not(s.proof)))
 run staleEpochCannotVerifyNewFrameTest=init.then(start).then(before).then(fire(ExplainedChange)).then(witness).then(fire(Verify(1))).then(check(s.proof and s.proofEpoch==2))
 run oldBeforeNewAfterRefusedTest=init.then(start).then(before).then(fire(ExplainedChange)).then(after).then(verify).then(check(not(s.proof)))
 run thirdEpochPositiveTest=init.then(start).then(fire(ExplainedChange)).then(fire(ExplainedChange)).then(witness).then(done).then(join).then(result).then(normal).then(finishHelper).then(accept).then(check(s.accepted and s.proofEpoch==3))
 run finalEpochPositiveTest=init.then(start).then(selectEpoch15).then(fire(ExplainedChange)).then(witness).then(done).then(join).then(result).then(normal).then(finishHelper).then(accept).then(check(s.accepted and s.proofEpoch==16))
 run finalEpochChangeRefusedTest=init.then(start).then(selectEpoch15).then(fire(ExplainedChange)).then(fire(ExplainedChange)).then(check(s.fault and s.epoch==16 and not(s.proof)))
 run vanishedChildCannotProveAfterExitTest=init.then(start).then(before).then(normal).then(after).then(verify).then(check(not(s.proof)))
 run retiredResultInertTest=init.then(start).then(witness).then(fire(Retire)).then(done).then(join).then(fire(Result(1))).then(check(not(s.kernel)and s.workerJoined and s.lease==2))
 run lateResultInertWithObservedTeardownTest=init.then(start).then(witness).then(fire(Expire)).then(done).then(join).then(result).then(check(not(s.kernel)and s.workerJoined and not(s.fault)))
 run oldResultAfterAcceptancePreservesTest=init.then(start).then(witness).then(done).then(join).then(result).then(normal).then(finishHelper).then(accept).then(fire(Result(0))).then(check(s.accepted and s.kernel and s.workerJoined and s.lease==1))
 run oldProcessCallbacksAfterAcceptanceInertTest=init.then(start).then(witness).then(done).then(join).then(result).then(normal).then(finishHelper).then(accept).then(fire(OldExit(0))).then(fire(OldEOF(0))).then(fire(OldReceipt(0))).then(check(s.accepted and s.kernel and s.normalExit and s.workerJoined))
 run duplicateCurrentResultInvalidatesTest=init.then(start).then(witness).then(done).then(join).then(result).then(result).then(check(s.fault and not(s.kernel)))
 run rootChangedWhileQueuedRefusesTest=init.then(start).then(witness).then(done).then(fire(RootChange)).then(result).then(check(not(s.kernel)))
 run declaredChangedWhileQueuedRefusesTest=init.then(start).then(witness).then(done).then(fire(DeclaredChange)).then(result).then(check(not(s.kernel)))
 run ownerChangedWhileQueuedRefusesTest=init.then(start).then(witness).then(done).then(fire(OwnerChange)).then(result).then(check(not(s.kernel)))
 run contextChangedWhileQueuedRefusesTest=init.then(start).then(witness).then(done).then(fire(ContextChange)).then(result).then(check(not(s.kernel)))
 run wrongThreadCommitRefusedTest=init.then(start).then(witness).then(done).then(fire(WrongThreadCommit)).then(result).then(check(not(s.kernel)and s.workerQObject==0))
 run workerMustFinishBeforeCommitTest=init.then(start).then(witness).then(result).then(check(not(s.kernel)))
 run workerNotJoinedBlocksCompletionTest=init.then(start).then(witness).then(done).then(result).then(normal).then(finishHelper).then(accept).then(check(not(s.accepted)))
 run retiredJobStillRequiresNormalJoinTest=init.then(start).then(fire(Retire)).then(done).then(join).then(check(s.workerJoined and s.jobs==1 and s.launches==1 and not(s.kernel)))
 run sourceFaultStillRequiresNormalWorkerJoinTest=init.then(start).then(fire(HardFault)).then(done).then(join).then(check(s.workerJoined and s.fault and not(s.kernel)))
 run missingEOFBlocksCompletionTest=init.then(start).then(witness).then(done).then(join).then(result).then(normal).then(fire(Gone)).then(fire(Receipt)).then(accept).then(check(not(s.accepted)))
 run missingReceiptBlocksCompletionTest=init.then(start).then(witness).then(done).then(join).then(result).then(normal).then(fire(OutEOF)).then(fire(ErrEOF)).then(fire(Gone)).then(accept).then(check(not(s.accepted)))
 run crashBlocksCompletionTest=init.then(start).then(witness).then(done).then(join).then(result).then(fire(CrashExit)).then(fire(OutEOF)).then(fire(ErrEOF)).then(fire(Gone)).then(fire(Receipt)).then(accept).then(check(not(s.accepted)))
 run duplicateStartedNoRelaunchTest=init.then(start).then(start).then(check(s.fault and s.launches==1 and s.jobs==1))
 run duplicateCurrentEOFRevokesTest=init.then(start).then(witness).then(done).then(join).then(result).then(normal).then(finishHelper).then(accept).then(fire(OutEOF)).then(check(s.fault and not(s.accepted)))
 run postAcceptanceRetirementRevokesTest=init.then(start).then(witness).then(done).then(join).then(result).then(normal).then(finishHelper).then(accept).then(fire(Retire)).then(check(not(s.accepted)and s.workerJoined))
}
