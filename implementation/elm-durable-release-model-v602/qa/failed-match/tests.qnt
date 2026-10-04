module tests {
 import release.* from "./release"
 run normalReleaseTest = init.then(establish).then(prepare).then(finish).then(fire(Ack)).then(fire(Explicit(2))).then(all {assert(s.effect and s.ack and not(reserved(s)) and allProps),fire(Crash)})
 run preparedCrashStaysBlockedTest = init.then(establish).then(prepare).then(fire(Crash)).then(fire(Ack)).then(fire(Explicit(2))).then(all {assert(reserved(s) and not(s.ack) and not(s.effect) and allProps),finish}).then(fire(Ack)).then(all {assert(s.ack and allProps),fire(Explicit(2))})
 run unlinkBeforePrepareRefusedTest = init.then(fire(Unlink)).then(all {assert(s.file and allProps),fire(Crash)})
 run ackBeforeFinalSyncRefusedTest = init.then(establish).then(prepare).then(fire(Unlink)).then(fire(SyncUnlinkDir)).then(fire(WriteReleased)).then(fire(Ack)).then(all {assert(not(s.ack) and reserved(s) and allProps),fire(SyncReleased)})
 run unlinkCrashRestoresExactReservationTest = init.then(establish).then(prepare).then(fire(Unlink)).then(fire(Crash)).then(all {assert(s.file and s.durableFile and reserved(s) and allProps),finish})
 run durableUnlinkCrashStillBlockedTest = init.then(establish).then(prepare).then(fire(Unlink)).then(fire(SyncUnlinkDir)).then(fire(Crash)).then(fire(Ack)).then(all {assert(not(s.file) and reserved(s) and not(s.ack) and allProps),fire(WriteReleased)})
 run releasedCrashNeverResurrectsTest = init.then(establish).then(prepare).then(finish).then(fire(Crash)).then(fire(RecreateOld)).then(all {assert(not(s.file) and not(s.durableFile) and allProps),fire(Ack)})
 run historyUnknownNotCommitTest = init.then(establish).then(prepare).then(finish).then(fire(Ack)).then(fire(Explicit(1))).then(all {assert(s.history.contains(1) and not(s.committed) and not(s.effect) and allProps),fire(Crash)})
 run registeredProofRefusedTest = init.then(fire(Proof(0,1,1,1))).then(fire(RequestReads)).then(all {assert(not(s.proof) and not(s.reads) and allProps),fire(Crash)})
 run foreignProofRefusedTest = init.then(fire(NativeRetire)).then(fire(Proof(1,2,1,1))).then(all {assert(not(s.proof) and allProps),fire(Crash)})
 run staleProofRefusedTest = init.then(fire(NativeRetire)).then(fire(Proof(1,1,0,1))).then(fire(Proof(1,1,1,0))).then(all {assert(not(s.proof) and allProps),fire(Crash)})
 run futureProofRefusedTest = init.then(fire(NativeRetire)).then(fire(Proof(1,1,1,3))).then(all {assert(not(s.proof) and allProps),fire(Crash)})
 run oneReadCannotPrepareTest = init.then(fire(NativeRetire)).then(fire(Proof(1,1,1,1))).then(fire(RequestReads)).then(fire(Observe(1,11,1,2))).then(fire(WriteProof)).then(all {assert(not(s.proofWritten) and allProps),fire(Crash)})
 run crossedRequestsRefusedTest = init.then(fire(NativeRetire)).then(fire(Proof(1,1,1,1))).then(fire(RequestReads)).then(fire(Observe(1,12,1,2))).then(fire(Observe(2,11,1,2))).then(all {assert(not(s.actionRead) and not(s.geometry) and allProps),fire(Crash)})
 run staleObservationRefusedTest = init.then(fire(NativeRetire)).then(fire(Proof(1,1,1,1))).then(fire(RequestReads)).then(fire(Observe(2,12,1,1))).then(all {assert(not(s.geometry) and allProps),fire(Crash)})
 run historyFullBlocksNewTest = init.then(establish).then(prepare).then(finish).then(fire(Ack)).then(fire(Remember(2))).then(fire(Explicit(2))).then(all {assert(not(s.effect) and s.history.size()==2 and allProps),fire(Crash)})
}
