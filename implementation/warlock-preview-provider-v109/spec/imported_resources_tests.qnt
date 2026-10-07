module imported_resources_tests {
 import imported_resources.* from "./imported_resources"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run originalMappedReader=init.then(fire(OpenReader)).then(fire(Read)).then(check(s.reader and s.offset==1 and s.last==1 and s.bytes==4096))
 run dispatchDeniesReadBeforePoll=init.then(fire(OpenReader)).then(fire(Reconcile)).then(fire(Read)).then(check(s.last== -1 and s.producer and s.mapped and s.reader))
 run dispatchDeniesNewReader=init.then(fire(Reconcile)).then(fire(OpenReader)).then(check(s.last== -1 and not(s.reader) and s.mapped))
 run lockKeepsBackendAndMapping=init.then(fire(Reconcile)).then(fire(Lock)).then(fire(Poll)).then(check(s.producer and s.mapped and s.bytes==4096 and not(s.terminal)))
 run backendZeroKeepsReaderMapping=init.then(fire(OpenReader)).then(fire(Reconcile)).then(fire(Poll)).then(check(not(s.producer) and s.reader and s.mapped and s.bytes==4096 and not(s.terminal)))
 run readerCloseAloneIsNoProof=init.then(fire(OpenReader)).then(fire(Reconcile)).then(fire(Poll)).then(fire(CloseReader)).then(check(s.mapped and s.bytes==4096 and s.proofs==0 and not(s.terminal)))
 run finalPollClosesMapping=init.then(fire(OpenReader)).then(fire(Reconcile)).then(fire(Poll)).then(fire(CloseReader)).then(fire(Poll)).then(check(s.terminal and not(s.mapped) and s.proofs==2 and s.bytes==0))
 run lockedReaderCloseKeepsProducer=init.then(fire(OpenReader)).then(fire(Reconcile)).then(fire(Lock)).then(fire(CloseReader)).then(fire(Poll)).then(check(s.producer and s.mapped and not(s.reader) and not(s.terminal)))
 run unlockAndPollDrainsOriginal=init.then(fire(Reconcile)).then(fire(Lock)).then(fire(Poll)).then(fire(Unlock)).then(fire(Poll)).then(check(s.terminal and s.proofs==2 and not(s.producer)))
 run proofAckRemovesOnlyJob=init.then(fire(Reconcile)).then(fire(Poll)).then(fire(Ack)).then(fire(Close)).then(check(not(s.known) and s.last== -1 and s.captures==1 and s.transfers==1))
 run activeActorPreventsClose=init.then(fire(Reconcile)).then(fire(Poll)).then(fire(Close)).then(check(s.terminal and s.last== -1))
 run repeatedReconcileNeverCaptures=init.then(fire(Reconcile)).then(fire(Reconcile)).then(fire(Poll)).then(fire(Reconcile)).then(check(s.terminal and s.captures==1 and s.transfers==1))
 run ordinaryReaderCloseKeepsStorage=init.then(fire(OpenReader)).then(fire(Read)).then(fire(CloseReader)).then(fire(Poll)).then(fire(OpenReader)).then(check(s.reader and s.offset==0 and s.producer and s.mapped))
 run quarantinePersistsAfterProofAck=init.then(fire(Reconcile)).then(fire(Poll)).then(fire(Ack)).then(fire(OpenReader)).then(check(s.quarantined and s.last== -1 and not(s.reader)))
}
