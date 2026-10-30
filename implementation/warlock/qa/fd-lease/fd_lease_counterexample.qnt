module fd_lease_counterexample {
 import fd_lease.* from "./fd_lease"
 run brokenIntegerCloseDetectedTest = init.then(retireRoot).then(closeRetiredOriginal)
   .then(reuseRootSlot).then(brokenStaleIntegerClose)
   .expect(s.wrongClose and not(noLeakOrWrongClose) and not(s.root.open))
}
