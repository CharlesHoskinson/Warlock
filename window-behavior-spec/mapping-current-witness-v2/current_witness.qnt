module current_witness {
 type State={started:bool,alive:bool,deadline:bool,source:bool,root:int,originalRoot:int,declared:int,originalDeclared:int,owner:int,originalOwner:int,frame:int,epoch:int,beforeEpoch:int,afterEpoch:int,beforeFrame:int,afterFrame:int,beforeRoot:int,afterRoot:int,beforeSeen:bool,afterSeen:bool,kernel:bool,fault:bool,discarded:Set[int],launches:int,nativeRetries:int,nativeWrites:int}
 type Event=Start|Before|After|Verify(int)|KnownVMAChange|ConfirmedRangeGone|HardSourceFault|RootChange|DeclaredChange|OwnerChange|ChildGone|Expire|HelperSuccess|CallerFlags
 var s:State
 action init=s'={started:false,alive:true,deadline:true,source:true,root:1,originalRoot:0,declared:1,originalDeclared:1,owner:1,originalOwner:1,frame:1,epoch:1,beforeEpoch:0,afterEpoch:0,beforeFrame:0,afterFrame:0,beforeRoot:0,afterRoot:0,beforeSeen:false,afterSeen:false,kernel:false,fault:false,discarded:Set(),launches:0,nativeRetries:0,nativeWrites:0}
 pure def original(a:State):bool=all{a.started,a.alive,a.deadline,a.source,not(a.fault),a.root==a.originalRoot,a.declared==a.originalDeclared,a.owner==a.originalOwner}
 pure def complete(a:State):bool=all{original(a),a.beforeSeen,a.afterSeen,a.beforeEpoch==a.epoch,a.afterEpoch==a.epoch,a.beforeFrame==a.frame,a.afterFrame==a.frame,a.beforeRoot==a.originalRoot,a.afterRoot==a.originalRoot,not(a.discarded.contains(a.epoch))}
 pure def discard(a:State):State=if(original(a)and a.epoch<16){...a,epoch:a.epoch+1,frame:a.frame+1,beforeSeen:false,afterSeen:false,kernel:false,discarded:a.discarded.union(Set(a.epoch))}else {...a,kernel:false,fault:true}
 action fire(e:Event):bool={s'=match e {
 |Start=>if(s.started){...s,kernel:false,fault:true}else {...s,started:true,originalRoot:s.root,launches:s.launches+1}
 |Before=>if(original(s)){...s,kernel:false,beforeEpoch:s.epoch,beforeFrame:s.frame,beforeRoot:s.root,beforeSeen:true,afterSeen:false}else {...s,kernel:false,fault:true}
 |After=>if(original(s)){...s,kernel:false,afterEpoch:s.epoch,afterFrame:s.frame,afterRoot:s.root,afterSeen:true}else {...s,kernel:false,fault:true}
 |Verify(n)=>if(n!=s.epoch)s else {...s,kernel:complete(s)}
 |KnownVMAChange=>discard(s)
 |ConfirmedRangeGone=>discard(s)
 |HardSourceFault=>{...s,source:false,fault:true,kernel:false}
 |RootChange=>{...s,root:s.root+1,fault:true,kernel:false}
 |DeclaredChange=>{...s,declared:s.declared+1,fault:true,kernel:false}
 |OwnerChange=>{...s,owner:s.owner+1,fault:true,kernel:false}
 |ChildGone=>{...s,alive:false,kernel:false}
 |Expire=>{...s,deadline:false,kernel:false}
 |HelperSuccess=>s
 |CallerFlags=>s
 }}
 val allProps=all{not(s.kernel)or complete(s),s.launches<=1,s.nativeRetries==0,s.nativeWrites==0,s.epoch<=16}
 action step=nondet e=Set(Start,Before,After,Verify(1),Verify(2),KnownVMAChange,ConfirmedRangeGone,HardSourceFault,RootChange,DeclaredChange,OwnerChange,ChildGone,Expire,HelperSuccess,CallerFlags).oneOf();fire(e)
 action check(v:bool):bool=all{assert(v),s'=s}
 action start=fire(Start)
 action before=fire(Before)
 action after=fire(After)
 action verify=fire(Verify(1))
 run firstCompleteEpochTest=init.then(start).then(before).then(after).then(verify).then(check(s.kernel))
 run incompleteNeverAuthorizedTest=init.then(start).then(before).then(verify).then(check(not(s.kernel)))
 run changedLoaderEpochDiscardsTest=init.then(start).then(before).then(fire(KnownVMAChange)).then(check(not(s.kernel)and s.epoch==2 and s.discarded.contains(1)))
 run entirelyFreshCurrentEpochTest=init.then(start).then(before).then(fire(KnownVMAChange)).then(before).then(after).then(fire(Verify(2))).then(check(s.kernel and s.launches==1))
 run vanishedRangeNeedsFreshEpochTest=init.then(start).then(before).then(fire(ConfirmedRangeGone)).then(after).then(fire(Verify(2))).then(check(not(s.kernel)))
 run oldBeforeNewAfterRefusedTest=init.then(start).then(before).then(fire(KnownVMAChange)).then(after).then(fire(Verify(2))).then(check(not(s.kernel)))
 run oldVerificationCannotAuthorizeTest=init.then(start).then(before).then(fire(KnownVMAChange)).then(before).then(after).then(verify).then(check(not(s.kernel)))
 run oldWitnessAfterNewAcceptanceInertTest=init.then(start).then(fire(KnownVMAChange)).then(before).then(after).then(fire(Verify(2))).then(verify).then(check(s.kernel))
 run unknownOrDeletedCodeHardFaultTest=init.then(start).then(before).then(fire(HardSourceFault)).then(fire(KnownVMAChange)).then(before).then(after).then(fire(Verify(2))).then(check(not(s.kernel)and s.fault))
 run sourceChangedCannotRebindTest=init.then(start).then(before).then(fire(DeclaredChange)).then(fire(KnownVMAChange)).then(before).then(after).then(verify).then(check(not(s.kernel)and s.fault))
 run PIDStartReplacementHardFaultTest=init.then(start).then(before).then(fire(RootChange)).then(fire(KnownVMAChange)).then(before).then(after).then(verify).then(check(not(s.kernel)and s.fault))
 run capturedOwnerChangedRefusedTest=init.then(start).then(before).then(fire(OwnerChange)).then(after).then(verify).then(check(not(s.kernel)))
 run helperSuccessDoesNotCreateKernelProofTest=init.then(start).then(fire(HelperSuccess)).then(verify).then(check(not(s.kernel)))
 run helperSuccessDoesNotRestoreExpiredProofTest=init.then(start).then(before).then(after).then(fire(Expire)).then(fire(HelperSuccess)).then(verify).then(check(not(s.kernel)))
 run callerCannotCreateKernelProofTest=init.then(start).then(fire(CallerFlags)).then(verify).then(check(not(s.kernel)))
 run childGoneCannotReobserveTest=init.then(start).then(before).then(fire(ChildGone)).then(before).then(after).then(verify).then(check(not(s.kernel)and s.fault))
 run deadlineCannotExtendTest=init.then(start).then(before).then(fire(Expire)).then(fire(KnownVMAChange)).then(before).then(after).then(verify).then(check(not(s.kernel)and s.fault))
 run duplicateStartedNeverRelaunchesTest=init.then(start).then(start).then(before).then(after).then(verify).then(check(s.launches==1 and s.fault and not(s.kernel)))
 action atEpochLimit=s'={...s,epoch:16}
 run epochLimitRefusesTest=init.then(start).then(atEpochLimit).then(fire(KnownVMAChange)).then(check(s.epoch==16 and s.fault and not(s.kernel)))
 run noProofFromNameChangeAloneTest=init.then(start).then(fire(KnownVMAChange)).then(fire(Verify(2))).then(check(not(s.kernel)))
}
