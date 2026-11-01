module status_scroll_test {
 import status_scroll.* from "./status-scroll"
 run initialNoResetTest = init.then(frame(1,1)).expect(s.epoch == 1 and s.pending == Set() and safety)
 run sameStatusRetainsEpochTest = init.then(frame(1,1)).then(frame(2,1)).expect(s.epoch == 1 and s.pending == Set() and safety)
 run changedStatusResetTest = init.then(frame(1,1)).then(frame(2,2)).then(task(2)).expect(s.reset == 1 and s.resetEpoch == 2 and safety)
 run staleTaskCannotResetTest = init.then(frame(1,1)).then(frame(2,2)).then(frame(3,3)).then(task(2)).expect(s.reset == 0 and s.epoch == 3 and safety)
 run latestTaskResetsTest = init.then(frame(1,1)).then(frame(2,2)).then(frame(3,3)).then(task(2)).then(task(3)).expect(s.reset == 1 and s.resetEpoch == 3 and safety)
 run pendingTargetCannotBecomeControlTest = init.then(frame(1,1)).then(frame(2,2)).then(frameWithControl(3,3,2)).expect(s.pending.contains(2) and s.control == 0 and safety)
 run stalePublicationTest = init.then(frame(2,1)).expect(s.publication == 2 and s.epoch == 1).then(frame(1,2).fail())
 run fullCounterRetiresTest = init.then(frame(1,1)).then(frame(2,2)).then(frame(3,3)).then(frame(4,1)).then(task(3)).expect(s.epoch == 3 and s.exhausted and not(s.visible) and s.reset == 0 and safety)
 run invalidFrameRetiresSnapshotTest = init.then(frame(1,1)).then(frame(2,2)).then(invalid).then(task(2)).expect(s.epoch == 2 and not(s.visible) and s.reset == 0 and safety)
 run validStaleRetainsSnapshotTest = init.then(frame(1,1)).then(stale).expect(s.epoch == 1 and s.visible and s.pending == Set() and safety)
}
