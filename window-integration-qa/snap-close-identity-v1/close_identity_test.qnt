module close_identity_test {
 import close_identity.* from "./close_identity"
 run delayedOldCloseKeepsNewRecordTest=init.then(fire(QueueClose({epoch:1,pid:10}))).then(fire(Record)).then(fire(RunClose))
  .then(all{assert(stored and record.epoch==2 and staleClosePreservesNewRecord),fire(Sync)})
 run exactOldLifetimeCloseDeletesRecordTest=init.then(fire(QueueClose({epoch:1,pid:10}))).then(fire(RunClose))
  .then(all{assert(not(stored) and staleClosePreservesNewRecord),fire(Sync)})
 run ordinaryUserUnsnapStillRemovesCurrentTest=init.then(fire(Record)).then(fire(UserUnsnap))
  .then(all{assert(not(stored) and record.epoch==2 and staleClosePreservesNewRecord),fire(Sync)})
}
