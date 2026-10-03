module thread_callback {
 type State={lease:int,accepted:bool,kernel:bool,fault:bool,pending:Set[int],ownerWrites:int,foreignRegistryWrites:int,nativeWrites:int,joined:bool}
 var s:State
 action init=s'={lease:1,accepted:true,kernel:true,fault:false,pending:Set(),ownerWrites:0,foreignRegistryWrites:0,nativeWrites:0,joined:true}
 pure def drain(a:State):State=if(a.pending.contains(a.lease)){...a,pending:Set(),accepted:false,kernel:false,fault:true,ownerWrites:a.ownerWrites+1}else {...a,pending:Set()}
 type Event=WrongThread(int)|OwnerDrain|OwnerQuery|OwnerCommit|ReplaceLease|WorkerJoined|Overflow
 action fire(e:Event):bool={s'=match e {
 |WrongThread(n)=>{...s,pending:s.pending.union(Set(n))}
 |OwnerDrain=>drain(s)
 |OwnerQuery=>drain(s)
 |OwnerCommit=>drain(s)
 |ReplaceLease=>{...drain(s),lease:s.lease+1,accepted:false,kernel:false}
 |WorkerJoined=>{...s,joined:true}
 |Overflow=>{...s,fault:true,accepted:false,kernel:false}
 }}
 val allProps=all{not(s.accepted)or all{s.kernel,not(s.fault)},s.foreignRegistryWrites==0,s.nativeWrites==0}
 action step=nondet e=Set(WrongThread(s.lease),WrongThread(0),OwnerDrain,OwnerQuery,OwnerCommit,ReplaceLease,WorkerJoined,Overflow).oneOf();fire(e)
 action check(v:bool):bool=all{assert(v),s'=s}
 run actualCurrentWrongThreadContainedFaultTest=init.then(fire(WrongThread(1))).then(fire(OwnerDrain)).then(check(s.fault and not(s.accepted)and not(s.kernel)))
 run queryBeforeQueuedDeliveryMustDrainTest=init.then(fire(WrongThread(1))).then(fire(OwnerQuery)).then(check(not(s.accepted)and s.pending==Set()))
 run commitBeforeQueuedDeliveryMustDrainTest=init.then(fire(WrongThread(1))).then(fire(OwnerCommit)).then(check(not(s.kernel)))
 run oldWrongThreadCallbackPreservesCurrentRecordTest=init.then(fire(WrongThread(0))).then(fire(OwnerDrain)).then(check(s.accepted and s.kernel and not(s.fault)and s.ownerWrites==0 and s.lease==1))
 run oldWrongThreadQueryIsInertTest=init.then(fire(WrongThread(0))).then(fire(OwnerQuery)).then(check(s.accepted and s.ownerWrites==0))
 run mixedCurrentAndOldFaultMatchesCurrentTest=init.then(fire(WrongThread(0))).then(fire(WrongThread(1))).then(fire(OwnerDrain)).then(check(s.fault and s.ownerWrites==1))
 run oldFaultCannotPoisonReplacedLeaseTest=init.then(fire(ReplaceLease)).then(fire(WrongThread(1))).then(fire(OwnerDrain)).then(check(s.lease==2 and not(s.fault)and s.ownerWrites==0))
 run currentFaultPreservesNormalJobAccountingTest=init.then(fire(WrongThread(1))).then(fire(OwnerDrain)).then(fire(WorkerJoined)).then(check(s.joined and not(s.accepted)))
 run oldFaultPreservesNormalJobAccountingTest=init.then(fire(WrongThread(0))).then(fire(OwnerDrain)).then(check(s.joined and s.accepted))
 run repeatedCurrentFaultNeverRestoresTest=init.then(fire(WrongThread(1))).then(fire(OwnerDrain)).then(fire(WrongThread(1))).then(fire(OwnerQuery)).then(check(s.fault and not(s.accepted)))
 run overflowRefusesUnknownDroppedAuthorityTest=init.then(fire(Overflow)).then(check(not(s.accepted)and s.fault))
 run currentWrongThreadImmediatelyBeforeRearmMustDrainTest=init.then(fire(WrongThread(1))).then(fire(ReplaceLease)).then(check(s.lease==2 and s.fault and s.ownerWrites==1 and not(s.kernel)and not(s.accepted)and s.pending==Set()))
}
