module fd_lease_test {
  import fd_lease.* from "./fd_lease"
  run borrowRetireUseCloseTest = init.then(borrowA).then(retireRoot).then(closeRetiredOriginal).then(useA).then(closeA).expect(s.used and not(s.visible) and not(s.aRoot.open) and safety)
  run concurrentBorrowRetireTest = init.then(borrowA).then(borrowB).then(retireRoot).then(closeRetiredOriginal).then(useA).then(closeA).expect(s.bRoot.open and s.bProc.open and safety).then(closeB).expect(safety)
  run failedDupNoLeakTest = init.then(borrowFail).expect(not(s.aRoot.open) and s.visible and safety).then(borrowA).expect(s.aRoot.open and safety)
  run deferredCancelClosesObserverTest = init.then(borrowA).then(probeRegular).then(maskedObserverHandoff).then(cancelObserver).expect(not(s.observer.open) and s.interrupted=="afterInstall" and safety)
  run procInodePositiveTest = init.then(borrowA).then(probeRegular).then(maskedObserverHandoff).then(observe).expect(s.used and s.observer.inode==s.probe.inode and safety)
  run reusedNumberRejectsStaleOwnerTest = init.then(retireRoot).then(closeRetiredOriginal).then(reuseRootSlot).then(rejectStaleClose).expect(s.root.slot==1 and s.root.epoch==2 and s.root.owner=="foreign" and s.staleRejected and safety)
  run staleEpochCannotCloseReusedSlotTest = init.then(retireRoot).then(closeRetiredOriginal).then(reuseRootSlot).then(closeOldRoot.fail())
  run interruptBeforeInvalidationTest = init.then(interruptBeforeRetire).then(retireRoot).then(closeRetiredOriginal).expect(not(s.visible) and not(s.root.open) and s.interrupted=="beforeInvalidate" and safety)
  run interruptAfterInvalidationTest = init.then(retireRoot).then(interruptAfterRetire).then(closeRetiredOriginal).expect(not(s.visible) and not(s.proc.open) and s.interrupted=="afterInvalidate" and safety)
  run retiredRootCannotBorrowTest = init.then(retireRoot).then(borrowA.fail())
  run closedLeaseCannotUseTest = init.then(borrowA).then(closeA).then(useA.fail())
  run doubleCloseRefusedTest = init.then(borrowA).then(closeA).then(closeA.fail())
  run brokenLongGateCounterexampleTest = init.then(brokenEnterLongGate).then(brokenOuterClose).expect(not(rootValidity) and not(finiteGate))
  run brokenUnmaskedHandoffCounterexampleTest = init.then(borrowA).then(probeRegular).then(brokenUnmaskedHandoff).expect(not(observerOwned) and not(noLeakOrWrongClose))
}
