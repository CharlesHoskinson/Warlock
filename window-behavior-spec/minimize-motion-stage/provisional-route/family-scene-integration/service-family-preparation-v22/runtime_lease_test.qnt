module runtime_lease_test {
 import runtime_lease.* from "./runtime_lease"
 action check(p:bool):bool=all{assert(p),s'=s}
 action ready=fire(Acquire).then(fire(Observe))
 run exactAcquiredObservedLeaseMayWriteTest=init.then(ready).then(fire(Write)).then(check(s.write and allProps))
 run replacedRuntimeRootRevokesWriteTest=init.then(ready).then(fire(RootChange)).then(fire(Observe)).then(fire(Write)).then(check(not(s.write)))
 run replacedLockInodeCannotListenTest=init.then(ready).then(fire(LockChange)).then(fire(Observe)).then(fire(Listen)).then(check(not(s.listening)))
 run changedOwnerNonceRevokesWriteTest=init.then(ready).then(fire(OwnerChange)).then(fire(Observe)).then(fire(Write)).then(check(not(s.write)))
 run unlockedDescriptorDoesNotOwnLedgerTest=init.then(ready).then(fire(Unlock)).then(fire(Observe)).then(fire(Write)).then(check(not(s.write)))
}
