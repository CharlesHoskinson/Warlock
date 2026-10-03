module bootstrap_lifecycle_test {
 import bootstrap_lifecycle.* from "./bootstrap_lifecycle"
 action check(v:bool):bool=all{assert(v),s'=s}
 action constructed=init.then(fire(Create))
 action acked=constructed.then(fire(FlushSuccess)).then(fire(ParentConfigure)).then(fire(SurfaceAck))
 run originalPassiveReadableOnlyBootstrapDeadlockTest=constructed.then(check(s.queued and not(s.sent))).then(fire(ParentConfigure)).then(fire(Announce)).then(check(not(s.announced)))
 run explicitInitialFlushParentConfigureAckThenPublishTest=acked.then(fire(Announce)).then(check(s.announced and not(s.queued)))
 run actualEagainMustRefuseStartupTest=constructed.then(fire(FlushNegative)).then(fire(ParentConfigure)).then(fire(SurfaceAck)).then(fire(Announce)).then(check(s.failed and not(s.announced)))
 run actualEpipeMustRefuseStartupTest=constructed.then(fire(FlushNegative)).then(fire(Incidental)).then(check(s.failed and not(s.sent)))
 run unknownFlushErrorNeverGrantsOutputTest=constructed.then(fire(FlushNegative)).then(fire(FlushSuccess)).then(check(not(s.sent)))
 run configureCannotPublishWithoutSurfaceAckTest=constructed.then(fire(FlushSuccess)).then(fire(ParentConfigure)).then(fire(Announce)).then(check(not(s.announced)))
 run ackCannotPrecedeConfigureTest=constructed.then(fire(FlushSuccess)).then(fire(SurfaceAck)).then(fire(Announce)).then(check(not(s.acked) and not(s.announced)))
 run parentLostBeforeFlushBlocksPublicationTest=constructed.then(fire(ParentLost)).then(fire(FlushSuccess)).then(check(not(s.sent)))
 run parentLostAfterAckBlocksQueuedPublicationTest=acked.then(fire(ParentLost)).then(fire(Announce)).then(check(not(s.announced)))
 run incidentalParentTrafficCanMaskOriginalGapTest=constructed.then(fire(Incidental)).then(fire(ParentConfigure)).then(fire(SurfaceAck)).then(fire(Announce)).then(check(s.announced))
 run repeatedFlushNeverAnnouncesByItselfTest=constructed.then(fire(FlushSuccess)).then(fire(FlushSuccess)).then(check(not(s.announced)))
 run wrongOwnerNeverGrantsPublicationTest=constructed.then(fire(WrongOwner)).then(fire(FlushSuccess)).then(fire(ParentConfigure)).then(fire(SurfaceAck)).then(fire(Announce)).then(check(not(s.announced)))
}
