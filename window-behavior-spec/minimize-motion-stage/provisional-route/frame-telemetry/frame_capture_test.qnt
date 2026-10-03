module frame_capture_test {
 import frame_capture.* from "./frame_capture"
 run swapKeepsSynchronizedRectangleTest=init.then(fire(Sync(1))).then(fire(Move)).then(fire(Swap(1))).then(all{assert(s.records.nth(0).x==0 and s.x==1 and allProps),fire(Move)})
 run reversalDoesNotRelabelPriorFrameTest=init.then(fire(Sync(1))).then(fire(Reverse)).then(fire(Swap(1))).then(all{assert(s.records.nth(0).token==1 and s.token==2 and allProps),fire(Move)})
 run retiredWindowCannotReportNewFrameTest=init.then(fire(Sync(1))).then(fire(Replace)).then(fire(Swap(1))).then(all{assert(s.stale and s.records.length()==0 and allProps),fire(Move)})
 run duplicateSwapCannotRecordTwiceTest=init.then(fire(Sync(1))).then(fire(Swap(1))).then(fire(Swap(1))).then(all{assert(s.stale and s.records.length()==1 and allProps),fire(Move)})
 run newWindowSynchronizationGetsFreshGenerationTest=init.then(fire(Sync(1))).then(fire(Replace)).then(fire(Sync(2))).then(fire(Swap(1))).then(fire(Swap(2))).then(all{assert(s.records.nth(0).generation==2 and s.records.nth(0).sequence==2 and allProps),fire(Move)})
 run oldWindowSyncDoesNotDiscardCurrentFrameTest=init.then(fire(Replace)).then(fire(Sync(2))).then(fire(Sync(1))).then(fire(Swap(2))).then(all{assert(s.records.nth(0).generation==2 and allProps),fire(Move)})
}
