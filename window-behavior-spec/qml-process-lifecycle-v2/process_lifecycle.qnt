module process_lifecycle {
 val Fields=Set("pid","start","parent","group","uid","cgroup","namespace","exe","argv","environment","entry","config","process","stdout","stderr","engine","epoch","provider","owner","nonce")
 val SAFE_MAX=9007199254740991
 val DynamicKernelFields=Set("pid","start")
 val DeclaredFields=Fields.exclude(DynamicKernelFields)
 val KernelFields=Set("pid","start","parent","group","uid","cgroup","namespace","exe","argv","environment","entry")
 val ObserverFields=Fields.exclude(KernelFields).exclude(Set("owner","nonce"))
 val ActorFields=KernelFields.union(ObserverFields)
 type State={id:str->int,armId:str->int,capturedId:str->int,lease:int,active:bool,started:bool,kernel:bool,exited:bool,normal:bool,code:int,out:bool,err:bool,gone:bool,receipt:bool,current:bool,fault:bool,accepted:bool,normalLife:bool,source:bool,nativeWrites:int,automaticRetries:int}
 type Event=Arm|Started({lease:int,kernel:bool})|Exit({lease:int,normal:bool,code:int})|Out(int)|Err(int)|Gone(int)|Receipt({lease:int,strict:bool})|Verify|Cancel|SourceFault|ReplaceProcess|ReplaceCollector|CommandChange|PIDReuse|LateRawChange|OldCallback(int)|CallerFlags|IdentityChange(str)
 var s:State
 action init=s'={id:Fields.mapBy(f=>1),armId:Fields.mapBy(f=>0),capturedId:Fields.mapBy(f=>0),lease:0,active:false,started:false,kernel:false,exited:false,normal:false,code:-1,out:false,err:false,gone:false,receipt:false,current:true,fault:false,accepted:false,normalLife:false,source:true,nativeWrites:0,automaticRetries:0}
 pure def life(a:State):bool=all{a.active,a.started,a.kernel,a.exited,a.normal,a.out,a.err,a.gone,not(a.fault),a.source,ActorFields.forall(f=>a.id.get(f)==a.capturedId.get(f))}
 pure def complete(a:State):bool=all{life(a),a.code==0,a.receipt,a.current,a.id==a.capturedId}
 action fire(e:Event):bool={
  val b={...s,accepted:false,normalLife:false}
  s'=match e {
  |Arm=>if(s.source and s.lease<SAFE_MAX-1 and (not(s.active)or life(s))){...b,lease:s.lease+1,active:true,armId:s.id,started:false,kernel:false,exited:false,normal:false,code:-1,out:false,err:false,gone:false,receipt:false,current:true,fault:false}else {...b,fault:true}
  |Started(v)=>if(v.lease!=s.lease)s else if(not(s.active)or s.started){...b,fault:true}else {...b,started:true,kernel:v.kernel,capturedId:Fields.mapBy(f=>if(DynamicKernelFields.contains(f))s.id.get(f)else s.armId.get(f)),fault:s.fault or not(v.kernel)or not(DeclaredFields.forall(f=>s.id.get(f)==s.armId.get(f)))}
  |Exit(v)=>if(v.lease!=s.lease)s else if(not(s.started)or s.exited){...b,fault:true}else {...b,exited:true,normal:v.normal,code:v.code,fault:s.fault or not(v.normal)}
  |Out(n)=>if(n!=s.lease)s else if(not(s.started)or s.out){...b,fault:true}else {...b,out:true}
  |Err(n)=>if(n!=s.lease)s else if(not(s.started)or s.err){...b,fault:true}else {...b,err:true}
  |Gone(n)=>if(n!=s.lease)s else if(not(s.exited)){...b,fault:true}else {...b,gone:true}
  |Receipt(v)=>if(v.lease!=s.lease)s else if(not(life(s))){...b,fault:true}else {...b,receipt:v.strict,fault:s.fault or not(v.strict)}
  |Verify=>{...b,normalLife:life(s),accepted:complete(s)}
  |Cancel=>{...b,current:false}
  |SourceFault=>{...b,source:false,fault:true,current:false}
  |ReplaceProcess=>{...b,fault:true,current:false}
  |ReplaceCollector=>{...b,fault:true,current:false}
  |CommandChange=>{...b,fault:true,current:false}
  |PIDReuse=>{...b,fault:true,gone:false}
  |LateRawChange=>{...b,fault:true}
  |OldCallback(n)=>if(n!=s.lease)s else {...b,fault:true}
  |IdentityChange(f)=>{...b,id:s.id.set(f,s.id.get(f)+1)}
  |CallerFlags=>b
  }
 }
 val allProps=all{not(s.accepted)or complete(s),not(s.normalLife)or life(s),s.nativeWrites==0,s.automaticRetries==0,s.lease>=0,s.lease<SAFE_MAX}
 action step=nondet e=Set(Arm,Started({lease:1,kernel:true}),Started({lease:1,kernel:false}),Started({lease:2,kernel:true}),Exit({lease:1,normal:true,code:0}),Exit({lease:1,normal:true,code:2}),Exit({lease:1,normal:false,code:0}),Out(1),Err(1),Gone(1),Receipt({lease:1,strict:true}),Receipt({lease:1,strict:false}),Verify,Cancel,SourceFault,ReplaceProcess,ReplaceCollector,CommandChange,PIDReuse,LateRawChange,OldCallback(0),CallerFlags,IdentityChange("pid"),IdentityChange("start"),IdentityChange("exe"),IdentityChange("argv"),IdentityChange("config"),IdentityChange("process"),IdentityChange("stdout"),IdentityChange("stderr"),IdentityChange("owner"),IdentityChange("nonce"),IdentityChange("epoch")).oneOf();fire(e)
 action check(v:bool):bool=all{assert(v),s'=s}
 action arm=fire(Arm)
 action start=fire(Started({lease:1,kernel:true}))
 action exit=fire(Exit({lease:1,normal:true,code:0}))
 action out=fire(Out(1))
 action err=fire(Err(1))
 action gone=fire(Gone(1))
 action receipt=fire(Receipt({lease:1,strict:true}))
 action verify=fire(Verify)
 action allLife=start.then(exit).then(out).then(err).then(gone).then(receipt)
 run normalCompleteTest=init.then(arm).then(allLife).then(verify).then(check(s.accepted and s.normalLife))
 run eofBeforeExitTest=init.then(arm).then(start).then(out).then(err).then(exit).then(gone).then(receipt).then(verify).then(check(s.accepted))
 run stderrFirstTest=init.then(arm).then(start).then(err).then(exit).then(out).then(gone).then(receipt).then(verify).then(check(s.accepted))
 run missingStartTest=init.then(arm).then(exit).then(out).then(err).then(gone).then(receipt).then(verify).then(check(not(s.accepted)))
 run missingKernelTest=init.then(arm).then(fire(Started({lease:1,kernel:false}))).then(exit).then(out).then(err).then(gone).then(receipt).then(verify).then(check(not(s.accepted)))
 run missingStdoutTest=init.then(arm).then(start).then(exit).then(err).then(gone).then(receipt).then(verify).then(check(not(s.accepted)))
 run missingStderrTest=init.then(arm).then(start).then(exit).then(out).then(gone).then(receipt).then(verify).then(check(not(s.accepted)))
 run missingExitTest=init.then(arm).then(start).then(out).then(err).then(gone).then(receipt).then(verify).then(check(not(s.accepted)))
 run missingGoneTest=init.then(arm).then(start).then(exit).then(out).then(err).then(receipt).then(verify).then(check(not(s.accepted)))
 run crashZeroNotNormalTest=init.then(arm).then(start).then(fire(Exit({lease:1,normal:false,code:0}))).then(out).then(err).then(gone).then(receipt).then(verify).then(check(not(s.accepted)and not(s.normalLife)))
 run nativeRefusalNormalNotCompleteTest=init.then(arm).then(start).then(fire(Exit({lease:1,normal:true,code:2}))).then(out).then(err).then(gone).then(receipt).then(verify).then(check(s.normalLife and not(s.accepted)))
 run malformedReceiptTest=init.then(arm).then(allLife).then(fire(Receipt({lease:1,strict:false}))).then(verify).then(check(not(s.accepted)))
 run cancelPreservesNormalLifeTest=init.then(arm).then(start).then(fire(Cancel)).then(exit).then(out).then(err).then(gone).then(receipt).then(verify).then(check(s.normalLife and not(s.accepted)))
 run sourceReloadRevokesTest=init.then(arm).then(start).then(fire(SourceFault)).then(exit).then(out).then(err).then(gone).then(receipt).then(verify).then(check(not(s.accepted)))
 run processReplacementTest=init.then(arm).then(allLife).then(fire(ReplaceProcess)).then(verify).then(check(not(s.accepted)))
 run collectorReplacementTest=init.then(arm).then(allLife).then(fire(ReplaceCollector)).then(verify).then(check(not(s.accepted)))
 run commandChangedTest=init.then(arm).then(allLife).then(fire(CommandChange)).then(verify).then(check(not(s.accepted)))
 run pidReuseTest=init.then(arm).then(allLife).then(fire(PIDReuse)).then(verify).then(check(not(s.accepted)and not(s.normalLife)))
 run duplicateStartTest=init.then(arm).then(start).then(start).then(exit).then(out).then(err).then(gone).then(receipt).then(verify).then(check(not(s.accepted)))
 run duplicateExitTest=init.then(arm).then(allLife).then(exit).then(verify).then(check(not(s.accepted)))
 run duplicateEOFTest=init.then(arm).then(allLife).then(out).then(verify).then(check(not(s.accepted)))
 run lateRawChangeTest=init.then(arm).then(allLife).then(verify).then(fire(LateRawChange)).then(verify).then(check(not(s.accepted)))
 run rearmPendingRefusedTest=init.then(arm).then(start).then(arm).then(verify).then(check(not(s.accepted)and s.fault))
 run newLeaseIgnoresOldCallbackTest=init.then(arm).then(allLife).then(arm).then(fire(OldCallback(1))).then(check(s.lease==2 and not(s.fault)and not(s.started)))
 run callerFlagsCannotCompleteTest=init.then(fire(CallerFlags)).then(verify).then(check(not(s.accepted)))
 run earlyReceiptCannotBecomeCompletionTest=init.then(arm).then(receipt).then(allLife).then(verify).then(check(not(s.accepted)))
 run changedPidIdentityTest=init.then(arm).then(allLife).then(fire(IdentityChange("pid"))).then(verify).then(check(not(s.accepted)))
 run changedStartIdentityTest=init.then(arm).then(allLife).then(fire(IdentityChange("start"))).then(verify).then(check(not(s.accepted)))
 run changedParentIdentityTest=init.then(arm).then(allLife).then(fire(IdentityChange("parent"))).then(verify).then(check(not(s.accepted)))
 run changedGroupIdentityTest=init.then(arm).then(allLife).then(fire(IdentityChange("group"))).then(verify).then(check(not(s.accepted)))
 run changedUidIdentityTest=init.then(arm).then(allLife).then(fire(IdentityChange("uid"))).then(verify).then(check(not(s.accepted)))
 run changedCgroupIdentityTest=init.then(arm).then(allLife).then(fire(IdentityChange("cgroup"))).then(verify).then(check(not(s.accepted)))
 run changedNamespaceIdentityTest=init.then(arm).then(allLife).then(fire(IdentityChange("namespace"))).then(verify).then(check(not(s.accepted)))
 run changedExeIdentityTest=init.then(arm).then(allLife).then(fire(IdentityChange("exe"))).then(verify).then(check(not(s.accepted)))
 run changedArgvIdentityTest=init.then(arm).then(allLife).then(fire(IdentityChange("argv"))).then(verify).then(check(not(s.accepted)))
 run changedEnvironmentIdentityTest=init.then(arm).then(allLife).then(fire(IdentityChange("environment"))).then(verify).then(check(not(s.accepted)))
 run changedEntryIdentityTest=init.then(arm).then(allLife).then(fire(IdentityChange("entry"))).then(verify).then(check(not(s.accepted)))
 run changedConfigIdentityTest=init.then(arm).then(allLife).then(fire(IdentityChange("config"))).then(verify).then(check(not(s.accepted)))
 run changedProcessIdentityTest=init.then(arm).then(allLife).then(fire(IdentityChange("process"))).then(verify).then(check(not(s.accepted)))
 run changedStdoutIdentityTest=init.then(arm).then(allLife).then(fire(IdentityChange("stdout"))).then(verify).then(check(not(s.accepted)))
 run changedStderrIdentityTest=init.then(arm).then(allLife).then(fire(IdentityChange("stderr"))).then(verify).then(check(not(s.accepted)))
 run changedEngineIdentityTest=init.then(arm).then(allLife).then(fire(IdentityChange("engine"))).then(verify).then(check(not(s.accepted)))
 run changedEpochIdentityTest=init.then(arm).then(allLife).then(fire(IdentityChange("epoch"))).then(verify).then(check(not(s.accepted)))
 run changedProviderIdentityTest=init.then(arm).then(allLife).then(fire(IdentityChange("provider"))).then(verify).then(check(not(s.accepted)))
 run changedOwnerIdentityTest=init.then(arm).then(allLife).then(fire(IdentityChange("owner"))).then(verify).then(check(not(s.accepted)))
 run changedNonceIdentityTest=init.then(arm).then(allLife).then(fire(IdentityChange("nonce"))).then(verify).then(check(not(s.accepted)))
 run changedProcessBeforeStartTest=init.then(arm).then(fire(IdentityChange("process"))).then(allLife).then(verify).then(check(not(s.accepted)))
 run preStartParentChangeRefusedTest=init.then(arm).then(fire(IdentityChange("parent"))).then(allLife).then(verify).then(check(not(s.accepted)and s.fault))
 run preStartGroupChangeRefusedTest=init.then(arm).then(fire(IdentityChange("group"))).then(allLife).then(verify).then(check(not(s.accepted)and s.fault))
 run preStartUidChangeRefusedTest=init.then(arm).then(fire(IdentityChange("uid"))).then(allLife).then(verify).then(check(not(s.accepted)and s.fault))
 run preStartCgroupChangeRefusedTest=init.then(arm).then(fire(IdentityChange("cgroup"))).then(allLife).then(verify).then(check(not(s.accepted)and s.fault))
 run preStartNamespaceChangeRefusedTest=init.then(arm).then(fire(IdentityChange("namespace"))).then(allLife).then(verify).then(check(not(s.accepted)and s.fault))
 run preStartExeChangeRefusedTest=init.then(arm).then(fire(IdentityChange("exe"))).then(allLife).then(verify).then(check(not(s.accepted)and s.fault))
 run preStartArgvChangeRefusedTest=init.then(arm).then(fire(IdentityChange("argv"))).then(allLife).then(verify).then(check(not(s.accepted)and s.fault))
 run preStartEnvironmentChangeRefusedTest=init.then(arm).then(fire(IdentityChange("environment"))).then(allLife).then(verify).then(check(not(s.accepted)and s.fault))
 run preStartEntryChangeRefusedTest=init.then(arm).then(fire(IdentityChange("entry"))).then(allLife).then(verify).then(check(not(s.accepted)and s.fault))
 run preStartConfigChangeRefusedTest=init.then(arm).then(fire(IdentityChange("config"))).then(allLife).then(verify).then(check(not(s.accepted)and s.fault))
 run preStartEngineChangeRefusedTest=init.then(arm).then(fire(IdentityChange("engine"))).then(allLife).then(verify).then(check(not(s.accepted)and s.fault))
 run preStartEpochChangeRefusedTest=init.then(arm).then(fire(IdentityChange("epoch"))).then(allLife).then(verify).then(check(not(s.accepted)and s.fault))
 run preStartProviderChangeRefusedTest=init.then(arm).then(fire(IdentityChange("provider"))).then(allLife).then(verify).then(check(not(s.accepted)and s.fault))
 run preStartOwnerChangeRefusedTest=init.then(arm).then(fire(IdentityChange("owner"))).then(allLife).then(verify).then(check(not(s.accepted)and s.fault))
 run preStartNonceChangeRefusedTest=init.then(arm).then(fire(IdentityChange("nonce"))).then(allLife).then(verify).then(check(not(s.accepted)and s.fault))
 run preStartStdoutChangeRefusedTest=init.then(arm).then(fire(IdentityChange("stdout"))).then(allLife).then(verify).then(check(not(s.accepted)and s.fault))
 run preStartStderrChangeRefusedTest=init.then(arm).then(fire(IdentityChange("stderr"))).then(allLife).then(verify).then(check(not(s.accepted)and s.fault))
 run dynamicPidStartMayBindAtStartedTest=init.then(arm).then(fire(IdentityChange("pid"))).then(fire(IdentityChange("start"))).then(allLife).then(verify).then(check(s.accepted))
 action atCapacity=s'= {...s,lease:SAFE_MAX-1}
 run exhaustedLeaseRefusedTest=init.then(atCapacity).then(arm).then(check(s.fault and not(s.active)and s.lease==SAFE_MAX-1))
 action preserveOldStarted={val before=s;fire(Started({lease:0,kernel:false})).then(check(s==before))}
 run oldStartedPreservesAcceptedSnapshotTest=init.then(arm).then(allLife).then(verify).then(preserveOldStarted)
 action preserveOldExit={val before=s;fire(Exit({lease:0,normal:false,code:3})).then(check(s==before))}
 run oldExitPreservesAcceptedSnapshotTest=init.then(arm).then(allLife).then(verify).then(preserveOldExit)
 action preserveOldOut={val before=s;fire(Out(0)).then(check(s==before))}
 run oldOutPreservesAcceptedSnapshotTest=init.then(arm).then(allLife).then(verify).then(preserveOldOut)
 action preserveOldErr={val before=s;fire(Err(0)).then(check(s==before))}
 run oldErrPreservesAcceptedSnapshotTest=init.then(arm).then(allLife).then(verify).then(preserveOldErr)
 action preserveOldGone={val before=s;fire(Gone(0)).then(check(s==before))}
 run oldGonePreservesAcceptedSnapshotTest=init.then(arm).then(allLife).then(verify).then(preserveOldGone)
 action preserveOldReceipt={val before=s;fire(Receipt({lease:0,strict:false})).then(check(s==before))}
 run oldReceiptPreservesAcceptedSnapshotTest=init.then(arm).then(allLife).then(verify).then(preserveOldReceipt)
 action preserveOldOldCallback={val before=s;fire(OldCallback(0)).then(check(s==before))}
 run oldOldCallbackPreservesAcceptedSnapshotTest=init.then(arm).then(allLife).then(verify).then(preserveOldOldCallback)
 run currentLeaseOldCallbackNotInertTest=init.then(arm).then(allLife).then(verify).then(fire(OldCallback(1))).then(check(s.fault and not(s.accepted)and not(s.normalLife)))
}
