module freeze_contract_test {
 import freeze_contract.* from "./freeze_contract"
 run freezeBeforeSlowPreparationTest=init.then(fire(Reserve(1))).then(fire(Tick)).then(fire(Tick)).then(all{assert(s.rect==37 and s.held and allProps),fire(Validate(2))}).then(fire(Begin(2))).then(all{assert(s.from==37 and allProps),fire(Ready(2))})
 run staleReadyCannotHideAfterReservationTest=init.then(fire(Reserve(1))).then(fire(Ready(1))).then(all{assert(s.stale and s.held and allProps),fire(Validate(2))})
 run latestReservationRetainsRectangleTest=init.then(fire(Reserve(1))).then(fire(Reserve(1))).then(fire(Begin(2))).then(all{assert(s.stale and s.held and s.rect==37 and allProps),fire(Validate(3))}).then(fire(Begin(3)))
 run staleIdentityCannotFreezeTest=init.then(fire(Reserve(2))).then(all{assert(s.stale and not(s.held) and allProps),fire(Tick)})
 run closeReuseCannotCommitTest=init.then(fire(Reserve(1))).then(fire(Close)).then(fire(Reuse)).then(fire(Finish(2))).then(all{assert(s.stale and not(s.minimized) and not(s.held) and allProps),fire(Tick)})
 run reducedReleasesFrozenPixelsTest=init.then(fire(Reserve(1))).then(fire(Reduce(1))).then(all{assert(not(s.held) and not(s.minimized) and allProps),fire(Ready(2))})
 run reloadReleasesFrozenPixelsTest=init.then(fire(Reserve(1))).then(fire(Reload(1))).then(all{assert(not(s.held) and not(s.minimized) and allProps),fire(Ready(2))})
 run rejectionHasNoNativeAuthorityTest=init.then(fire(Reserve(1))).then(fire(Reject(2))).then(all{assert(not(s.held) and s.minimized and allProps),fire(Ready(2))})
 run replacementDuringHoldCannotSettleTest=init.then(fire(Reserve(1))).then(fire(Replace)).then(fire(Timeout(2))).then(all{assert(not(s.minimized) and not(s.held) and allProps),fire(Ready(2))})
 run deadlineRevalidatesReservedIdentityTest=init.then(fire(Reserve(1))).then(fire(Timeout(2))).then(all{assert(s.minimized and not(s.held) and allProps),fire(Ready(2))})
 run liveCancelledEpochNeverExpiresTest=init.then(fire(Reserve(1))).then(fire(Validate(2))).then(fire(Reject(2))).then(fire(Tick)).then(fire(Tick)).then(fire(Begin(2))).then(all{assert(s.stale and s.phase=="idle" and not(s.held) and allProps),fire(Tick)})
 run reversalDuringPreparationRetainsVisiblePixelsTest=init.then(fire(Reserve(1))).then(fire(Reserve(1))).then(fire(Validate(3))).then(fire(Begin(3))).then(all{assert(s.pixels==99 and s.from==37 and allProps),fire(Ready(3))})
}
