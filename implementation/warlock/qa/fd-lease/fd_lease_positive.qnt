module fd_lease_positive {
 import fd_lease.* from "./fd_lease"
 run retiredAllocationCloseEnabledTest = init.then(retireRoot).then(closeOldRoot)
   .expect(not(s.root.open) and s.proc.open and not(s.visible) and safety)
}
