module actor_service_binding_test {
  import actor_service_binding.* from "./actor_service_binding"
  action check(p:bool):bool=all{assert(p),s'=s}
  action launched=init.then(fire(Register(true))).then(fire(Release))
  action semantic=launched.then(fire(ActualReturn(true)))
    .then(fire(Semantic({exact:true,durable:true}))).then(fire(KeeperAck(true)))
    .then(fire(ServicePublication(true)))
  run groupGoneAndZeroExitCannotReplaceSemanticCallerTest=launched
    .then(fire(ActualReturn(true))).then(fire(PhysicalGone)).then(fire(Close))
    .then(check(not(s.closed)))
  run unreturnedNativeCallRemainsQuarantinedTest=launched.then(fire(PhysicalGone))
    .then(fire(Semantic({exact:true,durable:true}))).then(fire(KeeperAck(true)))
    .then(fire(Close)).then(check(not(s.closed)))
  run exactSemanticAndPhysicalClosureFullInverseTest=semantic
    .then(fire(PhysicalGone)).then(fire(Close)).then(check(s.closed and allProps))
  run physicalClosureMayPrecedeGuardedSemanticResultTest=launched
    .then(fire(ActualReturn(true))).then(fire(PhysicalGone))
    .then(fire(Semantic({exact:true,durable:true}))).then(fire(KeeperAck(true)))
    .then(fire(ServicePublication(true))).then(fire(Close)).then(check(s.closed))
  run undurableRegistrationNeverReleasesTest=init.then(fire(Register(false)))
    .then(fire(Release)).then(check(s.fault and not(s.released)))
  run nativeFailureCannotBecomeSuccessfulReturnTest=launched
    .then(fire(ActualReturn(false))).then(fire(ActualReturn(true)))
    .then(fire(Semantic({exact:true,durable:true}))).then(fire(Close))
    .then(check(s.fault and not(s.closed)))
  run wrongCallerSourceLifetimeReceiptOrScopeRefusedTest=launched
    .then(fire(ActualReturn(true))).then(fire(Semantic({exact:false,durable:true})))
    .then(fire(KeeperAck(true))).then(check(not(s.acknowledged)))
  run semanticJournalFsyncFailureCannotCloseTest=launched
    .then(fire(ActualReturn(true))).then(fire(Semantic({exact:true,durable:false})))
    .then(fire(KeeperAck(true))).then(fire(PhysicalGone)).then(fire(Close))
    .then(check(s.fault and not(s.closed)))
  run unauthenticatedKeeperAckCannotCloseTest=launched.then(fire(ActualReturn(true)))
    .then(fire(Semantic({exact:true,durable:true}))).then(fire(KeeperAck(false)))
    .then(fire(PhysicalGone)).then(fire(Close)).then(check(not(s.closed)))
  run keeperAckCannotReplaceServicePublicationTest=launched
    .then(fire(ActualReturn(true))).then(fire(Semantic({exact:true,durable:true})))
    .then(fire(KeeperAck(true))).then(fire(PhysicalGone)).then(fire(Close))
    .then(check(not(s.closed)))
  run failedActorRecordPublicationRefusesNormalClosureTest=semantic
    .then(fire(ServicePublication(false))).then(fire(PhysicalGone)).then(fire(Close))
    .then(check(s.fault and not(s.closed)))
  run sourceReplacementRevokesPartialCompletionTest=semantic.then(fire(Replace))
    .then(fire(PhysicalGone)).then(fire(Close)).then(check(not(s.closed)))
}
