module batch_preview_lock_test {
 import batch_preview_lock.* from "./batch_preview_lock"
 action check(p:bool):bool=all{assert(p),s'=s}
 run cleanupCannotWaitForCaptureTest=init.then(fire(Prepare)).then(fire(Cleanup)).then(check(s.cleanupDone and not(s.cleanupWaiting)))
 run receiptHeldCleanupCannotDeadlockHelperTest=init.then(fire(Prepare)).then(fire(Cleanup)).then(fire(HelperPublish)).then(check(s.helperWaiting and not(s.cleanupWaiting) and allProps))
 run releasingReceiptUnblocksHelperTest=init.then(fire(Prepare)).then(fire(Cleanup)).then(fire(HelperPublish)).then(fire(ReleaseReceipt)).then(check(not(s.helperWaiting) and allProps))
 run oldCompletedLeaseCleanupIndependentTest=init.then(fire(Cleanup)).then(fire(Prepare)).then(fire(HelperPublish)).then(check(s.cleanupDone and allProps))
}
