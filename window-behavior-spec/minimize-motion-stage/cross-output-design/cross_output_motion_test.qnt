module cross_output_motion_test {
 import cross_output_motion.* from "./cross_output_motion"
 action capture1=fire(Capture({identity:1,epoch:1,complete:true,pixels:107}))
 action readyBoth1=fire(Ready({identity:1,epoch:1,output:0})).then(fire(Ready({identity:1,epoch:1,output:1}))).then(fire(Destination({identity:1,epoch:1})))
 action start1=fire(Start({identity:1,epoch:1}))
 run allOutputsPresentBeforeHideTest=init.then(capture1).then(fire(Ready({identity:1,epoch:1,output:0}))).then(start1).then(all{assert(s.stale and not(s.minimized) and allProps),readyBoth1}).then(start1)
 run spanningCoverageSharesClockTest=init.then(capture1).then(readyBoth1).then(start1).then(fire(Tick)).then(all{assert(leftW>0 and rightW>0 and allProps),fire(Tick)})
 run reversalKeepsCurrentGlobalRectangleTest=init.then(capture1).then(readyBoth1).then(start1).then(fire(Tick)).then(fire(Reverse)).then(all{assert(s.fromX==s.x and s.fromW==s.w and s.atlasPixels==107 and allProps),fire(Finish({identity:1,epoch:1}))})
 run outputRemovalSettlesLatestIdentityTest=init.then(fire(Reverse)).then(fire(RemoveOutput(1))).then(all{assert(not(s.minimized) and s.phase=="idle" and allProps),fire(Finish({identity:1,epoch:1}))})
 run incompleteMonitorCropsCannotAnimateTest=init.then(fire(Capture({identity:1,epoch:1,complete:false,pixels:107}))).then(readyBoth1).then(start1).then(all{assert(s.phase=="fallback" and not(s.minimized) and allProps),fire(Tick)})
 run reusedIdentityCannotCommitTest=init.then(capture1).then(fire(Close)).then(fire(Reuse)).then(fire(Finish({identity:1,epoch:1}))).then(all{assert(not(s.minimized) and s.stale and s.atlasIdentity==0 and not(s.completeAtlas) and allProps),fire(Tick)})
 run oldCaptureCannotPopulateReusedIdentityTest=init.then(fire(Close)).then(fire(Reuse)).then(fire(Reverse)).then(fire(Capture({identity:1,epoch:1,complete:true,pixels:107}))).then(all{assert(s.stale and s.atlasIdentity==0 and s.nativePixels==207 and allProps),fire(Tick)})
 run staleEpochCaptureCannotReplaceCurrentPixelsTest=init.then(capture1).then(fire(Reverse)).then(fire(Capture({identity:1,epoch:1,complete:true,pixels:107}))).then(all{assert(s.stale and not(s.completeAtlas) and s.atlasPixels==107 and allProps),fire(Tick)})
 run wrongPixelsCannotClaimCurrentIdentityTest=init.then(fire(Capture({identity:1,epoch:1,complete:true,pixels:207}))).then(all{assert(s.stale and s.atlasIdentity==0 and allProps),fire(Tick)})
 run missingDestinationCannotHideTest=init.then(capture1).then(fire(Ready({identity:1,epoch:1,output:0}))).then(fire(Ready({identity:1,epoch:1,output:1}))).then(start1).then(all{assert(s.stale and not(s.minimized) and allProps),fire(Tick)})
 run removedReaddedOutputNeedsNewHandshakeTest=init.then(capture1).then(readyBoth1).then(fire(RemoveOutput(1))).then(fire(AddOutput(1))).then(fire(Reverse)).then(fire(Capture({identity:1,epoch:3,complete:true,pixels:107}))).then(fire(Ready({identity:1,epoch:1,output:1}))).then(fire(Start({identity:1,epoch:3}))).then(all{assert(s.stale and s.ready==Set() and s.phase=="loading" and allProps),fire(Tick)})
}
