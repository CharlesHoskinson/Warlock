module source_tests {
 import source.* from "./source"
 action check(ok:bool):bool=all {assert(ok and safety),s'=s}
 run reservedFailureClearsChargeTest=init.then(fire(Admit)).then(fire(Refuse)).then(check(s.phase==3 and s.bytes==0 and s.proof==List(1)))
 run physicalBufferCannotRefuseTest=init.then(fire(Admit)).then(fire(Allocate)).then(fire(Refuse)).then(check(s.phase==2 and s.physical==1 and s.bytes==1 and s.proof==List()))
 run cancellationRaceBothProofsTest=init.then(fire(Admit)).then(fire(Cancel)).then(fire(Refuse)).then(check(s.proof==List(1,2) and s.bytes==0))
 run duplicateRefusalStableIdentityTest=init.then(fire(Admit)).then(fire(Refuse)).then(fire(Refuse)).then(check(s.proof==List(1) and s.seq==2))
 run receiptExhaustionRetainsOwnershipTest=init.then(fire(Admit)).then(exhaust).then(fire(Refuse)).then(check(s.phase==1 and s.bytes==1 and s.proof==List()))
 run lateAllocationCannotPublishTest=init.then(fire(Admit)).then(fire(Refuse)).then(fire(Allocate)).then(check(s.phase==3 and s.physical==0 and s.bytes==0))
 run originalDeadlinePreservedTest=init.then(fire(Admit)).then(fire(Tick)).then(fire(Tick)).then(fire(Refuse)).then(check(s.deadline==3 and s.now==3 and s.phase==3 and s.bytes==0))
}
