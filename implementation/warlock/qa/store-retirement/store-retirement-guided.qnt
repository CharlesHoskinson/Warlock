// Positive reachability sampler: restrict choices to existing actions only.
// No new state assignments, resets, close receipts or weakened invariants.
// The separate uniform campaign and its zero two-close witness stay retained.
module store_retirement_guided {
  import store_retirement.* from "./store-retirement"
  action twoNestedSuccessStep = any {
    all {s.gate==Free, s.r1.phase==Absent, begin},
    all {s.gate==Busy, s.r1.phase==Absent, register(1)},
    all {s.gate==Busy, s.r1.phase==Acquiring, not(s.r1.possibleOwned), acquireRaw(1)},
    all {s.gate==Busy, s.r1.phase==Acquiring, s.r1.possibleOwned, not(s.r1.retained), retainValue(1)},
    all {s.gate==Busy, s.r1.phase==Acquiring, s.r1.retained, markOpen(1)},
    all {s.gate==Busy, s.r1.phase==Open, s.r2.phase==Absent, register(2)},
    all {s.gate==Busy, s.r2.phase==Acquiring, not(s.r2.possibleOwned), acquireRaw(2)},
    all {s.gate==Busy, s.r2.phase==Acquiring, s.r2.possibleOwned, not(s.r2.retained), retainValue(2)},
    all {s.gate==Busy, s.r2.phase==Acquiring, s.r2.retained, markOpen(2)},
    all {s.gate==Busy, s.r1.phase==Open, s.r2.phase==Open, closeBegin(2)},
    all {s.gate==Busy, s.r2.phase==Closing, closeSuccess(2)},
    all {s.gate==Busy, s.r1.phase==Open, s.r2.phase==Closed, closeBegin(1)},
    all {s.gate==Busy, s.r1.phase==Closing, s.r2.phase==Closed, closeSuccess(1)},
    all {s.gate==Busy, s.r1.phase==Closed, s.r2.phase==Closed, endRun},
    all {s.gate==Free, s.r1.phase==Closed, s.r2.phase==Closed, sealScan},
    all {s.gate==Sealed, sealScan}
  }
}
