module ReceiptLifecycle_test {
  import ReceiptLifecycle.* from "./receipt-lifecycle"
  run sameOutputCommitTest = init.then(beginOld).then(receive(1, 1, 1, Committed)).expect(s.currentStatus == Committed and not(s.oldPresent) and s.sends == 1)
  run outputChangedLateCommitTest = init.then(beginOld).then(changeOutput).expect(s.currentStatus == Unknown and s.oldStatus == Pending and s.oldIssued).then(receive(1, 1, 1, Committed)).expect(s.scene == 2 and s.currentStatus == Committed and not(s.oldPresent) and not(s.oldIssued) and s.sends == 1 and exactCurrentTerminalSettled)
  run brokenBaselineWitnessTest = init.then(beginOld).then(changeOutput).then(brokenReceiveOld).expect(s.scene == 2 and s.currentStatus == Unknown and not(s.oldPresent) and not(s.oldIssued) and not(exactCurrentTerminalSettled))
  run unrelatedNewCurrentTest = init.then(beginOld).then(changeOutput).then(beginNew).then(receive(1, 1, 1, Committed)).expect(s.current == 2 and s.currentStatus == Pending and s.newPresent and s.newStatus == Pending and s.newIssued and not(s.oldPresent) and s.sends == 2 and otherCurrentPreserved)
  run foreignBindingTest = init.then(beginOld).then(ignored(2, 1, 1)).expect(s.currentStatus == Pending and s.oldPresent and s.oldIssued and s.sends == 1)
  run foreignProtocolTest = init.then(beginOld).then(ignored(1, 2, 1)).expect(s.currentStatus == Pending and s.oldPresent and s.oldIssued and s.sends == 1)
  run foreignIntentTest = init.then(beginOld).then(ignored(1, 1, 3)).expect(s.currentStatus == Pending and s.oldPresent and s.oldIssued and s.sends == 1)
  run duplicateTest = init.then(beginOld).then(receive(1, 1, 1, Committed)).then(ignored(1, 1, 1)).expect(s.currentStatus == Committed and not(s.oldIssued) and s.sends == 1)
  run disconnectUnknownTest = init.then(beginOld).then(disconnect).expect(s.currentStatus == Unknown and s.oldStatus == Unknown and s.oldIssued and s.oldPresent and s.sends == 1)
  run unknownReceiptTest = init.then(beginOld).then(receive(1, 1, 1, Unknown)).expect(s.currentStatus == Unknown and s.oldStatus == Unknown and s.oldPresent and s.oldIssued and s.sends == 1)
  run validatedRecoveryReleaseTest = init.then(beginOld).then(changeOutput).then(recoverOld).expect(s.oldStatus == Unknown and s.oldPresent and s.oldIssued).then(releaseOld).expect(not(s.oldPresent) and not(s.oldIssued) and s.currentStatus == Unknown and s.scene == 2 and s.sends == 1)
  run refusalTest = init.then(beginOld).then(changeOutput).then(receive(1, 1, 1, Refused)).expect(s.currentStatus == Refused and not(s.oldPresent) and s.scene == 2 and s.sends == 1)
}
