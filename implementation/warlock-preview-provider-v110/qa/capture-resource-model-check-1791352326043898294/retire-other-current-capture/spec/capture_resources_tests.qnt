module capture_resources_tests {
 import capture_resources.* from "./capture_resources"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run liveExportBlocksProducer=init.then(fire(Retire)).then(check(s.producer and s.exported and s.status==2))
 run lockPreservesOriginalProducer=init.then(fire(Lock)).then(fire(Release)).then(fire(Retire)).then(check(s.producer and not(s.exported) and s.status==3))
 run originalExportReleaseUnderLock=init.then(fire(Lock)).then(fire(Release)).then(check(s.producer and not(s.exported) and s.seenProducer==4096))
 run lostReleaseAcknowledgmentRetainsUnknown=init.then(fire(LostRelease)).then(check(s.unknown and s.seenExport and not(s.exported) and s.cursor==0))
 run freshObservationRepairsLostRelease=init.then(fire(LostRelease)).then(fire(Observe)).then(check(not(s.unknown) and not(s.seenExport) and s.seenProducer==4096))
 run releaseRetryIsIdempotent=init.then(fire(LostRelease)).then(fire(Release)).then(check(not(s.unknown) and not(s.exported) and s.sequence==2))
 run lostProducerAcknowledgmentRetainsUnknown=init.then(fire(Release)).then(fire(LostRetire)).then(check(s.unknown and s.seenProducer==4096 and not(s.producer)))
 run freshObservationRepairsLostProducer=init.then(fire(Release)).then(fire(LostRetire)).then(fire(Observe)).then(check(not(s.unknown) and s.seenProducer==0))
 run failedResponseAllocationPreservesResources=init.then(fire(FailPrepare)).then(check(s.producer and s.exported and s.sequence==0 and s.last== -1))
 run wrongTransferCannotReleaseLiveExport=init.then(fire(BadTransfer)).then(check(s.producer and s.exported and s.sequence==0 and s.last== -1))
 run wrongSubjectCannotRetireProducer=init.then(fire(BadSubject)).then(check(s.producer and s.exported and s.sequence==0 and s.last== -1))
 run malformedReplyCannotAdvanceCursor=init.then(fire(Observe)).then(fire(BadReply)).then(check(s.sequence==2 and s.cursor==1 and s.unknown))
 run oldTargetCannotEraseOtherCapture=init.then(fire(Release)).then(fire(Retire)).then(fire(OtherCapture)).then(fire(Release)).then(fire(Retire)).then(fire(Observe)).then(check(s.other and not(s.producer) and s.seenProducer==0))
 run frontendConfirmationIsNoResourceProof=init.then(fire(LostRelease)).then(fire(Confirm)).then(check(s.unknown and s.producer and s.seenExport))
}
