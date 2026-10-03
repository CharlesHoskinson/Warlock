module disconnect_fixture {
 type State={prepared:bool,evidence:bool,held:bool,hook:bool,returned:bool,foreign:int,joined:bool,pending:bool,fault:bool,retired:bool,deadlock:bool,accepted:bool,launches:int,retries:int,controls:int}
 type Event=Persist|HookStart|Activate|UnsafeHookJoin|HookReturn|OutsideJoin|Drain|Commit
 var s:State
 action init=s'={prepared:true,evidence:false,held:false,hook:false,returned:false,foreign:0,joined:false,pending:false,fault:false,retired:false,deadlock:false,accepted:false,launches:1,retries:0,controls:0}
 action fire(e:Event):bool={s'=match e {
 |Persist=>{...s,evidence:true}
 |HookStart=>if(s.prepared and s.evidence and not(s.hook)){...s,held:true,hook:true,foreign:1}else s
 |Activate=>if(s.foreign==1){...s,foreign:if(s.held)2 else 3,pending:not(s.held)}else if(s.foreign==2 and not(s.held)){...s,foreign:3,pending:true}else s
 |UnsafeHookJoin=>if(s.held and s.foreign<3){...s,deadlock:true}else s
 |HookReturn=>if(s.hook and not(s.deadlock)){...s,held:false,returned:true}else s
 |OutsideJoin=>if(s.returned and not(s.held)and s.foreign==3){...s,joined:true}else s
 |Drain=>if(s.pending){...s,pending:false,fault:true}else s
 |Commit=>if(s.evidence and s.returned and s.joined and not(s.deadlock)){...s,fault:s.fault or s.pending,retired:not(s.fault or s.pending)}else s
 }}
 val allProps=all{not(s.joined)or all{s.returned,not(s.held),s.foreign==3},not(s.retired)or all{s.evidence,s.joined,not(s.pending),not(s.fault),not(s.deadlock)},not(s.accepted),s.launches==1,s.retries==0,s.controls==0}
 action step=nondet e=Set(Persist,HookStart,Activate,UnsafeHookJoin,HookReturn,OutsideJoin,Drain,Commit).oneOf();fire(e)
 action check(v:bool):bool=all{assert(v),s'=s}
 run originalInsideHookJoinDeadlockRetainedTest=init.then(fire(Persist)).then(fire(HookStart)).then(fire(Activate)).then(fire(UnsafeHookJoin)).then(fire(HookReturn)).then(fire(Commit)).then(check(s.deadlock and s.held and not(s.retired)))
 run hookRequiresDurablePreconditionEvidenceTest=init.then(fire(HookStart)).then(check(not(s.hook)and s.foreign==0))
 run hookReturnReleasesActivationLockBeforeJoinTest=init.then(fire(Persist)).then(fire(HookStart)).then(fire(Activate)).then(fire(OutsideJoin)).then(check(not(s.joined))).then(fire(HookReturn)).then(fire(Activate)).then(fire(OutsideJoin)).then(check(s.joined and not(s.held)))
 run actualQueueAdmittedAfterUnlockPreventsCommitTest=init.then(fire(Persist)).then(fire(HookStart)).then(fire(Activate)).then(fire(HookReturn)).then(fire(Activate)).then(fire(OutsideJoin)).then(fire(Commit)).then(check(s.fault and not(s.retired)))
 run ownerDrainAfterOutsideJoinRefusesNormalPastTest=init.then(fire(Persist)).then(fire(HookStart)).then(fire(HookReturn)).then(fire(Activate)).then(fire(OutsideJoin)).then(fire(Drain)).then(fire(Commit)).then(check(s.fault and not(s.retired)))
 run missingActualCollectorActivationCannotProveTest=init.then(fire(Persist)).then(fire(HookStart)).then(fire(HookReturn)).then(fire(OutsideJoin)).then(fire(Commit)).then(check(not(s.joined)and not(s.retired)and not(s.fault)))
 run noSecondHelperLaunchOrControlFromDiagnosticJoinTest=init.then(fire(Persist)).then(fire(HookStart)).then(fire(HookReturn)).then(fire(Activate)).then(fire(OutsideJoin)).then(fire(Commit)).then(check(s.launches==1 and s.retries==0 and s.controls==0 and not(s.accepted)))
}
