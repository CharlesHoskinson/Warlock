module disconnect_fixture {
 type State={evidence:bool,held:bool,requested:bool,returned:bool,foreign:int,joined:bool,pending:bool,fault:bool,retired:bool,deadlock:bool,accepted:bool,launches:int,retries:int,controls:int}
 type Event=Persist|PlainHook|Return|OutsideEmit|Activate|Join|Drain|Commit|UnsafeEmitJoin
 var s:State
 action init=s'={evidence:false,held:false,requested:false,returned:false,foreign:0,joined:false,pending:false,fault:false,retired:false,deadlock:false,accepted:false,launches:1,retries:0,controls:0}
 action fire(e:Event):bool={s'=match e {
 |Persist=>{...s,evidence:true}
 |PlainHook=>if(s.evidence and not(s.requested)){...s,held:true,requested:true}else s
 |Return=>if(s.requested and not(s.deadlock)){...s,held:false,returned:true}else s
 |OutsideEmit=>if(s.returned and not(s.held)and s.foreign==0){...s,foreign:1}else s
 |Activate=>if(s.foreign==1 and not(s.held)){...s,foreign:2,pending:true}else s
 |Join=>if(s.returned and not(s.held)and s.foreign==2){...s,joined:true}else s
 |Drain=>if(s.pending){...s,pending:false,fault:true}else s
 |Commit=>if(s.returned and s.joined and not(s.deadlock)){...s,fault:s.fault or s.pending,retired:not(s.fault or s.pending)}else s
 |UnsafeEmitJoin=>if(s.held){...s,deadlock:true}else s
 }}
 val allProps=all{not(s.joined)or all{s.returned,not(s.held),s.foreign==2},not(s.retired)or all{s.evidence,s.joined,not(s.pending),not(s.fault),not(s.deadlock)},not(s.accepted),s.launches==1,s.retries==0,s.controls==0}
 action step=nondet e=Set(Persist,PlainHook,Return,OutsideEmit,Activate,Join,Drain,Commit,UnsafeEmitJoin).oneOf();fire(e)
 action check(v:bool):bool=all{assert(v),s'=s}
 run notificationContainsNoQObjectEmissionTest=init.then(fire(Persist)).then(fire(PlainHook)).then(fire(OutsideEmit)).then(fire(Activate)).then(check(s.held and s.requested and s.foreign==0 and not(s.pending)))
 run originalInsideNotificationDeadlockRetainedTest=init.then(fire(Persist)).then(fire(PlainHook)).then(fire(UnsafeEmitJoin)).then(fire(Return)).then(fire(Commit)).then(check(s.deadlock and s.held and not(s.retired)))
 run persistedBaselineRequiredBeforePlainHookTest=init.then(fire(PlainHook)).then(check(not(s.requested)))
 run genuineSignalAtOutsideSourceBoundaryQueuesTest=init.then(fire(Persist)).then(fire(PlainHook)).then(fire(Return)).then(fire(OutsideEmit)).then(fire(Activate)).then(fire(Join)).then(check(s.joined and s.pending and not(s.held)))
 run currentFaultAfterSourceBoundaryRefusesRetirementTest=init.then(fire(Persist)).then(fire(PlainHook)).then(fire(Return)).then(fire(OutsideEmit)).then(fire(Activate)).then(fire(Join)).then(fire(Drain)).then(fire(Commit)).then(check(s.fault and not(s.retired)))
 run admittedUndrainedSignalCannotPassFinalCommitTest=init.then(fire(Persist)).then(fire(PlainHook)).then(fire(Return)).then(fire(OutsideEmit)).then(fire(Activate)).then(fire(Join)).then(fire(Commit)).then(check(s.fault and not(s.retired)))
 run missingActualSignalCannotBecomeJoinOrProofTest=init.then(fire(Persist)).then(fire(PlainHook)).then(fire(Return)).then(fire(OutsideEmit)).then(fire(Join)).then(fire(Commit)).then(check(not(s.joined)and not(s.retired)and not(s.fault)))
 run notificationCannotJoinDiagnosticThreadTest=init.then(fire(Persist)).then(fire(PlainHook)).then(fire(Join)).then(check(not(s.joined)and s.foreign==0))
 run diagnosticHasNoHelperControlOrSuccessTest=init.then(fire(Persist)).then(fire(PlainHook)).then(fire(Return)).then(fire(OutsideEmit)).then(fire(Activate)).then(fire(Join)).then(fire(Commit)).then(check(s.launches==1 and s.retries==0 and s.controls==0 and not(s.accepted)))
}
