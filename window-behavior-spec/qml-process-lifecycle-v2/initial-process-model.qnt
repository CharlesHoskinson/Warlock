module process_lifecycle {
 type State={lease:int,active:bool,started:bool,kernel:bool,exited:bool,normal:bool,code:int,out:bool,err:bool,gone:bool,receipt:bool,current:bool,fault:bool,accepted:bool,normalLife:bool,source:bool,nativeWrites:int,automaticRetries:int}
 type Event=Arm|Started({lease:int,kernel:bool})|Exit({lease:int,normal:bool,code:int})|Out(int)|Err(int)|Gone(int)|Receipt({lease:int,strict:bool})|Verify|Cancel|SourceFault|ReplaceProcess|ReplaceCollector|CommandChange|PIDReuse|LateRawChange|OldCallback(int)|CallerFlags
 var s:State
 action init=s'={lease:0,active:false,started:false,kernel:false,exited:false,normal:false,code:-1,out:false,err:false,gone:false,receipt:false,current:true,fault:false,accepted:false,normalLife:false,source:true,nativeWrites:0,automaticRetries:0}
 pure def life(a:State):bool=all{a.active,a.started,a.kernel,a.exited,a.normal,a.out,a.err,a.gone,not(a.fault),a.source}
 pure def complete(a:State):bool=all{life(a),a.code==0,a.receipt,a.current}
 action fire(e:Event):bool={
  val b={...s,accepted:false,normalLife:false}
  s'=match e {
  |Arm=>if(s.source and (not(s.active)or life(s))){...b,lease:s.lease+1,active:true,started:false,kernel:false,exited:false,normal:false,code:-1,out:false,err:false,gone:false,receipt:false,current:true,fault:false}else {...b,fault:true}
  |Started(v)=>if(v.lease!=s.lease)b else if(not(s.active)or s.started){...b,fault:true}else {...b,started:true,kernel:v.kernel,fault:s.fault or not(v.kernel)}
  |Exit(v)=>if(v.lease!=s.lease)b else if(not(s.started)or s.exited){...b,fault:true}else {...b,exited:true,normal:v.normal,code:v.code,fault:s.fault or not(v.normal)}
  |Out(n)=>if(n!=s.lease)b else if(not(s.started)or s.out){...b,fault:true}else {...b,out:true}
  |Err(n)=>if(n!=s.lease)b else if(not(s.started)or s.err){...b,fault:true}else {...b,err:true}
  |Gone(n)=>if(n!=s.lease)b else if(not(s.exited)){...b,fault:true}else {...b,gone:true}
  |Receipt(v)=>if(v.lease!=s.lease)b else {...b,receipt:v.strict,fault:s.fault or not(v.strict)}
  |Verify=>{...b,normalLife:life(s),accepted:complete(s)}
  |Cancel=>{...b,current:false}
  |SourceFault=>{...b,source:false,fault:true,current:false}
  |ReplaceProcess=>{...b,fault:true,current:false}
  |ReplaceCollector=>{...b,fault:true,current:false}
  |CommandChange=>{...b,fault:true,current:false}
  |PIDReuse=>{...b,fault:true,gone:false}
  |LateRawChange=>{...b,fault:true}
  |OldCallback(n)=>b
  |CallerFlags=>b
  }
 }
 val allProps=all{not(s.accepted)or complete(s),not(s.normalLife)or life(s),s.nativeWrites==0,s.automaticRetries==0,s.lease>=0}
 action step=nondet e=Set(Arm,Started({lease:1,kernel:true}),Started({lease:1,kernel:false}),Started({lease:2,kernel:true}),Exit({lease:1,normal:true,code:0}),Exit({lease:1,normal:true,code:2}),Exit({lease:1,normal:false,code:0}),Out(1),Err(1),Gone(1),Receipt({lease:1,strict:true}),Receipt({lease:1,strict:false}),Verify,Cancel,SourceFault,ReplaceProcess,ReplaceCollector,CommandChange,PIDReuse,LateRawChange,OldCallback(0),CallerFlags).oneOf();fire(e)
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
}
