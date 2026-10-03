module provisional_motion_test {
 import provisional_motion.* from "./provisional_motion"
 run pendingValidationKeepsPixelsMovingWithoutNativeCommitTest=init.then(fire(Request)).then(fire(Tick)).then(all{assert(s.x==4 and s.nativeMin and s.phase=="provisional" and allProps),fire(Tick)})
 run speculativeEndpointCannotRestoreNativeTest=init.then(fire(Request)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(End({identity:1,epoch:2}))).then(all{assert(s.x==0 and s.nativeMin and s.unauthorizedEnd and allProps),fire(Tick)})
 run promotionPreservesCurrentRectangleTest=init.then(fire(Request)).then(fire(Tick)).then(fire(Validate({identity:1,epoch:2}))).then(all{assert(s.x==4 and s.promotedEvent and s.accepted==false and s.nativeMin and allProps),fire(Tick)})
 run rapidThirdIntentUsesCurrentPixelsTest=init.then(fire(Request)).then(fire(Tick)).then(fire(Request)).then(fire(Tick)).then(all{assert(s.x==5 and s.from==4 and s.pixels==107 and s.phase=="provisional" and allProps),fire(Tick)})
 run staleValidationCannotPromoteNewerIntentTest=init.then(fire(Request)).then(fire(Request)).then(fire(Validate({identity:1,epoch:2}))).then(all{assert(s.stale and not(s.validated) and s.phase=="provisional" and allProps),fire(Tick)})
 run rejectionRollsPixelsTowardPreviouslyAcceptedEndpointTest=init.then(fire(Request)).then(fire(Tick)).then(fire(Reject({identity:1,epoch:2}))).then(fire(Tick)).then(all{assert(s.x==5 and s.to==10 and s.accepted and s.nativeMin and allProps),fire(Tick)})
 run reusedIdentityRejectsOldTimeoutAuthorityTest=init.then(fire(Request)).then(fire(Reuse)).then(fire(Timeout({identity:1,epoch:2}))).then(all{assert(s.stale and not(s.nativeMin) and s.pixelsIdentity==0 and allProps),fire(Tick)})
 run reductionDuringUnvalidatedRequestSettlesPriorAcceptedIntentTest=init.then(fire(Request)).then(fire(Reduce({identity:1,epoch:2}))).then(all{assert(s.nativeMin and s.accepted and s.phase=="idle" and allProps),fire(End({identity:1,epoch:2}))})
}
