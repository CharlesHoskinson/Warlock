module staging_reservation_test {
 import staging_reservation.* from "./staging_reservation"
 action check(p:bool):bool=all{assert(p),s'=s}
 action full:bool={val claims=0.to(63).map(e=>{epoch:e,serial:e+1,material:7});s'={...initial,pending:claims,checked:claims,published:claims,serial:64}}
 run unrelatedCleanupReturnsWhileActualScanPendingTest=init.then(fire(Reserve(1))).then(fire(Read(original))).then(fire(Release(99))).then(check(s.cleanupReturned and s.scans.size()==1 and allProps))
 run exactStagingEpochReleaseRefusesTest=init.then(fire(Reserve(1))).then(fire(Read(original))).then(fire(Release(1))).then(check(s.releaseRefused and not(s.cleanupReturned) and allProps))
 run stagingEpochPreventsDisposeTest=init.then(fire(Reserve(1))).then(fire(Dispose)).then(check(s.releaseRefused and not(s.cleanupReturned) and allProps))
 run duplicateEpochCannotReserveTwiceTest=init.then(fire(Reserve(1))).then(fire(Reserve(1))).then(check(s.staging.size()==1 and s.serial==1 and allProps))
 run staleReservationCannotCommitForeignMaterialTest=init.then(fire(Reserve(1))).then(fire(Read(original))).then(fire(Material((original,true)))).then(fire(Commit(wrong))).then(check(s.pending.size()==0 and s.staging.contains(original) and allProps))
 run exactValidatedMaterialCommitsTest=init.then(fire(Reserve(1))).then(fire(Read(original))).then(fire(Material((original,true)))).then(fire(Commit(original))).then(check(s.pending.contains(original) and s.staging.size()==0 and allProps))
 run failedMaterialCannotPublishTest=init.then(fire(Reserve(1))).then(fire(Read(original))).then(fire(Material((original,false)))).then(fire(Commit(original))).then(fire(Abort(original))).then(check(s.pending.size()==0 and s.staging.size()==0 and allProps))
 run abortCannotFreeLiveScanMaterialTest=init.then(fire(Reserve(1))).then(fire(Read(original))).then(fire(Abort(original))).then(check(s.staging.contains(original) and allProps))
 run combined64CapacityRefusesNewStageTest=init.then(full).then(fire(Reserve(99))).then(check(s.staging.size()==0 and s.serial==64 and allProps))
 run helperCannotBeginBeforeAllStagesFinishTest=init.then(fire(Reserve(1))).then(fire(Read(original))).then(fire(BatchStart)).then(check(s.active.size()==0 and allProps))
 run unknownOwnedGroupKeepsExactEpochProtectedTest=init.then(fire(Reserve(1))).then(fire(Read(original))).then(fire(Material((original,true)))).then(fire(Commit(original))).then(fire(BatchStart)).then(fire(UnknownGroup)).then(fire(GroupClosed)).then(fire(Release(1))).then(check(s.quarantined and s.active.contains(original) and s.releaseRefused and allProps))
 run unknownGroupCannotAuthorizeAnotherStageTest=init.then(fire(Reserve(1))).then(fire(Read(original))).then(fire(Material((original,true)))).then(fire(Commit(original))).then(fire(BatchStart)).then(fire(UnknownGroup)).then(fire(Reserve(2))).then(check(s.staging.size()==0 and s.quarantined and allProps))
 run unrelatedOldEpochCleanupSurvivesQuarantineTest=init.then(fire(Reserve(1))).then(fire(Read(original))).then(fire(Material((original,true)))).then(fire(Commit(original))).then(fire(BatchStart)).then(fire(UnknownGroup)).then(fire(Release(99))).then(check(s.cleanupReturned and s.quarantined and s.active.contains(original) and allProps))
 run oldReadHoldingLifecycleReproducesActualCounterexampleTest=init.then(fire(Reserve(1))).then(fire(OldLockedRead(original))).then(fire(Release(99))).then(check(s.cleanupWaiting and not(s.cleanupReturned) and not(allProps)))
 run replacedReservationCannotBorrowValidatedMaterialTest=init.then(fire(Reserve(1))).then(fire(Read(original))).then(fire(ReplaceReservation(wrong))).then(fire(Material((original,true)))).then(fire(Commit(original))).then(fire(Release(1))).then(check(s.quarantined and s.active.contains(original) and s.pending.size()==0 and s.staging.contains(wrong) and s.releaseRefused and allProps))
 run staleReservationCannotAuthorizeNormalDisposeTest=init.then(fire(Reserve(1))).then(fire(Read(original))).then(fire(ReplaceReservation(wrong))).then(fire(Material((original,true)))).then(fire(Commit(original))).then(fire(Dispose)).then(check(s.quarantined and s.releaseRefused and not(s.cleanupReturned) and allProps))
}
